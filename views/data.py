"""Données & méthode : sources utilisées et hypothèses de calcul."""
import streamlit as st

from i18n import t

st.markdown(f'<div class="eyebrow">{t("nav_data")}</div>', unsafe_allow_html=True)
st.title(t("data_title"))

st.subheader(t("data_sources"))
st.markdown(
    f"- [sonnendach.ch](https://www.uvek-gis.admin.ch/BFE/sonnendach/) · {t('src_cadastre')}\n"
    f"- [PVGIS](https://re.jrc.ec.europa.eu/pvg_tools/) · {t('src_pvgis')}\n"
    f"- [Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api) · {t('src_meteo')}\n"
    "- [SWISSIMAGE](https://www.swisstopo.admin.ch/) · © swisstopo"
)

st.subheader(t("data_method"))
st.markdown(t("method_text"))
