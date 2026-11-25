"""Estimation solaire : adresse -> toit -> pans équipés -> production annuelle."""
import math
import re

import folium
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from branca.element import MacroElement
from jinja2 import Template
from folium.plugins import Draw
from streamlit_folium import st_folium

from search_box import address_box

import geo
import pv
from http_cache import ApiError
from i18n import kwh, klass, lang, months, orientation, t, t_fixed

# Palette des graphiques (mode sombre) : encre, grille, séries
INK, INK2, MUTED, GRID, AXIS = "#f0efec", "#c3c2b7", "#898781", "#2c2c2a", "#383835"
BLUE, ORANGE = "#3987e5", "#d95926"
BAND = "rgba(57,135,229,0.22)"
# Carte : pans équipés en bleu, aptitude en rampe chaude (faible -> excellente)
PANEL = "#3987e5"
CLASS_COLORS = {1: "#d9d6cc", 2: "#e9cf8e", 3: "#e0a35a", 4: "#c96f3b", 5: "#9c4424"}
SWISSIMAGE = "https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.swissimage/default/current/3857/{z}/{x}/{y}.jpeg"
OSM_PLAN = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"  # plan avec rues et numéros de maison
MAP_HEIGHT = 580
SWISS_CENTER, SWISS_ZOOM = (46.82, 8.23), 8
OBSTACLE = "#ff8c1a"
CUSTOM = "#a78bfa"  # pans dessinés à la main
STEP = 0.25  # pas du décalage des panneaux, en m
OBSTACLE_PRESETS = {"obst_velux": (0.78, 1.40), "obst_chimney": (0.6, 0.6)}  # largeur, longueur dans la pente


class Compass(MacroElement):
    """Boussole (nord en haut) dans le coin supérieur droit de la carte."""

    _template = Template("""
{% macro script(this, kwargs) %}
var compass = L.control({position: 'topright'});
compass.onAdd = function () {
  var d = L.DomUtil.create('div');
  // Pas de fond : une ombre portée suffit à rester lisible sur la vue aérienne comme sur le plan
  d.style.cssText = 'filter:drop-shadow(0 1px 2px rgba(0,0,0,.85)) drop-shadow(0 0 4px rgba(0,0,0,.5));'
    + 'pointer-events:none;';
  d.innerHTML = '<svg width="58" height="72" viewBox="0 0 34 42" aria-label="N">'
    + '<text x="17" y="10" text-anchor="middle" font-size="11" font-weight="700" fill="#ffffff" '
    + 'font-family="Inter, sans-serif">N</text>'
    + '<polygon points="17,13 23,27 17,24.5 11,27" fill="#e4572e" stroke="#ffffff" stroke-width=".6"/>'
    + '<polygon points="17,41 23,27 17,29.5 11,27" fill="#f0efec" stroke="#ffffff" stroke-width=".6"/></svg>';
  return d;
};
compass.addTo({{ this._parent.get_name() }});
{% endmacro %}
""")


class DragEnd(MacroElement):
    """Marqueurs déplaçables : quand on en lâche un, ou quand on valide la hauteur saisie dans son champ, déclenche
    un « clic » sur le marqueur. streamlit-folium renvoie à Python la position et l'infobulle du dernier objet
    cliqué : on y ajoute un texte caché (« @drag », et « @h:id:valeur » pour une hauteur) pour distinguer ces
    gestes d'un vrai clic, puis on remet l'infobulle d'origine."""

    _template = Template("""
{% macro script(this, kwargs) %}
{{ this._parent.get_name() }}.eachLayer(function (l) {
  if (!(l instanceof L.Marker) || !l.options.draggable) return;
  function emit(m, extra) {
    var tt = m.getTooltip();
    if (!tt) return;
    var orig = tt.getContent();
    m.setTooltipContent(orig + extra + '<span style="display:none">@drag</span>');
    m.fire('click', {latlng: m.getLatLng(), sourceTarget: m, target: m});
    m.setTooltipContent(orig);
  }
  l.on('dragend', function (e) { emit(e.target, ''); });
  l.on('add', function () {  // champ de hauteur à côté du point
    var inp = l._icon && l._icon.querySelector('input');
    if (!inp) return;
    ['mousedown', 'touchstart', 'click', 'dblclick', 'keydown', 'keyup', 'wheel'].forEach(function (ev) {
      L.DomEvent.on(inp, ev, L.DomEvent.stopPropagation);  // ni glissement du point ni de la carte en tapant
    });
    inp.addEventListener('keydown', function (e) { if (e.key === 'Enter') inp.blur(); });
    inp.addEventListener('change', function () {
      if (inp.value === '' || isNaN(parseFloat(inp.value))) return;
      emit(l, '<span style="display:none">@h:' + inp.dataset.pid + ':' + parseFloat(inp.value) + '</span>');
    });
  });
});
{% endmacro %}
""")


class Legend(MacroElement):
    """Légende en bas à gauche : couleur de l'aptitude du toit (cadastre solaire), pans équipés, obstacles."""

    _template = Template("""
{% macro script(this, kwargs) %}
var legend = L.control({position: 'bottomleft'});
legend.onAdd = function () {
  var d = L.DomUtil.create('div');
  d.style.cssText = 'background:rgba(20,23,28,.88);color:#f0efec;padding:8px 11px;border-radius:6px;'
    + 'font:12px/1.55 Inter,system-ui,sans-serif;box-shadow:0 1px 4px rgba(0,0,0,.5);';
  d.innerHTML = {{ this.html|tojson }};
  return d;
};
legend.addTo({{ this._parent.get_name() }});
{% endmacro %}
""")

    def __init__(self, items, title):
        super().__init__()
        self._name = "Legend"
        row = ('<div><span style="display:inline-block;width:12px;height:12px;border-radius:2px;margin-right:7px;'
               'vertical-align:-1px;background:{c};border:1px solid rgba(255,255,255,.6)"></span>{label}</div>')
        self.html = (f'<div style="font-weight:600;margin-bottom:2px">{title}</div>'
                     + "".join(row.format(c=c, label=label) for c, label in items))


def base_map(center, zoom, legend=True, draw=False, bounds=None):
    """Carte limitée à la Suisse : vue aérienne swisstopo (par défaut) ou plan avec rues et numéros,
    au choix dans la carte. Boussole, sans échelle."""
    fmap = folium.Map(location=center, zoom_start=zoom, min_zoom=7, max_zoom=23, tiles=None, control_scale=False,
                      max_bounds=True, min_lat=45.4, max_lat=48.2, min_lon=5.4, max_lon=11.0)
    folium.TileLayer(SWISSIMAGE, attr="© swisstopo", name=t("map_satellite"), max_native_zoom=20,
                     max_zoom=23).add_to(fmap)
    folium.TileLayer(OSM_PLAN, attr="© OpenStreetMap", name=t("map_plan"), max_native_zoom=19,
                     max_zoom=23, show=False).add_to(fmap)
    folium.LayerControl(position="topleft", collapsed=False).add_to(fmap)
    Compass().add_to(fmap)
    if draw:  # polygones et rectangles seulement, sans les boutons d'édition ni de suppression
        Draw(draw_options={"polyline": False, "circle": False, "marker": False, "circlemarker": False,
                           "polygon": {"shapeOptions": {"color": CUSTOM}}, "rectangle": {"shapeOptions": {"color": CUSTOM}}},
             edit_options={"edit": False, "remove": False}).add_to(fmap)
    if bounds:
        fmap.fit_bounds(bounds, padding=(30, 30))
    if legend:
        items = [(CLASS_COLORS[k], klass(k)) for k in range(1, 6)]
        Legend(items + [(PANEL, t("legend_panels")), (OBSTACLE, t("legend_obstacle"))],
               t("col_class")).add_to(fmap)
    return fmap


