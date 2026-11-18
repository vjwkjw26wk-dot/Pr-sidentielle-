# Validation du modèle bouclé M8 (version 0.1)

Généré par `tests/validation_M8.py`.

## 1. Simulations rétrospectives du modèle complet

Toutes les équations sont bouclées ; seules les variables exogènes sont observées. Les mesures de politique publique ne sont pas introduites une à une : les recettes suivent les assiettes à taux apparents constants, sauf l'impôt sur les sociétés (taux normal) ; les dépenses publiques hors consommation, prestations et intérêts sont prises observées en part du PIB. La dette évolue avec le solde seulement (ajustements stock-flux nuls).

### Base 2014, simulation 2015-2019 (coefficients estimés sur 1997-2014)

| Variable | Croissance annuelle moyenne observée | Simulée | Erreur sur le niveau en 2019 |
|---|---|---|---|
| PIB en volume | +1.5 % | +1.3 % | -1.0 % |
| Consommation des ménages | +1.4 % | +1.7 % | +1.3 % |
| Investissement total | +2.9 % | +1.9 % | -4.9 % |
| Exportations | +3.4 % | +4.0 % | +2.9 % |
| Importations | +3.8 % | +4.5 % | +3.1 % |
| Emploi total | +0.9 % | +0.7 % | -0.7 % |
| Prix à la consommation | +0.8 % | +0.9 % | +0.4 % |
| Salaire moyen par tête (marchand) | +1.0 % | +2.1 % | +5.3 % |
| Revenu disponible brut (valeur) | +2.3 % | +2.5 % | +0.9 % |
| Taux de chômage en 2019 | 8.2 % | 8.8 % | +0.6 point |
| Solde public en 2019 (% du PIB) | -2.4 | -2.5 | -0.1 point |
| Dette publique en 2019 (% du PIB) | 98.2 | 100.4 | +2.2 points |
| Taux d'utilisation des capacités, industrie, en 2019 | 84.1 % | 80.9 % | -3.2 point |

### Base 2022, simulation 2023-2024 (coefficients estimés sur 1997-2019)

| Variable | Croissance annuelle moyenne observée | Simulée | Erreur sur le niveau en 2024 |
|---|---|---|---|
| PIB en volume | +1.6 % | -0.2 % | -3.5 % |
| Consommation des ménages | +0.9 % | +0.1 % | -1.5 % |
| Investissement total | +0.2 % | +0.3 % | +0.2 % |
| Exportations | +2.8 % | -2.6 % | -10.2 % |
| Importations | -0.4 % | -0.7 % | -0.6 % |
| Emploi total | +0.9 % | +0.6 % | -0.6 % |
| Prix à la consommation | +4.6 % | +3.0 % | -2.9 % |
| Salaire moyen par tête (marchand) | +3.8 % | +2.3 % | -2.8 % |
| Revenu disponible brut (valeur) | +6.5 % | +2.2 % | -7.8 % |
| Taux de chômage en 2024 | 7.2 % | 7.7 % | +0.5 point |
| Solde public en 2024 (% du PIB) | -5.8 | -4.1 | +1.6 point |
| Dette publique en 2024 (% du PIB) | 112.6 | 114.9 | +2.2 points |
| Taux d'utilisation des capacités, industrie, en 2024 | 80.5 % | 76.6 % | -3.8 point |

## 2. Variantes (écarts au compte central, base 2022, 2023-2030)

Compte central conventionnel, et non une prévision (`exogenes_projection`), avec fermeture d'offre ρ = 0,3 (amortissement 1,0) (résorption progressive de l'écart de chômage au chômage structurel, décision A12). Écarts en % (volumes, prix) ou en points.

### Prix de l'énergie importée +20 % (dès 2024 ; ≈ +34 Md€ sur la facture de 2022, 169 Md€)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | -0.43 % | -0.85 % | -0.57 % | -0.64 % | -0.89 % | -61 | +0.19 | -0.2 | +1.10 % | +0.42 % | -0.07 | +0.06 |
| 2026 | -0.51 % | -1.19 % | -0.70 % | -1.11 % | -1.08 % | -117 | +0.36 | -0.3 | +1.84 % | +0.47 % | -0.42 | +0.83 |
| 2028 | -0.43 % | -1.34 % | -0.65 % | -1.15 % | -0.99 % | -133 | +0.40 | -0.2 | +1.84 % | +0.14 % | -0.58 | +2.17 |
| 2030 | -0.32 % | -1.43 % | -0.58 % | -1.10 % | -0.88 % | -119 | +0.36 | -0.1 | +1.66 % | -0.23 % | -0.66 | +3.65 |

