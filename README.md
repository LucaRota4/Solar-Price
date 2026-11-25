# Solar Reality Check

> **Work in progress.** Only the first step is built and usable today: a production estimate for a real Swiss roof. The rest of what this project is meant to do is described below as *planned*. Numbers are indicative and have not been validated against measured production yet.

**An estimate of what a solar roof produces in Switzerland, aiming to be more precise than a typical installer's quote.**

A quote usually starts from a generic yield for a "south-facing roof" and a rounded surface. This project instead works from the actual roof: every face has its own size, tilt and orientation, obstacles take room away from the panels, and the production of each face is computed on its own. At the end of the project it will also show what the timing of that production is worth, because the sun produces most when every other roof does too, which is when electricity is cheapest, sometimes negative.

It is a personal project by [Luca Rota](https://github.com/LucaRota4). It runs on free public data, with no account and no API key.

## What it can do today

- **Find the roof.** Type an address (suggestions appear while you type) or click the map. Roofs load around the view as you browse, from the Swiss solar cadastre (sonnendach.ch).
- **Pick faces.** Click the roof faces to equip, from any building. Width, length, tilt, orientation and heights come from the cadastre and can all be corrected; the panel count adapts.
- **Redraw what is wrong.** A cross roof or a missing face? Draw it yourself. Each corner is a draggable point with its own height, and tilt and orientation follow from the heights. Corners that land close to each other merge, new heights are inferred from the neighbouring roofs, and you can set the real length of every side or slide the whole face.
- **Place the panels.** Faces are filled automatically inside their real outline (edge margin, panel size and power adjustable). Or switch a face to hand placement: drag panels around with snapping, add them and remove them, even over an obstacle.
- **Account for obstacles.** Roof windows, chimneys or custom sizes. Automatic filling avoids them, and you can move, resize and delete them. Handles and numbers only appear for the face or obstacle you are editing.
- **Estimate the production.** Yearly and monthly yield from PVGIS for each face with its own tilt and orientation, with the assumptions shown next to the numbers.
- Available in French, German, Italian and English.

## What it will be able to do when it is finished (planned, not built yet)

- **Value, not only energy.** Hourly Swiss market prices, the share of the production that is worth less than average (capture rate), the energy sold at low or negative prices, and the resulting loss in CHF.
- **Tariff scenarios.** The current quarterly reference price compared with quarter-hourly pricing and with curtailment of the peaks.
- **Real weather, year by year,** next to the long-term average.
- **Shading** from trees and neighbouring buildings, and inverter sizing and losses.
- **Battery and self-consumption,** from a consumption profile.
- **Long-term projection** with panel ageing.

## Assumptions and limits

- Production is PVGIS's 2005-2023 average, computed for 1 kWp per face and scaled to the installed power. System losses default to 14 % (cables, inverter, dust on the panels).
- There is **no shading** model yet, and roof obstacles are not detected automatically.
- Heights are relative to a common origin you choose; for now they drive the tilt, not shading.
- The accuracy of the estimate has not been compared with real installations yet.
- This is an indicative estimate. It does not replace an installer's study.

## Run it locally

```bash
python -m venv .venv
.venv/Scripts/activate        # on macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Downloaded data is cached on disk in `cache/` (ignored by git), so repeated runs are fast and light on the public APIs.

## Data sources

| Data | Source |
|---|---|
| Roof faces, tilt, orientation, suitability | [sonnendach.ch](https://www.uvek-gis.admin.ch/BFE/sonnendach/), Swiss Federal Office of Energy, via the geo.admin.ch API |
| Address search | geo.admin.ch SearchServer |
| Solar production | [PVGIS](https://re.jrc.ec.europa.eu/pvg_tools/), European Commission Joint Research Centre |
| Historical hourly weather (for the planned year-by-year analysis) | [Open-Meteo](https://open-meteo.com/) (CC BY 4.0) |
| Aerial imagery | SWISSIMAGE © swisstopo |
| Street map | © OpenStreetMap contributors |

## Project layout

```
app.py                  entry point: navigation, language, style
views/estimate.py       the estimate page: map, faces, panels, obstacles, production
geo.py                  geometry: roof faces, panel layout, snapping, planes from heights
pv.py                   PVGIS and Open-Meteo production
http_cache.py           JSON requests with disk cache
i18n.py                 texts in French, German, Italian and English
search_box.py           address box with suggestions (small Streamlit component, no build step)
```

## Author

Luca Rota · [github.com/LucaRota4](https://github.com/LucaRota4)
