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

Compte central conventionnel, et non une prévision (`exogenes_projection`). Écarts en % (volumes, prix) ou en points.

### Prix de l'énergie importée +20 % (dès 2024 ; ≈ +34 Md€ sur la facture de 2022, 169 Md€)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | -0.26 % | -0.79 % | -0.07 % | -0.61 % | -0.93 % | -45 | +0.14 | +0.1 | +1.07 % | +0.41 % | -0.04 | -0.09 |
| 2026 | -0.32 % | -1.18 % | -0.08 % | -1.10 % | -1.66 % | -93 | +0.28 | +0.3 | +1.88 % | +0.55 % | -0.35 | +0.46 |
| 2028 | -0.32 % | -1.34 % | -0.05 % | -1.18 % | -1.89 % | -116 | +0.35 | +0.4 | +1.93 % | +0.31 % | -0.49 | +1.56 |
| 2030 | -0.28 % | -1.40 % | -0.04 % | -1.15 % | -1.96 % | -115 | +0.35 | +0.4 | +1.77 % | -0.01 % | -0.55 | +2.81 |

### Salaires +2 % (choc ponctuel en 2024)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | -0.13 % | +0.13 % | -0.08 % | -0.66 % | -0.17 % | -8 | +0.02 | -0.3 | +1.44 % | +2.59 % | +0.36 | -2.44 |
| 2026 | -0.06 % | +0.43 % | -0.08 % | -0.60 % | +0.07 % | -34 | +0.10 | -0.3 | +1.32 % | +2.36 % | +0.16 | -2.52 |
| 2028 | -0.07 % | +0.37 % | -0.07 % | -0.54 % | +0.07 % | -58 | +0.18 | -0.2 | +1.20 % | +2.11 % | +0.13 | -2.46 |
| 2030 | -0.07 % | +0.35 % | -0.07 % | -0.49 % | +0.06 % | -62 | +0.19 | -0.2 | +1.08 % | +1.85 % | +0.12 | -2.37 |

### Taux d'IS de 25,8 % à 20 % (dès 2024)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +0.05 % | +0.03 % | +0.37 % | +0.01 % | +0.13 % | +6 | -0.02 | +0.0 | -0.01 % | -0.00 % | -0.43 | +0.39 |
| 2026 | +0.17 % | +0.12 % | +1.15 % | +0.01 % | +0.38 % | +28 | -0.09 | -0.2 | -0.00 % | +0.03 % | -0.40 | +1.05 |
| 2028 | +0.27 % | +0.22 % | +1.84 % | -0.00 % | +0.60 % | +57 | -0.17 | -0.7 | +0.05 % | +0.15 % | -0.36 | +1.52 |
| 2030 | +0.34 % | +0.31 % | +2.42 % | -0.03 % | +0.78 % | +82 | -0.25 | -1.3 | +0.14 % | +0.33 % | -0.32 | +1.85 |

### Réindustrialisation, borne haute : parts importées −10 % immédiatement (≈ 38 Md€ sur 380 Md€ d'importations de ces produits en 2022), sans investissement ni surcoût — chimie, pharmacie, métallurgie, produits métalliques, électronique, équipements électriques, machines, automobile

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +1.44 % | +0.88 % | +1.02 % | +0.06 % | -1.67 % | +200 | -0.61 | +4.0 | +0.02 % | +0.28 % | +0.40 | -2.07 |
| 2026 | +1.43 % | +1.20 % | +0.84 % | -0.37 % | -1.71 % | +294 | -0.90 | +2.8 | +0.60 % | +1.18 % | +0.59 | -4.03 |
| 2028 | +1.40 % | +1.40 % | +0.77 % | -0.75 % | -1.72 % | +326 | -0.99 | +2.2 | +1.24 % | +2.24 % | +0.73 | -6.20 |
| 2030 | +1.15 % | +1.46 % | +0.60 % | -1.11 % | -1.47 % | +303 | -0.92 | +1.2 | +1.88 % | +3.30 % | +0.81 | -8.24 |

### Réindustrialisation, mêmes produits, −10 % atteint en 5 ans (dès 2024), avec investissement de capacité et surcoût de 10 % de la VA produite en France

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +0.41 % | +0.22 % | +0.86 % | +0.07 % | -0.16 % | +38 | -0.12 | +1.0 | -0.06 % | -0.01 % | +0.07 | -0.36 |
| 2026 | +1.07 % | +0.67 % | +1.62 % | +0.05 % | -0.72 % | +156 | -0.48 | +1.0 | +0.04 % | +0.26 % | +0.29 | -1.61 |
| 2028 | +1.75 % | +1.25 % | +2.41 % | -0.11 % | -1.25 % | +305 | -0.93 | +0.6 | +0.41 % | +0.97 % | +0.58 | -3.79 |
| 2030 | +1.44 % | +1.37 % | +1.76 % | -0.48 % | -1.07 % | +347 | -1.05 | -1.9 | +1.11 % | +2.05 % | +0.71 | -5.82 |

### Consommation publique +1 % du PIB en volume (dès 2024)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +1.39 % | +1.16 % | +0.27 % | +0.10 % | +0.92 % | +283 | -0.87 | +0.3 | -0.17 % | -0.05 % | -0.33 | -0.91 |
| 2026 | +1.36 % | +1.25 % | +0.29 % | -0.20 % | +0.82 % | +355 | -1.08 | +0.1 | +0.46 % | +0.96 % | -0.16 | -1.45 |
| 2028 | +1.30 % | +1.38 % | +0.21 % | -0.50 % | +0.79 % | +374 | -1.14 | -0.1 | +1.11 % | +2.05 % | -0.09 | -2.15 |
| 2030 | +1.24 % | +1.51 % | +0.16 % | -0.78 % | +0.79 % | +362 | -1.09 | -0.3 | +1.72 % | +3.09 % | -0.03 | -2.91 |

Durée : 22 s.