@st.cache_data(show_spinner=False)
def search(text):
    return geo.search_address(text)


@st.cache_data(show_spinner=False)
def roofs(lat, lon, radius=50):
    return geo.roofs_around(lat, lon, radius)


@st.cache_data(show_spinner=False)
def pvgis(lat, lon, tilt, az, loss):
    return pv.pvgis_monthly(lat, lon, tilt, az, loss)


def fail(e: ApiError):
    st.error(t("api_error", source=e.source, detail=e.detail), icon=":material/cloud_off:")
    st.stop()


def style(fig, title, ytitle, height=320):
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color=INK)),
        template="plotly_dark",
        height=height,
        margin=dict(l=8, r=8, t=44, b=8),
        font=dict(family="Inter, system-ui, -apple-system, Segoe UI, sans-serif", color=INK2, size=13),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", x=0, y=1.12, font=dict(color=INK2)),
        hoverlabel=dict(bgcolor="#1a1a19", font_color=INK, bordercolor="#383835"),
        bargap=0.3,
        barcornerradius=4,
    )
    fig.update_yaxes(title=ytitle, gridcolor=GRID, zeroline=False, linecolor=AXIS, tickfont_color=MUTED)
    fig.update_xaxes(showgrid=False, linecolor=AXIS, tickfont_color=MUTED)
    return fig


def fit_panels(width, length, pw, pl, margin, gap=0.02):
    """Nombre de panneaux sur un pan rectangulaire, en portrait ou en paysage (le meilleur des deux)."""
    w, l = width - 2 * margin, length - 2 * margin
    if w <= 0 or l <= 0:
        return 0
    n = lambda a, b: math.floor((w + gap) / (a + gap)) * math.floor((l + gap) / (b + gap))  # noqa: E731
    return max(n(pw, pl), n(pl, pw))


# ---- En-tête et adresse -----------------------------------------------------------------------
st.markdown(f'<div class="eyebrow">{t("nav_estimate")}</div>', unsafe_allow_html=True)
st.title(t("est_title"))
st.markdown(f'<p class="lead">{t("est_intro")}</p>', unsafe_allow_html=True)


CUSTOM_ID0 = 10**9  # identifiants des pans dessinés (les pans du cadastre sont bien plus petits)
store = st.session_state.setdefault("face_store", {})  # tous les pans chargés depuis le début (id -> pan)
custom = st.session_state.setdefault("custom_faces", [])  # pans dessinés à la main
seen_drawings = st.session_state.setdefault("seen_drawings", set())
st.session_state.setdefault("sel_faces", [])  # pans choisis (ids), dans l'ordre du choix
st.session_state.setdefault("cells_loaded", set())  # cases de 100 m dont les toits sont chargés
st.session_state.setdefault("show_panels", False)  # les panneaux ne sont posés qu'après « Suivant »
st.session_state.setdefault("obstacles", [])  # {lon, lat, w, l, face_id, kind}
st.session_state.setdefault("epoch", 0)  # change quand il faut recréer la carte (efface le tracé en cours)
st.session_state.setdefault("custom_n", 0)
st.session_state.setdefault("points", {})  # points partagés des pans dessinés : id -> [lon, lat, hauteur]
st.session_state.setdefault("point_n", 0)
st.session_state.setdefault("z_ver", 0)  # change quand le programme (et non l'utilisateur) modifie des hauteurs
st.session_state.setdefault("shifts", {})  # face_id -> décalage (s, d) en m du champ de panneaux


def valid_bounds(b) -> bool:
    """Vue de la carte renvoyée par le composant : vide ou à None tant que la carte n'est pas affichée."""
    try:
        return all(isinstance(b[k][c], (int, float)) for k in ("_southWest", "_northEast") for c in ("lat", "lng"))
    except (TypeError, KeyError):
        return False


def load_cells(bounds, limit=4) -> int:
    """Charge les toits des cases de 100 m qui recouvrent la vue de la carte (au plus `limit` par tour).
    Renvoie le nombre de cases chargées."""
    sw, ne = bounds["_southWest"], bounds["_northEast"]
    todo = [c for c in geo.cells_in_view(sw["lat"], sw["lng"], ne["lat"], ne["lng"])
            if c not in st.session_state.cells_loaded][:limit]
    for c in todo:
        try:
            store.update({f["id"]: f for f in roofs(*geo.cell_center(c), 55)})
        except ApiError as e:
            fail(e)
        st.session_state.cells_loaded.add(c)
    return len(todo)


def handle_click(out, tool) -> bool:
    """Clic sur la carte, selon l'outil : ajouter/retirer un pan (de n'importe quel bâtiment), poser ou
    supprimer un obstacle. True si quelque chose a changé."""
    click = (out or {}).get("last_clicked")
    if not click or tool == "draw":  # en mode dessin, les clics sont les sommets du polygone
        return False
    pos = (round(click["lat"], 7), round(click["lng"], 7))
    if st.session_state.get("last_click") == pos:  # clic déjà traité lors d'une exécution précédente
        return False
    st.session_state.last_click = pos
    c_lat, c_lon = pos
    find = lambda: next((f for f in store.values() if geo.contains(f["ring"], c_lon, c_lat)), None)  # noqa: E731
    hit = find()
    if tool == "faces":
        if hit is None:  # toit pas encore chargé : on charge les toits autour du clic
            try:
                store.update({f["id"]: f for f in roofs(c_lat, c_lon)})
            except ApiError as e:
                fail(e)
            hit = find()
            if hit is None:
                st.toast(t("click_no_roof"), icon=":material/roofing:")
                return False
            if not st.session_state.get("loc"):
                st.session_state.loc = {"lat": c_lat, "lon": c_lon}
        if hit["building_id"] == -1:  # pan dessiné : géré dans le panneau de dessin
            return False
        sel = st.session_state.sel_faces
        if hit["id"] in sel:  # un second clic retire le pan
            sel.remove(hit["id"])
        else:
            sel.append(hit["id"])
        return True
    if tool == "add":
        if hit is None:
            st.toast(t("click_no_face"), icon=":material/roofing:")
            return False
        st.session_state.obstacles.append({"lon": c_lon, "lat": c_lat, "w": st.session_state.obst_w,
                                           "l": st.session_state.obst_l, "face_id": hit["id"],
                                           "kind": st.session_state.obst_kind})
        return True
    if tool != "del":
        return False
    obstacles = st.session_state.obstacles  # le dernier posé qui contient le clic
    for ob in reversed(obstacles):
        if geo.contains(geo.obstacle_rect(store[ob["face_id"]], ob), c_lon, c_lat):
            obstacles.remove(ob)
            return True
    st.toast(t("click_no_obstacle"), icon=":material/roofing:")
    return False


SNAP_M = 0.6  # rayon d'aimantation des coins entre pans dessinés, en m


def new_point(lon, lat, z) -> int:
    st.session_state.point_n += 1
    st.session_state.points[st.session_state.point_n] = [lon, lat, round(float(z), 2)]
    return st.session_state.point_n


