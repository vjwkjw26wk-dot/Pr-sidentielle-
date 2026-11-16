# Validation du lot 4 (version 1.2) — population de foyers et impôt sur le revenu 2024

Généré par `tests/validation_M4.py` : échantillon de 2% des ménages du recensement 2022 (201821 foyers, 344527 personnes), durée 391 s. Masses ramenées aux 41.64 M de foyers DGFiP (couverture du modèle : 92.0%).

## Couverture et masses imputées

| Grandeur | Modèle | Référence |
|---|---|---|
| Personnes des ménages ordinaires | 66.38 M | 66,3 M (Insee, RP 2022) |
| Ménages | 30.97 M | 30,9 M (Insee, RP 2022) |
| Foyers fiscaux | 38.29 M | 41.64 M (DGFiP, dont 0,30 M de non-résidents) |
| Heures supplémentaires exonérées | 21.8 Md€ | 21.8 Md€ (calé) |
| Salaires de personnes travaillant à l'étranger | 15.0 Md€ | 19.7 Md€ (cases 1AF-1CF, y c. non-résidents) |
| Épargne retraite déductible | 9.6 Md€ | 9.6 Md€ (calé) |
| Reste (RFR − salaires et pensions − heures sup.) | 239 Md€ | capital, foncier, indépendants déclarés : 182 Md€ ; excédent traité comme inclus dans le RFR mais non imposé au barème : 17% du reste |

## Test 1 : par décile de RFR par part (DGFiP, revenus 2024), η = 0,8

Grandeurs testées : nombre de parts, impôt au barème par part. Les réductions et crédits (RICI) non modélisés un à un sont calés par décile ; la colonne « RICI modélisés » montre la part reconstituée sans calage. Euros par part ; valeurs DGFiP arrondies à 10 €.

| Décile | Parts, modèle | Parts, DGFiP | RFR/part, modèle | RFR/part, DGFiP | Barème/part, modèle | Barème/part, DGFiP | PFU/part, modèle | PFU/part, DGFiP | RICI modélisés/part | RICI/part, DGFiP | IR net/part, modèle | IR net/part, DGFiP |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1.38 | 1.53 | 1 235 | 310 | 0 | 10 | 3 | 0 | 10 | 30 | -10 | -20 |
| 2 | 1.59 | 1.86 | 4 883 | 5 030 | 0 | 10 | 4 | 0 | 46 | 50 | -45 | -40 |
| 3 | 2.01 | 1.74 | 9 096 | 9 510 | 0 | 0 | 11 | 10 | 93 | 70 | -82 | -60 |
| 4 | 1.71 | 1.67 | 12 447 | 12 680 | 0 | 0 | 18 | 10 | 116 | 90 | -98 | -80 |
| 5 | 1.68 | 1.70 | 15 317 | 15 510 | 32 | 60 | 25 | 10 | 144 | 110 | -87 | -40 |
| 6 | 1.56 | 1.59 | 18 187 | 18 210 | 273 | 300 | 32 | 10 | 183 | 140 | 121 | 180 |
| 7 | 1.51 | 1.55 | 21 128 | 21 110 | 673 | 710 | 43 | 20 | 217 | 180 | 498 | 540 |
| 8 | 1.53 | 1.55 | 25 007 | 24 860 | 1 296 | 1 290 | 61 | 20 | 263 | 260 | 1 095 | 1 060 |
| 9 | 1.55 | 1.55 | 31 629 | 31 020 | 2 726 | 2 510 | 108 | 50 | 316 | 420 | 2 414 | 2 140 |
| 10 | 1.54 | 1.60 | 69 581 | 67 310 | 12 141 | 10 050 | 1 129 | 1 440 | 406 | 1 570 | 11 993 | 10 210 |

Impôt au barème total : modèle 110.1 Md€ (η = 0,5 : 114.2 ; η = 1,2 : 105.9) ; DGFiP ≈ 98.6 Md€ (déduit des moyennes par décile).

## Test 2 : impôt net par tranche de RFR (IRCOM), η = 0,8

| Tranche de RFR | Part imposée, modèle | Part imposée, DGFiP | Impôt net, modèle (Md€) | Impôt net, DGFiP (Md€) |
|---|---|---|---|---|
| 0 à 15 000 | 23% | 3% | -0.3 | -0.7 |
| 15 001 à 20 000 | 55% | 29% | 0.0 | -0.1 |
| 20 001 à 30 000 | 80% | 61% | 3.4 | 4.0 |
| 30 001 à 50 000 | 83% | 72% | 11.5 | 12.8 |
| 50 001 à 100 000 | 95% | 91% | 30.9 | 26.6 |
| 100 001 à 200 000 | 100% | 97% | 24.6 | 20.5 |
| 200 001 à 1 000 000 | 100% | 98% | 19.7 | 18.5 |
| Plus de 1 000 000 | 100% | 100% | 11.3 | 10.1 |
| **Total** | | | **101.2** | **91.7** |

Sensibilité de l'impôt net total à η : 104.9 (η = 0,5), 101.2 (0,8), 97.5 (1,2) Md€.

