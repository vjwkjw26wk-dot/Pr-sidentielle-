# Lot 7 et M8 — Équations de comportement estimées et modèle bouclé (version 0.2)

**État : version 0.2 (délais de transmission des prix, réindustrialisation avec investissement et surcoût). Première version complète et testée de bout en bout. C'est un prototype à consolider : plusieurs paramètres
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
| Transmission des prix d'importation aux prix à la consommation (v0.2) | Sur 1998-2024 : 0,18 l'année même et 0,18 l'année suivante, soit une part transmise l'année même θ = 0,50. Sur 1998-2019, la transmission était immédiate (0,27, puis −0,05) | **estimé sur un échantillon qui inclut 2021-2024** : le délai n'apparaît qu'avec l'épisode énergétique (tarifs réglementés, bouclier tarifaire, contrats) ; le test 2023-2024 n'est donc plus entièrement hors échantillon |

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

### Délais de transmission des prix (v0.2)

Dans le modèle bouclé, les prix d'importation **répercutés** s'ajustent partiellement vers les prix observés :
ln pm_eff(t) = ln pm_eff(t−1) + θ · (ln pm(t) − ln pm_eff(t−1)), avec θ = 0,50. L'écart à l'année de base (hausses
pas encore répercutées) est reconstitué à partir des prix d'importation par produit des quatre années précédentes.
Le paramètre θ est modifiable par scénario (`Exogenes.theta_import`).

### Réindustrialisation (v0.2)

Variante paramétrée par `Exogenes.reindustrialisation` :
- **Parts importées des produits ciblés** : chaque produit a un facteur cible (0,9 = −10 %), atteint progressivement sur une durée de montée en charge.
- **Investissement de capacité** : capital nécessaire = rapport capital / valeur ajoutée de la branche observé à l'année de base, multiplié par la valeur ajoutée des capacités nouvelles ; s'y ajoute le renouvellement, au taux de dépréciation observé de la branche.
- **Surcoût** : la valeur ajoutée produite en France à la place des importations coûte un pourcentage de plus ; ce surcoût se répercute sur les prix par le modèle entrées-sorties.

Les autres parts importées gardent le comportement du compte central. Les contraintes de main-d'œuvre jouent par le
chômage et les salaires. Il n'y a encore ni contrainte de qualification, ni limite de capacité dans les autres branches.

### Tests rétrospectifs du modèle complet (`resultats/validation_M8.md`)