def sync_custom():
    """Contour, hauteurs, inclinaison et orientation des pans dessinés, relus depuis leurs points : un point
    partagé entre deux pans n'a qu'une position et qu'une hauteur."""
    pts = st.session_state.points
    for f in custom:
        if "pids" not in f:  # pan d'une ancienne session : on crée ses points
            f["pids"] = [new_point(x, y, z) for (x, y), z in zip(f["ring"], f["z"])]
        f["ring"] = [[pts[p][0], pts[p][1]] for p in f["pids"]]
        f["z"] = [pts[p][2] for p in f["pids"]]
        f["tilt"], az = geo.plane_tilt_azimuth(f["ring"], f["z"])
        if az is not None:
            f["azimuth"] = az
        f["area"] = geo.ring_area(f["ring"]) / max(math.cos(math.radians(f["tilt"])), 0.2)


def nearest_point(lon, lat, exclude=()):
    """Point existant à moins de SNAP_M (le plus proche), hors `exclude`."""
    best = None
    for pid, (x, y, _) in st.session_state.points.items():
        d = geo.dist_m(lon, lat, x, y)
        if pid not in exclude and d <= SNAP_M and (best is None or d < best[0]):
            best = (d, pid)
    return best[1] if best else None


def neighbor_z(lon, lat, exclude=(), main=None, drawn_only=False):
    """Hauteur du toit voisin au point (lon, lat) : les pans dessinés d'abord (hauteurs réglées à la main), puis le
    pan du cadastre sous le tracé, puis les autres. None s'il n'y a pas de toit à cet endroit."""
    for f in custom:
        if f["id"] not in exclude and geo.contains(f["ring"], lon, lat):
            return geo.fit_plane_z(f["ring"], f["z"], lon, lat)
    if drawn_only:
        return None
    for f in ([main] if main else []) + [f for f in store.values() if not f.get("custom") and f is not main]:
        if geo.contains(f["ring"], lon, lat):
            return geo.plane_z(f["ring"], f["tilt"], f["azimuth"], lon, lat)
    return None


def side_length(a, b) -> float:
    """Longueur réelle (3D, hauteurs comprises) du côté entre les points a et b."""
    pts = st.session_state.points
    h = geo.dist_m(pts[a][0], pts[a][1], pts[b][0], pts[b][1])
    return math.hypot(h, pts[b][2] - pts[a][2])


def resize_side(f, i, length):
    """Donne au côté i (du point i au point i+1) du pan dessiné f la longueur réelle `length` : les hauteurs restent
    fixes, le côté s'allonge ou se raccourcit à l'horizontale et tous les points de son côté du pan suivent
    (un rectangle reste un rectangle). Les points partagés entraînent les pans voisins."""
    pts, ids = st.session_state.points, f["pids"]
    a, b = ids[i], ids[(i + 1) % len(ids)]
    k = math.cos(math.radians(pts[a][1])) * geo.M_PER_DEG_LAT
    vx, vy = (pts[b][0] - pts[a][0]) * k, (pts[b][1] - pts[a][1]) * geo.M_PER_DEG_LAT
    h = math.hypot(vx, vy)
    if h < 1e-6:
        return
    h_new = math.sqrt(max(length ** 2 - (pts[b][2] - pts[a][2]) ** 2, 0.04))  # au moins 20 cm à l'horizontale
    ux, uy = vx / h, vy / h
    proj = lambda p: (pts[p][0] - pts[a][0]) * k * ux + (pts[p][1] - pts[a][1]) * geo.M_PER_DEG_LAT * uy  # noqa: E731
    centre = sum(proj(p) for p in ids) / len(ids)
    for p in {b} | {p for p in ids if p != a and proj(p) > centre}:
        pts[p][0] += ux * (h_new - h) / k
        pts[p][1] += uy * (h_new - h) / geo.M_PER_DEG_LAT


def resize_face(f, ks, kd):
    """Étire le pan dessiné f de ks le long du faîte et de kd dans la pente, autour de son centre. Les hauteurs
    restent fixes (l'inclinaison peut donc changer). Les points partagés entraînent les pans voisins."""
    pts, ids = st.session_state.points, f["pids"]
    cx, cy = sum(pts[p][0] for p in ids) / len(ids), sum(pts[p][1] for p in ids) / len(ids)
    k = math.cos(math.radians(cy)) * geo.M_PER_DEG_LAT
    a = math.radians(f["azimuth"])
    u, v = (math.cos(a), -math.sin(a)), (-math.sin(a), -math.cos(a))  # le long du faîte, dans la pente
    for p in ids:
        dx, dy = (pts[p][0] - cx) * k, (pts[p][1] - cy) * geo.M_PER_DEG_LAT
        s, d = (dx * u[0] + dy * u[1]) * ks, (dx * v[0] + dy * v[1]) * kd
        pts[p][0] = cx + (s * u[0] + d * v[0]) / k
        pts[p][1] = cy + (s * u[1] + d * v[1]) / geo.M_PER_DEG_LAT


def slide_face(f, dlon, dlat):
    """Fait glisser tout le pan dessiné f de (dlon, dlat) : les hauteurs de ses points ne changent pas. Ses points
    partagés avec un autre pan sont détachés (l'autre pan ne bouge pas) ; à la dépose, un coin proche d'un coin
    d'un autre pan fusionne avec lui."""
    pts, ids = st.session_state.points, f["pids"]
    others = {p for g in custom if g is not f for p in g["pids"]}
    for i, p in enumerate(ids):
        if p in others:
            ids[i] = new_point(pts[p][0], pts[p][1], pts[p][2])
    for p in ids:
        pts[p][0] += dlon
        pts[p][1] += dlat
    for i, p in enumerate(list(ids)):
        target = nearest_point(pts[p][0], pts[p][1], exclude=set(ids))
        if target is not None:
            ids[i] = target
            del pts[p]


def clear_all():
    """Efface tout : pans choisis, pans dessinés (sans rétablir les pans qu'ils remplaçaient), obstacles, positions."""
    st.session_state.sel_faces.clear()
    for f in custom:
        store.pop(f["id"], None)
    custom.clear()
    st.session_state.points = {}
    st.session_state.obstacles.clear()
    st.session_state.shifts.clear()
    st.session_state.show_panels = False
    st.session_state.epoch += 1
    st.session_state.z_ver += 1


