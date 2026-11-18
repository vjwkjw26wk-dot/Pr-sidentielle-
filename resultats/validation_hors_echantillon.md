# Validation historique hors échantillon (version 0.6)

Erreur quadratique moyenne (RMSE, points de pourcentage) des taux de croissance annuels simulés, comparée à deux modèles simples : « naïf » (croissance moyenne des cinq années précédant l'origine) et AR(1) (croissance annuelle régressée sur sa valeur passée, estimée jusqu'à l'origine). Un ratio modèle / naïf inférieur à 1 indique un gain de prévision conditionnelle. Le modèle bénéficie des exogènes observées (avantage informationnel que n'ont pas les modèles simples) : la comparaison mesure la valeur ajoutée des mécanismes conditionnellement à ces exogènes, non une capacité de prévision inconditionnelle.

## Origine 2012 (crise des dettes souveraines et reprise) : estimation jusqu'en 2012, simulation 2013-2016

| Variable | RMSE modèle | RMSE naïf | RMSE AR(1) | Modèle / naïf | Erreur de niveau en fin de période |
|---|---|---|---|---|---|
| pib | 0.74 | 0.50 | 0.65 | 1.46 | +1.5 % |
| c | 1.01 | 0.64 | 0.49 | 1.58 | +3.3 % |
| fbcf | 1.67 | 1.99 | 1.93 | 0.84 | +5.8 % |
| x | 1.54 | 1.70 | 1.08 | 0.91 | -0.7 % |
| m | 0.89 | 2.95 | 1.04 | 0.30 | -0.5 % |
| emploi | 0.32 | 0.37 | 0.28 | 0.85 | -0.6 % |
| pc | 0.94 | 0.85 | 1.08 | 1.11 | -1.4 % |
| chômage (points, fin) | | | | | +0.5 |

## Origine 2014 (période calme (estimation jusqu'en 2014)) : estimation jusqu'en 2014, simulation 2015-2018

| Variable | RMSE modèle | RMSE naïf | RMSE AR(1) | Modèle / naïf | Erreur de niveau en fin de période |
|---|---|---|---|---|---|
| pib | 0.64 | 0.50 | 0.46 | 1.27 | +0.0 % |
| c | 0.49 | 0.73 | 0.39 | 0.67 | +1.3 % |
| fbcf | 1.55 | 2.44 | 1.27 | 0.64 | -2.4 % |
| x | 0.69 | 1.32 | 1.00 | 0.52 | +1.8 % |
| m | 0.85 | 0.99 | 1.01 | 0.86 | +1.3 % |
| emploi | 0.32 | 0.53 | 0.33 | 0.60 | -0.1 % |
| pc | 0.29 | 0.74 | 0.81 | 0.39 | -0.2 % |
| chômage (points, fin) | | | | | +0.1 |

## Origine 2016 (période calme) : estimation jusqu'en 2016, simulation 2017-2019

| Variable | RMSE modèle | RMSE naïf | RMSE AR(1) | Modèle / naïf | Erreur de niveau en fin de période |
|---|---|---|---|---|---|
| pib | 0.64 | 1.16 | 0.53 | 0.56 | -1.9 % |
| c | 0.09 | 0.57 | 0.40 | 0.16 | -0.1 % |
| fbcf | 2.69 | 3.34 | 1.62 | 0.80 | -6.8 % |
| x | 1.13 | 1.10 | 1.03 | 1.03 | +3.0 % |
| m | 1.52 | 1.05 | 1.68 | 1.45 | +3.4 % |
| emploi | 0.39 | 0.71 | 0.39 | 0.55 | -1.1 % |
| pc | 0.40 | 0.87 | 0.53 | 0.46 | -0.7 % |
| chômage (points, fin) | | | | | +1.1 |

## Origine 2019 (crise sanitaire (rupture de régime)) : estimation jusqu'en 2019, simulation 2020-2022