### Salaires +2 % (choc ponctuel en 2024)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | -0.11 % | +0.16 % | -0.00 % | -0.65 % | -0.14 % | -5 | +0.02 | -0.3 | +1.43 % | +2.59 % | +0.37 | -2.49 |
| 2026 | +0.00 % | +0.52 % | +0.16 % | -0.60 % | +0.18 % | -21 | +0.06 | -0.3 | +1.31 % | +2.38 % | +0.19 | -2.72 |
| 2028 | +0.03 % | +0.50 % | +0.13 % | -0.55 % | +0.24 % | -33 | +0.10 | -0.2 | +1.22 % | +2.18 % | +0.18 | -2.86 |
| 2030 | +0.06 % | +0.47 % | +0.11 % | -0.52 % | +0.26 % | -29 | +0.09 | -0.2 | +1.14 % | +2.00 % | +0.19 | -3.01 |

### Taux d'IS de 25,8 % à 20 % (dès 2024)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +0.03 % | +0.01 % | +0.22 % | +0.00 % | +0.07 % | +3 | -0.01 | +0.0 | -0.01 % | -0.00 % | -0.43 | +0.41 |
| 2026 | +0.06 % | +0.03 % | +0.53 % | +0.00 % | +0.15 % | +10 | -0.03 | -0.1 | +0.00 % | +0.02 % | -0.43 | +1.19 |
| 2028 | +0.07 % | +0.05 % | +0.72 % | -0.00 % | +0.18 % | +15 | -0.05 | -0.3 | +0.02 % | +0.05 % | -0.44 | +1.96 |
| 2030 | +0.07 % | +0.06 % | +0.87 % | -0.01 % | +0.21 % | +18 | -0.05 | -0.5 | +0.04 % | +0.10 % | -0.45 | +2.72 |

### Réindustrialisation, borne haute : parts importées −10 % immédiatement (≈ 38 Md€ sur 380 Md€ d'importations de ces produits en 2022), sans investissement ni surcoût — chimie, pharmacie, métallurgie, produits métalliques, électronique, équipements électriques, machines, automobile

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +1.14 % | +0.49 % | +1.13 % | +0.03 % | -1.98 % | +155 | -0.48 | +3.8 | +0.08 % | +0.28 % | +0.33 | -1.77 |
| 2026 | +0.87 % | +0.62 % | +0.85 % | -0.35 % | -2.31 % | +175 | -0.54 | +2.6 | +0.55 % | +0.96 % | +0.42 | -3.05 |
| 2028 | +0.63 % | +0.69 % | +0.71 % | -0.62 % | -2.38 % | +143 | -0.43 | +1.8 | +0.92 % | +1.58 % | +0.46 | -4.25 |
| 2030 | +0.30 % | +0.68 % | +0.46 % | -0.79 % | -2.11 % | +81 | -0.24 | +0.8 | +1.18 % | +2.00 % | +0.45 | -5.13 |

### Réindustrialisation, mêmes produits, −10 % atteint en 5 ans (dès 2024), avec investissement de capacité et surcoût de 10 % de la VA produite en France

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +0.14 % | +0.06 % | +0.74 % | +0.02 % | +0.17 % | +14 | -0.04 | +0.1 | -0.03 % | -0.01 % | +0.02 | -0.12 |
| 2026 | +0.38 % | +0.16 % | +1.01 % | +0.07 % | -0.18 % | +46 | -0.14 | -0.3 | -0.01 % | +0.06 % | +0.08 | -0.46 |
| 2028 | +0.78 % | +0.36 % | +1.73 % | +0.06 % | -0.81 % | +114 | -0.35 | -0.2 | +0.10 % | +0.30 % | +0.23 | -1.41 |
| 2030 | +0.84 % | +0.50 % | +1.45 % | -0.06 % | -1.43 % | +145 | -0.44 | -0.6 | +0.36 % | +0.72 % | +0.33 | -2.49 |

### Consommation publique +1 % du PIB en volume (dès 2024)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +1.26 % | +0.67 % | +0.56 % | +0.08 % | +0.80 % | +257 | -0.79 | +0.2 | -0.14 % | -0.04 % | -0.42 | -0.74 |
| 2026 | +0.77 % | +0.61 % | +0.28 % | -0.20 % | -0.06 % | +230 | -0.70 | -0.0 | +0.44 % | +0.79 % | -0.36 | -0.41 |
| 2028 | +0.58 % | +0.68 % | +0.18 % | -0.37 % | -0.30 % | +188 | -0.57 | -0.2 | +0.80 % | +1.40 % | -0.37 | -0.09 |
| 2030 | +0.46 % | +0.72 % | +0.12 % | -0.48 % | -0.43 % | +140 | -0.42 | -0.3 | +1.05 % | +1.84 % | -0.40 | +0.37 |

Durée : 18 s.