def handle_drag(out) -> bool:
    """Coin d'un pan dessiné ou obstacle déplacé à la main (poignée lâchée ailleurs). True si on a bougé quelque
    chose. Un coin lâché près d'un coin d'un autre pan fusionne avec lui (aimantation) : un seul point, une seule
    hauteur."""
    tip = (out or {}).get("last_object_clicked_tooltip") or ""
    pos = (out or {}).get("last_object_clicked")
    m = re.search(r"@([cohf]):(\d+):(-?[\d.]+)\s*@drag", tip)
    if not m or not pos:
        return False
    key = (st.session_state.get("map_state"), out.get("last_object_clicked_count"), round(pos["lat"], 7),
           round(pos["lng"], 7))
    if st.session_state.get("last_drag") == key:  # déjà traité lors d'une exécution précédente
        return False
    st.session_state.last_drag = key
    kind, a = m.group(1), int(m.group(2))
    lon, lat = pos["lng"], pos["lat"]
    if kind == "h":  # hauteur saisie dans le champ à côté du point a
        if a not in st.session_state.points:
            return False
        st.session_state.points[a][2] = float(m.group(3))
        st.session_state.z_ver += 1
        sync_custom()
        return True
    if kind == "f":  # pan dessiné a : glissé d'un bloc, hauteurs inchangées
        face = next((f for f in custom if f["id"] == a), None)
        if face is None:
            return False
        pts = st.session_state.points
        cx = sum(pts[p][0] for p in face["pids"]) / len(face["pids"])
        cy = sum(pts[p][1] for p in face["pids"]) / len(face["pids"])
        slide_face(face, lon - cx, lat - cy)
        st.session_state.z_ver += 1
        sync_custom()
        return True
    if kind == "c":  # point a
        pts = st.session_state.points
        if a not in pts:
            return False
        mine = [f for f in custom if a in f["pids"]]
        target = nearest_point(lon, lat, exclude={p for f in mine for p in f["pids"]})  # jamais un coin du même pan
        if target is not None:
            for f in custom:
                f["pids"] = [target if p == a else p for p in f["pids"]]
            del pts[a]
        else:
            # Hauteur : le point reste dans le plan formé par les autres points de son pan (de chaque pan, s'il
            # est partagé : moyenne) ; un triangle n'a que deux autres points, on garde alors son plan d'avant
            zs = []
            for f in mine:
                rest = [p for p in f["pids"] if p != a]
                src = rest if len(rest) >= 3 else f["pids"]
                zs.append(geo.fit_plane_z([[pts[p][0], pts[p][1]] for p in src], [pts[p][2] for p in src], lon, lat))
            pts[a][0], pts[a][1] = lon, lat
            if zs:
                pts[a][2] = round(sum(zs) / len(zs), 2)
        st.session_state.z_ver += 1
        sync_custom()
        return True
    obstacles = st.session_state.obstacles  # obstacle d'indice a : il passe sur le pan sous la nouvelle position
    if a >= len(obstacles):
        return False
    hit = next((f for f in store.values() if geo.contains(f["ring"], lon, lat)), None)
    if hit is None:
        st.toast(t("obstacle_moved_off"), icon=":material/roofing:")
        return True  # la carte est redessinée avec l'ancienne position
    obstacles[a].update(lon=lon, lat=lat, face_id=hit["id"])
    return True


def handle_drawings(out) -> bool:
    """Polygones tracés avec l'outil de dessin -> nouveaux pans (une seule fois par tracé). La carte est
    recréée ensuite (epoch) pour effacer le tracé de l'outil : le pan est redessiné par l'application."""
    new = False
    for feat in (out or {}).get("all_drawings") or []:
        geom = feat.get("geometry", {})
        if geom.get("type") != "Polygon":
            continue
        ring = [list(p[:2]) for p in geom["coordinates"][0]]
        if ring[0] == ring[-1]:
            ring = ring[:-1]
        sig = tuple((round(x, 6), round(y, 6)) for x, y in ring)
        if len(ring) < 3 or sig in seen_drawings:
            continue
        seen_drawings.add(sig)
        st.session_state.custom_n += 1
        n = st.session_state.custom_n
        # Pans du cadastre sous le tracé : le plus recouvert donne l'inclinaison et l'orientation de départ ;
        # ceux déjà choisis sont remplacés par le pan dessiné (restaurés si on supprime celui-ci)
        under = []
        for f in store.values():
            if f.get("custom"):
                continue
            c_drawn, c_face = geo.coverage(ring, f["ring"]), geo.coverage(f["ring"], ring)
            if c_drawn >= 0.2 or c_face >= 0.5:
                under.append((c_drawn, f))
        main = max(under, key=lambda u: u[0])[1] if under else None
        tilt0, az0 = (main["tilt"], main["azimuth"]) if main else (30.0, 0.0)
        sel = st.session_state.sel_faces
        replaced = [f["id"] for _, f in under if f["id"] in sel]
        for i in replaced:
            sel.remove(i)
        # Coins : un point existant à moins de SNAP_M est réutilisé (aimantation), sinon un nouveau point
        pids = []
        for x, y in ring:
            pids.append(nearest_point(x, y, exclude=[p for p in pids if p is not None]))
        # Hauteurs : le plan déduit du pan remplacé, recalé pour passer par les points partagés et par les toits
        # voisins (un bas de toit qui s'arrête plus haut qu'un toit voisin descendant à 0 m n'est pas à 0 m)
        z_def = geo.plane_heights(ring, tilt0, az0)
        pts, diffs = st.session_state.points, []
        for i, (x, y) in enumerate(ring):
            zn = pts[pids[i]][2] if pids[i] is not None else neighbor_z(x, y, main=main)
            if zn is not None:
                diffs.append(zn - z_def[i])
        shift = sum(diffs) / len(diffs) if diffs else 0.0
        pids = [p if p is not None else new_point(x, y, z_def[i] + shift) for i, (p, (x, y)) in enumerate(zip(pids, ring))]
        custom.append({"id": CUSTOM_ID0 + n, "building_id": -1, "ring": ring, "z": [0.0] * len(ring), "pids": pids,
                       "tilt": tilt0, "azimuth": az0, "klasse": 0, "area": 0.0, "custom": True,
                       "irradiation": main["irradiation"] if main else 0.0, "replaced": replaced,
                       "name": f"{t('drawn_face')} {n}"})
        sync_custom()
        if replaced:
            st.toast(t("drawn_replaced", n=len(replaced), tilt=f"{tilt0:.0f}"), icon=":material/draw:")
        new = True
    if new:
        st.session_state.epoch += 1
        st.session_state.z_ver += 1
    return new


def delete_drawn(fid=None):
    """Supprime un pan dessiné (ou tous) et recrée la carte pour effacer son tracé."""
    sel = st.session_state.sel_faces
    for f in custom:  # les pans du cadastre qu'il remplaçait redeviennent choisis
        if fid is None or f["id"] == fid:
            sel += [i for i in f.get("replaced", []) if i not in sel and i in store]
    gone = {f["id"] for f in custom if fid is None or f["id"] == fid}
    custom[:] = [f for f in custom if f["id"] not in gone]
    st.session_state.obstacles[:] = [o for o in st.session_state.obstacles if o["face_id"] not in gone]
    for i in gone:
        store.pop(i, None)
        st.session_state.shifts.pop(i, None)
    used = {p for f in custom for p in f["pids"]}  # les points qui ne servent plus disparaissent
    st.session_state.points = {k: v for k, v in st.session_state.points.items() if k in used}
    st.session_state.epoch += 1
    st.session_state.z_ver += 1


def reset_roof():
    """Nouveau toit : on efface les choix du précédent (pans, obstacles, positions, pans dessinés)."""
    st.session_state.sel_faces = []
    st.session_state.obstacles.clear()
    st.session_state.shifts.clear()
    st.session_state.custom_faces.clear()
    st.session_state.points = {}
    st.session_state.epoch += 1
    st.session_state.show_panels = False
    st.session_state.cells_loaded = set()


# Le lieu sélectionné vient de l'adresse choisie dans les suggestions ou d'un clic sur un toit de la carte
addr = address_box(t("address_ph"), t("address_none"), key="address")
if addr and st.session_state.get("addr_sig") != (addr["label"], addr["t"]):  # nouvelle adresse : on s'y place
    st.session_state.addr_sig = (addr["label"], addr["t"])
    st.session_state.loc = {"lat": addr["lat"], "lon": addr["lon"]}
    reset_roof()

