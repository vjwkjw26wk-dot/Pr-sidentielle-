# Validation de M1 v2 (démographie) face aux projections de population 2026 de l'Insee

Généré par `tests/validation_M1.py`. Période 2023-2070. Écarts relatifs.

## Test A — réplication des 29 scénarios publiés (27 scénarios et 2 scénarios de travail) (hypothèses de l'Insee en entrée)

| Scénario | Population totale, écart max | Population par âge 0-104 ans, écart max | Naissances | Décès | Identité |
|---|---|---|---|---|---|
| 00_central | 2.9e-05 | 7.2e-04 | 3.9e-04 | 3.8e-04 | 3.1e-08 |
| 11_fec_haute | 3.1e-05 | 7.2e-04 | 3.8e-04 | 3.8e-04 | 2.6e-08 |
| 12_fec_basse | 2.8e-05 | 7.2e-04 | 3.9e-04 | 3.8e-04 | 2.2e-08 |
| 13_ev_haute | 2.8e-05 | 3.7e-02 | 3.9e-04 | 7.2e-04 | 2.6e-08 |
| 14_ev_basse | 3.0e-05 | 5.3e-02 | 3.8e-04 | 9.7e-04 | 2.6e-08 |
| 15_smi_haut | 2.8e-05 | 7.2e-04 | 3.9e-04 | 3.9e-04 | 2.2e-08 |
| 16_smi_bas | 3.1e-05 | 7.2e-04 | 3.9e-04 | 3.8e-04 | 1.6e-08 |
| 21_population_haute | 2.8e-05 | 3.7e-02 | 3.8e-04 | 7.1e-04 | 2.5e-08 |
| 22_population_basse | 3.1e-05 | 5.3e-02 | 3.9e-04 | 9.5e-04 | 2.4e-08 |
| 23_population_agee | 2.8e-05 | 3.7e-02 | 3.9e-04 | 7.3e-04 | 3.1e-08 |
| 24_population_jeune | 2.8e-05 | 5.3e-02 | 3.9e-04 | 9.6e-04 | 3.2e-08 |
| 52_ev_constante | 3.0e-05 | 5.7e-04 | 3.9e-04 | 3.8e-04 | 2.2e-08 |
| 53_smi_nul | 3.3e-05 | 7.9e-04 | 3.9e-04 | 3.8e-04 | 2.6e-08 |
| 31_fec_centrale_ev_haute_smi_haut | 2.6e-05 | 3.7e-02 | 3.9e-04 | 7.1e-04 | 2.6e-08 |
| 32_fec_centrale_ev_haute_smi_bas | 2.9e-05 | 3.7e-02 | 3.9e-04 | 7.3e-04 | 1.7e-08 |
| 33_fec_centrale_ev_basse_smi_haut | 2.7e-05 | 5.3e-02 | 3.9e-04 | 9.6e-04 | 2.2e-08 |
| 34_fec_centrale_ev_basse_smi_bas | 3.2e-05 | 5.3e-02 | 3.9e-04 | 9.5e-04 | 1.7e-08 |
| 35_fec_haute_ev_centrale_smi_haut | 2.9e-05 | 7.2e-04 | 3.9e-04 | 3.9e-04 | 3.1e-08 |
| 36_fec_haute_ev_centrale_smi_bas | 3.2e-05 | 7.2e-04 | 3.8e-04 | 3.8e-04 | 2.3e-08 |
| 37_fec_haute_ev_haute_smi_central | 2.9e-05 | 3.7e-02 | 3.9e-04 | 7.2e-04 | 3.5e-08 |
| 38_fec_haute_ev_haute_smi_bas | 3.0e-05 | 3.7e-02 | 3.8e-04 | 7.3e-04 | 2.6e-08 |
| 39_fec_haute_ev_basse_smi_central | 3.1e-05 | 5.3e-02 | 3.9e-04 | 9.7e-04 | 2.9e-08 |
| 40_fec_haute_ev_basse_smi_bas | 3.3e-05 | 5.3e-02 | 3.8e-04 | 9.5e-04 | 2.7e-08 |
| 41_fec_basse_ev_centrale_smi_haut | 2.6e-05 | 7.2e-04 | 3.9e-04 | 3.9e-04 | 2.4e-08 |
| 42_fec_basse_ev_centrale_smi_bas | 2.9e-05 | 7.2e-04 | 4.0e-04 | 3.9e-04 | 1.6e-08 |
| 43_fec_basse_ev_haute_smi_central | 2.6e-05 | 3.7e-02 | 3.9e-04 | 7.2e-04 | 1.5e-08 |
| 44_fec_basse_ev_haute_smi_haut | 2.5e-05 | 3.7e-02 | 4.0e-04 | 7.1e-04 | 3.6e-08 |
| 45_fec_basse_ev_basse_smi_central | 2.8e-05 | 5.3e-02 | 3.9e-04 | 9.7e-04 | 2.4e-08 |
| 46_fec_basse_ev_basse_smi_haut | 2.7e-05 | 5.3e-02 | 3.9e-04 | 9.6e-04 | 2.3e-08 |

