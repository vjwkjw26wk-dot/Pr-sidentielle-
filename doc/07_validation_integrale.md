# Phase 7 — Rapport de validation intégrale (version 0.2, 17 novembre 2026)

Ce rapport rassemble les tests de tous les modules et répond au critère d'acceptation du cahier des charges : des écarts
quantifiés et expliqués. Il distingue ce qui est validé, ce qui est plausible sans être vérifiable, et ce qui ne l'est
pas. Chaque ligne renvoie à un rapport détaillé du dossier `resultats/`.

## 1. Tests rétrospectifs et de reproduction

| Module | Test | Résultat | Statut |
|---|---|---|---|
| M1 Démographie | Reproduction des 29 scénarios Insee 2026 | écart de population ≤ 3,4·10⁻⁵ | **validé** |
| M3 Cadre comptable | Identités des comptes 2019-2025 ; agrégats Insee | exactes ; déficit et dette conformes | **validé** |
| M4 Impôt sur le revenu | Barème par décile (DGFiP), total | +2 % au total ; déciles 1-8 conformes, 9-10 à +7 % | **validé** (niveau) |
| M4/M10 Sensibilité de l'impôt | Barème −2 % contre chiffrages officiels et calcul direct | −15 % contre calcul direct ; −30 % contre chiffrages officiels (champ différent) | **acceptable**, marge documentée |
| M4 Prestations | RSA, allocations familiales, aides au logement ; recours | recours apparents cohérents avec la DREES | **validé** ; prime d'activité : éligibles −25 % |
| M5 Entrées-sorties | Identités 2010-2022 ; prix 2012-2022 | erreur de 0,3 à 0,8 point en année ordinaire ; 2020 et 2022 dégradés | **validé** hors grands chocs |
| Lot 7 Équations | Simulations hors échantillon 2013-2019 et 2022-2024 | meilleures que la tendance pour consommation, salaires, échanges ; investissement agrégé médiocre | **partiellement validé** |
| M8 Modèle bouclé | Rétrosimulation 2015-2019 (estimé jusqu'en 2014) | PIB +0,1 %, emploi 0,0 %, prix +0,5 %, solde +0,2 pt, dette +0,4 pt | **validé** en régime ordinaire |
| M8 Modèle bouclé | Rétrosimulation 2023-2024 | PIB −3,5 %, prix −2,9 %, exportations −10 %, revenu −7,7 % | **non validé** pour le choc énergétique |
| M9 Activité des seniors | Hors échantillon 2020-2025 (relèvement de l'âge légal) | 0 à 3 points d'écart par tranche d'âge | **validé** |
| M9 Pensions | Masse 2008-2022, calage sur 2015 seulement | ±2,3 % ; 2024 : +4,4 % (données provisoires) | **validé** |
| M11 Règle de la BCE | Simulation dynamique 2000-2025 | 0,5-1 point de 2000 à 2012 ; taux négatifs non reproduits | **partiellement validé** |

## 2. Comparaison des multiplicateurs aux références

| Choc (1 point de PIB) | Ce modèle : 1re année | 3e année | Références |
|---|---|---|---|
| Consommation ou emploi publics (v0.2 : équation de consommation corrigée, référence recalée) | +1,21 % | +0,76 % (5e année : +0,59 %) | Insee-DG Trésor : environ 0,9 la première année pour une baisse de dépense ; OFCE (e-mod.fr) : 0,6 à 1,2 selon la composition |
| — version 0.1 (pour mémoire) | +1,40 % | +0,77 % | |
| Transferts aux ménages | +0,54 % | ≈ +0,2 % | ordre de grandeur des modèles keynésiens : 0,5 à 1 |
| Impôt sur le revenu (+13,6 Md€, 0,5 pt de PIB) | −0,23 % de PIB (multiplicateur ≈ 0,5) | −0,18 % | 0,5 à 0,8 pour les prélèvements sur les ménages |

**Lecture.**
- **Version 0.2** : la variation contemporaine du chômage est retirée de l'équation de consommation (biais de simultanéité ; sa version retardée n'est pas significative). Le multiplicateur de première année passe de 1,40 à 1,21, dans le haut de la fourchette publiée.
- **Version 0.1** : le multiplicateur de la dépense publique la première année était un peu au-dessus de la fourchette publiée, qui va de 0,8 (variante TVA) à 1,2 (variantes investissement et emploi publics) pour l'OFCE en milieu de cycle. La consommation publique a un faible contenu en importations dans le tableau entrées-sorties, et le modèle n'a ni anticipations ni réaction budgétaire.
- **Profil dans le temps** : il est proche de celui des modèles macroéconométriques français après le recalibrage de la fermeture d'offre (décision A12).
- **Prélèvements sur les ménages** : leur multiplicateur est dans la fourchette.
- **Sources des références** : OFCE, « Petit précis de politique budgétaire par tous les temps », Revue de l'OFCE, 2011 ; Conseil des prélèvements obligatoires, rapport sur la TVA, 2015 (variantes e-mod.fr) ; modèle Mésange, Insee et DG Trésor, 2017.

## 3. Incertitude (Monte-Carlo, 40 tirages ; `resultats/validation_M12.md`)

Les paramètres estimés sont tirés dans leur loi estimée. Les paramètres calibrés sont tirés dans leur plage :
- élasticité de l'emploi au coût du travail : 0,2 à 0,6 ;
- effet du chômage sur les salaires : −0,8 % à −0,2 % ;
- fermeture d'offre ρ : 0,1 à 0,25.

| Variante | PIB en 2026 [intervalle à 90 %] | Solde public en 2026 (pt de PIB) | PIB en 2030 |
|---|---|---|---|
| Consommation publique +1 pt de PIB | +0,77 % [+0,53 ; +0,84] | −0,32 [−0,40 ; −0,23] | +0,39 % [−0,01 ; +0,62] |
| IS de 25,8 % à 20 % | +0,14 % [+0,04 ; +0,24] | −0,40 [−0,44 ; −0,35] | +0,21 % [+0,06 ; +0,30] |
| Énergie importée +20 % | −0,20 % [−0,35 ; +0,16] | −0,33 [−0,40 ; −0,11] | −0,03 % [−0,29 ; +0,52] |
| IR : première tranche de 11 % à 14 % | −0,18 % [−0,21 ; −0,09] | +0,29 [+0,27 ; +0,37] | −0,09 % [−0,15 ; +0,03] |
| Âge légal 65 ans | +0,05 % [+0,03 ; +0,10] | +0,01 [−0,01 ; +0,03] | +0,15 % [+0,10 ; +0,24] |

**Lecture.**
- **Effets budgétaires** (solde public à 2-3 ans) : ils sont les plus robustes. L'intervalle vaut environ ±0,1 point de PIB pour des mesures de 0,5 à 1 point.
- **Effets sur l'activité à moyen terme** : ils sont très incertains. Le signe peut même s'inverser pour le choc énergétique en 2030.
- **Couverture** : ces intervalles ne couvrent que l'incertitude des paramètres. Ils n'incluent ni la spécification des équations, ni les données, ni l'environnement international. Ce sont donc des minorants de l'incertitude réelle.

## 4. Ce qui est robuste, plausible ou non validé

- **Robuste** (niveaux A-B, tests passés) :
  - démographie ;
  - identités comptables ;
  - niveau de l'impôt sur le revenu et des grandes prestations ;
  - effets budgétaires directs des mesures paramétriques ;
  - activité des seniors et pensions ;
  - propagation des chocs entre branches et importations ;
  - dynamique de court terme en régime ordinaire.
- **Plausible, dépendant d'hypothèses** (niveaux C-D) :
  - effets de moyen terme sur le PIB (fermeture d'offre) ;
  - effet du coût du travail sur l'emploi et du chômage sur les salaires (calibrés) ;
  - effet de l'impôt sur les sociétés sur l'investissement (une seule élasticité, fragile) ;
  - rétroactions européennes et prime de risque ;
  - réindustrialisation (objectif exogène).
- **Non validé** :
  - grands chocs de prix (2022-2024) ;
  - exportations en période de reprise sectorielle (aéronautique) ;
  - revenus du patrimoine ;
  - réactions comportementales aux réformes socio-fiscales (non modélisées) ;
  - flux physiques d'énergie et de matières (non modélisés) ;
  - long terme au-delà de 10 ans (volumes non chaînés).

## 5. Conformité aux critères du cahier des charges

| Critère | État |
|---|---|
| Fondement scientifique (paramètres sourcés ou hypothèses explicites) | oui : registre des décisions A1-A14, niveaux de preuve par équation et par mesure |
| Données ouvertes, reproductibilité | oui : téléchargement scripté, empreintes, tests rejouables, dépôt Git |
| Cohérence comptable | oui : identités vérifiées (M3, M5, M8) |
| Validation rétrospective sur plusieurs années | oui pour 2015-2019 ; échec documenté pour 2023-2024 |
| Incertitudes | partiel : paramètres seulement |
| Comparaison à des modèles de référence | partielle : multiplicateurs comparés aux publications, pas d'exécution croisée |
| Neutralité | oui : mêmes méthodes pour toutes les mesures ; pas de note globale ; exemples de scénarios symétriques |
| Distinction entre résultats robustes et dépendants d'hypothèses | oui : section 4 et fiche de transparence de chaque simulation |

## 5 bis. Validations ajoutées en version 0.2 (simulateur 0.4)

1. **Recalage 2023-2025** (`M8_reference.md`). La trajectoire de référence reproduit les comptes observés :
   - croissance 1,6 / 1,5 / 0,8 % ;
   - solde public −5,4 / −5,8 / −5,1 % du PIB ;
   - dette 109,5 / 112,6 / 115,7 % du PIB.

   Il s'agit d'un calage par termes correctifs. Ce n'est donc pas une validation des équations : celle-ci reste celle
   du § 1 (2023-2024 non validé pour les prix et les exportations).
2. **Approximation additive de l'interface** (`resultats/validation_additivite.md`, 4 scénarios combinés).
   - Pour les scénarios A, B et D, l'écart entre la somme des mesures et le calcul complet est inférieur à 0,1 point
     pour tous les indicateurs en 2032.
   - Le scénario C combine la relocalisation industrielle, les droits de douane et le prix de l'énergie. L'écart y
     atteint 1,1 point de PIB et 4,6 points de dette, car la relocalisation impose les parts importées et neutralise la
     substitution par les prix. L'interface affiche un avertissement pour cette combinaison.
3. **Marges d'incertitude des écarts** (`outputs/incertitude_variantes.json`).
   - Méthode : Monte-Carlo, 20 tirages, sur 7 mesures représentatives.
   - Demi-largeur médiane de l'intervalle à 90 %, rapportée à l'écart central en 2032 : PIB 49 %, emploi 48 %,
     prix 52 %, solde public 43 %.
   - L'interface applique ces rapports à toutes les mesures. Les effets budgétaires directs (avant bouclage) ne sont
     pas concernés.
4. **Trajectoires de comparaison.** Elles servent à tester la sensibilité au taux de l'OAT (±1 point à partir de 2027)
   et à un redressement d'ampleur FMI.
   - Le redressement apporte un effort ex ante d'environ 4,3 points de PIB en 2031.
   - Selon le modèle, le solde ne s'améliore que de 2,3 points et la dette de 1 point seulement, car le PIB recule de
     2,8 %.
   - Ce résultat dépend fortement du multiplicateur et de l'absence de réaction de la politique monétaire dans cette
     variante.

## 6. Travaux de validation restants

1. Incertitude de spécification : variantes d'équations, comparaison de fermetures.
2. Exécution croisée de variantes publiées (fiches de variantes Mésange, OFCE), avec l'écart expliqué.
3. Rétrosimulation longue (2000-2019) avec une base entrées-sorties ancienne.
4. Validation distributive : niveau de vie par décile comparé à l'enquête Revenus fiscaux et sociaux de l'Insee.
5. Relecture scientifique externe (`10_dossier_relecture.md`).
6. Incertitude propre à chaque mesure, au lieu d'un rapport médian commun.