loc = st.session_state.get("loc")
if not loc:
    st.info(t("address_start"), icon=":material/home_pin:")
    out = st_folium(base_map(SWISS_CENTER, SWISS_ZOOM), height=MAP_HEIGHT, use_container_width=True,
                    returned_objects=["last_clicked"], key="swissmap")
    if handle_click(out, "faces"):
        st.rerun()
    st.stop()

tr = t_fixed()
# Outil de la carte et panneau de dessin : au-dessus de la carte, créés ici pour connaître l'outil tout de suite
tool_slot, draw_slot, map_c = st.container(), st.container(), st.container()
with tool_slot:
    tool = st.segmented_control(t("tool"), ["faces", "draw", "add", "del"],
                                format_func=lambda k: tr(f"tool_{k}"), default="faces", key="tool_sel",
                                help=t("tool_help") + " " + t("draw_help")) or "faces"
if tool not in ("faces", "draw", "add", "del"):  # valeur d'une ancienne session
    tool = "faces"
with draw_slot:
    if tool == "draw":
        st.info(t("draw_steps"), icon=":material/draw:")
        if not custom:
            st.caption(t("drawn_none"))
    if custom:
        st.markdown(f"**{t('drawn_title')}**")
        pts = st.session_state.points
        used = sorted(pts)
        owners = {p: [f["name"] for f in custom if p in f["pids"]] for p in used}
        st.caption(t("corner_heights"))
        # Un seul tableau pour tous les points : un point partagé entre deux pans n'y figure qu'une fois
        ed = st.data_editor(
            pd.DataFrame({t("col_height"): [pts[p][2] for p in used]},
                         index=[f"{t('corner')} {p} · {', '.join(owners[p])}" for p in used]),
            key=f"pts-{lang()}-{st.session_state.z_ver}-{'-'.join(map(str, used))}", width="stretch",
            column_config={t("col_height"): st.column_config.NumberColumn(min_value=-50, max_value=200, step=0.1)})
        for p, v in zip(used, ed[t("col_height")]):
            if pd.notna(v) and abs(float(v) - pts[p][2]) > 1e-9:
                pts[p][2] = float(v)
        sync_custom()
        for f in custom:
            c1, c2 = st.columns([6, 1], vertical_alignment="center")
            c1.markdown(f"**{f['name']}** · {f['area']:.0f} m² · {f['tilt']:.0f}° · {orientation(f['azimuth'])} · "
                        f"{t('corner')} {', '.join(map(str, f['pids']))}")
            c2.button(" ", icon=":material/delete:", key=f"del-{f['id']}", help=t("drawn_delete"),
                      on_click=delete_drawn, args=(f["id"],), width="stretch")
            with st.expander(f"{t('sides_title')} · {f['name']}"):
                st.caption(t("sides_help"))
                w0, l0 = geo.face_dimensions(f)  # largeur le long du faîte, longueur dans la pente
                sig = f"{w0:.2f}-{l0:.2f}"  # la clé suit la géométrie : après un déplacement, la saisie repart de la valeur réelle
                dc1, dc2 = st.columns(2)
                w_new = dc1.number_input(t("col_width"), 0.3, 300.0, round(w0, 1), 0.1, key=f"fw-{f['id']}-{lang()}-{sig}")
                l_new = dc2.number_input(t("col_length"), 0.3, 300.0, round(l0, 1), 0.1, key=f"fl-{f['id']}-{lang()}-{sig}")
                if abs(w_new - round(w0, 1)) > 0.04 or abs(l_new - round(l0, 1)) > 0.04:
                    resize_face(f, w_new / w0, l_new / l0)
                    sync_custom()
                    st.session_state.z_ver += 1
                ids = f["pids"]
                lens = [side_length(ids[i], ids[(i + 1) % len(ids)]) for i in range(len(ids))]
                col = t("side_len")
                ed_s = st.data_editor(
                    pd.DataFrame({col: [round(x, 2) for x in lens]},
                                 index=[f"{t('side')} {i + 1} ({ids[i]} → {ids[(i + 1) % len(ids)]})"
                                        for i in range(len(ids))]),
                    # la clé suit la géométrie : après un déplacement, les saisies d'avant ne sont pas rejouées
                    key=f"sides-{f['id']}-{lang()}-{'-'.join(f'{x:.2f}' for x in lens)}", width="stretch",
                    column_config={col: st.column_config.NumberColumn(min_value=0.2, max_value=300, step=0.05)})
                for i, (old, new) in enumerate(zip(lens, ed_s[col])):
                    if pd.notna(new) and abs(float(new) - round(old, 2)) > 0.004:  # un côté modifié à la fois
                        resize_side(f, i, float(new))
                        sync_custom()
                        st.session_state.z_ver += 1
                        break
        st.button(t("drawn_clear", n=len(custom)), icon=":material/delete_sweep:", on_click=delete_drawn)
sync_custom()  # inclinaison et orientation déduites des hauteurs des coins

try:
    near = roofs(loc["lat"], loc["lon"])  # tous les toits dans le périmètre autour du lieu sélectionné
except ApiError as e:
    fail(e)
store.update({f["id"]: f for f in near})
store.update({f["id"]: f for f in custom})
faces = list(store.values())
buildings = geo.buildings_by_distance(near, loc["lat"], loc["lon"])

# Bâtiments concernés : ceux des pans choisis (peu importe lesquels) et celui sous l'adresse
sel_ids = [i for i in st.session_state.sel_faces if i in store]
st.session_state.sel_faces = sel_ids
ctx = buildings[0] if buildings else None  # sert à cadrer la carte au départ
shown = list(dict.fromkeys([store[i]["building_id"] for i in sel_ids] + ([ctx] if ctx is not None else [])))
sel_key = "-".join(map(str, sel_ids))

bfaces = []  # pans choisis puis pans dessinés ; « Pan 2 » ou « Pan 1.2 » s'il y a plusieurs bâtiments
all_labels = {}
for bi, b in enumerate(shown, 1):
    for i, f in enumerate([f for f in faces if f["building_id"] == b], 1):
        label = f"{t('col_face')} {bi}.{i}" if len(shown) > 1 else f"{t('col_face')} {i}"
        all_labels[f["id"]] = label
for fid in sel_ids:
    f = store[fid]
    bfaces.append({**f, "label": all_labels[fid], "on": True,
                   "row": f"{all_labels[fid]} · {klass(f['klasse'])} · {f['area']:.0f} m²"})
for f in custom:
    bfaces.append({**f, "label": f["name"], "on": True, "row": f"{f['name']} · {f['area']:.0f} m²"})
obs_by_face = {}
for ob in st.session_state.obstacles:
    obs_by_face.setdefault(ob["face_id"], []).append(ob)

# Lieu de calcul de la production : centre des pans choisis
if bfaces:
    pts = [p for f in bfaces for p in f["ring"]]
    lon, lat = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
else:
    lat, lon = loc["lat"], loc["lon"]

# Panneau : la puissance suit la taille (densité de référence 430 Wc pour 1,72 × 1,13 m),
# mais changer la puissance ne change pas la taille. Ces réglages restent quand on change de pan.
REF_DENSITY = 430 / (1.72 * 1.13)  # Wc par m²
for k, v in (("panel_wp", 430), ("panel_l", 1.72), ("panel_w", 1.13), ("obst_w", 0.78), ("obst_l", 1.40),
             ("obst_kind", "obst_velux")):
    st.session_state.setdefault(k, v)


