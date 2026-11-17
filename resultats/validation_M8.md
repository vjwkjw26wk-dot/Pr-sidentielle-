# Validation du modèle bouclé M8 (version 0.1)

Généré par `tests/validation_M8.py`.

## 1. Simulations rétrospectives du modèle complet

Toutes les équations sont bouclées ; seules les variables exogènes sont observées. Les mesures de politique publique ne sont pas introduites une à une : les recettes suivent les assiettes à taux apparents constants, sauf l'impôt sur les sociétés (taux normal) ; les dépenses publiques hors consommation, prestations et intérêts sont prises observées en part du PIB. La dette évolue avec le solde seulement (ajustements stock-flux nuls).

### Base 2014, simulation 2015-2019 (coefficients estimés sur 1997-2014)

| Variable | Croissance annuelle moyenne observée | Simulée | Erreur sur le niveau en 2019 |
|---|---|---|---|
| PIB en volume | +1.5 % | +1.5 % | -0.3 % |
| Consommation des ménages | +1.4 % | +1.7 % | +1.4 % |
| Investissement total | +2.9 % | +2.9 % | -0.2 % |
| Exportations | +3.4 % | +4.0 % | +3.2 % |
| Importations | +3.8 % | +4.8 % | +5.0 % |
| Emploi total | +0.9 % | +0.8 % | -0.4 % |
| Prix à la consommation | +0.8 % | +0.8 % | +0.2 % |
| Salaire moyen par tête (marchand) | +1.0 % | +2.1 % | +5.2 % |
| Revenu disponible brut (valeur) | +2.3 % | +2.4 % | +0.1 % |
| Taux de chômage en 2019 | 8.2 % | 8.5 % | +0.4 point |
| Solde public en 2019 (% du PIB) | -2.4 | -2.4 | -0.0 point |
| Dette publique en 2019 (% du PIB) | 98.2 | 100.1 | +1.9 points |

### Base 2022, simulation 2023-2024 (coefficients estimés sur 1997-2019)

| Variable | Croissance annuelle moyenne observée | Simulée | Erreur sur le niveau en 2024 |
|---|---|---|---|
| PIB en volume | +1.6 % | -0.3 % | -3.6 % |
| Consommation des ménages | +0.9 % | +0.2 % | -1.4 % |
| Investissement total | +0.2 % | -1.7 % | -3.8 % |
| Exportations | +2.8 % | -2.6 % | -10.3 % |
| Importations | -0.4 % | -1.7 % | -2.5 % |
| Emploi total | +0.9 % | +0.6 % | -0.6 % |
| Prix à la consommation | +4.6 % | +3.1 % | -2.8 % |
| Salaire moyen par tête (marchand) | +3.8 % | +2.4 % | -2.8 % |
| Revenu disponible brut (valeur) | +6.5 % | +2.2 % | -7.9 % |
| Taux de chômage en 2024 | 7.2 % | 7.7 % | +0.6 point |
| Solde public en 2024 (% du PIB) | -5.8 | -4.1 | +1.7 point |
| Dette publique en 2024 (% du PIB) | 112.6 | 114.6 | +2.0 points |

## 2. Variantes (écarts au compte central, base 2022, 2023-2030)

Compte central conventionnel, et non une prévision (`exogenes_projection`). Écarts en % (volumes, prix) ou en points.

### Prix de l'énergie importée +20 % (dès 2024 ; ≈ +34 Md€ sur la facture de 2022, 169 Md€)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | -0.24 % | -0.75 % | -0.07 % | -0.61 % | -0.91 % | -42 | +0.13 | +1.07 % | +0.41 % | -0.04 | -0.11 |
| 2026 | -0.30 % | -1.11 % | -0.07 % | -1.09 % | -1.62 % | -87 | +0.27 | +1.88 % | +0.56 % | -0.34 | +0.40 |
| 2028 | -0.28 % | -1.26 % | -0.04 % | -1.16 % | -1.84 % | -108 | +0.33 | +1.94 % | +0.34 % | -0.47 | +1.46 |
| 2030 | -0.24 % | -1.30 % | -0.02 % | -1.13 % | -1.90 % | -105 | +0.32 | +1.80 % | +0.03 % | -0.53 | +2.67 |

