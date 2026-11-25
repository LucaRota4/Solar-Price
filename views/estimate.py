"""Estimation solaire : adresse -> toit -> pans équipés -> production annuelle."""
import math

import folium
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from branca.element import MacroElement
from jinja2 import Template
from folium.plugins import Draw
from streamlit_folium import st_folium

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


def base_map(center, zoom, legend=True, draw=False):
    """Carte limitée à la Suisse : vue aérienne swisstopo (par défaut) ou plan avec rues et numéros,
    au choix dans la carte. Boussole, sans échelle."""
    fmap = folium.Map(location=center, zoom_start=zoom, min_zoom=7, max_zoom=21, tiles=None, control_scale=False,
                      max_bounds=True, min_lat=45.4, max_lat=48.2, min_lon=5.4, max_lon=11.0)
    folium.TileLayer(SWISSIMAGE, attr="© swisstopo", name=t("map_satellite"), max_native_zoom=20,
                     max_zoom=21).add_to(fmap)
    folium.TileLayer(OSM_PLAN, attr="© OpenStreetMap", name=t("map_plan"), max_native_zoom=19,
                     max_zoom=21, show=False).add_to(fmap)
    folium.LayerControl(position="topleft", collapsed=False).add_to(fmap)
    Compass().add_to(fmap)
    if draw:  # polygones et rectangles seulement, sans les boutons d'édition ni de suppression
        Draw(draw_options={"polyline": False, "circle": False, "marker": False, "circlemarker": False,
                           "polygon": {"shapeOptions": {"color": CUSTOM}}, "rectangle": {"shapeOptions": {"color": CUSTOM}}},
             edit_options={"edit": False, "remove": False}).add_to(fmap)
    if legend:
        items = [(CLASS_COLORS[k], klass(k)) for k in range(1, 6)]
        Legend(items + [(PANEL, t("legend_panels")), (OBSTACLE, t("legend_obstacle"))],
               t("col_class")).add_to(fmap)
    return fmap


@st.cache_data(show_spinner=False)
def search(text):
    return geo.search_address(text)


@st.cache_data(show_spinner=False)
def roofs(lat, lon):
    return geo.roofs_around(lat, lon)


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
st.session_state.setdefault("buildings", [])  # bâtiments choisis, dans l'ordre du choix
st.session_state.setdefault("obstacles", [])  # {lon, lat, w, l, face_id, kind}
st.session_state.setdefault("shifts", {})  # face_id -> décalage (s, d) en m du champ de panneaux


def handle_click(out, tool) -> bool:
    """Clic sur la carte, selon l'outil : choisir/retirer un bâtiment, poser ou supprimer un obstacle.
    True si quelque chose a changé."""
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
    if tool == "pick":
        if hit is None:  # toit hors du périmètre chargé : on charge les toits autour du clic
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
        b, sel = hit["building_id"], st.session_state.buildings
        if b == -1:  # pan dessiné : pas un bâtiment
            return False
        if b in sel:
            if len(sel) == 1:  # on garde toujours au moins un bâtiment
                return False
            sel.remove(b)
        elif sel:  # un toit est déjà choisi : on demande avant de changer (dialogue ouvert au prochain tour)
            st.session_state.pending_building = b
        else:
            sel.append(b)
        return True
    if tool == "add":
        if hit is None:
            st.toast(t("click_no_face"), icon=":material/roofing:")
            return False
        st.session_state.obstacles.append({"lon": c_lon, "lat": c_lat, "w": st.session_state.obst_w,
                                           "l": st.session_state.obst_l, "face_id": hit["id"],
                                           "kind": st.session_state.obst_kind})
        return True
    obstacles = st.session_state.obstacles  # tool == "del" : le dernier posé qui contient le clic
    for ob in reversed(obstacles):
        if geo.contains(geo.obstacle_rect(store[ob["face_id"]], ob), c_lon, c_lat):
            obstacles.remove(ob)
            return True
    st.toast(t("click_no_obstacle"), icon=":material/roofing:")
    return False


def handle_drawings(out) -> bool:
    """Polygones tracés avec l'outil de dessin -> nouveaux pans (une seule fois par tracé)."""
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
        n = len(custom) + 1
        custom.append({"id": CUSTOM_ID0 + n, "building_id": -1, "ring": ring, "tilt": 30.0, "azimuth": 0.0,
                       "klasse": 0, "irradiation": 0.0, "area": geo.ring_area(ring) / math.cos(math.radians(30)),
                       "custom": True, "name": f"{t('drawn_face')} {n}"})
        new = True
    return new


