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
        "Entrez votre adresse ou cliquez sur un toit de la carte : il est détecté grâce au cadastre solaire suisse. "
        "Choisissez les pans à équiper et obtenez la production annuelle estimée.",
        "Geben Sie Ihre Adresse ein oder klicken Sie auf ein Dach der Karte: Es wird über den Solarkataster der "
        "Schweiz erkannt. Wählen Sie die Dachflächen aus und erhalten Sie die geschätzte Jahresproduktion.",
        "Inserite il vostro indirizzo o cliccate su un tetto della mappa: viene rilevato grazie al catasto solare "
        "svizzero. Scegliete le falde da equipaggiare e ottenete la produzione annua stimata.",
        "Enter your address or click a roof on the map: it is detected from the Swiss solar cadastre. "
        "Pick the roof faces to equip and get the estimated yearly production.",
    ),
    "click_no_roof": ("Pas de pan du cadastre solaire à cet endroit. Zoomez et cliquez sur un pan, ou dessinez-le avec l'outil « Dessiner un pan ».",
        'Keine Fläche des Solarkatasters an dieser Stelle. Zoomen Sie hinein und klicken Sie auf eine Fläche, oder zeichnen Sie sie mit «Fläche zeichnen».',
        'Nessuna falda del catasto solare in questo punto. Ingrandite e cliccate su una falda, oppure disegnatela con «Disegna falda».',
        'No solar-cadastre face here. Zoom in and click a face, or draw it with the “Draw a face” tool.',
    ),
    "mode_help": (
        "Simple : vous cochez les pans, l'app les remplit de panneaux. Détaillé : vous réglez vous-même les "
        "dimensions, l'inclinaison et l'orientation de chaque pan, et pouvez en ajouter.",
        "Einfach: Sie wählen die Flächen, die App belegt sie mit Modulen. Detailliert: Sie legen Masse, Neigung "
        "und Ausrichtung jeder Fläche selbst fest und können Flächen hinzufügen.",
        "Semplice: scegliete le falde, l'app le riempie di pannelli. Dettagliata: impostate voi dimensioni, "
        "inclinazione e orientamento di ogni falda, e potete aggiungerne.",
        "Simple: you tick the faces, the app fills them with panels. Detailed: you set the dimensions, tilt and "
        "orientation of each face yourself, and can add faces.",
    ),
    "analysis_help": (
        "De base : production d'une année moyenne (PVGIS, 2005-2023). Poussée : production année par année avec "
        "la météo réelle de chaque année, jusqu'en {y}.",
        "Basis: Produktion eines Durchschnittsjahrs (PVGIS, 2005-2023). Vertieft: Produktion Jahr für Jahr mit dem "
        "effektiven Wetter jedes Jahres, bis {y}.",
        "Di base: produzione di un anno medio (PVGIS, 2005-2023). Approfondita: produzione anno per anno con la "
        "meteo reale di ogni anno, fino al {y}.",
        "Basic: production of an average year (PVGIS, 2005-2023). Advanced: production year by year with each "
        "year's actual weather, up to {y}.",
    ),
    "mode_simple_desc": ("Mode simple : cochez les pans, ils sont remplis de panneaux automatiquement.",
                         "Einfacher Modus: Flächen wählen, sie werden automatisch mit Modulen belegt.",
                         "Modalità semplice: scegliete le falde, vengono riempite di pannelli automaticamente.",
                         "Simple mode: tick the faces, they are filled with panels automatically."),
    "mode_detailed_desc": ("Mode détaillé : réglez vous-même chaque pan.",
                           "Detaillierter Modus: Sie stellen jede Fläche selbst ein.",
                           "Modalità dettagliata: impostate voi ogni falda.",
                           "Detailed mode: you set each face yourself."),
    "analysis_basic_desc": ("Analyse de base : une année moyenne (PVGIS 2005-2023).",
                            "Basisanalyse: ein Durchschnittsjahr (PVGIS 2005-2023).",
                            "Analisi di base: un anno medio (PVGIS 2005-2023).",
                            "Basic analysis: an average year (PVGIS 2005-2023)."),
    "analysis_advanced_desc": ("Analyse poussée : chaque année avec sa météo réelle, jusqu'en {y}.",
                               "Vertiefte Analyse: jedes Jahr mit seinem effektiven Wetter, bis {y}.",
                               "Analisi approfondita: ogni anno con la sua meteo reale, fino al {y}.",
                               "Advanced analysis: each year with its actual weather, up to {y}."),
    "panel_wp_help": ("Se met à jour quand vous changez la taille du panneau (≈ 221 Wc/m²). Vous pouvez ensuite "
                      "l'ajuster : la taille, elle, ne change pas.",
                      "Passt sich an, wenn Sie die Modulgrösse ändern (≈ 221 Wp/m²). Danach frei anpassbar: Die "
                      "Grösse ändert sich dabei nicht.",
                      "Si aggiorna quando cambiate la dimensione del pannello (≈ 221 Wp/m²). Potete poi "
                      "modificarla: la dimensione non cambia.",
                      "Updates when you change the panel size (≈ 221 Wp/m²). You can then adjust it: the size "
                      "does not change."),
    "margin_help": ("Distance libre entre les panneaux et le bord du pan.",
                    "Freier Abstand zwischen Modulen und Dachrand.",
                    "Distanza libera tra i pannelli e il bordo della falda.",
                    "Free space between the panels and the edge of the face."),
    "address": ("Adresse", "Adresse", "Indirizzo", "Address"),
    "address_ph": ("Rue et numéro, NPA localité", "Strasse und Nummer, PLZ Ort", "Via e numero, NPA località",
                   "Street and number, postcode town"),
    "address_start": ("Entrez une adresse, ou zoomez sur la carte et cliquez sur un toit.", "Geben Sie eine Adresse ein oder zoomen Sie in die Karte und klicken Sie auf ein Dach.",
                      "Inserite un indirizzo, o ingrandite la mappa e cliccate su un tetto.", "Enter an address, or zoom into the map and click a roof."),
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
    "loss_help": ("Câbles, onduleur, salissures (poussière déposée sur les panneaux). 14 % est la valeur par défaut de PVGIS.",
                  "Kabel, Wechselrichter, Verschmutzung (Staub auf den Modulen). 14 % ist der Standardwert von PVGIS.",
                  "Cavi, inverter, sporcizia (polvere sui pannelli). 14 % è il valore predefinito di PVGIS.",
                  "Cables, inverter, soiling (dust on the panels). 14 % is the PVGIS default."),
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
    "map_note": ("Cliquez sur les pans à équiper (bleu), de n'importe quel bâtiment. Orange : obstacles. Violet : pans dessinés. Les toits se chargent autour de la vue quand vous zoomez.",
        'Klicken Sie die zu belegenden Flächen an (blau), von beliebigen Gebäuden. Orange: Hindernisse. Violett: gezeichnete Flächen. Die Dächer werden beim Zoomen rund um die Ansicht geladen.',
        'Cliccate le falde da equipaggiare (blu), di qualsiasi edificio. Arancione: ostacoli. Viola: falde disegnate. I tetti si caricano attorno alla vista quando ingrandite.',
        'Click the faces to equip (blue), from any building. Orange: obstacles. Purple: drawn faces. Roofs load around the view as you zoom in.',
    ),
    "tool": ("Outil de la carte", "Kartenwerkzeug", "Strumento della mappa", "Map tool"),
    "tool_pick": ("Choisir des toits", "Dächer wählen", "Scegli tetti", "Pick roofs"),
    "tool_add": ("Ajouter un obstacle", "Hindernis hinzufügen", "Aggiungi ostacolo", "Add obstacle"),
    "tool_del": ("Supprimer un obstacle", "Hindernis entfernen", "Rimuovi ostacolo", "Remove obstacle"),
    "tool_help": ("Pans : un clic ajoute ou retire un pan, de n'importe quel bâtiment. Obstacle : un clic sur un pan pose l'obstacle (fenêtre de toit, cheminée…), les panneaux l'évitent avec 10 cm de dégagement.",
        'Flächen: Ein Klick fügt eine Fläche hinzu oder entfernt sie, von beliebigen Gebäuden. Hindernis: Ein Klick auf eine Fläche setzt das Hindernis (Dachfenster, Kamin…), die Module halten 10 cm Abstand.',
        'Falde: un clic aggiunge o toglie una falda, di qualsiasi edificio. Ostacolo: un clic su una falda lo posiziona (lucernario, camino…), i pannelli lasciano 10 cm di distanza.',
        'Faces: a click adds or removes a face, from any building. Obstacle: a click on a face places it (roof window, chimney…); panels keep 10 cm clear.',
    ),
    "obst_type": ("Type d'obstacle", "Hindernistyp", "Tipo di ostacolo", "Obstacle type"),
    "obst_velux": ("Fenêtre de toit", "Dachfenster", "Lucernario", "Roof window"),
    "obst_chimney": ("Cheminée", "Kamin", "Camino", "Chimney"),
    "obst_custom": ("Autre", "Andere", "Altro", "Other"),
    "obst_w": ("Largeur (m)", "Breite (m)", "Larghezza (m)", "Width (m)"),
    "obst_l": ("Longueur dans la pente (m)", "Länge in Neigung (m)", "Lunghezza in pendenza (m)", "Slope length (m)"),
    "obst_clear": ("Effacer les obstacles ({n})", "Hindernisse löschen ({n})", "Cancella ostacoli ({n})",
                   "Clear obstacles ({n})"),
    "click_no_face": ("Cliquez à l'intérieur d'un pan de toit.", "Klicken Sie in eine Dachfläche.",
                      "Cliccate all'interno di una falda.", "Click inside a roof face."),
    "click_no_obstacle": ("Pas d'obstacle à cet endroit.", "Kein Hindernis an dieser Stelle.",
                          "Nessun ostacolo in questo punto.", "No obstacle here."),
    "legend_panels": ("Pans équipés", "Belegte Flächen", "Falde equipaggiate", "Equipped faces"),
    "legend_obstacle": ("Obstacle", "Hindernis", "Ostacolo", "Obstacle"),
    "shift_title": ("Positionner les panneaux", "Module positionieren", "Posizionare i pannelli",
                    "Position the panels"),
    "shift_note": (
        "Décale tout le champ de panneaux d'un pan, par pas de 25 cm, vu depuis l'extérieur du pan. Le champ "
        "s'aimante aux bords du pan, au centre et aux obstacles (rayon 12 cm) et reste dans les marges.",
        "Verschiebt das gesamte Modulfeld einer Fläche in 25-cm-Schritten, von aussen auf die Fläche gesehen. "
        "Das Feld rastet an Flächenrändern, Mitte und Hindernissen ein (12 cm) und bleibt innerhalb der Ränder.",
        "Sposta tutto il campo di pannelli di una falda a passi di 25 cm, visto dall'esterno. Il campo si "
        "aggancia ai bordi della falda, al centro e agli ostacoli (12 cm) e resta nei margini.",
        "Moves a face's whole panel block in 25 cm steps, seen from outside the face. The block snaps to the "
        "face edges, the centre and obstacles (12 cm) and stays within the margins.",
    ),
    "shift_left": ("Gauche", "Links", "Sinistra", "Left"),
    "shift_right": ("Droite", "Rechts", "Destra", "Right"),
    "shift_up": ("Vers le faîte", "Zum First", "Verso il colmo", "Towards ridge"),
    "shift_down": ("Vers la gouttière", "Zur Traufe", "Verso la gronda", "Towards eaves"),
    "shift_reset": ("Recentrer", "Zentrieren", "Centra", "Recentre"),
    "step_1": ('1 · Pans',
        '1 · Flächen',
        '1 · Falde',
        '1 · Faces',
    ),
    "step_2": ('2 · Panneaux',
        '2 · Module',
        '2 · Pannelli',
        '2 · Panels',
    ),
    "step_3": ('3 · Obstacles et position',
        '3 · Hindernisse und Position',
        '3 · Ostacoli e posizione',
        '3 · Obstacles and position',
    ),
    "step_4": ('4 · Production',
        '4 · Produktion',
        '4 · Produzione',
        '4 · Production',
    ),
    "step_5": ("5 · Production", "5 · Produktion", "5 · Produzione", "5 · Production"),
    "step1_note": ("Choisissez la maison : entrez une adresse, ou cliquez sur un bâtiment de la carte (outil « Choisir la maison »). Aucun panneau n'est posé à ce stade. Passez à l'étape 2 avec « Suivant ».",
        'Wählen Sie das Haus: Adresse eingeben oder ein Gebäude auf der Karte anklicken (Werkzeug «Haus wählen»). In diesem Schritt werden noch keine Module platziert. Weiter mit «Weiter».',
        'Scegliete la casa: inserite un indirizzo o cliccate su un edificio della mappa (strumento «Scegli la casa»). In questa fase non viene posato alcun pannello. Proseguite con «Avanti».',
        'Pick the house: enter an address or click a building on the map (tool “Pick the house”). No panels are placed yet. Move on with “Next”.',
    ),
    "step2_note": ("Entrez une adresse (des suggestions apparaissent pendant la frappe) ou naviguez sur la carte : les toits se chargent autour de la vue. Cliquez sur les pans à équiper, de n'importe quel bâtiment (un second clic retire le pan). Si le toit est mal détecté (toit en croix, par exemple), dessinez un pan avec l'outil « Dessiner un pan ». Les valeurs viennent du cadastre solaire : si la largeur, la longueur, l'inclinaison ou l'orientation d'un pan est fausse, modifiez-la dans le tableau, le nombre de panneaux s'adapte.",
        'Geben Sie eine Adresse ein (Vorschläge erscheinen beim Tippen) oder navigieren Sie auf der Karte: Die Dächer werden rund um die Ansicht geladen. Klicken Sie die zu belegenden Flächen an, von beliebigen Gebäuden (erneuter Klick entfernt sie). Wurde das Dach schlecht erkannt (z. B. Kreuzdach), zeichnen Sie eine Fläche mit «Fläche zeichnen». Die Werte stammen aus dem Solarkataster: Stimmen Breite, Länge, Neigung oder Ausrichtung nicht, ändern Sie sie in der Tabelle, die Modulzahl passt sich an.',
        'Inserite un indirizzo (compaiono suggerimenti durante la digitazione) o navigate sulla mappa: i tetti si caricano attorno alla vista. Cliccate le falde da equipaggiare, di qualsiasi edificio (un nuovo clic la toglie). Se il tetto è rilevato male (es. a croce), disegnate una falda con «Disegna falda». I valori vengono dal catasto solare: se larghezza, lunghezza, inclinazione o orientamento sono errati, modificateli nella tabella e il numero di pannelli si adatta.',
        "Enter an address (suggestions appear as you type) or browse the map: roofs load around the view. Click the faces to equip, from any building (a second click removes one). If the roof was badly detected (a cross roof, say), draw a face with “Draw a face”. Values come from the solar cadastre: if a face's width, length, tilt or orientation is wrong, edit it in the table and the panel count adapts.",
    ),
    "tool_draw": ("Dessiner un pan", "Fläche zeichnen", "Disegna falda", "Draw a face"),
    "draw_help": (
        "Dessiner : tracez un polygone ou un rectangle sur la carte, il devient un pan (inclinaison 30° et "
        "orientation sud par défaut, à régler dans le tableau de l'étape 2).",
        "Zeichnen: Ziehen Sie ein Polygon oder Rechteck auf der Karte, es wird zur Fläche (Standard 30° Neigung, "
        "Süd, anpassbar in der Tabelle von Schritt 2).",
        "Disegna: tracciate un poligono o un rettangolo sulla mappa, diventa una falda (30° e sud per "
        "impostazione predefinita, da regolare nella tabella del passo 2).",
        "Draw: trace a polygon or rectangle on the map; it becomes a face (30° tilt, facing south by default, "
        "adjustable in the step 2 table).",
    ),
    "drawn_face": ("Pan dessiné", "Gezeichnete Fläche", "Falda disegnata", "Drawn face"),
    "drawn_clear": ('Tout supprimer ({n})',
        'Alle löschen ({n})',
        'Elimina tutte ({n})',
        'Delete all ({n})',
    ),
    "col_height": ("Hauteur (m)", "Höhe (m)", "Altezza (m)", "Height (m)"),
    "col_height_help": (
        "Hauteur du bord bas du pan par rapport à une origine (par exemple le sol). Pas encore utilisée dans le "
        "calcul : prévue pour l'ombrage.",
        "Höhe der Unterkante der Fläche relativ zu einem Ursprung (z. B. Boden). Noch nicht in der Berechnung "
        "verwendet: für die Verschattung vorgesehen.",
        "Altezza del bordo basso della falda rispetto a un'origine (es. il suolo). Non ancora usata nel calcolo: "
        "prevista per l'ombreggiamento.",
        "Height of the face's lower edge relative to an origin (the ground, say). Not used in the calculation "
        "yet: planned for shading.",
    ),
    "fill_auto": ("Remplir automatiquement tous les pans cochés", "Alle gewählten Flächen automatisch belegen",
                  "Riempi automaticamente tutte le falde spuntate", "Fill all ticked faces automatically"),
    "n_wanted": ("Nombre de panneaux voulu", "Gewünschte Modulzahl", "Numero di pannelli desiderato",
                 "Wanted number of panels"),
    "n_wanted_help": (
        "Les panneaux sont posés d'abord sur les pans les mieux ensoleillés. Décochez le remplissage "
        "automatique pour fixer le nombre.",
        "Die Module werden zuerst auf den sonnigsten Flächen platziert. Automatisches Belegen abwählen, um die "
        "Zahl festzulegen.",
        "I pannelli vanno prima sulle falde più soleggiate. Togliete il riempimento automatico per fissare il "
        "numero.",
        "Panels go first on the sunniest faces. Untick automatic filling to set the number.",
    ),
    "n_capacity": ("Place disponible : {n} panneaux.", "Verfügbarer Platz: {n} Module.",
                   "Spazio disponibile: {n} pannelli.", "Room for {n} panels."),
    "switch_title": ("Changer de toit ?", "Dach wechseln?", "Cambiare tetto?", "Switch roof?"),
    "switch_text": (
        "Vous avez déjà un toit choisi. Ajouter ce bâtiment à la sélection, ou le remplacer ? Remplacer efface les "
        "obstacles, les pans dessinés et les positions de panneaux du toit actuel.",
        "Sie haben bereits ein Dach gewählt. Dieses Gebäude zur Auswahl hinzufügen oder ersetzen? Ersetzen löscht "
        "Hindernisse, gezeichnete Flächen und Modulpositionen des aktuellen Dachs.",
        "Avete già scelto un tetto. Aggiungere questo edificio alla selezione o sostituirlo? Sostituire cancella "
        "ostacoli, falde disegnate e posizioni dei pannelli del tetto attuale.",
        "You already picked a roof. Add this building to the selection, or replace it? Replacing erases the "
        "current roof's obstacles, drawn faces and panel positions.",
    ),
    "switch_add": ("Ajouter", "Hinzufügen", "Aggiungi", "Add"),
    "switch_replace": ("Remplacer", "Ersetzen", "Sostituisci", "Replace"),
    "switch_cancel": ("Annuler", "Abbrechen", "Annulla", "Cancel"),
    "tool_house": ("Choisir la maison", "Haus wählen", "Scegli la casa", "Pick the house"),
    "tool_faces": ('Choisir des pans',
        'Flächen wählen',
        'Scegli le falde',
        'Pick faces',
    ),
    "next": ("Suivant", "Weiter", "Avanti", "Next"),
    "best_faces": ("Pré-sélectionner les meilleurs pans", "Beste Flächen vorwählen",
                   "Preseleziona le falde migliori", "Pre-select the best faces"),
    "faces_picked": ("Pans choisis : {n}.", "Gewählte Flächen: {n}.", "Falde scelte: {n}.", "Faces picked: {n}."),
    "show_first": ("Choisissez les pans (étape 2) puis cliquez sur « Suivant » pour poser les panneaux.",
                   "Wählen Sie die Flächen (Schritt 2) und klicken Sie auf «Weiter», um die Module zu platzieren.",
                   "Scegliete le falde (passo 2) e cliccate su «Avanti» per posare i pannelli.",
                   "Pick the faces (step 2), then click “Next” to place the panels."),
    "draw_steps": ("Pour dessiner un pan : 1) cliquez sur l'icône polygone ou rectangle en haut à gauche de la carte, sous « Satellite / Plan » ; 2) cliquez les coins du pan sur le toit (un polygone se ferme en cliquant sur son premier point, Échap annule). Zoomez sur le toit avant de tracer. Un pan tracé par-dessus des pans du cadastre déjà choisis les remplace et reprend leur inclinaison, leur orientation et leurs hauteurs ; vous réglez ensuite la hauteur de chaque coin (numérotés sur la carte).",
        'Fläche zeichnen: 1) Polygon- oder Rechteck-Symbol oben links auf der Karte anklicken (unter «Satellit / Karte»); 2) Ecken der Fläche auf dem Dach anklicken (ein Polygon schliesst sich mit Klick auf den ersten Punkt, Esc bricht ab). Zoomen Sie vor dem Zeichnen auf das Dach. Eine über bereits gewählte Katasterflächen gezeichnete Fläche ersetzt diese und übernimmt Neigung, Ausrichtung und Höhen; danach stellen Sie die Höhe jeder Ecke ein (auf der Karte nummeriert).',
        "Per disegnare una falda: 1) cliccate sull'icona poligono o rettangolo in alto a sinistra della mappa, sotto «Satellite / Mappa»; 2) cliccate gli angoli della falda sul tetto (un poligono si chiude cliccando sul primo punto, Esc annulla). Ingrandite il tetto prima di tracciare. Una falda tracciata sopra falde del catasto già scelte le sostituisce e ne riprende inclinazione, orientamento e altezze; poi regolate l'altezza di ogni angolo (numerati sulla mappa).",
        "To draw a face: 1) click the polygon or rectangle icon at the top left of the map, under “Satellite / Map”; 2) click the face's corners on the roof (a polygon closes by clicking its first point, Esc cancels). Zoom in on the roof before tracing. A face drawn over cadastre faces you already picked replaces them and takes over their tilt, orientation and heights; then set each corner's height (numbered on the map).",
    ),
    "drawn_none": ("Aucun pan dessiné pour l'instant.",
        'Noch keine gezeichnete Fläche.',
        'Nessuna falda disegnata per ora.',
        'No drawn face yet.',
    ),
    "corner_heights": ("Hauteur de chaque point (m, numéros sur la carte) par rapport à une origine commune (le sol, par exemple). À la création, elles reproduisent l'inclinaison et l'orientation du pan remplacé, recalées sur les toits voisins (un bas de toit qui s'arrête plus haut qu'un toit voisin n'est pas à 0 m). Un coin posé ou lâché à moins de 60 cm d'un coin d'un autre pan fusionne avec lui : un seul point, une seule hauteur. Glissez un point sur la carte pour le déplacer. Modifiez une hauteur et l'inclinaison et l'orientation des pans concernés sont recalculées.",
        'Höhe jedes Punkts (m, Nummern auf der Karte) relativ zu einem gemeinsamen Ursprung (z. B. Boden). Bei der Erstellung entsprechen sie Neigung und Ausrichtung der ersetzten Fläche, an Nachbardächer angepasst (eine Traufe, die höher endet als ein Nachbardach, liegt nicht bei 0 m). Eine Ecke, die weniger als 60 cm von der Ecke einer anderen Fläche gesetzt oder losgelassen wird, verschmilzt mit ihr: ein Punkt, eine Höhe. Ziehen Sie einen Punkt auf der Karte, um ihn zu verschieben. Ändern Sie eine Höhe, werden Neigung und Ausrichtung der betroffenen Flächen neu berechnet.',
        "Altezza di ogni punto (m, numeri sulla mappa) rispetto a un'origine comune (es. il suolo). Alla creazione riproducono inclinazione e orientamento della falda sostituita, adattate ai tetti vicini (una gronda che finisce più in alto di un tetto vicino non è a 0 m). Un angolo posato o rilasciato a meno di 60 cm dall'angolo di un'altra falda si fonde con esso: un solo punto, una sola altezza. Trascinate un punto sulla mappa per spostarlo. Modificate un'altezza e inclinazione e orientamento delle falde interessate vengono ricalcolati.",
        "Height of each point (m, numbers on the map) relative to a shared origin (the ground, say). When created, they reproduce the replaced face's tilt and orientation, adjusted to neighbouring roofs (an eave that ends higher than a neighbouring roof is not at 0 m). A corner placed or dropped within 60 cm of another face's corner merges with it: one point, one height. Drag a point on the map to move it. Change a height and the tilt and orientation of the faces concerned are recomputed.",
    ),
    "corner": ('Coin',
        'Ecke',
        'Angolo',
        'Corner',
    ),
    "col_hb": ('Hauteur du bas (m)',
        'Höhe unten (m)',
        'Altezza basso (m)',
        'Bottom height (m)',
    ),
    "col_ht": ('Hauteur du haut (m)',
        'Höhe oben (m)',
        'Altezza alto (m)',
        'Top height (m)',
    ),
    "heights_help": ("Pans du cadastre : hauteurs du bas et du haut du pan par rapport à une origine (par exemple le sol). Par défaut : bas à 0, haut tel que dans le cadastre. Si vous changez le haut (ou le bas), l'inclinaison est recalculée à partir de la différence de hauteur et de la profondeur du pan. Pans dessinés : on règle la hauteur de chaque coin dans « Pans dessinés », au-dessus de la carte.",
        'Katasterflächen: Höhen von Unter- und Oberkante relativ zu einem Ursprung (z. B. Boden). Standard: unten 0, oben wie im Kataster. Ändern Sie oben (oder unten), wird die Neigung aus Höhenunterschied und Tiefe neu berechnet. Gezeichnete Flächen: Die Höhe jeder Ecke wird unter «Gezeichnete Flächen» über der Karte eingestellt.',
        "Falde del catasto: altezze del bordo basso e alto rispetto a un'origine (es. il suolo). Predefinito: basso a 0, alto come nel catasto. Se cambiate l'alto (o il basso), l'inclinazione è ricalcolata dalla differenza di altezza e dalla profondità. Falde disegnate: l'altezza di ogni angolo si regola in «Falde disegnate», sopra la mappa.",
        "Cadastre faces: heights of the lower and upper edge relative to an origin (the ground, say). Default: bottom 0, top as in the cadastre. If you change the top (or the bottom), the tilt is recomputed from the height difference and the face's depth. Drawn faces: set each corner's height under “Drawn faces”, above the map.",
    ),
    "tilt_from_heights": ('Inclinaison calculée depuis les hauteurs : {rows}.',
        'Aus Höhen berechnete Neigung: {rows}.',
        'Inclinazione calcolata dalle altezze: {rows}.',
        'Tilt computed from heights: {rows}.',
    ),
    "drawn_delete": ('Supprimer ce pan',
        'Diese Fläche löschen',
        'Elimina questa falda',
        'Delete this face',
    ),
    "house_picked": (
        "Maison choisie (contour jaune sur la carte) : {n} pans, {area} m² de toit au total.",
        "Gewähltes Haus (gelbe Umrandung auf der Karte): {n} Flächen, insgesamt {area} m² Dach.",
        "Casa scelta (contorno giallo sulla mappa): {n} falde, {area} m² di tetto in totale.",
        "House picked (yellow outline on the map): {n} faces, {area} m² of roof in total.",
    ),
    "clear_sel": ('Tout désélectionner',
        'Alle abwählen',
        'Deseleziona tutto',
        'Clear selection',
    ),
    "zoom_more": ('Zoomez pour charger les toits autour de la vue.',
        'Zoomen Sie, um die Dächer rund um die Ansicht zu laden.',
        'Ingrandite per caricare i tetti attorno alla vista.',
        'Zoom in to load the roofs around the view.',
    ),
    "loading_roofs": ('Chargement des toits alentour…',
        'Dächer in der Umgebung werden geladen…',
        'Caricamento dei tetti circostanti…',
        'Loading nearby roofs…',
    ),
    "drawn_title": ('Pans dessinés',
        'Gezeichnete Flächen',
        'Falde disegnate',
        'Drawn faces',
    ),
    "drawn_replaced": ('Pan dessiné : {n} pan(s) du cadastre remplacé(s), inclinaison {tilt}° et orientation repris du pan principal.',
        'Gezeichnete Fläche: {n} Katasterfläche(n) ersetzt, Neigung {tilt}° und Ausrichtung von der Hauptfläche übernommen.',
        'Falda disegnata: {n} falda/e del catasto sostituita/e, inclinazione {tilt}° e orientamento ripresi dalla falda principale.',
        'Drawn face: {n} cadastre face(s) replaced, tilt {tilt}° and orientation taken from the main face.',
    ),
    "drag_hint": ("glissez pour déplacer", "zum Verschieben ziehen", "trascinate per spostare", "drag to move"),
    "obstacle_moved_off": ("L'obstacle doit rester sur un pan de toit.", "Das Hindernis muss auf einer Dachfläche bleiben.",
                           "L'ostacolo deve restare su una falda.", "The obstacle must stay on a roof face."),
    "map_satellite": ("Satellite", "Satellit", "Satellite", "Satellite"),
    "map_plan": ("Plan", "Karte", "Mappa", "Map"),
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