def size_changed():
    wp = REF_DENSITY * st.session_state.panel_l * st.session_state.panel_w
    st.session_state.panel_wp = int(min(800, max(100, round(wp / 5) * 5)))


def obstacle_changed():
    if st.session_state.obst_kind in OBSTACLE_PRESETS:
        st.session_state.obst_w, st.session_state.obst_l = OBSTACLE_PRESETS[st.session_state.obst_kind]


def nudge(fid, ds, dd):
    cur = st.session_state.shifts.get(fid, (0.0, 0.0))
    st.session_state.shifts[fid] = (cur[0] + ds, cur[1] + dd)


STEP_KEY = f"steps-{lang()}"


def goto(step, tool=None, show=False):
    """Bouton « Suivant » : ouvre l'étape, change l'outil de la carte, et pose les panneaux si show."""
    st.session_state[STEP_KEY] = t(f"step_{step - 1}")  # les appels gardent l'ancienne numérotation (2 = pans)
    if tool:
        st.session_state.tool_sel = tool
    if show:
        st.session_state.show_panels = True


def next_button(step, tool=None, show=False, disabled=False):
    st.button(t("next"), icon=":material/arrow_forward:", type="primary", on_click=goto, args=(step, tool, show),
              disabled=disabled, key=f"next-{step}")


def preselect_best():
    """Coche les pans d'aptitude bonne ou mieux du bâtiment sous l'adresse, sinon ses meilleurs."""
    fs = [f for f in faces if f["building_id"] == ctx and f["id"] not in st.session_state.sel_faces]
    best = min(3, max((f["klasse"] for f in fs), default=0))
    st.session_state.sel_faces += [f["id"] for f in fs if f["klasse"] >= best > 0]


# Page : carte, puis les étapes en onglets. Les onglets sont tous exécutés, donc les réglages d'une étape
# restent quand on en regarde une autre ; « Suivant » ouvre l'onglet suivant.
map_slot = map_c
tab2, tab3, tab4, tab5 = st.tabs([t(f"step_{i}") for i in range(1, 5)], key=STEP_KEY, on_change=lambda: None)

with tab3:
    h1, h2, h3, h4, h5 = st.columns(5)
    loss = h1.number_input(t("loss"), 0, 40, 14, help=t("loss_help"))
    panel_wp = h2.number_input(t("panel_wp"), 100, 800, step=5, key="panel_wp", help=t("panel_wp_help"))
    panel_l = h3.number_input(t("panel_l"), 0.5, 3.0, step=0.01, key="panel_l", on_change=size_changed)
    panel_w = h4.number_input(t("panel_w"), 0.5, 2.0, step=0.01, key="panel_w", on_change=size_changed)
    margin = h5.number_input(t("margin"), 0.0, 2.0, 0.3, step=0.1, help=t("margin_help"))
    f1, f2 = st.columns([2, 1], vertical_alignment="center")
    auto = f1.checkbox(t("fill_auto"), True, key="fill_auto")
    target = f2.number_input(t("n_wanted"), 1, 5000, 20, key="n_target", disabled=auto, help=t("n_wanted_help"))

with tab4:
    o1, o2, o3, o4 = st.columns([2, 1, 1, 2], vertical_alignment="bottom")
    o1.selectbox(t("obst_type"), [*OBSTACLE_PRESETS, "obst_custom"], format_func=tr, key="obst_kind",
                 on_change=obstacle_changed)
    o2.number_input(t("obst_w"), 0.1, 10.0, step=0.05, key="obst_w")
    o3.number_input(t("obst_l"), 0.1, 10.0, step=0.05, key="obst_l")
    o4.button(t("obst_clear", n=len(st.session_state.obstacles)), icon=":material/delete:",
              disabled=not st.session_state.obstacles, on_click=lambda: st.session_state.obstacles.clear())
    st.caption(t("tool_help"))


def place(f, n=None):
    """Panneaux d'un pan avec décalage et obstacles. n : nombre calculé à partir de dimensions saisies à la
    main ; on en retire les panneaux perdus à cause des obstacles et du décalage. Sans n, c'est la disposition
    réelle dans le contour. Renvoie (panneaux, nombre)."""
    shift = st.session_state.shifts.get(f["id"], (0.0, 0.0))
    layout, eff = geo.panel_layout(f, panel_w, panel_l, margin, shift=shift, obstacles=obs_by_face.get(f["id"], ()))
    st.session_state.shifts[f["id"]] = eff  # la valeur aimantée/bornée devient la référence
    if n is None:
        return layout, len(layout)
    lost = len(geo.panel_layout(f, panel_w, panel_l, margin)[0]) - len(layout)
    n = max(n - lost, 0)
    return layout[:n], n


# ---- Étape 2 : pans (un seul tableau, valeurs du cadastre modifiables) ------------------------
arrays = []  # un dict par pan équipé : tilt, azimuth, kwp, panels, face_id, layout, label, quality
with tab2:
    st.caption(f"{t('step2_note')} {t('faces_picked', n=len(bfaces))}")
    b1, b2, _ = st.columns([2, 2, 3])
    b1.button(t("best_faces"), icon=":material/auto_awesome:", on_click=preselect_best, width="stretch")
    b2.button(t("clear_sel"), icon=":material/delete_sweep:", disabled=not (bfaces or st.session_state.obstacles),
              width="stretch", help=t("clear_sel_help"), on_click=clear_all)
    inc, wid, lng, tilt, ori, hb, ht = (t(c) for c in ("col_include", "col_width", "col_length", "col_tilt_deg",
                                                       "col_orient_deg", "col_hb", "col_ht"))
    dims0, heights0, rows, index = {}, {}, [], []
    for f in bfaces:
        dims0[f["id"]] = geo.face_dimensions(f)
        run = dims0[f["id"]][1] * math.cos(math.radians(round(f["tilt"])))  # profondeur horizontale du pan
        if f.get("custom"):  # pan dessiné : les hauteurs se règlent coin par coin, au-dessus de la carte
            heights0[f["id"]] = (None, None)
        else:
            heights0[f["id"]] = (0.0, round(run * math.tan(math.radians(round(f["tilt"]))), 2))
        rows.append({inc: f["on"], wid: dims0[f["id"]][0], lng: dims0[f["id"]][1], tilt: round(f["tilt"]),
                     ori: round(f["azimuth"]), hb: heights0[f["id"]][0], ht: heights0[f["id"]][1],
                     "face_id": f["id"]})
        index.append(f["row"])
    if not rows and not any(f["building_id"] in shown for f in faces):  # rien de détecté : un pan à la main, sans position sur la carte
        rows.append({inc: True, wid: 10.0, lng: 6.0, tilt: 30, ori: 0, hb: 0.0, ht: 3.2, "face_id": None})
        index.append(f"{t('col_face')} 1")
    edited = st.data_editor(
        pd.DataFrame(rows, index=index, columns=[inc, wid, lng, tilt, ori, hb, ht, "face_id"]), width="stretch", num_rows="dynamic", key=f"faces-{sel_key}-{lang()}",
        column_config={
            inc: st.column_config.CheckboxColumn(default=True),
            wid: st.column_config.NumberColumn(min_value=0.5, max_value=200, step=0.1, default=8.0),
            lng: st.column_config.NumberColumn(min_value=0.5, max_value=100, step=0.1, default=5.0),
            tilt: st.column_config.NumberColumn(min_value=0, max_value=90, step=1, default=30),
            ori: st.column_config.NumberColumn(min_value=-180, max_value=180, step=1, default=0),
            hb: st.column_config.NumberColumn(min_value=-50, max_value=200, step=0.1, default=0.0,
                                              help=t("heights_help")),
            ht: st.column_config.NumberColumn(min_value=-50, max_value=200, step=0.1, default=3.2,
                                              help=t("heights_help")),
            "face_id": None,
        },
    )
    by_heights = []  # pans dont l'inclinaison vient des hauteurs saisies
    next_button(3, show=True, disabled=not bfaces)
    by_id = {f["id"]: f for f in bfaces}
    for name, r in edited.dropna(subset=[wid, lng, tilt, ori]).iterrows():
        if not r[inc]:
            continue
        f = by_id.get(r["face_id"])
        if f is None:  # pan saisi à la main : pas de contour, le nombre vient des dimensions
            n = fit_panels(r[wid], r[lng], panel_w, panel_l, margin)
            arrays.append({"tilt": r[tilt], "azimuth": r[ori], "kwp": n * panel_wp / 1000, "panels": n,
                           "face_id": None, "layout": [], "label": str(name), "quality": 0})
            continue
        tilt_eff = r[tilt]
        hb0, ht0 = heights0[f["id"]]
        if hb0 is not None and pd.notna(r[hb]) and pd.notna(r[ht]) and (abs(r[hb] - hb0) > 0.005
                                                                         or abs(r[ht] - ht0) > 0.005):
            run = max(r[lng] * math.cos(math.radians(r[tilt])), 0.1)  # profondeur horizontale du pan
            tilt_eff = min(math.degrees(math.atan2(max(r[ht] - r[hb], 0), run)), 90)
            by_heights.append(f"{f['label']} {tilt_eff:.0f}°")
        fe = {**f, "tilt": tilt_eff, "azimuth": r[ori]}  # la grille suit l'inclinaison et l'orientation
        w0, l0 = dims0[f["id"]]
        edited_dims = (abs(r[wid] - w0) > 0.05 or abs(r[lng] - l0) > 0.05) and not f.get("custom")
        # Dimensions inchangées : disposition réelle dans le contour ; modifiées : on recalcule le nombre
        layout, n = place(fe, fit_panels(r[wid], r[lng], panel_w, panel_l, margin) if edited_dims else None)
        arrays.append({"tilt": tilt_eff, "azimuth": r[ori], "kwp": n * panel_wp / 1000, "panels": n,
                       "face_id": f["id"], "layout": layout, "label": f["label"], "quality": f["irradiation"]})