@st.dialog(t("switch_title"))
def confirm_switch(b):
    st.write(t("switch_text"))
    add, replace, cancel = st.columns(3)
    if add.button(t("switch_add"), icon=":material/add:", width="stretch"):
        st.session_state.buildings.append(b)
        st.rerun()
    if replace.button(t("switch_replace"), icon=":material/swap_horiz:", type="primary", width="stretch"):
        st.session_state.buildings = [b]
        st.session_state.obstacles.clear()
        st.session_state.shifts.clear()
        st.session_state.custom_faces.clear()
        st.rerun()
    if cancel.button(t("switch_cancel"), width="stretch"):
        st.rerun()


# Le lieu sélectionné vient de l'adresse tapée ou d'un clic sur un toit de la carte
query = st.text_input(t("address"), placeholder=t("address_ph"), key="address").strip()
if query:
    try:
        results = search(query)
    except ApiError as e:
        fail(e)
    if not results:
        st.warning(t("address_none"))
    else:
        addr = results[0] if len(results) == 1 else st.selectbox(t("address_found"), results,
                                                                  format_func=lambda r: r["label"])
        if st.session_state.get("addr_sig") != (query, addr["label"]):  # nouvelle adresse : on s'y place
            st.session_state.addr_sig = (query, addr["label"])
            st.session_state.loc = {"lat": addr["lat"], "lon": addr["lon"]}
            st.session_state.buildings = []

loc = st.session_state.get("loc")
if not loc:
    st.info(t("address_start"), icon=":material/home_pin:")
    out = st_folium(base_map(SWISS_CENTER, SWISS_ZOOM), height=MAP_HEIGHT, use_container_width=True,
                    returned_objects=["last_clicked"], key="swissmap")
    if handle_click(out, "pick"):
        st.rerun()
    st.stop()

try:
    near = roofs(loc["lat"], loc["lon"])  # tous les toits dans le périmètre autour du lieu sélectionné
except ApiError as e:
    fail(e)
store.update({f["id"]: f for f in near})
store.update({f["id"]: f for f in custom})
faces = list(store.values())
buildings = geo.buildings_by_distance(near, loc["lat"], loc["lon"])
tr = t_fixed()

# Bâtiments actifs : ceux sur lesquels on a cliqué (plusieurs possibles), sinon celui sous l'adresse
present = {f["building_id"] for f in faces}
selected = [b for b in st.session_state.buildings if b in present]
if not selected and buildings:
    selected = [buildings[0]]
st.session_state.buildings = selected
sel_key = "-".join(map(str, selected))

pending = st.session_state.pop("pending_building", None)
if pending is not None and pending not in selected:
    confirm_switch(pending)  # fermer la fenêtre = annuler

bfaces = []  # pans des bâtiments choisis, puis pans dessinés ; « Pan 2 » ou « Pan 1.2 » s'il y a plusieurs bâtiments
for bi, b in enumerate(selected, 1):
    fs = [f for f in faces if f["building_id"] == b]
    best = min(3, max(f["klasse"] for f in fs))  # cochés par défaut : aptitude bonne ou mieux, sinon les meilleurs
    for i, f in enumerate(fs, 1):
        label = f"{t('col_face')} {bi}.{i}" if len(selected) > 1 else f"{t('col_face')} {i}"
        bfaces.append({**f, "label": label, "on": f["klasse"] >= best,
                       "row": f"{label} · {klass(f['klasse'])} · {f['area']:.0f} m²"})
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


# Page : carte, puis les étapes en onglets. Les onglets sont toujours tous exécutés, donc les réglages
# d'une étape restent quand on en regarde une autre.
map_slot = st.container()
tab1, tab2, tab3, tab4, tab5 = st.tabs([t(f"step_{i}") for i in range(1, 6)])

