# Lot 7 et M8 — Équations de comportement estimées et modèle bouclé (version 0.1)

**État : première version complète et testée de bout en bout. C'est un prototype à consolider : plusieurs paramètres
clés ne sont pas identifiés sur les données et sont calibrés ; les grands chocs de prix sont mal reproduits.**
Code : `src/m7_series.py`, `src/m7_equations.py`, `src/m8_modele.py`. Tests : `tests/validation_M7.py`,
`tests/validation_M8.py`. Rapports : `resultats/validation_M7.md`, `resultats/validation_M8.md`.

## 1. Données (toutes ouvertes, téléchargées par script)

| Série | Source | Période |
|---|---|---|
| Valeur ajoutée, production, rémunérations par branche (valeur, volume, prix de l'année précédente) | Eurostat `nama_10_a64` (comptes nationaux de l'Insee) | 1995-2025 |
| Emploi et heures par branche (total, salariés) | Eurostat `nama_10_a64_e` | 1995-2025 |
| FBCF par branche ; stock de capital net en volume | Eurostat `nama_10_a64_p5`, `nama_10_nfa_st` | 1995-2025 |
| PIB et emplois (France, Union européenne, zone euro), consommation des ménages | Eurostat `nama_10_gdp`, `nama_10_fcs` | 1980-2025 |
| Comptes des ménages, des sociétés non financières, des administrations publiques ; dette | Eurostat `nasa_10_nf_tr`, `gov_10a_main`, `gov_10dd_edpt1` | 1995-2025 |
| Taux de chômage au sens du BIT (France métropolitaine, trimestriel) | Insee, BDM, série 001688526 | 1975-2026 |
| Taux d'intérêt à 10 ans | Eurostat `irt_lt_mcby_a` | 1980-2025 |
| Taux normal de l'impôt sur les sociétés, contributions comprises | Législation (code général des impôts, art. 219), saisi dans `m7_series.taux_is` | 1995-2025 |

Branches : 25 branches marchandes (A38 regroupé). Immobilier (loyers imputés) et branches non marchandes exclus de
l'estimation ; dans le modèle bouclé, leur production suit la demande et leur emploi suit leur production.

## 2. Équations estimées (1997-2019, hors années Covid)

Méthode : modèles à correction d'erreur en une étape (relation de long terme et dynamique de court terme estimées
ensemble). Équations de branche : panel de 25 branches, effets fixes, moindres carrés pondérés par la taille de la
branche, écarts types groupés par année. Équations agrégées : moindres carrés ordinaires, écarts types robustes à
l'autocorrélation (Newey-West).

| Équation | Résultat principal | Statut |
|---|---|---|
| Emploi par branche (personnes) | Élasticité de court terme à la production 0,26 (t = 6) ; retour vers la cible au rythme de 21 % par an ; long terme proportionnel à la production, corrigé d'une tendance de productivité propre à chaque branche | **estimé** ; rendements constants imposés (la version libre donne 0,44, biaisée par la colinéarité avec les tendances) |
| — effet du coût réel du travail | Élasticité de long terme −0,4 | **calibré** : non identifié (la version libre donne −0,21, non robuste) ; valeur au milieu des estimations françaises de l'élasticité de substitution capital-travail |
| Prix de la valeur ajoutée par branche | Transmission immédiate du coût salarial unitaire 0,68 (t = 6) ; homogénéité de long terme imposée (la version libre donne 0,75) ; retour de la marge vers sa norme de 12 % par an | **estimé** |
| Investissement par branche | Accélérateur : élasticité de court terme à la production 0,67 (t = 3,3), effet retardé 0,26 | **estimé** |
| Investissement des sociétés non financières (agrégat) | Élasticité de long terme au coût d'usage du capital −0,18 (t = −3) ; effet du taux de marge positif mais non significatif | **estimé, fragile** (23 observations ; prévision hors échantillon médiocre) |
| Salaire moyen par tête (secteur marchand) | Indexation de court terme sur les prix à la consommation 0,39 ; retour de la part des salaires vers sa norme de 9 % par an | **estimé** |
| — effet du chômage | −0,4 % de croissance salariale par point d'écart du chômage à sa tendance | **calibré** : l'estimation libre donne un effet positif, biaisé par la composition de l'emploi (les emplois à bas salaire disparaissent d'abord quand le chômage monte) |
| Consommation des ménages | Élasticité de court terme au revenu réel 0,78 (t = 4) ; effet du chômage −0,5 % par point ; retour vers le revenu de 31 % par an | **estimé** |
| Importations | Élasticité à la demande pondérée 1,47 à court terme, 1,37 à long terme ; tendance de pénétration +0,6 % par an ; élasticité-prix −0,16 | **estimé** (élasticité-prix faible et peu significative) |
| Exportations | Élasticité à la demande mondiale 0,71 ; élasticité-prix −0,60 (t = −2) ; pas de relation de long terme identifiée, forme en différences | **estimé** |

## 3. Tests rétrospectifs, équation par équation (`resultats/validation_M7.md`)

Simulation dynamique hors échantillon : estimation 1997-2012 puis simulation 2013-2019 ; estimation 1997-2019 puis
simulation 2022-2024. Les équations battent une prévision naïve (tendance prolongée) pour la consommation, les
salaires, les importations et les exportations, et pour l'emploi en 2022-2024. Elles font moins bien pour les prix de
la valeur ajoutée en 2013-2019 et pour l'investissement des sociétés non financières (erreur de niveau de +11 % en
2024).

## 4. Modèle bouclé M8 (version 0.1)