### Salaires +2 % (choc ponctuel en 2024)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | -0.14 % | +0.12 % | -0.08 % | -0.67 % | -0.18 % | -8 | +0.03 | +1.45 % | +2.60 % | +0.36 | -2.45 |
| 2026 | -0.08 % | +0.40 % | -0.08 % | -0.62 % | +0.05 % | -36 | +0.11 | +1.33 % | +2.37 % | +0.15 | -2.52 |
| 2028 | -0.08 % | +0.35 % | -0.08 % | -0.56 % | +0.05 % | -60 | +0.18 | +1.21 % | +2.11 % | +0.13 | -2.45 |
| 2030 | -0.08 % | +0.32 % | -0.07 % | -0.51 % | +0.04 % | -64 | +0.19 | +1.09 % | +1.85 % | +0.12 | -2.36 |

### Taux d'IS de 25,8 % à 20 % (dès 2024)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +0.05 % | +0.03 % | +0.37 % | +0.01 % | +0.13 % | +6 | -0.02 | -0.01 % | -0.00 % | -0.43 | +0.40 |
| 2026 | +0.16 % | +0.11 % | +1.15 % | +0.00 % | +0.37 % | +28 | -0.08 | -0.00 % | +0.03 % | -0.40 | +1.05 |
| 2028 | +0.26 % | +0.20 % | +1.84 % | -0.03 % | +0.58 % | +55 | -0.17 | +0.06 % | +0.15 % | -0.37 | +1.53 |
| 2030 | +0.32 % | +0.29 % | +2.41 % | -0.08 % | +0.75 % | +80 | -0.24 | +0.17 % | +0.34 % | -0.33 | +1.84 |

### Réindustrialisation, borne haute : parts importées −10 % immédiatement (≈ 38 Md€ sur 380 Md€ d'importations de ces produits en 2022), sans investissement ni surcoût — chimie, pharmacie, métallurgie, produits métalliques, électronique, équipements électriques, machines, automobile

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +1.45 % | +0.82 % | +1.03 % | +0.20 % | -1.65 % | +198 | -0.61 | -0.01 % | +0.26 % | +0.37 | -1.89 |
| 2026 | +1.45 % | +1.09 % | +0.86 % | -0.14 % | -1.67 % | +289 | -0.88 | +0.53 % | +1.10 % | +0.54 | -3.68 |
| 2028 | +1.43 % | +1.25 % | +0.80 % | -0.45 % | -1.67 % | +318 | -0.97 | +1.13 % | +2.09 % | +0.67 | -5.68 |
| 2030 | +1.18 % | +1.29 % | +0.63 % | -0.78 % | -1.43 % | +295 | -0.89 | +1.72 % | +3.06 % | +0.74 | -7.57 |

### Réindustrialisation, mêmes produits, −10 % atteint en 5 ans (dès 2024), avec investissement de capacité et surcoût de 10 % de la VA produite en France

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +0.41 % | +0.20 % | +0.86 % | +0.08 % | -0.16 % | +38 | -0.12 | -0.07 % | -0.01 % | +0.06 | -0.34 |
| 2026 | +1.05 % | +0.62 % | +1.55 % | +0.09 % | -0.74 % | +151 | -0.46 | +0.03 % | +0.25 % | +0.28 | -1.53 |
| 2028 | +1.69 % | +1.13 % | +2.21 % | -0.06 % | -1.32 % | +291 | -0.88 | +0.39 % | +0.92 % | +0.55 | -3.61 |
| 2030 | +1.34 % | +1.21 % | +1.42 % | -0.49 % | -1.21 % | +322 | -0.97 | +1.06 % | +1.96 % | +0.67 | -5.56 |

### Consommation publique +1 % du PIB en volume (dès 2024)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +1.28 % | +0.85 % | +0.24 % | +0.08 % | +0.78 % | +265 | -0.81 | -0.14 % | -0.04 % | -0.39 | -0.77 |
| 2026 | +1.23 % | +0.87 % | +0.24 % | -0.19 % | +0.66 % | +323 | -0.99 | +0.44 % | +0.89 % | -0.25 | -1.07 |
| 2028 | +1.17 % | +0.96 % | +0.16 % | -0.47 % | +0.62 % | +335 | -1.02 | +1.02 % | +1.87 % | -0.20 | -1.49 |
| 2030 | +1.10 % | +1.05 % | +0.12 % | -0.72 % | +0.60 % | +320 | -0.97 | +1.56 % | +2.80 % | -0.16 | -1.95 |

Durée : 19 s.

