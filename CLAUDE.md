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
- Tout tourne en local (http://localhost:8501)

## Étapes (on avance dans l'ordre, une à la fois)
1. Production (fait, voir app.py, geo.py, pv.py) : l'utilisateur entre son
   adresse, le toit est détecté via le cadastre solaire suisse (sonnendach.ch,
   API geo.admin.ch). Deux modes : simple (on coche les pans à couvrir de
   panneaux) et détaillé (dimensions des pans, inclinaison, orientation,
   dimensions et puissance des panneaux, tout modifiable, pans ajoutables à la
   main). Deux analyses : de base (moyenne PVGIS 2005-2023) et poussée (année
   par année avec la météo horaire réelle d'Open-Meteo, jusqu'à l'année
   dernière, car PVGIS s'arrête en 2023). Graphiques : production annuelle,
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