# Validation du modèle bouclé M8 (version 0.1)

Généré par `tests/validation_M8.py`.

## 1. Simulations rétrospectives du modèle complet

Toutes les équations sont bouclées ; seules les variables exogènes sont observées. Les mesures de politique publique ne sont pas introduites une à une : les recettes suivent les assiettes à taux apparents constants, sauf l'impôt sur les sociétés (taux normal) ; les dépenses publiques hors consommation, prestations et intérêts sont prises observées en part du PIB. La dette évolue avec le solde seulement (ajustements stock-flux nuls).

### Base 2014, simulation 2015-2019 (coefficients estimés sur 1997-2014)

| Variable | Croissance annuelle moyenne observée | Simulée | Erreur sur le niveau en 2019 |
|---|---|---|---|
| PIB en volume | +1.5 % | +1.6 % | +0.1 % |
| Consommation des ménages | +1.4 % | +1.9 % | +2.6 % |
| Investissement total | +2.9 % | +2.9 % | -0.1 % |
| Exportations | +3.4 % | +4.0 % | +2.9 % |
| Importations | +3.8 % | +4.9 % | +5.4 % |
| Emploi total | +0.9 % | +0.9 % | -0.0 % |
| Prix à la consommation | +0.8 % | +0.9 % | +0.5 % |
| Salaire moyen par tête (marchand) | +1.0 % | +2.1 % | +5.6 % |
| Revenu disponible brut (valeur) | +2.3 % | +2.7 % | +1.6 % |
| Taux de chômage en 2019 | 8.2 % | 8.2 % | +0.0 point |
| Solde public en 2019 (% du PIB) | -2.4 | -2.2 | +0.2 point |
| Dette publique en 2019 (% du PIB) | 98.2 | 98.6 | +0.4 points |
| Taux d'utilisation des capacités, industrie, en 2019 | 84.1 % | 80.5 % | -3.6 point |

### Base 2022, simulation 2023-2024 (coefficients estimés sur 1997-2019)

| Variable | Croissance annuelle moyenne observée | Simulée | Erreur sur le niveau en 2024 |
|---|---|---|---|
| PIB en volume | +1.6 % | -0.2 % | -3.5 % |
| Consommation des ménages | +0.9 % | +0.3 % | -1.2 % |
| Investissement total | +0.2 % | -1.7 % | -3.8 % |
| Exportations | +2.8 % | -2.6 % | -10.2 % |
| Importations | -0.4 % | -1.6 % | -2.4 % |
| Emploi total | +0.9 % | +0.6 % | -0.6 % |
| Prix à la consommation | +4.6 % | +3.1 % | -2.9 % |
| Salaire moyen par tête (marchand) | +3.8 % | +2.3 % | -2.8 % |
| Revenu disponible brut (valeur) | +6.5 % | +2.3 % | -7.7 % |
| Taux de chômage en 2024 | 7.2 % | 7.7 % | +0.5 point |
| Solde public en 2024 (% du PIB) | -5.8 | -4.1 | +1.7 point |
| Dette publique en 2024 (% du PIB) | 112.6 | 114.6 | +2.0 points |
| Taux d'utilisation des capacités, industrie, en 2024 | 80.5 % | 77.4 % | -3.0 point |

## 2. Variantes (écarts au compte central, base 2022, 2023-2030)

Compte central conventionnel, et non une prévision (`exogenes_projection`), avec fermeture d'offre ρ = 0,3 (amortissement 1,0) (résorption progressive de l'écart de chômage au chômage structurel, décision A12). Écarts en % (volumes, prix) ou en points.

### Prix de l'énergie importée +20 % (dès 2024 ; ≈ +34 Md€ sur la facture de 2022, 169 Md€)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | -0.26 % | -0.80 % | -0.07 % | -0.61 % | -0.94 % | -45 | +0.14 | +0.1 | +1.07 % | +0.41 % | -0.05 | -0.08 |
| 2026 | -0.08 % | -0.99 % | +0.01 % | -1.10 % | -1.30 % | -45 | +0.14 | +0.4 | +1.87 % | +0.60 % | -0.29 | +0.11 |
| 2028 | +0.01 % | -1.05 % | +0.06 % | -1.24 % | -1.42 % | -35 | +0.11 | +0.5 | +2.05 % | +0.56 % | -0.38 | +0.77 |
| 2030 | +0.05 % | -1.06 % | +0.07 % | -1.28 % | -1.48 % | -21 | +0.06 | +0.4 | +2.07 % | +0.50 % | -0.42 | +1.53 |

