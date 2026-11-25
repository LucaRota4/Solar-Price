"""Adresse -> coordonnées, et pans de toit du cadastre solaire suisse (sonnendach.ch, OFEN).

Sources (geo.admin.ch, sans clé) :
  - SearchServer : géocodage des adresses suisses
  - identify sur la couche ch.bfe.solarenergie-eignung-daecher : un objet par pan de toit,
    avec surface, inclinaison, orientation et classe d'aptitude.

Convention d'orientation (identique à PVGIS et Open-Meteo) : 0° = sud, -90° = est,
90° = ouest, ±180° = nord.
"""
import math
import re

from http_cache import get_json

API = "https://api3.geo.admin.ch/rest/services/api"
ROOF_LAYER = "ch.bfe.solarenergie-eignung-daecher"
M_PER_DEG_LAT = 111_320


def search_address(text: str, limit: int = 6) -> list[dict]:
    data = get_json(
        f"{API}/SearchServer",
        {"searchText": text, "type": "locations", "origins": "address", "sr": 4326, "limit": limit},
        source="geo.admin.ch",
    )
    return [
        {
            "label": re.sub(r"<[^>]+>", "", r["attrs"]["label"]),
            "lat": r["attrs"]["lat"],
            "lon": r["attrs"]["lon"],
        }
        for r in data.get("results", [])
    ]


def _outer_ring(geom: dict) -> list[list[float]]:
    coords = geom["coordinates"]
    return coords[0][0] if geom["type"] == "MultiPolygon" else coords[0]


def roofs_around(lat: float, lon: float, radius_m: float = 50) -> list[dict]:
    """Tous les pans de toit dans un carré de ±radius_m autour du point."""
    dlat = radius_m / M_PER_DEG_LAT
    dlon = radius_m / (M_PER_DEG_LAT * math.cos(math.radians(lat)))
    env = f"{lon - dlon},{lat - dlat},{lon + dlon},{lat + dlat}"
    data = get_json(
        f"{API}/MapServer/identify",
        {
            "geometryType": "esriGeometryEnvelope",
            "geometry": env,
            "sr": 4326,
            "layers": f"all:{ROOF_LAYER}",
            "tolerance": 0,
            "mapExtent": env,
            "imageDisplay": "500,500,96",
            "returnGeometry": "true",
            "geometryFormat": "geojson",
            "lang": "fr",
            "limit": 200,
        },
        source="geo.admin.ch",
    )
    faces = []
    for f in data.get("results", []):
        a = f.get("properties") or f.get("attributes") or {}
        if f.get("id", 0) < 0 or "neigung" not in a:  # -99 = objet « échelle trop petite »
            continue
        if float(a["flaeche"]) < 1:  # pans dégénérés (arêtes) présents dans le cadastre
            continue
        faces.append(
            {
                "id": f["id"],
                "building_id": a["building_id"],
                "area": float(a["flaeche"]),
                "tilt": float(a["neigung"]),
                "azimuth": float(a["ausrichtung"]),
                "klasse": int(a["klasse"]),
                "irradiation": float(a.get("mstrahlung") or 0),  # kWh/m²/an sur le pan
                "ring": _outer_ring(f["geometry"]),
            }
        )
    return faces


CELL_M = 100  # côté d'une case de chargement des toits
_K_LON = M_PER_DEG_LAT * math.cos(math.radians(47))  # grille fixe, calée sur la latitude de la Suisse


def cells_in_view(south: float, west: float, north: float, east: float) -> list[tuple[int, int]]:
    """Cases de 100 m (indices entiers) qui recouvrent la vue de la carte."""
    dlat, dlon = CELL_M / M_PER_DEG_LAT, CELL_M / _K_LON
    return [(i, j) for i in range(math.floor(west / dlon), math.floor(east / dlon) + 1)
            for j in range(math.floor(south / dlat), math.floor(north / dlat) + 1)]


def cell_center(cell: tuple[int, int]) -> tuple[float, float]:
    """(lat, lon) du centre d'une case."""
    i, j = cell
    return (j + 0.5) * CELL_M / M_PER_DEG_LAT, (i + 0.5) * CELL_M / _K_LON


