"""Textes de l'interface en français, allemand, italien et anglais.

t("clé", var=...) renvoie le texte dans la langue choisie (st.session_state.lang).
Chaque entrée : (fr, de, it, en).
"""
import streamlit as st

LANGS = ["fr", "de", "it", "en"]
LANG_NAMES = {"fr": "Français", "de": "Deutsch", "it": "Italiano", "en": "English"}

TEXT = {
    # Navigation et pied de page
    "brand": ("Solar Price", "Solar Price", "Solar Price", "Solar Price"),
    "nav_estimate": ("Estimation solaire", "Solarschätzung", "Stima solare", "Solar estimate"),
    "nav_analysis": ("Analyse complète", "Gesamtanalyse", "Analisi completa", "Full analysis"),
    "nav_data": ("Données & méthode", "Daten & Methode", "Dati e metodo", "Data & method"),
    "built_by": ("Réalisé par", "Entwickelt von", "Realizzato da", "Built by"),
    "language": ("Langue", "Sprache", "Lingua", "Language"),
    # Estimation : en-tête et adresse
    "est_title": ("Production solaire de votre toit", "Solarproduktion Ihres Dachs",
                  "Produzione solare del vostro tetto", "Solar production of your roof"),
    "est_intro": (
        "Entrez votre adresse : le toit est détecté automatiquement grâce au cadastre solaire suisse. "
        "Choisissez les pans à équiper et obtenez la production annuelle estimée.",
        "Geben Sie Ihre Adresse ein: Das Dach wird über den Solarkataster der Schweiz automatisch erkannt. "
        "Wählen Sie die Dachflächen aus und erhalten Sie die geschätzte Jahresproduktion.",
        "Inserite il vostro indirizzo: il tetto viene rilevato automaticamente grazie al catasto solare svizzero. "
        "Scegliete le falde da equipaggiare e ottenete la produzione annua stimata.",
        "Enter your address: the roof is detected automatically from the Swiss solar cadastre. "
        "Pick the roof faces to equip and get the estimated yearly production.",
    ),
    "address": ("Adresse", "Adresse", "Indirizzo", "Address"),
    "address_ph": ("Rue et numéro, NPA localité", "Strasse und Nummer, PLZ Ort", "Via e numero, NPA località",
                   "Street and number, postcode town"),
    "address_start": ("Commencez par entrer une adresse en Suisse.", "Geben Sie zuerst eine Adresse in der Schweiz ein.",
                      "Iniziate inserendo un indirizzo in Svizzera.", "Start by entering an address in Switzerland."),
    "address_none": ("Adresse introuvable. Vérifiez l'orthographe ou ajoutez le NPA.",
                     "Adresse nicht gefunden. Prüfen Sie die Schreibweise oder ergänzen Sie die PLZ.",
                     "Indirizzo non trovato. Verificate l'ortografia o aggiungete il NPA.",
                     "Address not found. Check the spelling or add the postcode."),
    "address_found": ("Adresse trouvée", "Gefundene Adresse", "Indirizzo trovato", "Address found"),
    "api_error": ("{source} ne répond pas pour le moment ({detail}). Réessayez dans un instant.",
                  "{source} antwortet im Moment nicht ({detail}). Versuchen Sie es gleich nochmals.",
                  "{source} non risponde al momento ({detail}). Riprovate tra un istante.",
                  "{source} is not responding right now ({detail}). Try again in a moment."),
    # Modes
    "mode": ("Mode", "Modus", "Modalità", "Mode"),
    "simple": ("Simple", "Einfach", "Semplice", "Simple"),
    "detailed": ("Détaillé", "Detailliert", "Dettagliata", "Detailed"),
    "analysis": ("Analyse", "Analyse", "Analisi", "Analysis"),
    "basic": ("De base", "Basis", "Di base", "Basic"),
    "advanced": ("Poussée", "Vertieft", "Approfondita", "Advanced"),
    "building": ("Bâtiment", "Gebäude", "Edificio", "Building"),
    "building_here": ("Bâtiment à l'adresse", "Gebäude an der Adresse", "Edificio all'indirizzo", "Building at the address"),
    "building_near": ("Bâtiment voisin ({id})", "Nachbargebäude ({id})", "Edificio vicino ({id})", "Neighbouring building ({id})"),
    "building_help": ("Si le mauvais bâtiment est détecté, choisissez-en un autre.",
                      "Falls das falsche Gebäude erkannt wurde, wählen Sie ein anderes.",
                      "Se è stato rilevato l'edificio sbagliato, sceglietene un altro.",
                      "If the wrong building was detected, pick another one."),
    "no_roof": (
        "Aucun toit trouvé dans le cadastre solaire à cette adresse. Saisissez vos pans de toit à la main.",
        "Kein Dach im Solarkataster an dieser Adresse gefunden. Erfassen Sie Ihre Dachflächen von Hand.",
        "Nessun tetto trovato nel catasto solare a questo indirizzo. Inserite le falde a mano.",
        "No roof found in the solar cadastre at this address. Enter your roof faces by hand.",
    ),
    # Hypothèses
    "assumptions": ("Hypothèses de calcul", "Berechnungsannahmen", "Ipotesi di calcolo", "Calculation assumptions"),
    "loss": ("Pertes système (%)", "Systemverluste (%)", "Perdite di sistema (%)", "System losses (%)"),
    "loss_help": ("Câbles, onduleur, salissures. 14 % est la valeur par défaut de PVGIS.",
                  "Kabel, Wechselrichter, Verschmutzung. 14 % ist der Standardwert von PVGIS.",
                  "Cavi, inverter, sporcizia. 14 % è il valore predefinito di PVGIS.",
                  "Cables, inverter, soiling. 14 % is the PVGIS default."),
    "panel_wp": ("Puissance d'un panneau (Wc)", "Leistung pro Modul (Wp)", "Potenza di un pannello (Wp)", "Panel power (Wp)"),
    "panel_l": ("Longueur panneau (m)", "Modullänge (m)", "Lunghezza pannello (m)", "Panel length (m)"),
    "panel_w": ("Largeur panneau (m)", "Modulbreite (m)", "Larghezza pannello (m)", "Panel width (m)"),
    "usable": ("Part de chaque pan couverte de panneaux", "Mit Modulen belegter Anteil jeder Fläche",
               "Quota di ogni falda coperta da pannelli", "Share of each face covered with panels"),
    "usable_help": ("Marges, fenêtres de toit, cheminées : on ne couvre jamais 100 % d'un pan.",
                    "Randabstände, Dachfenster, Kamine: Eine Fläche wird nie zu 100 % belegt.",
                    "Margini, lucernari, camini: una falda non è mai coperta al 100 %.",
                    "Edges, roof windows, chimneys: a face is never 100 % covered."),
    "margin": ("Marge au bord des pans (m)", "Randabstand (m)", "Margine dal bordo (m)", "Edge margin (m)"),
    # Pans de toit
    "faces": ("Pans de toit", "Dachflächen", "Falde del tetto", "Roof faces"),
    "faces_simple_note": (
        "Cochez les pans à couvrir de panneaux. Par défaut : les pans d'aptitude bonne ou mieux, sinon les meilleurs.",
        "Wählen Sie die zu belegenden Flächen. Standard: Flächen mit guter oder besserer Eignung, sonst die besten.",
        "Selezionate le falde da coprire. Predefinite: le falde con idoneità buona o migliore, altrimenti le migliori.",
        "Tick the faces to cover with panels. Default: faces rated good or better, otherwise the best ones.",
    ),
    "faces_detail_note": (
        "Dimensions estimées depuis le cadastre : ajustez-les, changez l'inclinaison ou l'orientation "
        "(0° = sud, -90° = est, 90° = ouest), ou ajoutez des pans.",
        "Aus dem Kataster geschätzte Masse: Passen Sie sie an, ändern Sie Neigung oder Ausrichtung "
        "(0° = Süd, -90° = Ost, 90° = West) oder fügen Sie Flächen hinzu.",
        "Dimensioni stimate dal catasto: modificatele, cambiate inclinazione o orientamento "
        "(0° = sud, -90° = est, 90° = ovest), o aggiungete falde.",
        "Dimensions estimated from the cadastre: adjust them, change tilt or orientation "
        "(0° = south, -90° = east, 90° = west), or add faces.",
    ),
    "col_panels": ("Panneaux", "Module", "Pannelli", "Panels"),
    "col_include": ("Inclure", "Einbeziehen", "Includere", "Include"),
    "col_face": ("Pan", "Fläche", "Falda", "Face"),
    "col_orient": ("Orientation", "Ausrichtung", "Orientamento", "Orientation"),
    "col_tilt": ("Inclinaison", "Neigung", "Inclinazione", "Tilt"),
    "col_area": ("Surface (m²)", "Fläche (m²)", "Superficie (m²)", "Area (m²)"),
    "col_class": ("Aptitude", "Eignung", "Idoneità", "Suitability"),
    "col_irr": ("Ensoleillement (kWh/m²/an)", "Einstrahlung (kWh/m²/Jahr)", "Irraggiamento (kWh/m²/anno)",
                "Irradiation (kWh/m²/yr)"),
    "col_width": ("Largeur (m)", "Breite (m)", "Larghezza (m)", "Width (m)"),
    "col_length": ("Longueur pente (m)", "Länge in Neigung (m)", "Lunghezza in pendenza (m)", "Slope length (m)"),
    "col_tilt_deg": ("Inclinaison (°)", "Neigung (°)", "Inclinazione (°)", "Tilt (°)"),
    "col_orient_deg": ("Orientation (°)", "Ausrichtung (°)", "Orientamento (°)", "Orientation (°)"),
    "map_note": (
        "Bleu : pans équipés. Gris à brun : aptitude du pan selon le cadastre solaire. Point : l'adresse.",
        "Blau: belegte Flächen. Grau bis Braun: Eignung laut Solarkataster. Punkt: die Adresse.",
        "Blu: falde equipaggiate. Da grigio a marrone: idoneità secondo il catasto solare. Punto: l'indirizzo.",
        "Blue: equipped faces. Grey to brown: suitability from the solar cadastre. Dot: the address.",
    ),
    "pick_face": ("Sélectionnez au moins un pan de toit pour estimer la production.",
                  "Wählen Sie mindestens eine Dachfläche, um die Produktion zu schätzen.",
                  "Selezionate almeno una falda per stimare la produzione.",
                  "Select at least one roof face to estimate the production."),
    # Production
    "production": ("Production estimée", "Geschätzte Produktion", "Produzione stimata", "Estimated production"),
    "loading_pvgis": ("Calcul de la production (PVGIS)…", "Berechnung der Produktion (PVGIS)…",
                      "Calcolo della produzione (PVGIS)…", "Computing production (PVGIS)…"),
    "loading_meteo": ("Téléchargement de la météo heure par heure…", "Stündliche Wetterdaten werden geladen…",
                      "Scaricamento dei dati meteo orari…", "Downloading hourly weather…"),
    "m_annual": ("Production annuelle", "Jahresproduktion", "Produzione annua", "Yearly production"),
    "m_power": ("Puissance installée", "Installierte Leistung", "Potenza installata", "Installed power"),
    "m_specific": ("Rendement spécifique", "Spezifischer Ertrag", "Resa specifica", "Specific yield"),
    "unit_kwp": ("kWc", "kWp", "kWp", "kWp"),
    "m_panels": ("Panneaux", "Module", "Pannelli", "Panels"),
    "m_avg_years": ("Moyenne {a}-{b}", "Mittel {a}-{b}", "Media {a}-{b}", "Average {a}-{b}"),
    "m_year": ("Année {y}", "Jahr {y}", "Anno {y}", "Year {y}"),
    "m_vs_pvgis": ("{d} vs moyenne PVGIS", "{d} vs. PVGIS-Mittel", "{d} vs media PVGIS", "{d} vs PVGIS average"),
    "m_best": ("Meilleure année", "Bestes Jahr", "Anno migliore", "Best year"),
    "m_worst": ("Moins bonne année", "Schwächstes Jahr", "Anno peggiore", "Weakest year"),
    "n_panels": ("≈ {n} panneaux", "≈ {n} Module", "≈ {n} pannelli", "≈ {n} panels"),
    "years": ("Années analysées", "Analysierte Jahre", "Anni analizzati", "Years analysed"),
    "years_help": ("Météo réelle heure par heure, de {a} à {b}.", "Effektives Wetter Stunde für Stunde, {a} bis {b}.",
                   "Meteo reale ora per ora, dal {a} al {b}.", "Actual hourly weather, {a} to {b}."),
    "pick_year": ("Choisissez au moins une année.", "Wählen Sie mindestens ein Jahr.", "Scegliete almeno un anno.",
                  "Pick at least one year."),
    "c_monthly_avg": ("Production mensuelle moyenne", "Durchschnittliche Monatsproduktion",
                      "Produzione mensile media", "Average monthly production"),
    "c_yearly": ("Production par année", "Produktion pro Jahr", "Produzione per anno", "Production per year"),
    "c_monthly": ("Production mensuelle", "Monatsproduktion", "Produzione mensile", "Monthly production"),
    "c_day": ("Journée type", "Typischer Tag", "Giornata tipo", "Typical day"),
    "y_month": ("kWh par mois", "kWh pro Monat", "kWh al mese", "kWh per month"),
    "y_year": ("kWh par an", "kWh pro Jahr", "kWh all'anno", "kWh per year"),
    "y_hour": ("kWh par heure", "kWh pro Stunde", "kWh all'ora", "kWh per hour"),
    "average": ("Moyenne", "Mittel", "Media", "Average"),
    "range": ("Écart entre années (min-max)", "Spanne zwischen Jahren (Min-Max)", "Scarto tra anni (min-max)",
              "Range across years (min-max)"),
    "summer": ("Été", "Sommer", "Estate", "Summer"),
    "winter": ("Hiver", "Winter", "Inverno", "Winter"),
    "summer_months": ("juin-août", "Juni-Aug.", "giugno-agosto", "Jun-Aug"),
    "winter_months": ("déc-fév", "Dez.-Feb.", "dicembre-febbraio", "Dec-Feb"),
    "table": ("Tableau des valeurs", "Wertetabelle", "Tabella dei valori", "Data table"),
    "total": ("Total", "Total", "Totale", "Total"),
    "note_basic": (
        "Hypothèses : moyenne PVGIS 2005-2023 (satellite SARAH3, ombre du relief incluse), pertes système {loss} %, "
        "panneaux de {wp} Wc ({l} × {w} m). L'ombre des arbres et des bâtiments voisins n'est pas comptée.",
        "Annahmen: PVGIS-Mittel 2005-2023 (Satellit SARAH3, Geländeschatten berücksichtigt), Systemverluste {loss} %, "
        "Module mit {wp} Wp ({l} × {w} m). Schatten von Bäumen und Nachbargebäuden ist nicht berücksichtigt.",
        "Ipotesi: media PVGIS 2005-2023 (satellite SARAH3, ombra del rilievo inclusa), perdite di sistema {loss} %, "
        "pannelli da {wp} Wp ({l} × {w} m). L'ombra di alberi ed edifici vicini non è considerata.",
        "Assumptions: PVGIS average 2005-2023 (SARAH3 satellite, terrain shading included), system losses {loss} %, "
        "{wp} Wp panels ({l} × {w} m). Shading from trees and neighbouring buildings is not included.",
    ),
    "note_advanced": (
        "Hypothèses : météo horaire réelle Open-Meteo (réanalyse ERA5, maille d'environ 10 km), irradiation calculée "
        "sur le plan de chaque pan, perte de 0,4 %/°C au-dessus de 25 °C, pertes système {loss} %. Modèle plus simple "
        "que PVGIS : l'écart avec la moyenne PVGIS donne une idée de l'incertitude. Ombrage non compté.",
        "Annahmen: effektives Stundenwetter von Open-Meteo (ERA5-Reanalyse, Raster von rund 10 km), Einstrahlung "
        "auf die Ebene jeder Fläche berechnet, Verlust von 0,4 %/°C über 25 °C, Systemverluste {loss} %. Einfacheres "
        "Modell als PVGIS: Die Abweichung zum PVGIS-Mittel zeigt die Unsicherheit. Verschattung nicht berücksichtigt.",
        "Ipotesi: meteo oraria reale Open-Meteo (rianalisi ERA5, maglia di circa 10 km), irraggiamento calcolato sul "
        "piano di ogni falda, perdita dello 0,4 %/°C sopra i 25 °C, perdite di sistema {loss} %. Modello più semplice "
        "di PVGIS: lo scarto con la media PVGIS indica l'incertezza. Ombreggiamento non considerato.",
        "Assumptions: actual hourly weather from Open-Meteo (ERA5 reanalysis, ~10 km grid), irradiation computed on "
        "the plane of each face, 0.4 %/°C loss above 25 °C, system losses {loss} %. Simpler model than PVGIS: the gap "
        "to the PVGIS average gives an idea of the uncertainty. Shading not included.",
    ),
    # Analyse complète (à venir)
    "an_title": ("Analyse complète", "Gesamtanalyse", "Analisi completa", "Full analysis"),
    "an_soon": (
        "Bientôt : ce que vaut réellement votre production. Prix du marché heure par heure, kWh vendus à prix bas "
        "ou négatif, manque à gagner, rétribution actuelle et dès 2027, écrêtage et batterie.",
        "Demnächst: Was Ihre Produktion wirklich wert ist. Marktpreise Stunde für Stunde, zu tiefen oder negativen "
        "Preisen verkaufte kWh, Mindererlös, heutige Vergütung und ab 2027, Abregelung und Batterie.",
        "Prossimamente: quanto vale davvero la vostra produzione. Prezzi di mercato ora per ora, kWh venduti a prezzi "
        "bassi o negativi, mancato guadagno, rimunerazione attuale e dal 2027, limitazione e batteria.",
        "Coming soon: what your production is really worth. Hourly market prices, kWh sold at low or negative prices, "
        "lost revenue, current and 2027 feed-in rules, curtailment and battery.",
    ),
    "an_system": ("Installation retenue : {kwp:.1f} kWc, environ {kwh} kWh par an.",
                  "Gewählte Anlage: {kwp:.1f} kWp, rund {kwh} kWh pro Jahr.",
                  "Impianto scelto: {kwp:.1f} kWp, circa {kwh} kWh all'anno.",
                  "Selected system: {kwp:.1f} kWp, about {kwh} kWh per year."),
    "an_no_system": ("Commencez par l'estimation solaire pour définir votre installation.",
                     "Beginnen Sie mit der Solarschätzung, um Ihre Anlage festzulegen.",
                     "Iniziate dalla stima solare per definire il vostro impianto.",
                     "Start with the solar estimate to define your system."),
    # Données & méthode
    "data_title": ("Données & méthode", "Daten & Methode", "Dati e metodo", "Data & method"),
    "data_sources": ("Sources", "Quellen", "Fonti", "Sources"),
    "data_method": ("Méthode", "Methode", "Metodo", "Method"),
    "src_cadastre": (
        "Cadastre solaire suisse (sonnendach.ch, OFEN) via geo.admin.ch : adresse, contour, surface, inclinaison, "
        "orientation et aptitude de chaque pan de toit.",
        "Solarkataster Schweiz (sonnendach.ch, BFE) über geo.admin.ch: Adresse, Umriss, Fläche, Neigung, Ausrichtung "
        "und Eignung jeder Dachfläche.",
        "Catasto solare svizzero (tettosolare.ch, UFE) tramite geo.admin.ch: indirizzo, contorno, superficie, "
        "inclinazione, orientamento e idoneità di ogni falda.",
        "Swiss solar cadastre (sonnendach.ch, SFOE) via geo.admin.ch: address, outline, area, tilt, orientation and "
        "suitability of each roof face.",
    ),
    "src_pvgis": (
        "PVGIS (Commission européenne) : production moyenne de long terme 2005-2023, base satellite SARAH3.",
        "PVGIS (Europäische Kommission): langjährige Durchschnittsproduktion 2005-2023, Satellitendaten SARAH3.",
        "PVGIS (Commissione europea): produzione media di lungo periodo 2005-2023, dati satellitari SARAH3.",
        "PVGIS (European Commission): long-term average production 2005-2023, SARAH3 satellite data.",
    ),
    "src_meteo": (
        "Open-Meteo : météo horaire réelle (réanalyse ERA5) jusqu'à l'année dernière, pour l'analyse année par année.",
        "Open-Meteo: effektives Stundenwetter (ERA5-Reanalyse) bis zum Vorjahr, für die Analyse Jahr für Jahr.",
        "Open-Meteo: meteo oraria reale (rianalisi ERA5) fino all'anno scorso, per l'analisi anno per anno.",
        "Open-Meteo: actual hourly weather (ERA5 reanalysis) up to last year, for the year-by-year analysis.",
    ),
    "method_text": (
        "Simple : chaque pan coché est couvert à la part choisie, la puissance découle de la surface et de la "
        "densité des panneaux. Détaillé : le nombre de panneaux est calculé sur les dimensions de chaque pan, en "
        "portrait ou en paysage. La production est calculée pour 1 kWc par pan puis multipliée par sa puissance.",
        "Einfach: Jede gewählte Fläche wird zum gewählten Anteil belegt, die Leistung ergibt sich aus Fläche und "
        "Moduldichte. Detailliert: Die Modulanzahl wird aus den Massen jeder Fläche berechnet, hoch oder quer. Die "
        "Produktion wird pro Fläche für 1 kWp berechnet und mit deren Leistung multipliziert.",
        "Semplice: ogni falda scelta è coperta per la quota indicata, la potenza deriva da superficie e densità dei "
        "pannelli. Dettagliata: il numero di pannelli è calcolato dalle dimensioni di ogni falda, in verticale o in "
        "orizzontale. La produzione è calcolata per 1 kWp per falda e moltiplicata per la sua potenza.",
        "Simple: each ticked face is covered at the chosen share, power follows from area and panel density. "
        "Detailed: the number of panels is computed from each face's dimensions, portrait or landscape. Production "
        "is computed for 1 kWp per face, then multiplied by its power.",
    ),
}

