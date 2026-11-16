# Validation des prestations (version 1.1) — droits simulés et montants versés, 2024

Généré par `tests/validation_prestations.py` : 4 sous-échantillons indépendants de 0,5 % des ménages du recensement 2022 (ensemble = 2 %), mois de calcul 2024-10 annualisé × 12, probabilité mensuelle d'emploi des contrats non permanents 0.75 ; durée 591 s. Les intervalles sont ± 2 erreurs types d'échantillonnage.

## Droits simulés et montants versés

| Prestation | Éligibles simulés (M) | Bénéficiaires réels (M) | Droits simulés (Md€/an) | Versé (Md€) | Recours apparent, foyers | Recours apparent, masse | Recours estimé par la DREES |
|---|---|---|---|---|---|---|---|
| RSA | 3.20 ± 0.03 | 1.83 | 17.6 ± 0.3 | 11.9 | 57% (57%–58%) | 68% (67%–69%) | 63 à 67 % des foyers |
| Prime d'activité | 6.78 ± 0.11 | 4.55 | 15.5 ± 0.3 | 10.3 | 67% (66%–68%) | 66% (65%–68%) | ≈ 50 % des foyers ; 54 à 57 % de la masse |
| Allocations familiales | 4.64 ± 0.06 | 4.70 | 13.5 ± 0.1 | — | 101% (100%–103%) | — | proche de 100 % |
| Aides au logement | 5.44 ± 0.09 | 5.80 | 15.0 ± 0.3 | 16.0 | 107% (105%–108%) | 107% (105%–109%) | élevé (non publié) |

## Cohérence entre recours en nombre et recours en masse

Si les non-recourants ont des droits plus faibles que les recourants (constat de la DREES pour le RSA : 42 % des non-recourants ont un droit mensuel faible), le recours en masse doit dépasser le recours en nombre, et le montant moyen réellement versé doit dépasser le droit moyen simulé.

| Prestation | Droit moyen simulé (€/mois) | Montant moyen versé (€/mois) | Recours masse − recours foyers |
|---|---|---|---|
| RSA | 458 | 542 | +11 points |
| Prime d'activité | 190 | 189 | -1 points |
| Aides au logement | 229 | 230 | +0 points |

## Sensibilité de la prime d'activité à la variabilité des revenus

| Probabilité mensuelle d'emploi (contrats non permanents) | Éligibles (M) | Droits (Md€/an) | Recours apparent foyers | Recours apparent masse |
|---|---|---|---|---|
| 1.0 | 7.04 | 16.8 | 65% | 61% |
| 0.75 | 6.78 | 15.5 | 67% | 66% |
| 0.6 | 6.57 | 15.1 | 69% | 68% |

## Représentativité du sous-échantillon de 0,5 %

Écart type entre sous-échantillons de 0,5 % (erreur d'un calcul fait sur un seul sous-échantillon) :

| Prestation | Éligibles : écart type relatif | Droits : écart type relatif |
|---|---|---|
| RSA | 0.8% | 1.6% |
| Prime d'activité | 1.6% | 2.2% |
| Allocations familiales | 1.3% | 0.9% |
| Aides au logement | 1.6% | 2.1% |