| Erreur de niveau en fin de période | 2015-2019 (base 2014, estimation jusqu'en 2014) | 2023-2024 (base 2022) |
|---|---|---|
| PIB en volume | −0,3 % | −3,6 % |
| Consommation ; investissement ; emploi | +1,4 % ; −0,2 % ; −0,4 % | −1,4 % ; −3,8 % ; −0,6 % |
| Exportations ; importations | +3,2 % ; +5,0 % | −10,3 % ; −2,5 % |
| Prix à la consommation | +0,2 % | −2,8 % (v0.1 : −7,2 %) |
| Salaire moyen | +5,2 % | −2,8 % |
| Revenu disponible brut | +0,1 % | −7,9 % |
| Chômage ; solde public ; dette | +0,4 pt ; 0,0 pt ; +1,9 pt | +0,6 pt ; +1,7 pt ; +2,0 pt |

**Lecture.**
- **2015-2019, régime ordinaire** : le modèle bouclé reproduit la croissance, l'emploi, les prix et le solde public à moins de 1,5 % ou 0,5 point près sur cinq ans. Il surestime la croissance des salaires d'environ 1 point par an.
- **2023-2024** :
  - Les délais de transmission ramènent l'erreur sur les prix de −7,2 % à −2,8 %.
  - Trois défauts restent :
    - Les exportations sont mal suivies. La demande mondiale approchée par les importations de l'Union européenne baisse en 2023, alors que les exportations françaises progressent (aéronautique, énergie).
    - Le revenu des ménages est sous-estimé. Les revenus de la propriété (+15 % par an, avec la hausse des taux) et les loyers imputés ne sont indexés que sur le PIB nominal.
    - Par conséquent, le PIB est trop bas.

### Essais écartés (17 novembre 2026)

Deux améliorations ont été testées puis écartées, car elles dégradent la rétrosimulation 2015-2019 :
- **Demande mondiale adressée** construite avec le FMI : importations en volume des partenaires (Perspectives de l'économie mondiale), pondérées par leur part dans les exportations françaises (statistiques de commerce bilatéral), via DBnomics, couverture 99 %.
  - Elle améliore 2022-2024 : erreur sur les exportations −6,6 % au lieu de −10,3 %.
  - Elle dégrade 2013-2019 : −9,5 % au lieu de −0,2 % en équation seule.
  - Explication probable : les parts de marché françaises ont surtout reculé dans les années 2000, période d'estimation, puis se sont stabilisées.
  - La série reste disponible (`m7_series.demande_mondiale_adressee`).
- **Revenus du patrimoine des ménages par équations estimées** (dépendant du PIB nominal, des prix et des taux longs ; option `patrimoine_endogene`).
  - Elles dégradent 2015-2019 : revenu disponible −2,3 % au lieu de +0,1 %, et dette +5,4 points au lieu de +1,9. La hausse des dividendes de 2018, liée au prélèvement forfaitaire unique, n'est pas expliquée.
  - Elles améliorent à peine 2023-2024 : revenu disponible −7,0 % au lieu de −7,9 %.

### Variantes (écarts au compte central, base 2022)

Effets à cinq ans (2028) :

| Variante | PIB | Emploi | Prix | Solde public | Lecture |
|---|---|---|---|---|---|
| Énergie importée +20 % (≈ +34 Md€ sur la facture de 2022) | −0,3 % | −108 000 | +1,9 % | −0,5 pt | perte de pouvoir d'achat ; pas de substitution énergétique représentée |
| Salaires +2 % (ponctuel) | −0,1 % | −60 000 | +1,2 % | +0,1 pt | compétitivité et substitution contre effet revenu |
| IS de 25,8 % à 20 % | +0,26 % | +55 000 | ≈ 0 | −0,4 pt | investissement +1,8 % (+2,4 % en 2030) ; coût budgétaire peu compensé |
| Consommation publique +1 % du PIB | +1,2 % | +335 000 | +1,0 % | −0,2 pt | multiplicateur proche de 1,2, haut de fourchette (pas de politique monétaire ni de contraintes d'offre) |
| Réindustrialisation −10 % d'importations (≈ 38 Md€), immédiate et sans coût | +1,4 % | +318 000 | +1,1 % | +0,7 pt | borne haute |
| Même objectif en 5 ans, avec investissement de capacité et surcoût de 10 % | +1,7 % (+1,3 % en 2030) | +291 000 | +0,4 % | +0,6 pt | effet d'investissement transitoire ; résultat proportionnel à l'hypothèse de substitution, qui n'est pas expliquée par le modèle |

## 5. Ce qui est robuste et ce qui dépend des hypothèses

- **Plutôt robuste** : la propagation de la demande par les relations entre branches et les importations ; les
  ordres de grandeur de court terme de la consommation, de l'emploi et des comptes publics en régime ordinaire.
- **Dépendant d'hypothèses** :
  - l'effet du coût du travail sur l'emploi, et l'effet du chômage sur les salaires (calibrés) ;
  - l'effet de l'impôt sur les sociétés (une seule élasticité agrégée, fragile) ;
  - la tendance de productivité ;
  - la réindustrialisation, qui n'a pas de contrainte d'offre ;
  - toute variante de grande ampleur sur les prix ;
  - le délai de transmission des prix d'importation, estimé grâce au seul épisode 2021-2024.
- **Absent** :
  - politique monétaire et taux d'intérêt endogènes ;
  - contraintes de capacité et taux d'utilisation ;
  - flux physiques d'énergie et de matières ;
  - substitution entre énergies ;
  - offre de travail endogène et retraites (lot suivant) ;
  - branchement de la microsimulation M4 sur les revenus.

## 6. Suite

1. Exportations : traitement spécifique des grands contrats (aéronautique) et des prix des concurrents hors énergie.
2. Contraintes d'offre : taux d'utilisation des capacités et capital par branche dans les décisions d'investissement et
   de prix ; qualifications ; mécanisme expliquant la substitution aux importations (coûts relatifs, aides).
3. Activité et retraites : population active issue de M1 et des taux d'activité par âge sensibles aux règles de retraite ;
   pensions, cotisations, dépenses de retraite.
4. Comptes physiques de l'énergie (`nrg_bal_c`, téléchargé) reliés aux branches.
5. Branchement de M4 (impôts et prestations) dans le revenu des ménages.
