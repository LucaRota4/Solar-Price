"""Estimation solaire : adresse -> toit -> pans équipés -> production annuelle."""
import math

import folium
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from branca.element import MacroElement
from jinja2 import Template
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


def base_map(center, zoom):
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


@st.cache_data(show_spinner=False)
def hourly(lat, lon, tilt, az, loss, start, end):
    return pv.hourly_by_year(lat, lon, tilt, az, loss, start, end)


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

query = st.text_input(t("address"), placeholder=t("address_ph"), key="address")
if not query.strip():
    st.info(t("address_start"), icon=":material/home_pin:")
    st_folium(base_map(SWISS_CENTER, SWISS_ZOOM), height=MAP_HEIGHT, use_container_width=True, returned_objects=[])
    st.stop()

try:
    results = search(query.strip())
except ApiError as e:
    fail(e)
if not results:
    st.warning(t("address_none"))
    st.stop()
addr = results[0] if len(results) == 1 else st.selectbox(t("address_found"), results, format_func=lambda r: r["label"])
lat, lon = addr["lat"], addr["lon"]

try:
    faces = roofs(lat, lon)  # tous les toits dans le périmètre autour de l'adresse
except ApiError as e:
    fail(e)
buildings = geo.buildings_by_distance(faces, lat, lon)

tr = t_fixed()
c1, c2, _ = st.columns([2, 2, 3], vertical_alignment="bottom")
mode = c1.segmented_control(t("mode"), ["simple", "detailed"], format_func=tr, default="simple", key="mode") or "simple"
analysis = c2.segmented_control(t("analysis"), ["basic", "advanced"], format_func=tr, default="basic",
                                key="analysis_mode") or "basic"
# Bâtiment actif : celui à l'adresse, puis celui sur lequel on clique dans la carte
bkey = f"building@{lat:.6f},{lon:.6f}"
if bkey not in st.session_state:
    st.session_state[bkey] = buildings[0] if buildings else None
building = st.session_state[bkey]

bfaces = [f for f in faces if f["building_id"] == building]
if not bfaces:
    st.warning(t("no_roof"), icon=":material/roofing:")
    mode = "detailed"
# Pans cochés par défaut : aptitude bonne ou mieux, sinon les meilleurs disponibles
best = min(3, max((f["klasse"] for f in bfaces), default=3))

with st.expander(t("assumptions"), icon=":material/tune:"):
    h1, h2, h3, h4 = st.columns(4)
    loss = h1.number_input(t("loss"), 0, 40, 14, help=t("loss_help"))
    panel_wp = h2.number_input(t("panel_wp"), 100, 800, 430, step=10)
    panel_l = h3.number_input(t("panel_l"), 0.5, 3.0, 1.72, step=0.01)
    panel_w = h4.number_input(t("panel_w"), 0.5, 2.0, 1.13, step=0.01)
    if mode == "simple":
        usable = st.slider(t("usable"), 50, 100, 80, format="%d %%", help=t("usable_help"))
    else:
        margin = st.number_input(t("margin"), 0.0, 2.0, 0.3, step=0.1)

map_slot = st.container()

# ---- Pans équipés -----------------------------------------------------------------------------
arrays = []  # un dict par pan équipé : tilt, azimuth, kwp, panels, face_id
if mode == "simple":
    st.subheader(t("faces"))
    st.caption(t("faces_simple_note"))
    cols = [t(c) for c in ("col_panels", "col_face", "col_orient", "col_tilt", "col_area", "col_class", "col_irr")]
    table = pd.DataFrame(
        [[f["klasse"] >= best, f"{t('col_face')} {i}", orientation(f["azimuth"]), f"{f['tilt']:.0f}°",
          round(f["area"], 1), klass(f["klasse"]), round(f["irradiation"])] for i, f in enumerate(bfaces, 1)],
        columns=cols,
    )
    edited = st.data_editor(table, hide_index=True, width="stretch", key=f"simple-{building}-{lang()}",
                            disabled=cols[1:])
    density = panel_wp / 1000 / (panel_l * panel_w)  # kWc par m² de panneaux
    for f, on in zip(bfaces, edited[cols[0]]):
        if on:
            m2 = f["area"] * usable / 100
            arrays.append({"tilt": f["tilt"], "azimuth": f["azimuth"], "kwp": m2 * density,
                           "panels": math.floor(m2 / (panel_l * panel_w)), "face_id": f["id"]})
