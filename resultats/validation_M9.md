# Validation de M9 — activité des seniors et retraites (version 0.1)

Généré par `tests/validation_M9.py`.

## 1. Taux d'activité par âge (enquête Emploi) : observé / simulé, en %

Paramètres estimés sur 2003-2019 ; 2020-2025 hors échantillon. femmes : sorties précoces e0 = 0.70, tendance -1.6 pt/an, activité relative à l'AOD s = 1.26, décroissance k = 0.30 ; erreur quadratique moyenne 1.0 pt ; hommes : sorties précoces e0 = 0.73, tendance -1.4 pt/an, activité relative à l'AOD s = 1.26, décroissance k = 0.24 ; erreur quadratique moyenne 1.1 pt.

| Sexe | Âge | 2005 | 2010 | 2015 | 2019 | 2021 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|
| Femmes | 55-59 | 54 / 54 | 61 / 61 | 71 / 72 | 74 / 74 | 78 / 78 | 79 / 80 | 79 / 81 | 80 / 82 |
| Femmes | 60-64 | 14 / 13 | 17 / 19 | 29 / 27 | 34 / 36 | 37 / 40 | 42 / 43 | 45 / 46 | 46 / 48 |
| Femmes | 65-69 | 2 / 3 | 3 / 4 | 5 / 5 | 6 / 7 | 8 / 9 | 10 / 11 | 10 / 12 | 10 / 12 |
| Femmes | 70-74 | 1 / 1 | 1 / 1 | 2 / 1 | 2 / 1 | 2 / 1 | 2 / 2 | 2 / 2 | 3 / 2 |
| Hommes | 55-59 | 62 / 63 | 69 / 69 | 78 / 80 | 81 / 80 | 82 / 84 | 83 / 84 | 85 / 85 | 86 / 86 |
| Hommes | 60-64 | 15 / 15 | 20 / 21 | 30 / 29 | 36 / 37 | 39 / 41 | 42 / 43 | 46 / 46 | 48 / 48 |
| Hommes | 65-69 | 3 / 4 | 5 / 6 | 8 / 8 | 9 / 10 | 10 / 12 | 12 / 14 | 13 / 15 | 13 / 16 |
| Hommes | 70-74 | 2 / 1 | 2 / 2 | 3 / 2 | 4 / 3 | 3 / 3 | 4 / 3 | 4 / 3 | 4 / 4 |

Part des actifs supplémentaires de 60-64 ans en emploi (Δ taux d'emploi / Δ taux d'activité, 2010-2019) : 0.89.

## 2. Retraités de droit direct et masse des pensions (calage en 2015)

| Année | Retraités observés (M) | Simulés | Masse observée (Md€) | Simulée | Écart |
|---|---|---|---|---|---|
| 2008 | 14.53 | 14.81 | 215 | 215 | +0.0 % |
| 2010 | 15.19 | 15.32 | 234 | 233 | -0.3 % |
| 2012 | 15.45 | 15.42 | 253 | 247 | -2.3 % |
| 2014 | 15.93 | 15.86 | 268 | 266 | -0.8 % |
| 2016 | 16.23 | 15.94 | 278 | 272 | -2.1 % |
| 2018 | 16.44 | 16.38 | 291 | 289 | -0.7 % |
| 2020 | 16.97 | 16.84 | 305 | 310 | +1.6 % |
| 2022 | 17.04 | 17.16 | 324 | 329 | +1.3 % |
| 2024 | 17.36 | 17.62 | 364 | 380 | +4.4 % |