Écarts par grand groupe d'âge, scénario central :

| Groupe | 2040 | 2070 |
|---|---|---|
| 0-19 | -0.01% | -0.01% |
| 20-64 | +0.00% | -0.00% |
| 65+ | +0.00% | +0.00% |
| 80+ | +0.00% | +0.00% |
| 100+ | +0.02% | +0.00% |

## Test B — scénarios paramétriques construits à partir du seul scénario central

Départ au 1er janvier 2026 sur la population de chaque scénario ; effet = écart en 2070 à une projection centrale partant du même point (rapport non calculé si l'effet Insee est inférieur à 200 000).

Le générateur n'apprend que sur le central et trois variantes (15_smi_haut, 13_ev_haute, 14_ev_basse) ; chaque autre scénario est reconstruit à partir des seuls paramètres qu'un utilisateur fixerait.

| Scénario Insee | Paramètres transmis | Effet 2070 Insee | Effet 2070 M1 | Rapport | Population, écart max | Par âge, écart max | EV hommes 2070, écart (ans) |
|---|---|---|---|---|---|---|---|
| 11_fec_haute | ICF 1.70 ; solde +150 000 ; EV F 2070 90.0 (λ = -0.00) | +4.94 M | +4.94 M | 1.000 | 0.00% | 0.0% | -0.00 |
| 12_fec_basse | ICF 1.20 ; solde +150 000 ; EV F 2070 90.0 (λ = -0.00) | -4.54 M | -4.54 M | 1.000 | 0.00% | 0.0% | -0.00 |
| 16_smi_bas | ICF 1.45 ; solde +70 000 ; EV F 2070 90.0 (λ = -0.00) | -4.61 M | -4.61 M | 1.000 | 0.00% | 0.0% | -0.00 |
| 21_population_haute | ICF 1.70 ; solde +230 000 ; EV F 2070 93.0 (λ = +1.00) | +12.01 M | +12.01 M | 1.000 | 0.00% | 0.0% | -0.00 |
| 22_population_basse | ICF 1.20 ; solde +70 000 ; EV F 2070 87.0 (λ = -1.00) | -10.89 M | -10.89 M | 1.000 | 0.00% | 0.0% | +0.00 |
| 23_population_agee | ICF 1.20 ; solde +70 000 ; EV F 2070 93.0 (λ = +1.00) | -6.79 M | -6.79 M | 1.000 | 0.00% | 0.0% | -0.00 |
| 24_population_jeune | ICF 1.70 ; solde +230 000 ; EV F 2070 87.0 (λ = -1.00) | +7.70 M | +7.70 M | 1.000 | 0.00% | 0.0% | +0.00 |
| 52_ev_constante | rythme des gains de mortalité = 0 | -3.33 M | -3.33 M | 1.000 | 0.00% | 10.0% | +0.00 |
| 53_smi_nul | ICF 1.45 ; solde +0 ; EV F 2070 90.0 (λ = -0.00) | -7.95 M | -8.64 M | 1.088 | 1.21% | 19.2% | -0.00 |
| 31_fec_centrale_ev_haute_smi_haut | ICF 1.45 ; solde +230 000 ; EV F 2070 93.0 (λ = +1.00) | +6.79 M | +6.79 M | 1.000 | 0.00% | 0.0% | -0.00 |
| 32_fec_centrale_ev_haute_smi_bas | ICF 1.45 ; solde +70 000 ; EV F 2070 93.0 (λ = +1.00) | -2.51 M | -2.51 M | 1.000 | 0.00% | 0.0% | -0.00 |
| 33_fec_centrale_ev_basse_smi_haut | ICF 1.45 ; solde +230 000 ; EV F 2070 87.0 (λ = -1.00) | +2.50 M | +2.50 M | 1.000 | 0.00% | 0.0% | +0.00 |
| 34_fec_centrale_ev_basse_smi_bas | ICF 1.45 ; solde +70 000 ; EV F 2070 87.0 (λ = -1.00) | -6.63 M | -6.63 M | 1.000 | 0.00% | 0.0% | +0.00 |
| 35_fec_haute_ev_centrale_smi_haut | ICF 1.70 ; solde +230 000 ; EV F 2070 90.0 (λ = -0.00) | +9.82 M | +9.82 M | 1.000 | 0.00% | 0.0% | -0.00 |
| 36_fec_haute_ev_centrale_smi_bas | ICF 1.70 ; solde +70 000 ; EV F 2070 90.0 (λ = -0.00) | +0.05 M | +0.05 M | nan | 0.00% | 0.0% | -0.00 |
| 37_fec_haute_ev_haute_smi_central | ICF 1.70 ; solde +150 000 ; EV F 2070 93.0 (λ = +1.00) | +7.08 M | +7.08 M | 1.000 | 0.00% | 0.0% | -0.00 |
| 38_fec_haute_ev_haute_smi_bas | ICF 1.70 ; solde +70 000 ; EV F 2070 93.0 (λ = +1.00) | +2.15 M | +2.15 M | 1.000 | 0.00% | 0.0% | -0.00 |
| 39_fec_haute_ev_basse_smi_central | ICF 1.70 ; solde +150 000 ; EV F 2070 87.0 (λ = -1.00) | +2.86 M | +2.86 M | 1.000 | 0.00% | 0.0% | +0.00 |
| 40_fec_haute_ev_basse_smi_bas | ICF 1.70 ; solde +70 000 ; EV F 2070 87.0 (λ = -1.00) | -1.98 M | -1.98 M | 1.000 | 0.00% | 0.0% | +0.00 |
| 41_fec_basse_ev_centrale_smi_haut | ICF 1.20 ; solde +230 000 ; EV F 2070 90.0 (λ = -0.00) | -0.21 M | -0.21 M | 1.000 | 0.00% | 0.0% | -0.00 |
| 42_fec_basse_ev_centrale_smi_bas | ICF 1.20 ; solde +70 000 ; EV F 2070 90.0 (λ = -0.00) | -8.88 M | -8.88 M | 1.000 | 0.00% | 0.0% | -0.00 |
| 43_fec_basse_ev_haute_smi_central | ICF 1.20 ; solde +150 000 ; EV F 2070 93.0 (λ = +1.00) | -2.41 M | -2.41 M | 1.000 | 0.00% | 0.0% | -0.00 |
| 44_fec_basse_ev_haute_smi_haut | ICF 1.20 ; solde +230 000 ; EV F 2070 93.0 (λ = +1.00) | +1.97 M | +1.97 M | 1.000 | 0.00% | 0.0% | -0.00 |
| 45_fec_basse_ev_basse_smi_central | ICF 1.20 ; solde +150 000 ; EV F 2070 87.0 (λ = -1.00) | -6.60 M | -6.60 M | 1.000 | 0.00% | 0.0% | +0.00 |
| 46_fec_basse_ev_basse_smi_haut | ICF 1.20 ; solde +230 000 ; EV F 2070 87.0 (λ = -1.00) | -2.31 M | -2.31 M | 1.000 | 0.00% | 0.0% | +0.00 |