MONTHS = {
    "fr": ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sep", "Oct", "Nov", "Déc"],
    "de": ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"],
    "it": ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"],
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
}
CLASSES = {
    "fr": ["Faible", "Moyenne", "Bonne", "Très bonne", "Excellente"],
    "de": ["Gering", "Mittel", "Gut", "Sehr gut", "Hervorragend"],
    "it": ["Bassa", "Media", "Buona", "Molto buona", "Eccellente"],
    "en": ["Low", "Medium", "Good", "Very good", "Excellent"],
}
COMPASS = {  # sud, sud-ouest, ouest, ... dans le sens de l'azimut (0 = sud, 90 = ouest)
    "fr": ["Sud", "Sud-Ouest", "Ouest", "Nord-Ouest", "Nord", "Nord-Est", "Est", "Sud-Est"],
    "de": ["Süd", "Südwest", "West", "Nordwest", "Nord", "Nordost", "Ost", "Südost"],
    "it": ["Sud", "Sud-Ovest", "Ovest", "Nord-Ovest", "Nord", "Nord-Est", "Est", "Sud-Est"],
    "en": ["South", "South-West", "West", "North-West", "North", "North-East", "East", "South-East"],
}


def lang() -> str:
    return st.session_state.get("lang", "fr")


def t(key: str, **kw) -> str:
    text = TEXT[key][LANGS.index(lang())]
    return text.format(**kw) if kw else text


def t_fixed():
    """Comme t(), mais avec la langue figée maintenant. À utiliser pour les format_func des
    widgets, que Streamlit peut appeler hors de l'exécution du script."""
    i = LANGS.index(lang())

    def tr(key: str, **kw) -> str:
        text = TEXT[key][i]
        return text.format(**kw) if kw else text

    return tr


def months() -> list[str]:
    return MONTHS[lang()]


def klass(k: int) -> str:
    return CLASSES[lang()][k - 1]


def orientation(azimuth: float) -> str:
    return f"{COMPASS[lang()][round((azimuth % 360) / 45) % 8]} ({azimuth:+.0f}°)"


def kwh(x: float) -> str:
    """Nombre au format suisse : 12'345."""
    return f"{x:,.0f}".replace(",", "'")