def contains(ring, lon, lat) -> bool:
    inside = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        if (y1 > lat) != (y2 > lat) and lon < x1 + (lat - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def coverage(a, b, n: int = 14) -> float:
    """Part (0..1) de la surface du contour a recouverte par le contour b, par échantillonnage en grille."""
    ax, ay = [p[0] for p in a], [p[1] for p in a]
    bx, by = [p[0] for p in b], [p[1] for p in b]
    if max(ax) < min(bx) or min(ax) > max(bx) or max(ay) < min(by) or min(ay) > max(by):
        return 0.0
    pts = [(min(ax) + (max(ax) - min(ax)) * (i + 0.5) / n, min(ay) + (max(ay) - min(ay)) * (j + 0.5) / n)
           for i in range(n) for j in range(n)]
    inside = [p for p in pts if contains(a, *p)]
    return sum(contains(b, *p) for p in inside) / len(inside) if inside else 0.0


def _centroid(ring):
    return sum(p[0] for p in ring) / len(ring), sum(p[1] for p in ring) / len(ring)


def buildings_by_distance(faces: list[dict], lat: float, lon: float) -> list[int]:
    """Identifiants des bâtiments, celui sous l'adresse d'abord, puis du plus proche au plus loin."""
    k = math.cos(math.radians(lat))
    dist = {}
    for f in faces:
        if contains(f["ring"], lon, lat):
            d = 0.0
        else:
            cx, cy = _centroid(f["ring"])
            d = math.hypot((cx - lon) * k, cy - lat) * M_PER_DEG_LAT
        dist[f["building_id"]] = min(d, dist.get(f["building_id"], math.inf))
    return sorted(dist, key=dist.get)


def ring_area(ring) -> float:
    """Surface horizontale (m²) d'un contour [[lon, lat], ...]."""
    lon0, lat0 = ring[0]
    k = math.cos(math.radians(lat0)) * M_PER_DEG_LAT
    pts = [((x - lon0) * k, (y - lat0) * M_PER_DEG_LAT) for x, y in ring]
    return abs(sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]))) / 2


def _local(ring):
    lon0, lat0 = ring[0]
    k = math.cos(math.radians(lat0)) * M_PER_DEG_LAT
    return [((x - lon0) * k, (y - lat0) * M_PER_DEG_LAT) for x, y in ring]


def plane_heights(ring, tilt: float, azimuth: float) -> list[float]:
    """Hauteur (m) de chaque sommet pour un plan d'inclinaison et d'orientation donnés : le point le plus
    bas du contour est à 0, le reste monte vers le haut de la pente."""
    a = math.radians(azimuth)
    down = (-math.sin(a), -math.cos(a))  # direction de la pente, vers le bas
    d = [x * down[0] + y * down[1] for x, y in _local(ring)]
    return [round((max(d) - v) * math.tan(math.radians(tilt)), 2) for v in d]


def plane_tilt_azimuth(ring, heights) -> tuple[float, float | None]:
    """Plan z = a·x + b·y + c ajusté (moindres carrés) sur les sommets et leurs hauteurs : renvoie
    (inclinaison en °, orientation en ° avec 0 = sud, ou None si le plan est horizontal)."""
    import numpy as np

    pts = np.array(_local(ring))
    design = np.c_[pts, np.ones(len(pts))]
    (a, b, _), *_ = np.linalg.lstsq(design, np.array(heights, dtype=float), rcond=None)
    slope = math.hypot(a, b)
    if slope < 1e-4:
        return 0.0, None
    return math.degrees(math.atan(slope)), math.degrees(math.atan2(a, b))  # la pente descend vers (-a, -b)