| Variable | RMSE modèle | RMSE naïf | RMSE AR(1) | Modèle / naïf | Erreur de niveau en fin de période |
|---|---|---|---|---|---|
| pib | 4.13 | 6.07 | 6.14 | 0.68 | +1.1 % |
| c | 6.35 | 5.55 | 5.53 | 1.14 | +0.5 % |
| fbcf | 5.36 | 6.68 | 6.74 | 0.80 | -0.2 % |
| x | 5.86 | 12.83 | 12.78 | 0.46 | +14.9 % |
| m | 5.63 | 10.08 | 10.06 | 0.56 | +12.7 % |
| emploi | 0.73 | 1.40 | 1.39 | 0.52 | -1.6 % |
| pc | 0.50 | 2.42 | 2.21 | 0.21 | +0.4 % |
| chômage (points, fin) | | | | | +1.4 |

## Origine 2021 (choc d'inflation 2022-2023) : estimation jusqu'en 2019, simulation 2022-2024

| Variable | RMSE modèle | RMSE naïf | RMSE AR(1) | Modèle / naïf | Erreur de niveau en fin de période |
|---|---|---|---|---|---|
| pib | 1.50 | 1.06 | 0.58 | 1.41 | -4.2 % |
| c | 2.36 | 2.02 | 1.65 | 1.17 | -3.6 % |
| fbcf | 1.29 | 3.19 | 3.75 | 0.40 | -0.7 % |
| x | 4.66 | 4.90 | 2.87 | 0.95 | -5.4 % |
| m | 1.73 | 4.75 | 4.60 | 0.37 | +2.2 % |
| emploi | 1.14 | 0.69 | 0.47 | 1.65 | -3.3 % |
| pc | 2.66 | 4.11 | 4.09 | 0.65 | -5.4 % |
| chômage (points, fin) | | | | | +3.1 |

## Stabilité des coefficients (estimation sur différentes fenêtres)

Coefficient (erreur-type). La fenêtre 1997-2024 inclut 2020-2022 sans traitement particulier : elle illustre la sensibilité aux chocs exceptionnels, elle n'est pas utilisée par le modèle.

| Équation | Coefficient | 1997-2007 | 1997-2012 | 1997-2019 | 2003-2019 | 1997-2024 |
|---|---|---|---|---|---|---|
| consommation | dlrdb | +1.15 (0.33) | +1.04 (0.23) | +0.85 (0.21) | +0.54 (0.10) | +1.08 (0.31) |
| consommation | ecart_1 | -0.81 (0.30) | -0.30 (0.22) | -0.22 (0.21) | -0.03 (0.12) | -0.26 (0.10) |
| importations | dld | +1.50 (0.07) | +1.45 (0.10) | +1.46 (0.09) | +1.34 (0.07) | +1.23 (0.10) |
| importations | dlprel | +0.02 (0.04) | -0.03 (0.14) | -0.11 (0.10) | -0.12 (0.11) | +0.03 (0.11) |
| importations | lm_1 | -1.87 (0.16) | -0.90 (0.18) | -0.66 (0.15) | -0.68 (0.28) | -0.34 (0.24) |
| exportations | dldm | +0.91 (0.27) | +0.70 (0.14) | +0.71 (0.09) | +0.61 (0.09) | +0.87 (0.19) |
| exportations | dlprel | -0.43 (0.34) | -0.69 (0.37) | -0.59 (0.17) | -0.70 (0.24) | -0.68 (0.17) |
| salaires | dlpc | +0.73 (0.13) | +0.47 (0.25) | +0.39 (0.22) | -0.06 (0.12) | +0.37 (0.15) |
| salaires | ecm_1 | -0.38 (0.13) | -0.02 (0.06) | -0.09 (0.06) | -0.17 (0.05) | -0.05 (0.06) |
| investissement_snf | dlq | +2.39 (0.32) | +2.44 (0.33) | +1.95 (0.33) | +2.04 (0.40) | +1.04 (0.29) |
| investissement_snf | lcu_1 | -0.07 (0.01) | -0.07 (0.02) | -0.07 (0.02) | -0.05 (0.05) | -0.04 (0.02) |
