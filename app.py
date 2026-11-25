"""Point d'entrée : barre de navigation, langue, style et pied de page.

Lancer :  streamlit run app.py
"""
import streamlit as st

from i18n import LANG_NAMES, LANGS, t

st.set_page_config(page_title="Solar Price", page_icon=":material/solar_power:", layout="wide", initial_sidebar_state="expanded")

if "lang" not in st.session_state:
    st.session_state.lang = "fr"

st.markdown(
    """
<style>
.block-container { max-width: 1380px; }
[data-stale="true"] { opacity: 1 !important; transition: none !important; }  /* pas de voile gris pendant un recalcul */
h1 { font-weight: 650; letter-spacing: -0.02em; font-size: 2.1rem !important; }
h2, h3 { font-weight: 600; letter-spacing: -0.01em; }
.lead { color: #9a9ea8; font-size: 1.02rem; line-height: 1.6; max-width: 760px; margin: -0.4rem 0 1.6rem; }
.eyebrow { font-size: 0.72rem; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; color: #6da7ec; }
[data-testid="stMetric"] { border: 1px solid #2a2e36; border-radius: 8px; padding: 14px 16px; background: #14171c; }
[data-testid="stMetricLabel"] p { font-size: 0.78rem; color: #8a8f99; text-transform: uppercase; letter-spacing: 0.06em; }
[data-testid="stMetricValue"] { font-weight: 600; letter-spacing: -0.02em; }
.credits { display: flex; gap: 8px 20px; align-items: center; flex-wrap: wrap; margin-top: 3rem; padding-top: 1.1rem;
    border-top: 1px solid #2a2e36; font-size: 0.82rem; color: #7d818b; }
.credits a { display: inline-flex; align-items: center; gap: 7px; color: #b4b8c1 !important; text-decoration: none; }
.credits a:hover { color: #6da7ec !important; }
</style>
""",
    unsafe_allow_html=True,
)

pages = [
    st.Page("views/estimate.py", title=t("nav_estimate"), icon=":material/solar_power:", default=True),
    st.Page("views/analysis.py", title=t("nav_analysis"), icon=":material/query_stats:"),
    st.Page("views/data.py", title=t("nav_data"), icon=":material/dataset:"),
]
page = st.navigation(pages, position="top")

_, lang_col = st.columns([5, 1])
lang_col.selectbox(t("language"), LANGS, key="lang", format_func=LANG_NAMES.get, label_visibility="collapsed")

page.run()

GITHUB_LOGO = (
    '<svg viewBox="0 0 16 16" width="15" height="15" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 '
    "3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-"
    ".48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78"
    "-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 "
    "1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29"
    ".25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0016 8c0-4.42-3.58-8-8-8z\"/></svg>"
)
st.markdown(
    f'<div class="credits"><span>{t("built_by")}</span>'
    f'<a href="https://github.com/LucaRota4" target="_blank" rel="noopener">{GITHUB_LOGO}<span>LucaRota4</span></a>'
    "<span>· sonnendach.ch · PVGIS · Open-Meteo</span></div>",
    unsafe_allow_html=True,
)
