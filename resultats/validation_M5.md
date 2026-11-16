# Validation du bloc productif M5

Source : Eurostat, tableaux entrées-sorties symétriques de la France (64 produits, aux prix de base), 2010-2022 ; prix courants et prix de l'année précédente. Généré par `tests/validation_M5.py`.

## 1. Identités comptables

| Année | Produits | Production (Md€) | Valeur ajoutée (Md€) | Importations (Md€) | Écart max. ressources-emplois (M€) | Écart max. coûts-production (M€) |
|---|---|---|---|---|---|---|
| 2010 | 64 | 3 543 | 1 801 | 534 | 0.1 | 0.1 |
| 2011 | 64 | 3 685 | 1 849 | 599 | 1.6 | 0.1 |
| 2012 | 64 | 3 741 | 1 873 | 614 | 0.1 | 0.1 |
| 2013 | 64 | 3 761 | 1 898 | 618 | 0.2 | 0.1 |
| 2014 | 64 | 3 801 | 1 925 | 631 | 0.2 | 1.0 |
| 2015 | 64 | 3 852 | 1 967 | 655 | 0.1 | 0.1 |
| 2016 | 64 | 3 893 | 1 997 | 658 | 0.1 | 0.1 |
| 2017 | 64 | 4 054 | 2 046 | 703 | 0.1 | 0.1 |
| 2018 | 64 | 4 186 | 2 102 | 739 | 0.1 | 0.1 |
| 2019 | 64 | 4 315 | 2 169 | 754 | 0.1 | 1.5 |
| 2020 | 64 | 4 075 | 2 057 | 678 | 0.1 | 1.8 |
| 2021 | 64 | 4 521 | 2 213 | 789 | 1.8 | 0.1 |
| 2022 | 64 | 5 112 | 2 369 | 1 010 | 0.1 | 0.1 |

Les écarts sont des arrondis de publication (≤ 2 M€ sur des productions de plusieurs milliards).

## 2. Test rétrospectif du modèle de prix (coefficients de N−1, chocs observés en N)

Erreur absolue moyenne sur les 64 produits, pondérée par la production, en points de pourcentage de variation annuelle de prix ; corrélation entre variations prévues et observées.

| Année | Prix de production observés, moyenne pondérée | (a) Imports seuls : prévision moyenne | (a) erreur abs. moyenne | (a) corrélation | (b) Imports + VA : erreur abs. moyenne | (b) corrélation | Prix à la consommation des ménages : observé | (b) prévu |
|---|---|---|---|---|---|---|---|---|
| 2012 | +1.6 % | +0.4 % | 1.7 | 0.57 | 0.6 | 0.93 | +1.1 % | +1.2 % |
| 2013 | +0.3 % | -0.3 % | 1.6 | 0.55 | 0.7 | 0.81 | +0.5 % | +0.0 % |
| 2014 | -0.1 % | -0.4 % | 1.2 | 0.51 | 0.4 | 0.97 | -0.3 % | -0.5 % |
| 2015 | -0.0 % | -0.7 % | 1.4 | 0.87 | 0.8 | 0.89 | +0.1 % | +0.2 % |
| 2016 | -0.2 % | -0.5 % | 0.9 | 0.71 | 0.3 | 0.98 | +0.1 % | +0.0 % |
| 2017 | +0.9 % | +0.6 % | 1.2 | 0.80 | 0.7 | 0.92 | +0.7 % | +1.0 % |
| 2018 | +1.3 % | +0.6 % | 1.1 | 0.38 | 0.5 | 0.98 | +1.4 % | +1.4 % |
| 2019 | +1.0 % | -0.1 % | 1.4 | 0.36 | 0.3 | 0.94 | +0.7 % | +0.9 % |
| 2020 | +1.7 % | -0.6 % | 2.6 | 0.62 | 2.0 | 0.47 | +0.6 % | +2.6 % |
| 2021 | +3.5 % | +1.9 % | 2.5 | 0.56 | 1.2 | 0.97 | +1.3 % | +2.3 % |
| 2022 | +9.7 % | +4.9 % | 6.2 | 0.68 | 3.0 | 0.88 | +5.6 % | +9.0 % |

