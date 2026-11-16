# Validation du lot 3 — cadre comptable T0 (comptes des secteurs institutionnels, base 2020)

Source : Eurostat `nasa_10_nf_tr`, `nasa_10_f_bs`, `nasa_10_f_tr`, `gov_10dd_edpt1` (données transmises par l'Insee), M€ courants. Généré par `tests/validation_M3.py`.

## 1. Cohérence des comptes publiés (avant réconciliation)

| Année | Lignes non équilibrées | Écart de ligne max (M€) | Écart de B9 max entre calcul et publication (M€) |
|---|---|---|---|
| 2019 | 10 sur 33 | 1 | 4 |
| 2020 | 5 sur 33 | 1 | 2 |
| 2021 | 9 sur 33 | 4 | 2 |
| 2022 | 6 sur 33 | 2 | 2 |
| 2023 | 8 sur 33 | 3 | 1 |
| 2024 | 7 sur 33 | 1 | 3 |
| 2025 | 6 sur 33 | 1 | 2 |

Les écarts ne dépassent pas quelques M€ : ce sont des arrondis de publication. Ils sont reportés dans un compte explicite « ECART » ; aucune opération n'est modifiée.

## 2. Identités du cadre réconcilié

| Année | Max |Σ emplois − Σ ressources| par ligne | Max |B9 − B9 publié| | |Σ B9 tous secteurs| |
|---|---|---|---|
| 2019 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| 2020 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| 2021 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| 2022 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| 2023 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| 2024 | 0.0e+00 | 0.0e+00 | 0.0e+00 |
| 2025 | 0.0e+00 | 0.0e+00 | 0.0e+00 |

**Toutes les identités vérifiées à 1e-6 M€ près : oui.**

## 3. Agrégats

| Agrégat | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| PIB publié (B1GQ) | 2 432 207 | 2 318 276 | 2 508 102 | 2 653 997 | 2 833 826 | 2 935 236 | 2 991 056 |
| PIB optique production (Σ VA + impôts nets sur produits) | 2 432 207 | 2 318 276 | 2 508 103 | 2 653 997 | 2 833 826 | 2 935 237 | 2 991 056 |
| PIB optique demande (P3 + P5 + P6 − P7) | 2 432 207 | 2 318 275 | 2 508 102 | 2 653 998 | 2 833 828 | 2 935 237 | 2 991 056 |
| Capacité de financement APU (B9, M€) | -58 226 | -207 084 | -165 149 | -125 896 | -151 920 | -169 118 | -151 592 |
| Solde APU en % du PIB | -2.4 | -8.9 | -6.6 | -4.7 | -5.4 | -5.8 | -5.1 |
| Taux d'épargne des ménages S14 (B8G / (B6G + D8 net)), définition Insee | 14.6 | 20.4 | 19.1 | 16.9 | 17.0 | 18.5 | 17.9 |
| Dépenses publiques (OTE) en % du PIB | 55.3 | 61.7 | 59.5 | 58.4 | 56.8 | 57.0 | 57.3 |
| Recettes publiques (OTR) en % du PIB | 53.0 | 52.8 | 52.9 | 53.7 | 51.4 | 51.2 | 52.2 |
| Dépense de consommation finale des ménages S14 (M€) | 1 262 531 | 1 190 000 | 1 269 169 | 1 374 103 | 1 482 483 | 1 527 123 | 1 545 939 |

Écart maximal du PIB reconstitué au PIB publié : optique production 1 M€, optique demande 2 M€.

## 4. Flux et stocks

### Dette publique au sens de Maastricht

| Année | Dette (M€) | Dette (% PIB) | Solde (% PIB) | Δ dette (M€) | Ajustement stock-flux (M€) |
|---|---|---|---|---|---|
| 2020 | 2 663 852 | 114.9 | -8.9 | 276 453 | 69 369 |
| 2021 | 2 828 781 | 112.8 | -6.6 | 164 929 | -220 |
| 2022 | 2 955 639 | 111.4 | -4.7 | 126 858 | 962 |
| 2023 | 3 103 248 | 109.5 | -5.4 | 147 609 | -4 311 |
| 2024 | 3 306 097 | 112.6 | -5.8 | 202 849 | 33 731 |
| 2025 | 3 460 111 | 115.7 | -5.1 | 154 014 | 2 422 |

### Patrimoine financier net par secteur, 2024 (M€)

| Secteur | PFN fin t−1 | PFN fin t | B9 non financier | B9F financier | Écart B9 − B9F | Autres flux |
|---|---|---|---|---|---|---|
| S11 | -2 860 556 | -2 514 033 | 17 543 | -4 660 | 22 203 | 351 183 |
| S12 | -416 270 | -445 445 | -35 716 | -25 563 | -10 153 | -3 612 |
| S13 | -2 110 884 | -2 153 581 | -169 118 | -168 145 | -973 | 125 448 |
| S14_S15 | 4 895 485 | 5 073 423 | 182 650 | 170 452 | 12 198 | 7 486 |
| S2 | 492 225 | 39 635 | 4 641 | 27 916 | -23 275 | -480 506 |
| Somme, reste du monde compris (doit être nulle) | 0 | -1 | 0 | 0 | 0 | -1 |

### Patrimoine financier net par secteur, 2025 (M€)

| Secteur | PFN fin t−1 | PFN fin t | B9 non financier | B9F financier | Écart B9 − B9F | Autres flux |
|---|---|---|---|---|---|---|
| S11 | -2 514 033 | -2 700 348 | -4 835 | -25 593 | 20 758 | -160 722 |
| S12 | -445 445 | -605 273 | -21 853 | -7 374 | -14 479 | -152 454 |
| S13 | -2 153 581 | -2 134 326 | -151 592 | -150 607 | -985 | 169 862 |
| S14_S15 | 5 073 423 | 5 344 190 | 170 310 | 158 014 | 12 296 | 112 753 |
| S2 | 39 635 | 95 756 | 7 971 | 25 561 | -17 590 | 30 560 |
| Somme, reste du monde compris (doit être nulle) | -1 | -1 | 1 | 1 | 0 | -1 |

Σ des patrimoines financiers nets (y compris reste du monde) = 0 à l'arrondi près : le cadre de stocks est fermé. L'écart B9 − B9F (comptes non financiers et financiers) et les « autres flux » (réévaluations, changements de volume) sont des grandeurs explicites du cadre ; ils seront exogènes en simulation (scénario de prix d'actifs), sauf modélisation ultérieure.
