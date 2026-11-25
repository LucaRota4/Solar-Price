"""Production photovoltaïque d'un pan de toit, pour 1 kWc installé.

Deux sources :
  - PVGIS (Commission européenne, base SARAH3) : moyenne de long terme 2005-2023.
    Référence standard, utilisée pour l'analyse de base.
  - Open-Meteo (réanalyse ERA5) : météo horaire réelle jusqu'à l'année dernière,
    utilisée pour l'analyse année par année. PVGIS n'a pas de données après 2023.

Tout est calculé pour 1 kWc puis multiplié par la puissance du pan : un seul appel
par pan et par source, et le cache sert quand on change le nombre de panneaux.
"""
from datetime import date

import pandas as pd

from http_cache import get_json

PVGIS = "https://re.jrc.ec.europa.eu/api/v5_3"
OPEN_METEO = "https://archive-api.open-meteo.com/v1/archive"
PVGIS_YEARS = (2005, 2023)
FIRST_YEAR = 2005
LAST_YEAR = date.today().year - 1  # dernière année complète

# Modèle simple pour Open-Meteo (PVGIS a son propre modèle) :
TEMP_COEF = -0.004  # perte de puissance par °C au-dessus de 25 °C (silicium cristallin)
NOCT_FACTOR = (45 - 20) / 800  # échauffement du module par W/m² (NOCT 45 °C)


def pvgis_monthly(lat: float, lon: float, tilt: float, azimuth: float, loss: float) -> pd.Series:
    """Production mensuelle moyenne 2005-2023 (kWh par kWc), index 1..12."""
    data = get_json(
        f"{PVGIS}/PVcalc",
        {
            "lat": round(lat, 4),
            "lon": round(lon, 4),
            "peakpower": 1,
            "loss": loss,
            "angle": round(tilt),
            "aspect": round(azimuth),
            "outputformat": "json",
        },
        source="PVGIS",
    )
    months = data["outputs"]["monthly"]["fixed"]
    return pd.Series({m["month"]: m["E_m"] for m in months}, name="kWh")


def hourly_by_year(lat: float, lon: float, tilt: float, azimuth: float, loss: float,
                   start: int, end: int) -> pd.Series:
    """Production horaire (kWh par kWc, heure locale suisse) de start à end inclus."""
    data = get_json(
        OPEN_METEO,
        {
            "latitude": round(lat, 4),
            "longitude": round(lon, 4),
            "start_date": f"{start}-01-01",
            "end_date": f"{end}-12-31",
            "hourly": "global_tilted_irradiance,temperature_2m",
            "tilt": round(tilt),
            "azimuth": round(azimuth),
            "timezone": "Europe/Zurich",
        },
        source="Open-Meteo",
    )
    h = data["hourly"]
    df = pd.DataFrame(
        {"gti": h["global_tilted_irradiance"], "t": h["temperature_2m"]},
        index=pd.to_datetime(h["time"]),
    ).fillna(0)
    t_cell = df["t"] + df["gti"] * NOCT_FACTOR
    kw = df["gti"] / 1000 * (1 + TEMP_COEF * (t_cell - 25)) * (1 - loss / 100)
    return kw.clip(lower=0).rename("kWh")
