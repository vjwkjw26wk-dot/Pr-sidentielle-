# Validation du modèle bouclé M8 (version 0.1)

Généré par `tests/validation_M8.py`.

## 1. Simulations rétrospectives du modèle complet

Toutes les équations sont bouclées ; seules les variables exogènes sont observées. Les mesures de politique publique ne sont pas introduites une à une : les recettes suivent les assiettes à taux apparents constants, sauf l'impôt sur les sociétés (taux normal) ; les dépenses publiques hors consommation, prestations et intérêts sont prises observées en part du PIB. La dette évolue avec le solde seulement (ajustements stock-flux nuls).

### Base 2014, simulation 2015-2019 (coefficients estimés sur 1997-2014)

| Variable | Croissance annuelle moyenne observée | Simulée | Erreur sur le niveau en 2019 |
|---|---|---|---|
| PIB en volume | +1.5 % | +1.5 % | -0.2 % |
| Consommation des ménages | +1.4 % | +1.8 % | +1.7 % |
| Investissement total | +2.9 % | +2.8 % | -0.4 % |
| Exportations | +3.4 % | +4.0 % | +2.9 % |
| Importations | +3.8 % | +4.8 % | +4.7 % |
| Emploi total | +0.9 % | +0.8 % | -0.2 % |
| Prix à la consommation | +0.8 % | +0.9 % | +0.5 % |
| Salaire moyen par tête (marchand) | +1.0 % | +2.1 % | +5.6 % |
| Revenu disponible brut (valeur) | +2.3 % | +2.6 % | +1.4 % |
| Taux de chômage en 2019 | 8.2 % | 8.3 % | +0.2 point |
| Solde public en 2019 (% du PIB) | -2.4 | -2.3 | +0.1 point |
| Dette publique en 2019 (% du PIB) | 98.2 | 99.2 | +1.0 points |
| Taux d'utilisation des capacités, industrie, en 2019 | 84.1 % | 80.5 % | -3.6 point |

### Base 2022, simulation 2023-2024 (coefficients estimés sur 1997-2019)

| Variable | Croissance annuelle moyenne observée | Simulée | Erreur sur le niveau en 2024 |
|---|---|---|---|
| PIB en volume | +1.6 % | -0.5 % | -4.0 % |
| Consommation des ménages | +0.9 % | +0.0 % | -1.7 % |
| Investissement total | +0.2 % | -1.7 % | -3.7 % |
| Exportations | +2.8 % | -2.6 % | -10.2 % |
| Importations | -0.4 % | -1.3 % | -1.9 % |
| Emploi total | +0.9 % | +0.5 % | -0.8 % |
| Prix à la consommation | +4.6 % | +3.1 % | -2.9 % |
| Salaire moyen par tête (marchand) | +3.8 % | +2.3 % | -2.9 % |
| Revenu disponible brut (valeur) | +6.5 % | +2.1 % | -8.0 % |
| Taux de chômage en 2024 | 7.2 % | 7.9 % | +0.8 point |
| Solde public en 2024 (% du PIB) | -5.8 | -4.3 | +1.5 point |
| Dette publique en 2024 (% du PIB) | 112.6 | 115.4 | +2.8 points |
| Taux d'utilisation des capacités, industrie, en 2024 | 80.5 % | 76.6 % | -3.9 point |

## 2. Variantes (écarts au compte central, base 2022, 2023-2030)

Compte central conventionnel, et non une prévision (`exogenes_projection`), avec fermeture d'offre ρ = 0,3 (amortissement 1,0) (résorption progressive de l'écart de chômage au chômage structurel, décision A12). Écarts en % (volumes, prix) ou en points.

### Prix de l'énergie importée +20 % (dès 2024 ; ≈ +34 Md€ sur la facture de 2022, 169 Md€)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | -0.43 % | -0.85 % | -0.57 % | -0.64 % | -0.89 % | -61 | +0.19 | -0.2 | +1.10 % | +0.42 % | -0.07 | +0.06 |
| 2026 | -0.51 % | -1.19 % | -0.71 % | -1.11 % | -1.08 % | -117 | +0.36 | -0.3 | +1.84 % | +0.47 % | -0.42 | +0.83 |
| 2028 | -0.43 % | -1.34 % | -0.65 % | -1.15 % | -0.99 % | -133 | +0.40 | -0.2 | +1.84 % | +0.14 % | -0.58 | +2.17 |
| 2030 | -0.32 % | -1.43 % | -0.59 % | -1.10 % | -0.88 % | -119 | +0.36 | -0.1 | +1.67 % | -0.23 % | -0.66 | +3.67 |

