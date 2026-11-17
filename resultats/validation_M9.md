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

PIB, modèle de demande : M8 tel quel ; les seniors maintenus en emploi perçoivent un salaire (revenu, cotisations) mais la production reste déterminée par la demande. PIB, borne offre : à long terme, la production suit l'emploi (capital ajusté, productivité moyenne) : + Δemploi / emploi ; le solde public gagne alors le taux de prélèvements apparent sur ce surcroît de PIB. La réalité se situe entre les deux, plus près de la borne offre à long terme.

### Retour à 62 ans

| Année | AOD (génération ayant 63 ans) | Actifs (milliers) | Emplois seniors directs | Emploi total | Chômage (pt) | PIB, modèle de demande | PIB, borne offre | Pensions (Md€) | Solde public, modèle (pt de PIB) | Solde, borne offre | Dette, modèle (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2027 | 62.00 (1964) | -414 | -361 | -332 | -0.16 | +0.15 % | -1.01 % | +17.8 | -0.80 | -1.41 | +2.10 |
| 2030 | 62.00 (1967) | -738 | -643 | -609 | -0.24 | +0.11 % | -1.92 % | +24.0 | -1.21 | -2.30 | +4.84 |
| 2035 | 62.00 (1972) | -983 | -855 | -792 | -0.42 | +0.25 % | -2.39 % | +44.8 | -1.88 | -3.31 | +11.21 |

### Loi de 2023 sans suspension

| Année | AOD (génération ayant 63 ans) | Actifs (milliers) | Emplois seniors directs | Emploi total | Chômage (pt) | PIB, modèle de demande | PIB, borne offre | Pensions (Md€) | Solde public, modèle (pt de PIB) | Solde, borne offre | Dette, modèle (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2027 | 63.00 (1964) | +72 | +62 | +65 | +0.00 | +0.01 % | +0.21 % | -1.1 | +0.09 | +0.20 | -0.28 |
| 2030 | 63.75 (1967) | +82 | +71 | +75 | +0.00 | +0.01 % | +0.24 % | -1.5 | +0.12 | +0.24 | -0.60 |
| 2035 | 64.00 (1972) | +32 | +28 | +24 | +0.02 | +0.00 % | +0.09 % | -0.5 | +0.05 | +0.10 | -0.94 |

### 65 ans (+3 mois par génération dès 1964)

| Année | AOD (génération ayant 63 ans) | Actifs (milliers) | Emplois seniors directs | Emploi total | Chômage (pt) | PIB, modèle de demande | PIB, borne offre | Pensions (Md€) | Solde public, modèle (pt de PIB) | Solde, borne offre | Dette, modèle (pt de PIB) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2027 | 63.00 (1964) | +72 | +62 | +65 | +0.00 | +0.01 % | +0.21 % | -1.1 | +0.09 | +0.20 | -0.28 |
| 2030 | 63.75 (1967) | +126 | +110 | +114 | +0.01 | +0.02 % | +0.36 % | -2.2 | +0.17 | +0.36 | -0.67 |
| 2035 | 65.00 (1972) | +367 | +319 | +326 | +0.06 | +0.04 % | +1.03 % | -6.8 | +0.49 | +1.02 | -2.29 |

Durée : 40 s.

