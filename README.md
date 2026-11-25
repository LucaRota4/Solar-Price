# Solar Price

**How much does a solar roof really earn in Switzerland?** Installers quote an average yield. But the sun produces most at noon, when everybody's panels produce, and that is when electricity is cheapest, sometimes negative. Solar Price aims to show what that mismatch costs a homeowner, in energy and in money.

It is a personal project by [Luca Rota](https://github.com/LucaRota4). It runs entirely on free public data, with no account and no API key.

## Status

| Step | What | State |
|---|---|---|
| 1 | Production estimate from a real roof | **Done** (this is what you can try today) |
| 2 | Hourly market prices, capture rate, energy sold at negative prices | Planned |
| 3 | Tariff scenarios: quarterly feed-in today, quarter-hourly from 2027, curtailment | Planned |
| 4 | Battery and self-consumption | Planned |

The detailed list of ideas and what is next is in [ROADMAP.md](ROADMAP.md).

## What step 1 does

- **Find the roof.** Type an address (suggestions appear while you type) or click the map. Roofs load around the view as you browse, from the Swiss solar cadastre (sonnendach.ch).
- **Pick faces.** Click the roof faces to equip, from any building. Width, length, tilt, orientation and heights come from the cadastre and can all be corrected; the panel count adapts.
- **Redraw what is wrong.** A cross roof or a missing face? Draw the face yourself. Each corner is a draggable point with its own height; tilt and orientation follow from the heights. Corners that land close to each other merge, new heights are inferred from neighbouring roofs, and you can set the real length of every side.
- **Panels.** Faces are filled automatically inside their real outline (edge margin, panel size and power adjustable). Or switch a face to hand placement: drag panels around with snapping, add and remove them.
- **Obstacles.** Roof windows, chimneys or custom sizes. Panels avoid them, and you can move, resize and delete them.
- **Production.** Yearly and monthly yield from PVGIS, with the assumptions shown next to the numbers.
- French, German, Italian and English.

## Assumptions and limits

- Production is PVGIS's 2005-2023 average, computed for 1 kWp per face and scaled to the installed power. System losses default to 14 % (cables, inverter, dust on the panels).
- There is **no shading** model yet (trees, neighbouring buildings), and roof obstacles are not detected automatically.
- Heights are relative to a common origin you choose; they drive the tilt, not shading, for now.
- This is an indicative estimate. It does not replace an installer's study.

## Run it locally

```bash
python -m venv .venv
.venv/Scripts/activate        # on macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Downloaded data is cached on disk in `cache/` (ignored by git), so repeated runs are fast and light on the public APIs.

## Deploy

The app is a single Streamlit app (`app.py`) and runs as is on [Streamlit Community Cloud](https://share.streamlit.io): connect this repository, branch `main`, main file `app.py`. No secret is needed.

## Data sources

| Data | Source |
|---|---|
| Roof faces, tilt, orientation, suitability | [sonnendach.ch](https://www.uvek-gis.admin.ch/BFE/sonnendach/), Swiss Federal Office of Energy, via the geo.admin.ch API |
| Address search | geo.admin.ch SearchServer |
| Solar production | [PVGIS](https://re.jrc.ec.europa.eu/pvg_tools/), European Commission Joint Research Centre |
| Historical hourly weather (used later for year-by-year analysis) | [Open-Meteo](https://open-meteo.com/) (CC BY 4.0) |
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
