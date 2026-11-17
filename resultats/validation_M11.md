# Validation de M11 — couplage France-zone euro (version 0.1)

Généré par `tests/validation_M11.py`.

## 1. Règle de taux de la BCE (Euribor 3 mois, estimée 1999-2019)

| Paramètre | Valeur | t |
|---|---|---|
| lissage ρ | 0.73 | 6.2 |
| réponse de court terme à l'inflation | 0.39 | 2.2 |
| réponse de court terme à l'écart de production | 0.30 | 3.3 |
| réponse de long terme à l'inflation | 1.44 |  |
| transmission au taux long français β | 0.38 | 3.7 |

Simulation dynamique (le taux simulé de l'année précédente alimente l'année suivante), inflation et écart de production observés :

| Année | Euribor observé | Simulé |
|---|---|---|
| 2003 | 2.33 | 2.21 |
| 2008 | 4.64 | 4.19 |
| 2012 | 0.57 | 1.33 |
| 2016 | -0.26 | -1.18 |
| 2019 | -0.36 | 1.13 |
| 2021 | -0.55 | -0.34 |
| 2022 | 0.35 | 3.14 |
| 2023 | 3.43 | 4.17 |
| 2024 | 3.57 | 3.67 |
| 2025 | 2.18 | 3.10 |

Le plancher effectif des taux (2015-2021, taux négatifs et achats d'actifs) n'est pas représenté ; la remontée de 2022-2023 est reproduite avec retard.

## 2. Variantes (écarts au compte central, base 2022)

### Dépense publique française +1 pt de PIB, sans rétroaction européenne

| Année | PIB | Inflation (pt, cumul prix) | Taux BCE (pt) | Taux long FR (pt) | Demande des partenaires | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|
| 2024 | +1.40 % | -0.17 | +0.00 | +0.00 | +0.00 % | -0.34 | -0.92 |
| 2026 | +0.77 % | +0.49 | +0.00 | +0.00 | +0.00 % | -0.32 | -0.65 |
| 2030 | +0.39 % | +1.09 | +0.00 | +0.00 | +0.00 % | -0.44 | +0.33 |
| 2035 | +0.31 % | +1.31 | +0.00 | +0.00 | +0.00 % | -0.53 | +2.32 |

### … avec BCE et demande des partenaires (sans prime de risque)

| Année | PIB | Inflation (pt, cumul prix) | Taux BCE (pt) | Taux long FR (pt) | Demande des partenaires | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|
| 2024 | +1.40 % | -0.17 | +0.08 | +0.03 | +0.09 % | -0.34 | -0.92 |
| 2026 | +0.76 % | +0.49 | +0.20 | +0.08 | -0.01 % | -0.34 | -0.60 |
| 2030 | +0.37 % | +1.08 | +0.16 | +0.06 | -0.06 % | -0.51 | +0.62 |
| 2035 | +0.30 % | +1.28 | +0.05 | +0.02 | -0.08 % | -0.61 | +2.97 |

### … avec en plus la prime de risque (3 pb par point de dette)

| Année | PIB | Inflation (pt, cumul prix) | Taux BCE (pt) | Taux long FR (pt) | Demande des partenaires | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|
| 2024 | +1.41 % | -0.17 | +0.08 | +0.00 | +0.09 % | -0.33 | -0.93 |
| 2026 | +0.76 % | +0.49 | +0.20 | +0.06 | -0.01 % | -0.33 | -0.62 |
| 2030 | +0.36 % | +1.08 | +0.16 | +0.08 | -0.06 % | -0.50 | +0.57 |
| 2035 | +0.28 % | +1.28 | +0.04 | +0.11 | -0.08 % | -0.67 | +3.08 |

### Relance coordonnée dans toute la zone euro (+1 pt de PIB partout)

| Année | PIB | Inflation (pt, cumul prix) | Taux BCE (pt) | Taux long FR (pt) | Demande des partenaires | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|
| 2024 | +1.60 % | -0.23 | +0.10 | +0.01 | +0.18 % | -0.32 | -1.08 |
| 2026 | +0.85 % | +0.54 | +0.25 | +0.07 | +0.04 % | -0.39 | -0.75 |
| 2030 | +0.25 % | +1.20 | +0.18 | +0.11 | -0.06 % | -0.83 | +1.45 |
| 2035 | +0.17 % | +1.28 | +0.01 | +0.19 | -0.10 % | -1.23 | +6.35 |

### Transferts aux ménages +1 pt de PIB, avec rétroactions et prime de risque

| Année | PIB | Inflation (pt, cumul prix) | Taux BCE (pt) | Taux long FR (pt) | Demande des partenaires | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|
| 2024 | +0.54 % | -0.12 | +0.03 | +0.02 | +0.06 % | -0.74 | +0.32 |
| 2026 | +0.40 % | +0.14 | +0.09 | +0.08 | +0.03 % | -0.70 | +1.43 |
| 2030 | +0.18 % | +0.49 | +0.11 | +0.16 | +0.00 % | -0.87 | +4.04 |
| 2035 | +0.07 % | +0.64 | +0.05 | +0.28 | -0.02 % | -1.22 | +8.62 |

Durée : 85 s.