if by_heights:
    with tab2:
        st.caption(t("tilt_from_heights", rows=", ".join(by_heights)))

# Nombre de panneaux voulu : on remplit d'abord les pans les mieux ensoleillés
capacity = sum(a["panels"] for a in arrays)
if not auto:
    left = target
    for a in sorted(arrays, key=lambda a: -a["quality"]):
        take = min(a["panels"], left)
        left -= take
        a["layout"], a["panels"], a["kwp"] = a["layout"][:take], take, take * panel_wp / 1000
with tab3:
    st.caption(t("n_capacity", n=capacity))
    next_button(4, "add")

# ---- Étape 4 : position des panneaux (aimantation) --------------------------------------------
with tab4:
    st.subheader(t("shift_title"))
    st.caption(t("shift_note"))
    for a in (a for a in arrays if a["layout"] or a["face_id"] in st.session_state.shifts):
        if a["face_id"] is None:
            continue
        fid = a["face_id"]
        row = st.columns([3, 1, 1, 1, 1, 2], vertical_alignment="center")
        row[0].markdown(f"**{a['label']}** · {a['panels']} {t('m_panels').lower()}")
        for col, key, icon, d in ((row[1], "shift_left", "arrow_back", (-STEP, 0)),
                                  (row[2], "shift_right", "arrow_forward", (STEP, 0)),
                                  (row[3], "shift_up", "arrow_upward", (0, -STEP)),
                                  (row[4], "shift_down", "arrow_downward", (0, STEP))):
            col.button(" ", icon=f":material/{icon}:", help=t(key), key=f"{key}-{fid}", on_click=nudge,
                       args=(fid, *d), width="stretch")
        row[5].button(t("shift_reset"), key=f"reset-{fid}", width="stretch",
                      on_click=lambda i=fid: st.session_state.shifts.pop(i, None))

with tab4:
    next_button(5)

