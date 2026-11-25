"""Barre d'adresse avec suggestions pendant la frappe (sans valider).

Petit composant Streamlit sans build : le navigateur interroge directement l'API de recherche geo.admin.ch
(même source que geo.search_address) et renvoie l'adresse choisie. Aucune dépendance en plus.
"""
from pathlib import Path

import streamlit.components.v1 as components

_component = components.declare_component("search_box", path=str(Path(__file__).parent / "search_box_frontend"))


def address_box(placeholder: str, no_result: str, value: str = "", key: str = "address"):
    """Renvoie {label, lat, lon, t} après un choix dans la liste, sinon None."""
    return _component(placeholder=placeholder, no_result=no_result, value=value, key=key, default=None)