### Salaires +2 % (choc ponctuel en 2024)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | -0.11 % | +0.16 % | -0.00 % | -0.65 % | -0.14 % | -5 | +0.02 | -0.3 | +1.43 % | +2.59 % | +0.37 | -2.49 |
| 2026 | +0.00 % | +0.52 % | +0.16 % | -0.60 % | +0.18 % | -21 | +0.06 | -0.3 | +1.31 % | +2.38 % | +0.19 | -2.73 |
| 2028 | +0.03 % | +0.50 % | +0.13 % | -0.55 % | +0.24 % | -33 | +0.10 | -0.2 | +1.22 % | +2.18 % | +0.18 | -2.87 |
| 2030 | +0.06 % | +0.47 % | +0.12 % | -0.52 % | +0.26 % | -29 | +0.09 | -0.2 | +1.14 % | +2.00 % | +0.19 | -3.03 |

### Taux d'IS de 25,8 % à 20 % (dès 2024)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +0.05 % | +0.02 % | +0.38 % | +0.01 % | +0.13 % | +5 | -0.02 | +0.0 | -0.01 % | -0.00 % | -0.42 | +0.39 |
| 2026 | +0.13 % | +0.07 % | +1.18 % | +0.01 % | +0.33 % | +22 | -0.07 | -0.2 | -0.00 % | +0.03 % | -0.41 | +1.09 |
| 2028 | +0.18 % | +0.11 % | +1.88 % | -0.00 % | +0.48 % | +38 | -0.12 | -0.7 | +0.04 % | +0.12 % | -0.39 | +1.70 |
| 2030 | +0.21 % | +0.16 % | +2.46 % | -0.01 % | +0.58 % | +49 | -0.15 | -1.3 | +0.10 % | +0.23 % | -0.39 | +2.27 |

### Réindustrialisation, borne haute : parts importées −10 % immédiatement (≈ 38 Md€ sur 380 Md€ d'importations de ces produits en 2022), sans investissement ni surcoût — chimie, pharmacie, métallurgie, produits métalliques, électronique, équipements électriques, machines, automobile

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +1.14 % | +0.48 % | +1.13 % | +0.03 % | -1.98 % | +154 | -0.47 | +3.8 | +0.08 % | +0.28 % | +0.33 | -1.77 |
| 2026 | +0.87 % | +0.62 % | +0.84 % | -0.35 % | -2.31 % | +174 | -0.53 | +2.6 | +0.55 % | +0.96 % | +0.42 | -3.05 |
| 2028 | +0.64 % | +0.69 % | +0.71 % | -0.62 % | -2.41 % | +143 | -0.43 | +1.8 | +0.92 % | +1.57 % | +0.46 | -4.27 |
| 2030 | +0.32 % | +0.68 % | +0.48 % | -0.79 % | -2.16 % | +82 | -0.25 | +0.9 | +1.18 % | +2.00 % | +0.45 | -5.17 |

### Réindustrialisation, mêmes produits, −10 % atteint en 5 ans (dès 2024), avec investissement de capacité et surcoût de 10 % de la VA produite en France

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +0.14 % | +0.06 % | +0.74 % | +0.02 % | +0.17 % | +14 | -0.04 | +0.1 | -0.03 % | -0.01 % | +0.02 | -0.12 |
| 2026 | +0.38 % | +0.16 % | +1.01 % | +0.07 % | -0.18 % | +46 | -0.14 | -0.3 | -0.01 % | +0.06 % | +0.08 | -0.46 |
| 2028 | +0.79 % | +0.36 % | +1.75 % | +0.06 % | -0.84 % | +114 | -0.35 | -0.2 | +0.10 % | +0.30 % | +0.23 | -1.42 |
| 2030 | +0.85 % | +0.50 % | +1.47 % | -0.06 % | -1.48 % | +146 | -0.44 | -0.6 | +0.36 % | +0.72 % | +0.33 | -2.52 |

### Consommation publique +1 % du PIB en volume (dès 2024)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +1.26 % | +0.67 % | +0.56 % | +0.08 % | +0.81 % | +257 | -0.79 | +0.2 | -0.14 % | -0.04 % | -0.42 | -0.74 |
| 2026 | +0.77 % | +0.61 % | +0.28 % | -0.20 % | -0.06 % | +230 | -0.70 | -0.0 | +0.44 % | +0.79 % | -0.36 | -0.41 |
| 2028 | +0.58 % | +0.68 % | +0.18 % | -0.37 % | -0.30 % | +188 | -0.57 | -0.2 | +0.80 % | +1.40 % | -0.37 | -0.09 |
| 2030 | +0.46 % | +0.72 % | +0.13 % | -0.48 % | -0.44 % | +140 | -0.42 | -0.3 | +1.05 % | +1.84 % | -0.41 | +0.37 |

Durée : 21 s.