else:
    st.subheader(t("faces"))
    st.caption(t("faces_detail_note"))
    inc, face, wid, lng, tilt, ori = (t(c) for c in ("col_include", "col_face", "col_width", "col_length",
                                                    "col_tilt_deg", "col_orient_deg"))
    rows = []
    for i, f in enumerate(bfaces, 1):
        w, l = geo.face_dimensions(f)
        rows.append({inc: f["klasse"] >= best, face: f"{face} {i}", wid: w, lng: l, tilt: round(f["tilt"]),
                     ori: round(f["azimuth"]), "face_id": f["id"]})
    if not rows:
        rows.append({inc: True, face: f"{face} 1", wid: 10.0, lng: 6.0, tilt: 30, ori: 0, "face_id": None})
    edited = st.data_editor(
        pd.DataFrame(rows), hide_index=True, width="stretch", num_rows="dynamic", key=f"detail-{building}-{lang()}",
        column_config={
            inc: st.column_config.CheckboxColumn(default=True),
            wid: st.column_config.NumberColumn(min_value=0.5, max_value=200, step=0.1, default=8.0),
            lng: st.column_config.NumberColumn(min_value=0.5, max_value=100, step=0.1, default=5.0),
            tilt: st.column_config.NumberColumn(min_value=0, max_value=90, step=1, default=30),
            ori: st.column_config.NumberColumn(min_value=-180, max_value=180, step=1, default=0),
            "face_id": None,
        },
    )
    for _, r in edited.dropna(subset=[wid, lng, tilt, ori]).iterrows():
        if r[inc]:
            n = fit_panels(r[wid], r[lng], panel_w, panel_l, margin)
            arrays.append({"tilt": r[tilt], "azimuth": r[ori], "kwp": n * panel_wp / 1000, "panels": n,
                           "face_id": r["face_id"]})

# ---- Carte : vue aérienne swisstopo, affichée au-dessus des tableaux --------------------------
with map_slot:
    equipped = {a["face_id"] for a in arrays if a["kwp"] > 0}
    fmap = base_map([lat, lon], 20)
    for f in faces:
        mine = f["building_id"] == building
        fill = PANEL if f["id"] in equipped else CLASS_COLORS[f["klasse"]]
        folium.Polygon(
            [(y, x) for x, y in f["ring"]],
            color="#ffffff", weight=1.4 if mine else 0.6, fill=True, fill_color=fill,
            fill_opacity=(0.85 if f["id"] in equipped else 0.6) if mine else 0.28,
            tooltip=f"{orientation(f['azimuth'])} · {f['tilt']:.0f}° · {f['area']:.0f} m² · {klass(f['klasse'])}",
        ).add_to(fmap)
    folium.CircleMarker([lat, lon], radius=6, color="#ffffff", weight=2, fill=True, fill_color="#e4572e",
                        fill_opacity=1).add_to(fmap)
    if bfaces:
        pts = [(y, x) for f in bfaces for x, y in f["ring"]]
        fmap.fit_bounds([[min(p[0] for p in pts), min(p[1] for p in pts)],
                         [max(p[0] for p in pts), max(p[1] for p in pts)]], padding=(30, 30))
    out = st_folium(fmap, height=MAP_HEIGHT, use_container_width=True, returned_objects=["last_clicked"],
                    key=f"map-{bkey}")
    st.caption(t("map_note"))
    click = (out or {}).get("last_clicked")
    if click:
        hit = next((f["building_id"] for f in faces if geo.contains(f["ring"], click["lng"], click["lat"])), None)
        if hit is not None and hit != building:
            st.session_state[bkey] = hit
            st.rerun()

kwp = sum(a["kwp"] for a in arrays)
if kwp <= 0:
    st.session_state.pop("system", None)
    st.info(t("pick_face"), icon=":material/solar_power:")
    st.stop()

# ---- Production -------------------------------------------------------------------------------
st.subheader(t("production"))
try:
    with st.spinner(t("loading_pvgis")):
        monthly_lt = sum(pvgis(lat, lon, a["tilt"], a["azimuth"], loss) * a["kwp"] for a in arrays)
except ApiError as e:
    fail(e)
annual_lt = monthly_lt.sum()
panels = sum(a["panels"] for a in arrays)
st.session_state.system = {"lat": lat, "lon": lon, "loss": loss, "kwp": kwp, "annual": annual_lt, "arrays": arrays}

if analysis == "basic":
    m = st.columns(4)
    m[0].metric(t("m_annual"), f"{kwh(annual_lt)} kWh")
    m[1].metric(t("m_power"), f"{kwp:.1f} {t('unit_kwp')}")
    m[2].metric(t("m_specific"), f"{kwh(annual_lt / kwp)} kWh/{t('unit_kwp')}")
    m[3].metric(t("m_panels"), f"≈ {panels}")

    fig = go.Figure(go.Bar(x=months(), y=monthly_lt.values, marker_color=BLUE,
                           hovertemplate="%{x} : %{y:,.0f} kWh<extra></extra>"))
    st.plotly_chart(style(fig, t("c_monthly_avg"), t("y_month")), width="stretch")
    st.caption(t("note_basic", loss=loss, wp=panel_wp, l=panel_l, w=panel_w))
