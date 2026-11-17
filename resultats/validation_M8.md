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
| 2024 | -0.26 % | -0.79 % | -0.07 % | -0.61 % | -0.93 % | -45 | +0.14 | +0.1 | +1.07 % | +0.41 % | -0.04 | -0.09 |
| 2026 | -0.20 % | -1.08 % | -0.04 % | -1.10 % | -1.47 % | -70 | +0.21 | +0.4 | +1.87 % | +0.57 % | -0.33 | +0.31 |
| 2028 | -0.11 % | -1.16 % | +0.02 % | -1.20 % | -1.58 % | -68 | +0.21 | +0.5 | +1.98 % | +0.43 % | -0.43 | +1.15 |
| 2030 | -0.03 % | -1.15 % | +0.05 % | -1.22 % | -1.59 % | -48 | +0.15 | +0.4 | +1.93 % | +0.27 % | -0.47 | +2.06 |

### Salaires +2 % (choc ponctuel en 2024)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | -0.13 % | +0.12 % | -0.08 % | -0.66 % | -0.17 % | -8 | +0.02 | -0.3 | +1.44 % | +2.59 % | +0.36 | -2.45 |
| 2026 | -0.04 % | +0.44 % | -0.07 % | -0.60 % | +0.11 % | -30 | +0.09 | -0.3 | +1.31 % | +2.36 % | +0.16 | -2.59 |
| 2028 | +0.02 % | +0.45 % | -0.04 % | -0.54 % | +0.20 % | -39 | +0.12 | -0.2 | +1.20 % | +2.13 % | +0.16 | -2.68 |
| 2030 | +0.06 % | +0.46 % | -0.02 % | -0.50 % | +0.25 % | -30 | +0.09 | -0.2 | +1.12 % | +1.94 % | +0.18 | -2.82 |

### Taux d'IS de 25,8 % à 20 % (dès 2024)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +0.05 % | +0.03 % | +0.37 % | +0.01 % | +0.13 % | +6 | -0.02 | +0.0 | -0.01 % | -0.00 % | -0.43 | +0.39 |
| 2026 | +0.14 % | +0.10 % | +1.14 % | +0.01 % | +0.34 % | +24 | -0.07 | -0.2 | -0.00 % | +0.03 % | -0.40 | +1.07 |
| 2028 | +0.19 % | +0.16 % | +1.80 % | -0.00 % | +0.48 % | +41 | -0.12 | -0.7 | +0.05 % | +0.12 % | -0.38 | +1.66 |
| 2030 | +0.21 % | +0.19 % | +2.36 % | -0.01 % | +0.57 % | +50 | -0.15 | -1.3 | +0.11 % | +0.25 % | -0.38 | +2.21 |

### Réindustrialisation, borne haute : parts importées −10 % immédiatement (≈ 38 Md€ sur 380 Md€ d'importations de ces produits en 2022), sans investissement ni surcoût — chimie, pharmacie, métallurgie, produits métalliques, électronique, équipements électriques, machines, automobile

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +1.18 % | +0.71 % | +0.92 % | +0.02 % | -1.95 % | +164 | -0.50 | +3.8 | +0.08 % | +0.29 % | +0.36 | -1.86 |
| 2026 | +0.84 % | +0.73 % | +0.58 % | -0.37 % | -2.35 % | +176 | -0.54 | +2.5 | +0.58 % | +1.00 % | +0.43 | -3.13 |
| 2028 | +0.63 % | +0.69 % | +0.47 % | -0.62 % | -2.57 % | +137 | -0.42 | +1.9 | +0.95 % | +1.60 % | +0.45 | -4.30 |
| 2030 | +0.37 % | +0.60 % | +0.33 % | -0.80 % | -2.44 % | +78 | -0.24 | +1.1 | +1.21 % | +2.03 % | +0.44 | -5.21 |

### Réindustrialisation, mêmes produits, −10 % atteint en 5 ans (dès 2024), avec investissement de capacité et surcoût de 10 % de la VA produite en France

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +0.41 % | +0.22 % | +0.86 % | +0.07 % | -0.16 % | +38 | -0.12 | +1.0 | -0.06 % | -0.01 % | +0.07 | -0.36 |
| 2026 | +0.87 % | +0.53 % | +1.52 % | +0.03 % | -0.94 % | +123 | -0.38 | +0.9 | +0.06 % | +0.25 % | +0.25 | -1.41 |
| 2028 | +1.25 % | +0.84 % | +2.17 % | -0.10 % | -1.82 % | +202 | -0.61 | +0.4 | +0.38 % | +0.79 % | +0.45 | -3.01 |
| 2030 | +0.71 % | +0.69 % | +1.45 % | -0.37 % | -2.01 % | +165 | -0.50 | -2.0 | +0.85 % | +1.47 % | +0.46 | -4.06 |

### Consommation publique +1 % du PIB en volume (dès 2024)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | TUC industrie (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +1.40 % | +1.17 % | +0.27 % | +0.10 % | +0.93 % | +283 | -0.87 | +0.3 | -0.17 % | -0.05 % | -0.34 | -0.92 |
| 2026 | +0.77 % | +0.79 % | +0.05 % | -0.22 % | -0.11 % | +239 | -0.73 | -0.0 | +0.49 % | +0.86 % | -0.32 | -0.65 |
| 2028 | +0.52 % | +0.66 % | -0.08 % | -0.40 % | -0.41 % | +179 | -0.54 | -0.2 | +0.87 % | +1.49 % | -0.38 | -0.26 |
| 2030 | +0.39 % | +0.61 % | -0.12 % | -0.50 % | -0.55 % | +122 | -0.37 | -0.3 | +1.09 % | +1.87 % | -0.44 | +0.33 |

Durée : 20 s.

