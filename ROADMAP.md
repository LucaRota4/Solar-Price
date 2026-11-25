# Idées et suite du projet

Récapitulatif des idées discutées, pas encore faites. À relire avant chaque nouvelle étape.
Les règles métier marquées « à vérifier » doivent être confirmées avant d'être affichées.

## Fait

Étape 1, terminée le 2026-11-25 :

- Adresse ou clic sur n'importe quel toit de la carte, toits chargés dans un rayon de 50 m (cadastre solaire)
- Carte de la Suisse par défaut, vue satellite ou plan, boussole
- Mode simple (pans cochés, remplis de panneaux) et détaillé (dimensions, inclinaison, orientation, pans ajoutés à la main)
- Panneaux dessinés dans le contour réel des pans ; la puissance suit la taille du panneau
- Analyse de base (PVGIS 2005-2023) et poussée (année par année, Open-Meteo, jusqu'à l'année dernière)
- Mode sombre, barre de navigation en haut, français, allemand, italien, anglais

Retouches du 2026-11-25 (testées en headless, pas encore vues dans le navigateur) :

- Page en 5 étapes (onglets) : toit, pans, panneaux, obstacles et position, production ; hypothèses sous la carte
- Parcours en 4 étapes (onglets) : pans, panneaux, obstacles et position, production ; chaque étape a son « Suivant »
  qui ouvre l'onglet suivant, et les panneaux ne sont posés qu'après le « Suivant » de l'étape 1
- Un clic sur un pan le choisit (second clic : le retire), de n'importe quel bâtiment, sans étape « choisir la
  maison » ni fenêtre de confirmation ; boutons « Pré-sélectionner les meilleurs pans » et « Tout désélectionner »
- Recherche d'adresse avec suggestions pendant la frappe (petit composant sans dépendance, search_box.py)
- Les toits se chargent autour de la vue en naviguant sur la carte (cases de 100 m, dès le zoom 17)
- Un seul tableau de pans (valeurs du cadastre modifiables : largeur, longueur, inclinaison, orientation, hauteur) ;
  les modes simple/détaillé sont supprimés
- Obstacles (fenêtre de toit, cheminée, autre) posés au clic, les panneaux les évitent (10 cm de dégagement)
- Décalage du champ de panneaux d'un pan par pas de 25 cm, avec aimantation (bords, centre, obstacles)
- Pans dessinés à la main (toits en croix mal détectés), nombre de panneaux voulu ou remplissage automatique
- Carte stable : les couches qui bougent n'obligent plus à recharger la carte, la vue ne saute plus ; zoom
  jusqu'à 23 (au-delà de 20, l'image est agrandie)
- Pans dessinés : un pan tracé par-dessus des pans du cadastre déjà choisis les remplace et reprend l'inclinaison,
  l'orientation et les hauteurs du pan le plus recouvert (supprimer le pan dessiné les restaure) ; coins numérotés
  sur la carte, hauteur de chaque coin modifiable dans « Pans dessinés » au-dessus de la carte, l'inclinaison et
  l'orientation en sont déduites (plan passant par les coins)
- Pans du cadastre : hauteur du bas et du haut dans le tableau, modifier le haut recalcule l'inclinaison
- Légende de l'aptitude du toit en bas à gauche de la carte

## À reprendre plus tard (retiré de la page pour l'instant)

- **Analyse poussée** (année par année, Open-Meteo) : retirée de la page, le code est dans pv.py
  (`hourly_by_year`) et dans l'historique git (commit 011b4a3, views/estimate.py).
- **Glisser-déposer réel** d'un panneau ou d'un groupe sur la carte : demande un composant JS personnalisé
  (streamlit-folium ne renvoie pas les déplacements) ; aujourd'hui : flèches avec aimantation.
- **Hauteurs des pans** : elles servent à calculer l'inclinaison ; leur usage pour l'ombrage (obstacles, pans voisins
  plus hauts) reste à faire.
- Pans dessinés : accrochage des coins sur les coins des pans voisins (toits en croix), sans retracer.
- **Découpage final des sections** : le parcours complet d'abord, puis on organise ce que voit l'utilisateur
  (ne pas le charger de tout dès le début).
- Pas de panneaux individuels sélectionnables ni de tailles de panneaux différentes sur un même pan.
- Vérifier au navigateur : le bug de la cellule en surimpression du tableau (cellules en lecture seule) devrait
  avoir disparu, car le tableau n'a plus de colonne en lecture seule.

## Production et installation

1. **Édition des panneaux à la main sur la carte** : sélectionner, supprimer, ajouter, déplacer,
   redimensionner un panneau ou tous. Piste : plugin Draw de folium (mode édition), puis relire la
   disposition modifiée et recalculer la puissance. La disposition « à la main » remplace l'automatique.
2. **Obstacles et ombrage** : ajouter des arbres ou bâtiments (position, distance, hauteur, largeur)
   et montrer la perte (« cet arbre coûte X % de production »).
   - Calcul heure par heure : position du soleil, la lumière directe est bloquée quand le soleil est
     derrière l'obstacle, la diffuse est gardée.
   - Raccourci : convertir les obstacles en horizon personnalisé pour PVGIS (paramètre `userhorizon`).
   - Arbre sans feuilles en hiver : coefficient de transparence.
   - Plus tard : obstacles détectés automatiquement avec le modèle 3D swissSURFACE3D (swisstopo).
   - Limite : l'ombre partielle d'une partie des panneaux dépend du câblage, non modélisée au début.
3. **Projection sur 15 à 25 ans** : production année après année et cumulée, avec perte annuelle
   des panneaux réglable (environ 0,5 %/an, un peu plus la première année, à vérifier).
4. **Onduleurs** :
   - Choix « une seule entrée MPPT / une entrée par orientation / micro-onduleurs », avec une perte de
     désaccord quand des pans d'orientations différentes partagent une entrée.
   - Taille de l'onduleur (ratio DC/AC) : écrêtage calculé avec les données horaires.
   - Durée de vie 10-15 ans : un remplacement sur 25 ans, à compter dans l'économie.
5. (fait) Chargement des toits en se baladant.

## Valeur de la production (étapes 2 à 4 du CLAUDE.md)

6. Prix du marché heure par heure (Energy-Charts, zone CH), taux de capture, kWh vendus à prix bas
   ou négatif, manque à gagner.
7. Scénarios de rétribution : trimestrielle actuelle, au quart d'heure dès 2027, écrêtage.
8. Batterie : profil de consommation, gain surtout par l'autoconsommation.

## Circuit court : vendre aux voisins et aux entreprises

9. Idée venue d'un ami qui envisage des panneaux sur le toit de son immeuble et de vendre une partie
   de l'électricité aux voisins et à une entreprise, un peu moins cher que le tarif du réseau.
   - Choisir les acheteurs sur la carte : immeubles voisins, entreprises.
   - Pour chacun : quantité (part de la production ou profil de consommation), prix (fixe, indexé
     sur le marché, ou remise sur le tarif du gestionnaire de réseau).
   - Résultat : revenu par acheteur, part autoconsommée localement, gain pour le producteur et
     économie pour les acheteurs, comparés à l'injection simple.
   - Cadres suisses à vérifier : regroupement pour la consommation propre (RCP / ZEV), RCP virtuel,
     communautés électriques locales (CEL / LEG) prévues dès 2026 avec réduction du timbre de réseau,
     conditions (même commune, même niveau de réseau, etc.).

## Diffusion

10. Héberger l'app (Streamlit Community Cloud, dépôt privé), puis créer une vitrine publique
    `Solar-Price-Showcase` avec description et lien, comme pour d_neutral et Immeuble-Site.