else:
    years_all = list(range(pv.LAST_YEAR, pv.FIRST_YEAR - 1, -1))
    years = st.multiselect(t("years"), years_all, default=years_all[:3],
                           help=t("years_help", a=pv.FIRST_YEAR, b=pv.LAST_YEAR))
    if not years:
        st.info(t("pick_year"))
        st.stop()
    try:
        with st.spinner(t("loading_meteo")):
            series = [hourly(lat, lon, a["tilt"], a["azimuth"], loss, min(years), max(years)) * a["kwp"]
                      for a in arrays]
    except ApiError as e:
        fail(e)
    h = pd.concat(series, axis=1).sum(axis=1)
    h = h[h.index.year.isin(years)]
    annual = h.groupby(h.index.year).sum()
    by_month = h.groupby([h.index.year, h.index.month]).sum().unstack()  # années x mois
    avg = annual.mean()

    m = st.columns(4)
    label = t("m_avg_years", a=min(years), b=max(years)) if len(years) > 1 else t("m_year", y=years[0])
    m[0].metric(label, f"{kwh(avg)} kWh", t("m_vs_pvgis", d=f"{avg / annual_lt - 1:+.1%}"), delta_color="off")
    m[1].metric(t("m_best"), f"{annual.idxmax()}", f"{kwh(annual.max())} kWh", delta_color="off")
    m[2].metric(t("m_worst"), f"{annual.idxmin()}", f"{kwh(annual.min())} kWh", delta_color="off")
    m[3].metric(t("m_power"), f"{kwp:.1f} {t('unit_kwp')}", t("n_panels", n=panels), delta_color="off")

    left, right = st.columns(2)
    with left:
        fig = go.Figure(go.Bar(x=[str(y) for y in annual.index], y=annual.values, marker_color=BLUE,
                               hovertemplate="%{x} : %{y:,.0f} kWh<extra></extra>"))
        fig.add_hline(y=avg, line=dict(color=INK, width=2, dash="dash"),
                      annotation_text=f"{t('average')} {kwh(avg)} kWh", annotation_font_color=INK2,
                      annotation_position="top left")
        st.plotly_chart(style(fig, t("c_yearly"), t("y_year")).update_layout(showlegend=False), width="stretch")
    with right:
        lo, hi, mean = by_month.min(), by_month.max(), by_month.mean()
        fig = go.Figure()
        if len(years) > 1:
            fig.add_trace(go.Scatter(x=months(), y=hi.values, line=dict(width=0), hoverinfo="skip", showlegend=False))
            fig.add_trace(go.Scatter(x=months(), y=lo.values, fill="tonexty", fillcolor=BAND, line=dict(width=0),
                                     name=t("range"), hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=months(), y=mean.values, line=dict(color=BLUE, width=2), mode="lines+markers",
                                 marker=dict(size=8), name=t("average"),
                                 hovertemplate="%{x} : %{y:,.0f} kWh<extra></extra>"))
        st.plotly_chart(style(fig, t("c_monthly"), t("y_month")).update_layout(hovermode="x"), width="stretch")

    season = h.index.month.map(lambda x: "summer" if x in (6, 7, 8) else "winter" if x in (12, 1, 2) else None)
    profile = h.groupby([season, h.index.hour]).mean().unstack(0)
    fig = go.Figure()
    for key, color in (("summer", ORANGE), ("winter", BLUE)):
        if key not in profile:
            continue
        fig.add_trace(go.Scatter(x=profile.index, y=profile[key].values, line=dict(color=color, width=2),
                                 name=f"{t(key)} ({t(key + '_months')})",
                                 hovertemplate=f"{t(key)} %{{x}} h : %{{y:.2f}} kWh<extra></extra>"))
        fig.add_annotation(x=int(profile[key].idxmax()), y=profile[key].max(), text=t(key), showarrow=False,
                           yshift=12, font_color=INK2)
    fig.update_xaxes(tickvals=list(range(0, 24, 3)), ticksuffix=" h")
    st.plotly_chart(style(fig, t("c_day"), t("y_hour")).update_layout(hovermode="x unified"), width="stretch")

    with st.expander(t("table"), icon=":material/table:"):
        tab = by_month.set_axis(months(), axis=1)
        tab[t("total")] = annual
        st.dataframe(tab.round(0), width="stretch",
                     column_config={c: st.column_config.NumberColumn(format="%d") for c in tab.columns})
    st.caption(t("note_advanced", loss=loss))
