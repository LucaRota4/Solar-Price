# Projet : calculateur de perte de valeur du solaire (Suisse)

## Objectif
Site web local qui montre à un particulier combien il perd en énergie et en
argent à cause de la mauvaise répartition de la production solaire (prix bas
ou négatifs aux heures de forte production), ce que les installateurs ne
montrent pas en général.

## Utilisateur
Développeur expérimenté. Pas besoin d'explications de base : va droit au but,
code concis, et ne commente que ce qui n'est pas évident (surtout les choix
métier). Réponds en français.

## Stack
- Python + Streamlit (une seule app, lancée avec `streamlit run app.py`)
- requests, pandas, plotly
- Tout tourne en local sur http://localhost:8502 (le port 8501 sert à un autre projet) :
  `.venv\Scripts\python.exe -m streamlit run app.py --server.port 8502`
- Après une modification de i18n.py, geo.py ou pv.py, redémarrer le serveur : Streamlit ne
  recharge pas toujours les modules importés.

## À chaque session (obligatoire)
1. Au début : lire ROADMAP.md pour savoir ce qui est fait et ce qui reste. Ce fichier est local et ignoré par git :
   ne jamais le commiter ni le publier, et ne pas le citer en détail dans le README ni les messages de commit.
2. Pendant : dès que Luca mentionne une idée « pour plus tard », l'ajouter à ROADMAP.md dans la
   bonne section, sans attendre la fin.
3. Quand une chose est terminée et testée : la déplacer dans « Fait » de ROADMAP.md, avec la date.
4. À la fin de chaque étape : commiter et pousser sur GitHub (le code a déjà été perdu une fois).

## Étapes (on avance dans l'ordre, une à la fois)
1. Production (fait, voir app.py, geo.py, pv.py) : l'utilisateur entre son
   adresse, le toit est détecté via le cadastre solaire suisse (sonnendach.ch,
   API geo.admin.ch). Parcours en 5 étapes (toit,
   pans, panneaux, obstacles et position, production) : un tableau de pans aux valeurs du cadastre modifiables,
   pans dessinables à la main, obstacles, plusieurs bâtiments. Analyse de base (moyenne PVGIS 2005-2023) ;
   l'analyse poussée (Open-Meteo) est en pause (voir ROADMAP). Graphiques : production annuelle,
   mensuelle, journée type été/hiver.
2. Prix : API Energy-Charts (zone bzn=CH, prix day-ahead en EUR/MWh, à convertir
   en CHF). Calculer le taux de capture, les kWh vendus à prix négatif, le
   manque à gagner.
3. Scénarios : rétribution trimestrielle actuelle, rétribution au quart d'heure
   (2027), écrêtage.
4. Batterie : nécessite un profil de consommation. Le gain principal est
   l'autoconsommation, pas l'arbitrage spot.

## Règles métier suisses (à vérifier avant d'afficher)
- Prix spot unique pour toute la Suisse, mais la rétribution réelle dépend du
  gestionnaire de réseau (champ à régler manuellement par l'utilisateur).
- 2026 : prix de marché de référence trimestriel, pondéré par la production PV,
  avec une rétribution minimale pour les petites installations.
- 2027 : prix au quart d'heure, décompte trimestriel.

## Règles de travail
- Pas de clé API en dur dans le code. Mets en cache les données téléchargées.
- Gère les erreurs (API indisponible) avec un message clair.
- Demande-moi avant d'ajouter une dépendance ou de supprimer un fichier.
- Les chiffres affichés à l'utilisateur doivent indiquer leurs hypothèses.