Détail 2022 (choc énergétique), produits les plus touchés : variation des prix de production, %.

| Produit | Prix d'importation | Observé | (a) Imports seuls | (b) Imports + VA |
|---|---|---|---|---|
| Cokéfaction et raffinage | +81.5 | +42.7 | +69.8 | +73.6 |
| Électricité, gaz, vapeur | +63.3 | +76.4 | +26.0 | +57.4 |
| Industries extractives (dont pétrole brut, gaz) | +117.9 | +10.1 | +6.7 | +13.2 |
| Métallurgie | +21.7 | +30.8 | +18.8 | +62.3 |
| Chimie | +25.3 | +27.3 | +13.5 | +34.5 |
| Minéraux non métalliques | +13.8 | +14.8 | +7.6 | +17.9 |
| Papier-carton | +24.0 | +24.3 | +8.6 | +25.5 |
| Agriculture | +14.9 | +21.4 | +6.7 | +18.4 |
| Industries agroalimentaires | +14.8 | +13.6 | +5.5 | +14.0 |
| Transports terrestres | +6.5 | +5.7 | +6.7 | +8.8 |
| Automobile | +4.2 | +5.3 | +4.2 | +9.3 |
| Construction | +9.4 | +8.7 | +4.5 | +10.8 |

## 3. Test rétrospectif du modèle de quantités

Production en volume de N (aux prix de N−1) prévue par x = (I − Ad,N−1)⁻¹ · fd,N, la demande finale intérieure de N étant déflatée par les prix de production observés. Erreur absolue moyenne pondérée sur les 64 produits, en % de la production.

| Année | Croissance observée du volume de production | Prévue | Erreur abs. moyenne par produit |
|---|---|---|---|
| 2012 | +0.0 % | +0.1 % | 1.3 % |
| 2013 | +0.3 % | +0.6 % | 1.2 % |
| 2014 | +1.2 % | +1.4 % | 1.2 % |
| 2015 | +1.6 % | +2.5 % | 1.6 % |
| 2016 | +1.3 % | +1.3 % | 0.9 % |
| 2017 | +3.2 % | +2.6 % | 1.2 % |
| 2018 | +2.0 % | +2.1 % | 1.3 % |
| 2019 | +2.1 % | +1.8 % | 0.9 % |
| 2020 | -7.0 % | -8.1 % | 5.4 % |
| 2021 | +7.7 % | +7.4 % | 1.4 % |
| 2022 | +4.7 % | +4.3 % | 2.1 % |

## 4. Illustrations (tableau 2021)

Contenu en importations par euro de demande finale (direct et indirect), produits les plus dépendants :

| Produit | Importations induites par € |
|---|---|
| Cokéfaction et raffinage | 0.73 |
| Autres matériels de transport (aéronautique, naval, ferroviaire) | 0.52 |
| Métallurgie | 0.50 |
| Automobile | 0.48 |
| Chimie | 0.42 |
| Équipements électriques | 0.40 |
| Caoutchouc et plastiques | 0.39 |
| Papier-carton | 0.38 |

Contenu moyen en importations de la demande finale intérieure : 0.18 € par €.

Hausse de 50 % des prix de l'énergie importée (produits B, C19, D), coefficients et valeur ajoutée unitaire fixes :

- prix de production, moyenne pondérée : +1.3 % ;
- prix à la consommation des ménages : +1.7 % ;
- produits les plus touchés : Cokéfaction et raffinage +29.2 % ; Électricité, gaz, vapeur +11.5 % ; Métallurgie +5.3 % ; Transport aérien +5.2 % ; Chimie +3.5 %.