### Salaires +2 % (choc ponctuel en 2024)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | -0.14 % | +0.12 % | -0.08 % | -0.66 % | -0.18 % | -8 | +0.03 | -0.3 | +1.44 % | +2.59 % | +0.36 | -2.46 |
| 2026 | -0.01 % | +0.46 % | -0.06 % | -0.59 % | +0.14 % | -25 | +0.07 | -0.3 | +1.31 % | +2.37 % | +0.17 | -2.66 |
| 2028 | +0.09 % | +0.51 % | -0.01 % | -0.54 % | +0.31 % | -23 | +0.07 | -0.2 | +1.21 % | +2.17 % | +0.19 | -2.87 |
| 2030 | +0.11 % | +0.52 % | -0.00 % | -0.52 % | +0.32 % | -13 | +0.04 | -0.2 | +1.16 % | +2.03 % | +0.21 | -3.13 |

### Taux d'IS de 25,8 % à 20 % (dès 2024)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +0.05 % | +0.03 % | +0.37 % | +0.01 % | +0.13 % | +6 | -0.02 | +0.0 | -0.01 % | -0.00 % | -0.42 | +0.39 |
| 2026 | +0.10 % | +0.07 % | +1.12 % | +0.00 % | +0.28 % | +18 | -0.05 | -0.2 | +0.00 % | +0.03 % | -0.41 | +1.11 |
| 2028 | +0.12 % | +0.10 % | +1.77 % | +0.00 % | +0.38 % | +26 | -0.08 | -0.7 | +0.04 % | +0.09 % | -0.41 | +1.81 |
| 2030 | +0.13 % | +0.11 % | +2.32 % | +0.01 % | +0.45 % | +29 | -0.09 | -1.3 | +0.07 % | +0.17 % | -0.42 | +2.51 |

### Réindustrialisation, borne haute : parts importées −10 % immédiatement (≈ 38 Md€ sur 380 Md€ d'importations de ces produits en 2022), sans investissement ni surcoût — chimie, pharmacie, métallurgie, produits métalliques, électronique, équipements électriques, machines, automobile

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +0.68 % | +0.37 % | +0.74 % | -0.04 % | -2.49 % | +96 | -0.30 | +3.4 | +0.18 % | +0.32 % | +0.29 | -1.43 |
| 2026 | +0.45 % | +0.38 % | +0.43 % | -0.33 % | -2.76 % | +83 | -0.25 | +2.3 | +0.47 % | +0.75 % | +0.29 | -2.27 |
| 2028 | +0.40 % | +0.40 % | +0.40 % | -0.48 % | -2.81 % | +57 | -0.17 | +1.9 | +0.65 % | +1.07 % | +0.31 | -3.07 |
| 2030 | +0.26 % | +0.38 % | +0.32 % | -0.59 % | -2.59 % | +27 | -0.08 | +1.3 | +0.78 % | +1.31 % | +0.31 | -3.71 |

### Réindustrialisation, mêmes produits, −10 % atteint en 5 ans (dès 2024), avec investissement de capacité et surcoût de 10 % de la VA produite en France

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +0.41 % | +0.22 % | +0.86 % | +0.07 % | -0.16 % | +38 | -0.12 | +1.0 | -0.07 % | -0.01 % | +0.07 | -0.37 |
| 2026 | +0.66 % | +0.37 % | +1.41 % | +0.02 % | -1.18 % | +84 | -0.26 | +0.8 | +0.08 % | +0.21 % | +0.20 | -1.13 |
| 2028 | +0.88 % | +0.53 % | +2.00 % | -0.07 % | -2.22 % | +121 | -0.37 | +0.2 | +0.30 % | +0.59 % | +0.33 | -2.25 |
| 2030 | +0.44 % | +0.37 % | +1.34 % | -0.24 % | -2.34 % | +76 | -0.23 | -2.0 | +0.58 % | +0.98 % | +0.29 | -2.77 |

### Consommation publique +1 % du PIB en volume (dès 2024)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +1.41 % | +1.17 % | +0.28 % | +0.10 % | +0.94 % | +283 | -0.87 | +0.3 | -0.17 % | -0.05 % | -0.34 | -0.94 |
| 2026 | +0.42 % | +0.49 % | -0.16 % | -0.17 % | -0.59 % | +139 | -0.42 | -0.1 | +0.37 % | +0.61 % | -0.50 | +0.22 |
| 2028 | +0.25 % | +0.33 % | -0.16 % | -0.24 % | -0.79 % | +79 | -0.24 | -0.2 | +0.53 % | +0.89 % | -0.56 | +1.21 |
| 2030 | +0.23 % | +0.32 % | -0.15 % | -0.27 % | -0.81 % | +51 | -0.15 | -0.2 | +0.60 % | +1.03 % | -0.61 | +2.24 |

Durée : 20 s.

