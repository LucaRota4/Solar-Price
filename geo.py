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


def contains(ring, lon, lat) -> bool:
    inside = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        if (y1 > lat) != (y2 > lat) and lon < x1 + (lat - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


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


def panel_layout(face: dict, pw: float, pl: float, margin: float, gap: float = 0.02) -> list[list[list[float]]]:
    """Panneaux posés en grille dans le contour réel du pan, en portrait ou en paysage (le plus
    de panneaux des deux). Renvoie un contour [[lon, lat], ...] par panneau.

    Repère du pan : s le long du faîte, d dans la pente (en projection au sol, d'où le
    cos(inclinaison) sur la longueur des panneaux). Un panneau est gardé si ses quatre coins,
    élargis de la marge, sont dans le contour.
    """
    ring = face["ring"]
    lon0, lat0 = ring[0]
    k = math.cos(math.radians(lat0)) * M_PER_DEG_LAT
    a = math.radians(face["azimuth"])
    u = (math.cos(a), -math.sin(a))  # le long du faîte
    v = (-math.sin(a), -math.cos(a))  # dans la pente
    pts = [((x - lon0) * k, (y - lat0) * M_PER_DEG_LAT) for x, y in ring]
    poly = [(p[0] * u[0] + p[1] * u[1], p[0] * v[0] + p[1] * v[1]) for p in pts]
    s_min, s_max = min(p[0] for p in poly), max(p[0] for p in poly)
    d_min, d_max = min(p[1] for p in poly), max(p[1] for p in poly)
    cos_t = math.cos(math.radians(face["tilt"]))
    m_s, m_d = margin, margin * cos_t

    def grid(ws, wd):  # ws, wd : taille du panneau le long du faîte et dans la pente (projetée)
        ns = int((s_max - s_min - 2 * m_s + gap) // (ws + gap))
        nd = int((d_max - d_min - 2 * m_d + gap * cos_t) // (wd + gap * cos_t))
        s0 = s_min + (s_max - s_min - ns * (ws + gap) + gap) / 2  # grille centrée
        d0 = d_min + (d_max - d_min - nd * (wd + gap * cos_t) + gap * cos_t) / 2
        out = []
        for i in range(max(ns, 0)):
            for j in range(max(nd, 0)):
                s, d = s0 + i * (ws + gap), d0 + j * (wd + gap * cos_t)
                corners = [(s, d), (s + ws, d), (s + ws, d + wd), (s, d + wd)]
                padded = [(s - m_s, d - m_d), (s + ws + m_s, d - m_d), (s + ws + m_s, d + wd + m_d),
                          (s - m_s, d + wd + m_d)]
                if all(contains(poly, ps, pd) for ps, pd in padded):
                    out.append(corners)
        return out

    rects = max(grid(pw, pl * cos_t), grid(pl, pw * cos_t), key=len)
    to_lonlat = lambda s, d: [lon0 + (s * u[0] + d * v[0]) / k,  # noqa: E731
                              lat0 + (s * u[1] + d * v[1]) / M_PER_DEG_LAT]
    return [[to_lonlat(s, d) for s, d in r] for r in rects]