with tab1:
    st.caption(t("step1_note", n=len(selected)))

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
    st.caption(t("step2_note"))
    inc, wid, lng, tilt, ori, hgt = (t(c) for c in ("col_include", "col_width", "col_length", "col_tilt_deg",
                                                    "col_orient_deg", "col_height"))
    dims0, rows, index = {}, [], []
    for f in bfaces:
        dims0[f["id"]] = geo.face_dimensions(f)
        rows.append({inc: f["on"], wid: dims0[f["id"]][0], lng: dims0[f["id"]][1], tilt: round(f["tilt"]),
                     ori: round(f["azimuth"]), hgt: 0.0, "face_id": f["id"]})
        index.append(f["row"])
    if not rows:  # rien de détecté : un pan à la main, sans position sur la carte
        rows.append({inc: True, wid: 10.0, lng: 6.0, tilt: 30, ori: 0, hgt: 0.0, "face_id": None})
        index.append(f"{t('col_face')} 1")
    edited = st.data_editor(
        pd.DataFrame(rows, index=index), width="stretch", num_rows="dynamic", key=f"faces-{sel_key}-{lang()}",
        column_config={
            inc: st.column_config.CheckboxColumn(default=True),
            wid: st.column_config.NumberColumn(min_value=0.5, max_value=200, step=0.1, default=8.0),
            lng: st.column_config.NumberColumn(min_value=0.5, max_value=100, step=0.1, default=5.0),
            tilt: st.column_config.NumberColumn(min_value=0, max_value=90, step=1, default=30),
            ori: st.column_config.NumberColumn(min_value=-180, max_value=180, step=1, default=0),
            hgt: st.column_config.NumberColumn(min_value=-50, max_value=200, step=0.1, default=0.0,
                                               help=t("col_height_help")),
            "face_id": None,
        },
    )
    if custom:
        st.button(t("drawn_clear", n=len(custom)), icon=":material/delete:", on_click=custom.clear)
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
        fe = {**f, "tilt": r[tilt], "azimuth": r[ori]}  # la grille suit l'inclinaison et l'orientation saisies
        w0, l0 = dims0[f["id"]]
        edited_dims = abs(r[wid] - w0) > 0.05 or abs(r[lng] - l0) > 0.05
        # Dimensions inchangées : disposition réelle dans le contour ; modifiées : on recalcule le nombre
        layout, n = place(fe, fit_panels(r[wid], r[lng], panel_w, panel_l, margin) if edited_dims else None)
        arrays.append({"tilt": r[tilt], "azimuth": r[ori], "kwp": n * panel_wp / 1000, "panels": n,
                       "face_id": f["id"], "layout": layout, "label": f["label"], "quality": f["irradiation"]})

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

# ---- Carte : vue aérienne swisstopo --------------------------------------------------------------
with map_slot:
    tool = st.segmented_control(t("tool"), ["pick", "draw", "add", "del"], format_func=lambda k: tr(f"tool_{k}"),
                                default="pick", key="tool_sel", help=t("tool_help") + "\n\n" + t("draw_help")
                                ) or "pick"
    equipped = {a["face_id"] for a in arrays if a["kwp"] > 0}
    fmap = base_map([lat, lon], 20, draw=tool == "draw")
    for f in faces:
        is_custom = f.get("custom", False)
        mine = is_custom or f["building_id"] in selected
        fill = PANEL if f["id"] in equipped else CUSTOM if is_custom else CLASS_COLORS[f["klasse"]]
        tip = (f"{f['name']} · {f['area']:.0f} m²" if is_custom else
               f"{orientation(f['azimuth'])} · {f['tilt']:.0f}° · {f['area']:.0f} m² · {klass(f['klasse'])}")
        folium.Polygon(
            [(y, x) for x, y in f["ring"]],
            color=CUSTOM if is_custom else "#ffffff", weight=1.4 if mine else 0.6, fill=True, fill_color=fill,
            fill_opacity=(0.3 if f["id"] in equipped else 0.6) if mine else 0.28, tooltip=tip,
            interactive=tool != "draw",
        ).add_to(fmap)
    for a in arrays:  # les panneaux, un rectangle chacun
        for rect in a["layout"]:
            folium.Polygon([(y, x) for x, y in rect], color="#9cc3f5", weight=0.6, fill=True,
                           fill_color="#16233a", fill_opacity=0.92, interactive=False).add_to(fmap)
    for ob in st.session_state.obstacles:
        folium.Polygon([(y, x) for x, y in geo.obstacle_rect(store[ob["face_id"]], ob)], color="#ffffff",
                       weight=1, fill=True, fill_color=OBSTACLE, fill_opacity=0.9,
                       tooltip=f"{tr(ob['kind'])} · {ob['w']:.2f} × {ob['l']:.2f} m", interactive=False).add_to(fmap)
    pts = [(y, x) for f in bfaces for x, y in f["ring"]]
    if pts:
        fmap.fit_bounds([[min(p[0] for p in pts), min(p[1] for p in pts)],
                         [max(p[0] for p in pts), max(p[1] for p in pts)]], padding=(30, 30))
    out = st_folium(fmap, height=MAP_HEIGHT, use_container_width=True,
                    returned_objects=["last_clicked", "all_drawings"], key="roofmap")
    st.caption(t("map_note"))
    if (tool == "draw" and handle_drawings(out)) or handle_click(out, tool):
        st.rerun()

# ---- Étape 5 : production ---------------------------------------------------------------------
with tab5:
    kwp = sum(a["kwp"] for a in arrays)
    if kwp <= 0:
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