Sources : Eurostat `spr_pns_ben` (OLD_TOT, y compris les retraités résidant à l'étranger), `spr_exp_pens` (OLD) ; 2024 provisoire.

## 3. Variantes de règle de retraite dans le modèle bouclé (écarts à la législation actuelle)

Compte central : législation actuelle (LFSS 2026), population active issue de M9. Les pensions des variantes sont calculées avec les prix et salaires simulés par M8 dans le compte central.

PIB, modèle de demande : M8 tel quel ; les seniors maintenus en emploi perçoivent un salaire (revenu, cotisations) mais la production reste déterminée par la demande. PIB, borne offre : à long terme, la production suit l'emploi (capital ajusté, productivité moyenne) : + Δemploi / emploi ; le solde public gagne alors le taux de prélèvements apparent sur ce surcroît de PIB. Fermeture d'offre (ρ = 0,3, amortissement 1,0) : M8 avec résorption progressive de l'écart de chômage au chômage structurel (décision A12) ; les actifs supplémentaires sont absorbés par la hausse de la demande et de la production, et non plus ajoutés directement à l'emploi.

### Retour à 62 ans

| Année | AOD (génération ayant 63 ans) | Actifs (milliers) | Emploi : demande / fermeture d'offre | Chômage (pt) : demande / fermeture | PIB : demande / fermeture / borne offre | Pensions (Md€) | Solde public (pt de PIB) : demande / fermeture / borne offre | Dette (pt de PIB) : demande / fermeture |
|---|---|---|---|---|---|---|---|---|
| 2027 | 62.00 (1964) | -414 | -332 / -181 | -0.16 / -0.61 | +0.15 % / -0.65 % / -1.01 % | +17.8 | -0.80 / -0.57 / -1.41 | +2.10 / +1.30 |
| 2030 | 62.00 (1967) | -738 | -609 / -425 | -0.24 / -0.79 | +0.11 % / -1.66 % / -1.92 % | +24.0 | -1.21 / -0.88 / -2.30 | +4.84 / +3.63 |
| 2035 | 62.00 (1972) | -983 | -792 / -754 | -0.42 / -0.49 | +0.25 % / -2.35 % / -2.39 % | +44.8 | -1.88 / -1.67 / -3.31 | +11.21 / +9.53 |
| 2040 | 62.00 (1977) | -1078 | -906 / -919 | -0.41 / -0.27 | +0.12 % / -2.66 % / -2.72 % | +48.7 | -2.06 / -1.98 / -3.63 | +17.93 / +17.19 |

### Loi de 2023 sans suspension

| Année | AOD (génération ayant 63 ans) | Actifs (milliers) | Emploi : demande / fermeture d'offre | Chômage (pt) : demande / fermeture | PIB : demande / fermeture / borne offre | Pensions (Md€) | Solde public (pt de PIB) : demande / fermeture / borne offre | Dette (pt de PIB) : demande / fermeture |
|---|---|---|---|---|---|---|---|---|
| 2027 | 63.00 (1964) | +72 | +65 / +37 | +0.00 / +0.09 | +0.01 % / +0.17 % / +0.21 % | -1.1 | +0.09 / +0.05 / +0.20 | -0.28 / -0.15 |
| 2030 | 63.75 (1967) | +82 | +75 / +63 | +0.00 / +0.04 | +0.01 % / +0.22 % / +0.24 % | -1.5 | +0.12 / +0.09 / +0.24 | -0.60 / -0.36 |
| 2035 | 64.00 (1972) | +32 | +24 / +36 | +0.02 / -0.02 | +0.00 % / +0.07 % / +0.09 % | -0.5 | +0.05 / +0.06 / +0.10 | -0.94 / -0.79 |
| 2040 | 64.00 (1977) | +7 | +9 / +18 | -0.01 / -0.03 | +0.01 % / +0.03 % / +0.03 % | -0.0 | +0.03 / +0.04 / +0.04 | -1.01 / -1.00 |

### 65 ans (+3 mois par génération dès 1964)

| Année | AOD (génération ayant 63 ans) | Actifs (milliers) | Emploi : demande / fermeture d'offre | Chômage (pt) : demande / fermeture | PIB : demande / fermeture / borne offre | Pensions (Md€) | Solde public (pt de PIB) : demande / fermeture / borne offre | Dette (pt de PIB) : demande / fermeture |
|---|---|---|---|---|---|---|---|---|
| 2027 | 63.00 (1964) | +72 | +65 / +37 | +0.00 / +0.09 | +0.01 % / +0.17 % / +0.21 % | -1.1 | +0.09 / +0.05 / +0.20 | -0.28 / -0.15 |
| 2030 | 63.75 (1967) | +126 | +114 / +66 | +0.01 / +0.15 | +0.02 % / +0.25 % / +0.36 % | -2.2 | +0.17 / +0.09 / +0.36 | -0.67 / -0.36 |
| 2035 | 65.00 (1972) | +367 | +326 / +202 | +0.06 / +0.41 | +0.04 % / +0.78 % / +1.03 % | -6.8 | +0.49 / +0.29 / +1.02 | -2.29 / -1.49 |
| 2040 | 65.00 (1977) | +560 | +516 / +420 | +0.07 / +0.30 | +0.09 % / +1.35 % / +1.56 % | -12.2 | +0.81 / +0.58 / +1.63 | -5.21 / -3.52 |

Durée : 60 s.

