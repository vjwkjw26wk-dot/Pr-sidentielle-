# Registre des décisions — arbitrages A1 à A8

Décisions prises le 16 novembre 2026 dans le cadre fixé par le porteur du projet. Une décision peut être révisée si un test de validation l'invalide ; la révision est alors consignée ici.

## A1 — Cœur macroéconomique : trois couches compatibles

**Décision.** Le cœur combine trois approches, chacune dans le rôle où elle est la plus solide :

1. **Cadre comptable stock-flux complet** (comptes des secteurs institutionnels, base 2020) : toutes les identités, la dette et les patrimoines financiers. Il ne contient aucune hypothèse de comportement.
2. **Bloc productif multisectoriel entrées-sorties** : production, consommations intermédiaires, importations par produit, énergie.
3. **Équations de comportement semi-structurelles** à correction d'erreur (consommation, investissement, emploi, prix, salaires, commerce extérieur), estimées sur données françaises ouvertes.

**Compatibilité.** Les trois couches partagent une seule nomenclature (comptes nationaux annuels, branches A17 ou A38) et un seul millésime. Les équations de comportement déterminent des flux ; le cadre comptable en déduit les soldes et les stocks ; le bloc entrées-sorties répartit la demande par branche. Aucune grandeur n'est déterminée deux fois.

**Alternatives écartées comme cœur.** DSGE estimé : difficile à coupler à une microsimulation ménage par ménage et à valider sans équipe dédiée. Multi-agents : validation pour l'évaluation de politiques françaises non démontrée. Elles restent des modèles de comparaison possibles (A6).

**Pas de temps.** Annuel. Les données ouvertes détaillées (comptes de secteurs, tableaux entrées-sorties, distribution des revenus) sont annuelles.

**Mise en œuvre de la couche 1 (16 novembre 2026)** : `M3_cadre_comptable.md`. Les impôts nets sur produits sont portés par un pseudo-secteur S1N, comme dans les comptes d'Eurostat ; les écarts d'arrondi des données publiées sont isolés dans un compte « ECART » explicite plutôt que répartis sur les opérations.

## A2 — Couplage : itératif, annuel, avec contrôle des identités

Boucle descendante-ascendante à chaque année simulée, sur un vecteur de variables de liaison ; relaxation (amortissement) des itérations ; convergence exigée sur l'écart relatif maximal ; résultat refusé si une identité comptable est violée ou si la boucle ne converge pas. Les tolérances seront fixées par tests numériques au lot 8.

## A3 — Microsimulation : OpenFisca-France

OpenFisca-France est retenu comme moteur de la législation. **Vérification du 16 novembre 2026 :** version 177.0.0, licence AGPL-3.0 (compatible avec une publication ouverte du simulateur, à condition de publier le code modifié) ; législation 2026 présente (barème de la loi de finances pour 2026, revalorisations d'avril 2026) ; 11 cas types sur 11 conformes à l'euro près face à des valeurs recalculées indépendamment. Reste à vérifier : les masses agrégées face aux comptes publics, après le lot 4.

## A4 — Population synthétique : calage sur marges publiées, sans prétention individuelle

Méthode retenue : tirage d'individus et de ménages à partir de distributions publiées, puis ajustement proportionnel itératif (IPF) et calage sur marges. Les corrélations non publiées ne seront pas inventées : elles seront bornées par des hypothèses explicites (indépendance conditionnelle) et testées en sensibilité. Alternatives à comparer au lot 4 : copules estimées sur des tableaux croisés publiés.

**Révision du 16 novembre 2026.** Le fichier détail du recensement 2022 (Insee, licence ouverte, sans habilitation) fournit de vrais ménages anonymisés, avec la structure familiale, l'âge, l'activité et le groupe socioprofessionnel de chaque membre. Il remplace le tirage synthétique pour la structure des ménages : aucune corrélation entre composition familiale et activité n'est plus inventée. Le recensement ne contient pas les revenus. Ils sont imputés par rang : le score est tiré des caractéristiques individuelles (grilles Insee et DREES), le niveau est ancré sur la distribution fiscale de la DGFiP. Les corrélations non publiées restent ainsi limitées au classement des foyers à l'intérieur de la distribution, et elles sont testées par l'impôt (`M4_population.md`).

## A5 — Démographie : cohortes par sexe et âge simple — construit (voir `M1_demographie.md`)

Fécondité, mortalité, migrations en scénarios exogènes alignés sur l'Insee ; effets des politiques sur la démographie seulement là où ils sont estimables (âge de départ à la retraite et taux d'activité : lot 2 ; fécondité et migrations : scénarios).

**Révision du 16 novembre 2026.** La version 1 calait 4 paramètres sur le scénario central de l'Insee à partir de données Eurostat. Les fichiers détaillés des projections 2026 étant désormais téléchargeables, la version 2 applique directement la méthode et les hypothèses de l'Insee (quotients par âge atteint, fécondité, solde migratoire par sexe et âge, ajustement). Raisons : réplication exacte des 29 scénarios au lieu d'écarts de 2 à 4 % en 2070, et effet des migrations correct (la v1 le sous-estimait de 16 %). Les variantes hors Insee passent par un générateur construit sur les directions de variation de l'Insee.

## A6 — Bibliothèque multi-modèles

Une configuration de référence (A1) ; modèles de comparaison introduits un par fonction économique, après validation de la référence. Premier modèle de comparaison prévu : fermeture purement keynésienne à prix fixes du même cadre comptable, pour isoler ce que les équations de prix et de salaires apportent.

## A7 — Données ouvertes uniquement

Aucune source sous habilitation. Chaque source est inscrite dans `02_registre_des_donnees.md` avec licence, mode d'accès et contrôle d'intégrité. Conséquence acceptée : pas de microdonnées fiscales ni d'entreprises ; les revenus des ménages sont reconstruits à partir de distributions publiées (A4), et le bloc productif reste sectoriel. Seule microdonnée ménages utilisée : le fichier détail du recensement, en accès libre (sans revenus).

## A8 — Conservation du travail

**Décision (16 novembre 2026).** L'espace de calcul n'est pas conservé d'une session à l'autre et aucun dépôt Git n'est relié au projet. Le code est versé dans le projet (`modele/code/`) ; les données brutes ne sont pas conservées mais retéléchargées par script, avec contrôle d'empreinte (`modele/resultats/registre_telechargements.json`). À réviser si un dépôt Git est relié : il deviendrait alors la référence pour le code.