def dist_m(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Distance approximative en mètres entre deux points (lon, lat)."""
    k = math.cos(math.radians((lat1 + lat2) / 2))
    return math.hypot((lon2 - lon1) * k, lat2 - lat1) * M_PER_DEG_LAT


def plane_z(ring, tilt: float, azimuth: float, lon: float, lat: float) -> float:
    """Hauteur (m) au point (lon, lat) du plan d'un pan du cadastre (inclinaison, orientation) dont le point le
    plus bas est à 0 : même convention que plane_heights."""
    a = math.radians(azimuth)
    down = (-math.sin(a), -math.cos(a))
    d = [x * down[0] + y * down[1] for x, y in _local(ring)]
    lon0, lat0 = ring[0]
    k = math.cos(math.radians(lat0)) * M_PER_DEG_LAT
    dp = (lon - lon0) * k * down[0] + (lat - lat0) * M_PER_DEG_LAT * down[1]
    return (max(d) - dp) * math.tan(math.radians(tilt))


def fit_plane_z(ring, heights, lon: float, lat: float) -> float:
    """Hauteur (m) au point (lon, lat) du plan ajusté sur les sommets d'un pan et leurs hauteurs."""
    import numpy as np

    pts = np.array(_local(ring))
    design = np.c_[pts, np.ones(len(pts))]
    (a, b, c), *_ = np.linalg.lstsq(design, np.array(heights, dtype=float), rcond=None)
    lon0, lat0 = ring[0]
    k = math.cos(math.radians(lat0)) * M_PER_DEG_LAT
    return float(a * (lon - lon0) * k + b * (lat - lat0) * M_PER_DEG_LAT + c)


def face_dimensions(face: dict) -> tuple[float, float]:
    """Dimensions approximatives du pan (largeur le long du faîte, longueur dans la pente), en m.

    Projection du contour sur l'axe de la pente et sur l'axe perpendiculaire, puis
    correction de l'inclinaison pour la longueur. Exact pour un pan rectangulaire,
    approximatif sinon (à ajuster à la main en mode détaillé).
    """
    ring = face["ring"]
    lon0, lat0 = ring[0]
    k = math.cos(math.radians(lat0)) * M_PER_DEG_LAT
    pts = [((x - lon0) * k, (y - lat0) * M_PER_DEG_LAT) for x, y in ring]
    a = math.radians(face["azimuth"])
    down = (-math.sin(a), -math.cos(a))  # direction de la pente (vers où le pan regarde)
    along = (math.cos(a), -math.sin(a))
    proj = lambda v: [p[0] * v[0] + p[1] * v[1] for p in pts]  # noqa: E731
    depth = max(proj(down)) - min(proj(down))
    width = max(proj(along)) - min(proj(along))
    length = depth / max(math.cos(math.radians(face["tilt"])), 0.2)
    return round(width, 1), round(length, 1)


def _frame(face: dict):
    """Repère local du pan : mètres autour du premier point, s le long du faîte (vers la droite vu
    de l'extérieur), d dans la pente (vers le bas, en projection au sol)."""
    lon0, lat0 = face["ring"][0]
    k = math.cos(math.radians(lat0)) * M_PER_DEG_LAT
    a = math.radians(face["azimuth"])
    u = (math.cos(a), -math.sin(a))
    v = (-math.sin(a), -math.cos(a))

    def to_sd(lon, lat):
        x, y = (lon - lon0) * k, (lat - lat0) * M_PER_DEG_LAT
        return x * u[0] + y * u[1], x * v[0] + y * v[1]

    def to_lonlat(s, d):
        return [lon0 + (s * u[0] + d * v[0]) / k, lat0 + (s * u[1] + d * v[1]) / M_PER_DEG_LAT]

    return to_sd, to_lonlat


def obstacle_rect(face: dict, ob: dict) -> list[list[float]]:
    """Contour [[lon, lat], ...] d'un obstacle (centre, largeur le long du faîte, longueur dans la pente)."""
    to_sd, to_lonlat = _frame(face)
    s, d = to_sd(ob["lon"], ob["lat"])
    hw, hl = ob["w"] / 2, ob["l"] * math.cos(math.radians(face["tilt"])) / 2
    return [to_lonlat(s + a, d + b) for a, b in ((-hw, -hl), (hw, -hl), (hw, hl), (-hw, hl))]


def panel_layout(face: dict, pw: float, pl: float, margin: float, gap: float = 0.02, shift=(0.0, 0.0),
                 obstacles=(), clearance: float = 0.1, snap: float = 0.12):
    """Panneaux posés en grille dans le contour réel du pan, en portrait ou en paysage (le plus
    de panneaux des deux). Renvoie (contours [[lon, lat], ...], décalage effectif (s, d) en m).

    Repère du pan : s le long du faîte, d dans la pente (en projection au sol, d'où le
    cos(inclinaison) sur la longueur des panneaux). Un panneau est gardé si ses quatre coins,
    élargis de la marge, sont dans le contour, et s'il ne touche aucun obstacle (dégagement
    `clearance` autour). Le choix portrait/paysage est fait sans décalage.

    Décalage : la grille se déplace de `shift`, bornée par les marges du pan, avec une
    aimantation (rayon `snap`) sur : bord gauche/droit/haut/bas, centre, et bords des obstacles.
    """
    to_sd, to_lonlat = _frame(face)
    poly = [to_sd(x, y) for x, y in face["ring"]]
    s_min, s_max = min(p[0] for p in poly), max(p[0] for p in poly)
    d_min, d_max = min(p[1] for p in poly), max(p[1] for p in poly)
    cos_t = math.cos(math.radians(face["tilt"]))
    m_s, m_d = margin, margin * cos_t
    obs = []  # rectangles (s0, s1, d0, d1) agrandis du dégagement
    for ob in obstacles:
        s, d = to_sd(ob["lon"], ob["lat"])
        hw, hl = ob["w"] / 2 + clearance, ob["l"] * cos_t / 2 + clearance
        obs.append((s - hw, s + hw, d - hl, d + hl))

    def grid(ws, wd):
        ns = int((s_max - s_min - 2 * m_s + gap) // (ws + gap))
        nd = int((d_max - d_min - 2 * m_d + gap * cos_t) // (wd + gap * cos_t))
        ns, nd = max(ns, 0), max(nd, 0)
        ps, pd = ws + gap, wd + gap * cos_t  # pas de la grille
        s0 = s_min + (s_max - s_min - ns * ps + gap) / 2  # grille centrée
        d0 = d_min + (d_max - d_min - nd * pd + gap * cos_t) / 2
        return ns, nd, ps, pd, s0, d0

    def cells(ws, wd, ds=0.0, dd=0.0):
        ns, nd, ps, pd, s0, d0 = grid(ws, wd)
        out = []
        for i in range(ns):
            for j in range(nd):
                s, d = s0 + ds + i * ps, d0 + dd + j * pd
                padded = [(s - m_s, d - m_d), (s + ws + m_s, d - m_d), (s + ws + m_s, d + wd + m_d),
                          (s - m_s, d + wd + m_d)]
                if not all(contains(poly, a, b) for a, b in padded):
                    continue
                if any(s < o1 and s + ws > o0 and d < q1 and d + wd > q0 for o0, o1, q0, q1 in obs):
                    continue
                out.append([(s, d), (s + ws, d), (s + ws, d + wd), (s, d + wd)])
        return out

    (ws, wd) = max(((pw, pl * cos_t), (pl, pw * cos_t)), key=lambda w: len(cells(*w)))

    def snapped(value, lo, hi, targets):
        value = min(max(value, lo), hi) if lo <= hi else 0.0
        near = min(targets, key=lambda c: abs(c - value), default=None)
        return near if near is not None and abs(near - value) <= snap else value

    ns, nd, ps, pd, s0, d0 = grid(ws, wd)
    # Plage permise : le bloc de panneaux reste à l'intérieur des marges du pan
    s_lo, s_hi = s_min + m_s - s0, s_max - m_s - (s0 + ns * ps - gap)
    d_lo, d_hi = d_min + m_d - d0, d_max - m_d - (d0 + nd * pd - gap * cos_t)
    s_tg, d_tg = [0.0, s_lo, s_hi], [0.0, d_lo, d_hi]
    for o0, o1, q0, q1 in obs:  # bord d'une colonne/rangée collé au bord de l'obstacle
        for i in range(ns + 1):
            s_tg += [o0 - (s0 + i * ps - gap), o1 - (s0 + i * ps)]
        for j in range(nd + 1):
            d_tg += [q0 - (d0 + j * pd - gap * cos_t), q1 - (d0 + j * pd)]
    s_tg = [c for c in s_tg if s_lo <= c <= s_hi]
    d_tg = [c for c in d_tg if d_lo <= c <= d_hi]
    ds = snapped(shift[0], s_lo, s_hi, s_tg)
    dd = snapped(shift[1], d_lo, d_hi, d_tg)
    return [[to_lonlat(s, d) for s, d in r] for r in cells(ws, wd, ds, dd)], (ds, dd)
