"""Analyse complète (étapes 2 à 4 : prix, scénarios, batterie). Pour l'instant : à venir."""
import streamlit as st

from i18n import kwh, t

st.markdown(f'<div class="eyebrow">{t("nav_analysis")}</div>', unsafe_allow_html=True)
st.title(t("an_title"))
st.markdown(f'<p class="lead">{t("an_soon")}</p>', unsafe_allow_html=True)

system = st.session_state.get("system")
if system:
    st.success(t("an_system", kwp=system["kwp"], kwh=kwh(system["annual"])), icon=":material/solar_power:")
else:
    st.info(t("an_no_system"), icon=":material/arrow_back:")
    st.page_link("views/estimate.py", label=t("nav_estimate"), icon=":material/solar_power:")