# ---- Carte : vue aérienne swisstopo --------------------------------------------------------------
with map_slot:
    show = st.session_state.show_panels
    equipped = {a["face_id"] for a in arrays if a["kwp"] > 0} if show else set(sel_ids)
    # Les couches qui bougent (pans, panneaux, obstacles) vont dans un groupe ajouté à la carte sans la
    # recréer : la vue ne bouge plus. La carte n'est recréée que si la maison change, ou pour effacer un
    # tracé (epoch) ; la vue courante est alors conservée.
    fit_sig = (round(loc["lat"], 5), round(loc["lon"], 5), ctx)  # la maison affichée, pas les pans choisis
    state = (lang(), fit_sig, st.session_state.epoch, tool == "draw")
    prev = st.session_state.get("map_state")
    if prev != state:
        st.session_state.map_state = state
        st.session_state.base_view = st.session_state.get("live_view") if prev and prev[1] == fit_sig else None
    view = st.session_state.get("base_view")
    pts = [(y, x) for f in faces if f["building_id"] == ctx for x, y in f["ring"]]
    bounds = [[min(p[0] for p in pts), min(p[1] for p in pts)],
              [max(p[0] for p in pts), max(p[1] for p in pts)]] if pts else None
    center = [(bounds[0][0] + bounds[1][0]) / 2, (bounds[0][1] + bounds[1][1]) / 2] if bounds else [lat, lon]
    fmap = base_map(view["center"] if view else center, view["zoom"] if view else 20, draw=tool == "draw",
                    bounds=None if view else bounds)
    dyn = folium.FeatureGroup(name="dyn", control=False)
    vb = st.session_state.get("live_bounds")
    vb = vb if valid_bounds(vb) else None  # on ne dessine que les pans dans la vue (et ceux choisis)

    def visible(f, m=0.0005):
        if not vb or f.get("custom") or f["id"] in equipped:
            return True
        xs, ys = [p[0] for p in f["ring"]], [p[1] for p in f["ring"]]
        (s_, w_), (n_, e_) = (vb["_southWest"]["lat"], vb["_southWest"]["lng"]), (vb["_northEast"]["lat"],
                                                                                  vb["_northEast"]["lng"])
        return not (max(ys) < s_ - m or min(ys) > n_ + m or max(xs) < w_ - m or min(xs) > e_ + m)

    for f in filter(visible, faces):
        is_custom = f.get("custom", False)
        fill = PANEL if f["id"] in equipped else CUSTOM if is_custom else CLASS_COLORS[f["klasse"]]
        tip = (f"{f['name']} · {f['area']:.0f} m² · {f['tilt']:.0f}°" if is_custom else
               f"{orientation(f['azimuth'])} · {f['tilt']:.0f}° · {f['area']:.0f} m² · {klass(f['klasse'])}")
        folium.Polygon(
            [(y, x) for x, y in f["ring"]],
            color=CUSTOM if is_custom else "#9cc3f5" if f["id"] in equipped else "#ffffff",
            weight=2 if f["id"] in equipped else 1.1, fill=True, fill_color=fill,
            fill_opacity=0.3 if f["id"] in equipped else 0.55, tooltip=tip, interactive=tool != "draw",
        ).add_to(dyn)
    for pid, (x, y, z) in st.session_state.points.items():  # points des pans dessinés : numéro, hauteur modifiable
        folium.Marker(
            [y, x], draggable=True,
            tooltip=(f"{t('corner')} {pid} · {z:.2f} m ({t('drag_hint')})"
                     f'<span style="display:none">@c:{pid}:0</span>'),
            icon=folium.DivIcon(icon_size=(96, 22), icon_anchor=(11, 11), html=(
                '<div style="display:flex;align-items:center;gap:4px">'
                f'<div style="flex:none;width:20px;height:20px;border-radius:50%;background:{CUSTOM};color:#14171c;'
                f'font:700 11px/20px Inter,sans-serif;text-align:center;border:1.5px solid #fff;cursor:grab">{pid}</div>'
                f'<input type="number" step="0.1" value="{z:.2f}" data-pid="{pid}" title="{t("col_height")}" '
                'style="width:62px;height:20px;box-sizing:border-box;padding:0 3px;border-radius:4px;'
                'border:1px solid #fff;background:rgba(20,23,28,.9);color:#f0efec;font:600 11px Inter,sans-serif">'
                '</div>')),
        ).add_to(dyn)
    for f in custom:  # poignée au centre de chaque pan dessiné : on le glisse d'un bloc, hauteurs inchangées
        pp = [st.session_state.points[p] for p in f["pids"]]
        folium.Marker(
            [sum(q[1] for q in pp) / len(pp), sum(q[0] for q in pp) / len(pp)], draggable=True,
            tooltip=(f"{f['name']} ({t('slide_hint')})" f'<span style="display:none">@f:{f["id"]}:0</span>'),
            icon=folium.DivIcon(icon_size=(26, 26), icon_anchor=(13, 13), html=(
                f'<div style="width:26px;height:26px;border-radius:50%;background:{CUSTOM};color:#14171c;'
                'font:700 16px/24px Inter,sans-serif;text-align:center;border:2px solid #fff;cursor:grab;'
                'box-shadow:0 0 4px rgba(0,0,0,.7)">✥</div>')),
        ).add_to(dyn)
    for f in custom:  # longueur réelle de chaque côté, au milieu du côté
        for i, p in enumerate(f["pids"]):
            q = f["pids"][(i + 1) % len(f["pids"])]
            (x1, y1, _), (x2, y2, _) = st.session_state.points[p], st.session_state.points[q]
            folium.Marker(
                [(y1 + y2) / 2, (x1 + x2) / 2], interactive=False,
                icon=folium.DivIcon(icon_size=(60, 16), icon_anchor=(30, 8), html=(
                    '<div style="text-align:center;font:600 11px Inter,sans-serif;color:#fff;'
                    f'text-shadow:0 0 3px #000,0 0 3px #000">{side_length(p, q):.2f} m</div>')),
            ).add_to(dyn)
    for a in arrays if show else []:  # les panneaux, un rectangle chacun, posés après « Suivant »
        for rect in a["layout"]:
            folium.Polygon([(y, x) for x, y in rect], color="#9cc3f5", weight=0.6, fill=True,
                           fill_color="#16233a", fill_opacity=0.92, interactive=False).add_to(dyn)
    for k, ob in enumerate(st.session_state.obstacles):
        folium.Polygon([(y, x) for x, y in geo.obstacle_rect(store[ob["face_id"]], ob)], color="#ffffff",
                       weight=1, fill=True, fill_color=OBSTACLE, fill_opacity=0.9, interactive=False).add_to(dyn)
        folium.Marker(  # poignée au centre, à glisser pour déplacer l'obstacle
            [ob["lat"], ob["lon"]], draggable=True,
            tooltip=(f"{tr(ob['kind'])} · {ob['w']:.2f} × {ob['l']:.2f} m ({t('drag_hint')})"
                     f'<span style="display:none">@o:{k}:0</span>'),
            icon=folium.DivIcon(icon_size=(18, 18), icon_anchor=(9, 9), html=(
                f'<div style="width:18px;height:18px;border-radius:50%;background:{OBSTACLE};border:2px solid #fff;'
                'box-shadow:0 0 3px rgba(0,0,0,.7);cursor:grab"></div>')),
        ).add_to(dyn)
    dyn.add_child(DragEnd())  # en dernier : les marqueurs doivent déjà exister
    out = st_folium(fmap, feature_group_to_add=dyn, height=MAP_HEIGHT, use_container_width=True,
                    returned_objects=["last_clicked", "all_drawings", "center", "zoom", "bounds", "last_object_clicked",
                                      "last_object_clicked_tooltip", "last_object_clicked_count"],
                    key=f"roofmap-{st.session_state.epoch}-{lang()}-{tool == 'draw'}")
    if out and out.get("center") and out.get("zoom"):  # vue actuelle, pour recréer la carte au même endroit
        st.session_state.live_view = {"center": [out["center"]["lat"], out["center"]["lng"]], "zoom": out["zoom"]}
    st.caption(t("map_note"))
    changed = handle_drawings(out) or handle_drag(out) or handle_click(out, tool)
    if out and valid_bounds(out.get("bounds")):  # les toits se chargent autour de la vue, sans cliquer
        st.session_state.live_bounds = out["bounds"]
        if (out.get("zoom") or 0) >= 17:
            with st.spinner(t("loading_roofs")):
                changed = load_cells(out["bounds"]) > 0 or changed
        else:
            st.caption(t("zoom_more"))
    if changed:
        st.rerun()

# ---- Étape 5 : production ---------------------------------------------------------------------
with tab5:
    kwp = sum(a["kwp"] for a in arrays)
    if not st.session_state.show_panels:
        st.session_state.pop("system", None)
        st.info(t("show_first"), icon=":material/solar_power:")
    elif kwp <= 0:
        st.session_state.pop("system", None)
        st.info(t("pick_face"), icon=":material/solar_power:")
    else:
        try:
            with st.spinner(t("loading_pvgis")):
                monthly = sum(pvgis(round(lat, 4), round(lon, 4), a["tilt"], a["azimuth"], loss) * a["kwp"]
                              for a in arrays if a["kwp"] > 0)
        except ApiError as e:
            fail(e)
        annual = monthly.sum()
        panels = sum(a["panels"] for a in arrays)
        st.session_state.system = {"lat": lat, "lon": lon, "loss": loss, "kwp": kwp, "annual": annual,
                                   "arrays": arrays}
        m = st.columns(4)
        m[0].metric(t("m_annual"), f"{kwh(annual)} kWh")
        m[1].metric(t("m_power"), f"{kwp:.1f} {t('unit_kwp')}")
        m[2].metric(t("m_specific"), f"{kwh(annual / kwp)} kWh/{t('unit_kwp')}")
        m[3].metric(t("m_panels"), f"≈ {panels}")
        fig = go.Figure(go.Bar(x=months(), y=monthly.values, marker_color=BLUE,
                               hovertemplate="%{x} : %{y:,.0f} kWh<extra></extra>"))
        st.plotly_chart(style(fig, t("c_monthly_avg"), t("y_month")), width="stretch")
        st.caption(t("note_basic", loss=loss, wp=panel_wp, l=panel_l, w=panel_w))