Enchaînement annuel, résolu par itérations : prix (marges, modèle de prix entrées-sorties à 64 produits, prix
d'importation par produit) → salaires → demande finale (consommation, investissement, exportations ; consommation
publique exogène) → importations (équation agrégée, structure par produit du tableau de base) → production par produit
(Leontief) → valeur ajoutée et emploi par branche → chômage → revenus des ménages → comptes publics et dette.

Choix de construction (décision A10) :
- **Constantes recalées** sur les résidus moyens des cinq dernières années observées plutôt qu'extrapolation des effets
  fixes de branche ; sans ce recalage, l'emploi simulé 2015-2019 dérivait de −7 % à +4 % selon la période d'estimation.
- **Tendance de productivité de chaque branche = paramètre de scénario** (par défaut, moyenne des 8 dernières années
  observées), comme dans les projections du Conseil d'orientation des retraites. C'est le paramètre de long terme le plus
  incertain du modèle.
- Volumes aux prix de l'année de base (pas de chaînage).
- **Finances publiques** : taux apparents de l'année de base appliqués aux assiettes (TVA et impôts sur les produits sur
  la consommation, cotisations sur la masse salariale, impôt sur le revenu sur les revenus des ménages, impôt sur les
  sociétés sur l'excédent des branches marchandes × taux normal). Le taux apparent de la dette rejoint le taux de marché
  à raison d'un huitième par an. Pas d'ajustements stock-flux. La microsimulation M4 n'est pas encore branchée : une
  réforme fiscale détaillée passe aujourd'hui par M4 seul.

### Tests rétrospectifs du modèle complet (`resultats/validation_M8.md`)

| | 2015-2019 (base 2014, estimation jusqu'en 2014) | 2023-2024 (base 2022) |
|---|---|---|
| PIB en volume, erreur de niveau en fin de période | −0,4 % | −2,8 % |
| Consommation, investissement, emploi | −0,2 % ; −0,4 % ; −0,9 % | +0,6 % ; −3,7 % ; −0,2 % |
| Exportations ; importations | +3,0 % ; +3,9 % | −7,6 % ; +1,5 % |
| Prix à la consommation | +0,7 % | **−7,2 %** |
| Salaire moyen | +4,8 % | −4,3 % |
| Chômage, solde public, dette | +0,8 pt ; −0,2 pt ; +1,8 pt | +0,2 pt ; +2,3 pt ; +1,9 pt |

**Lecture.** En régime ordinaire (2015-2019), le modèle bouclé reproduit la croissance, la demande, l'emploi, les prix
et les comptes publics à moins de 1 % ou 1 point près sur cinq ans ; il surestime la croissance des salaires.
Après le choc énergétique (2023-2024), il manque l'inflation : il ne représente pas les délais de transmission des prix
de l'énergie (tarifs réglementés, bouclier tarifaire, contrats), ni le rattrapage des salaires qui a suivi. Il en
découle une erreur sur le revenu nominal et le solde public. C'est la priorité de la version suivante.

### Variantes (écarts au compte central, base 2022)

Effets à cinq ans (2028) :

| Variante | PIB | Emploi | Prix | Solde public | Lecture |
|---|---|---|---|---|---|
| Énergie importée +50 % | −0,4 % | −190 000 | +3,3 % | −0,9 pt | sens attendu ; transmission aux prix probablement surestimée (pas de substitution énergétique) |
| Salaires +2 % (ponctuel) | −0,1 % | −66 000 | +1,3 % | +0,1 pt | effet compétitivité et substitution contre effet revenu |
| IS de 25,8 % à 20 % | +0,25 % | +53 000 | ≈ 0 | −0,4 pt | investissement +1,8 % ; coût budgétaire peu compensé à cinq ans |
| Consommation publique +1 % du PIB | +1,15 % | +333 000 | +1,1 % | −0,2 pt | multiplicateur proche de 1,2, dans la fourchette haute des estimations, faute de politique monétaire et de contraintes d'offre |
| Réindustrialisation : parts importées −20 % dans six filières | +2,8 % | +650 000 | +2,5 % | +1,3 pt | **majorant** : aucune contrainte de capacité, de qualification ni de coût de production intérieur n'est représentée |

## 5. Ce qui est robuste et ce qui dépend des hypothèses

- **Plutôt robuste** : la propagation de la demande par les relations entre branches et les importations ; les
  ordres de grandeur de court terme de la consommation, de l'emploi et des comptes publics en régime ordinaire.
- **Dépendant d'hypothèses** :
  - l'effet du coût du travail sur l'emploi, et l'effet du chômage sur les salaires (calibrés) ;
  - l'effet de l'impôt sur les sociétés (une seule élasticité agrégée, fragile) ;
  - la tendance de productivité ;
  - la réindustrialisation, qui n'a pas de contrainte d'offre ;
  - toute variante de grande ampleur sur les prix.
- **Absent** :
  - politique monétaire et taux d'intérêt endogènes ;
  - contraintes de capacité et taux d'utilisation ;
  - flux physiques d'énergie et de matières ;
  - substitution entre énergies ;
  - offre de travail endogène et retraites (lot suivant) ;
  - branchement de la microsimulation M4 sur les revenus.

## 6. Suite

1. Délais de transmission des prix (énergie et alimentation), estimés sur les tableaux entrées-sorties 2010-2022.
2. Contraintes d'offre : taux d'utilisation des capacités et capital par branche dans les décisions d'investissement et
   de prix ; coûts relatifs de production pour la réindustrialisation.
3. Activité et retraites : population active issue de M1 et des taux d'activité par âge sensibles aux règles de retraite ;
   pensions, cotisations, dépenses de retraite.
4. Comptes physiques de l'énergie (`nrg_bal_c`, téléchargé) reliés aux branches.
5. Branchement de M4 (impôts et prestations) dans le revenu des ménages.
