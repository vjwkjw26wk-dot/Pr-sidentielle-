# Validation du modèle bouclé M8 (version 0.1)

Généré par `tests/validation_M8.py`.

## 1. Simulations rétrospectives du modèle complet

Toutes les équations sont bouclées ; seules les variables exogènes sont observées. Les mesures de politique publique ne sont pas introduites une à une : les recettes suivent les assiettes à taux apparents constants, sauf l'impôt sur les sociétés (taux normal) ; les dépenses publiques hors consommation, prestations et intérêts sont prises observées en part du PIB. La dette évolue avec le solde seulement (ajustements stock-flux nuls).

### Base 2014, simulation 2015-2019 (coefficients estimés sur 1997-2014)

| Variable | Croissance annuelle moyenne observée | Simulée | Erreur sur le niveau en 2019 |
|---|---|---|---|
| PIB en volume | +1.5 % | +1.5 % | -0.4 % |
| Consommation des ménages | +1.4 % | +1.7 % | +1.2 % |
| Investissement total | +2.9 % | +2.9 % | -0.2 % |
| Exportations | +3.4 % | +3.9 % | +2.8 % |
| Importations | +3.8 % | +4.8 % | +4.6 % |
| Emploi total | +0.9 % | +0.8 % | -0.5 % |
| Prix à la consommation | +0.8 % | +0.9 % | +0.7 % |
| Salaire moyen par tête (marchand) | +1.0 % | +2.1 % | +5.5 % |
| Revenu disponible brut (valeur) | +2.3 % | +2.4 % | +0.5 % |
| Taux de chômage en 2019 | 8.2 % | 8.6 % | +0.4 point |
| Solde public en 2019 (% du PIB) | -2.4 | -2.6 | -0.2 point |
| Dette publique en 2019 (% du PIB) | 98.2 | 99.9 | +1.8 points |

### Base 2022, simulation 2023-2024 (coefficients estimés sur 1997-2019)

| Variable | Croissance annuelle moyenne observée | Simulée | Erreur sur le niveau en 2024 |
|---|---|---|---|
| PIB en volume | +1.6 % | +0.1 % | -2.8 % |
| Consommation des ménages | +0.9 % | +1.6 % | +1.4 % |
| Investissement total | +0.2 % | -1.6 % | -3.6 % |
| Exportations | +2.8 % | -1.1 % | -7.5 % |
| Importations | -0.4 % | +0.5 % | +1.8 % |
| Emploi total | +0.9 % | +0.9 % | +0.0 % |
| Prix à la consommation | +4.6 % | +0.8 % | -7.2 % |
| Salaire moyen par tête (marchand) | +3.8 % | +1.5 % | -4.3 % |
| Revenu disponible brut (valeur) | +6.5 % | +1.3 % | -9.4 % |
| Taux de chômage en 2024 | 7.2 % | 7.1 % | -0.0 point |
| Solde public en 2024 (% du PIB) | -5.8 | -3.5 | +2.3 point |
| Dette publique en 2024 (% du PIB) | 112.6 | 114.5 | +1.9 points |

## 2. Variantes (écarts au compte central, base 2022)

Compte central conventionnel, et non une prévision (`exogenes_projection`). Écarts en % (volumes, prix) ou en points.

### Énergie importée +50 % (dès 2024)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | -0.94 % | -2.96 % | -0.25 % | -2.38 % | -3.58 % | -168 | +0.52 | +4.32 % | +1.67 % | -0.13 | -0.46 |
| 2026 | -0.50 % | -2.17 % | -0.07 % | -2.14 % | -3.30 % | -184 | +0.56 | +3.75 % | +0.95 % | -0.78 | +1.38 |
| 2028 | -0.42 % | -2.26 % | -0.04 % | -2.00 % | -3.35 % | -189 | +0.57 | +3.33 % | +0.33 % | -0.86 | +3.44 |

### Salaires +2 % (choc ponctuel en 2024)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | -0.15 % | +0.09 % | -0.09 % | -0.70 % | -0.21 % | -10 | +0.03 | +1.50 % | +2.61 % | +0.35 | -2.45 |
| 2026 | -0.09 % | +0.37 % | -0.09 % | -0.65 % | +0.02 % | -40 | +0.12 | +1.38 % | +2.38 % | +0.13 | -2.48 |
| 2028 | -0.10 % | +0.32 % | -0.09 % | -0.59 % | +0.02 % | -66 | +0.20 | +1.25 % | +2.11 % | +0.11 | -2.35 |

### Taux d'IS de 25,8 % à 20 % (dès 2024)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +0.05 % | +0.03 % | +0.37 % | +0.01 % | +0.12 % | +6 | -0.02 | -0.01 % | -0.00 % | -0.44 | +0.40 |
| 2026 | +0.16 % | +0.11 % | +1.15 % | +0.00 % | +0.36 % | +27 | -0.08 | -0.00 % | +0.03 % | -0.41 | +1.07 |
| 2028 | +0.25 % | +0.19 % | +1.83 % | -0.03 % | +0.57 % | +53 | -0.16 | +0.06 % | +0.15 % | -0.37 | +1.56 |

### Réindustrialisation : parts importées −20 % (chimie, pharmacie, métallurgie, électronique, équipements, automobile)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +3.05 % | +1.72 % | +2.17 % | +0.42 % | -3.33 % | +415 | -1.27 | -0.01 % | +0.53 % | +0.75 | -3.89 |
| 2026 | +3.05 % | +2.29 % | +1.81 % | -0.31 % | -3.33 % | +611 | -1.87 | +1.17 % | +2.34 % | +1.08 | -7.49 |
| 2028 | +2.76 % | +2.52 % | +1.51 % | -1.05 % | -3.13 % | +648 | -1.97 | +2.51 % | +4.46 % | +1.28 | -11.19 |

### Consommation publique +1 % du PIB en volume (dès 2024)

| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2024 | +1.27 % | +0.86 % | +0.24 % | +0.09 % | +0.78 % | +265 | -0.82 | -0.15 % | -0.04 % | -0.38 | -0.78 |
| 2026 | +1.22 % | +0.87 % | +0.24 % | -0.20 % | +0.65 % | +323 | -0.99 | +0.46 % | +0.90 % | -0.25 | -1.08 |
| 2028 | +1.15 % | +0.94 % | +0.16 % | -0.50 % | +0.59 % | +333 | -1.01 | +1.07 % | +1.89 % | -0.20 | -1.46 |

Durée : 14 s.

