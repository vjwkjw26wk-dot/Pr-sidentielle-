# Validation des prestations (version 1) — droits simulés et montants versés, 2024

Généré par `tests/validation_prestations.py` (44943 familles au sens de la CAF, sous-échantillon de 0,5 % des ménages du recensement 2022), mois de calcul 2024-10, annualisé × 12 ; durée 131 s.

| Prestation | Familles bénéficiaires simulées | Versé : foyers | Droits simulés (Md€/an) | Versé (Md€) | Recours apparent (masse) | Recours apparent (foyers) | Référence |
|---|---|---|---|---|---|---|---|
| RSA | 2.90 M | 1.83 M | 15.4 | 11.9 | 77% | 63% | CNAF : 11,9 Md€ versés en 2024, 1,83 M de foyers |
| Prime d'activité | 6.25 M | 4.55 M | 15.0 | 10.3 | 69% | 73% | CNAF : ≈ 10,3 Md€ (2,37 + 2,46 + 2,71 Md€ aux trois premiers trimestres), ≈ 4,5 M de foyers |
| Allocations familiales | 4.77 M | 4.70 M | 14.0 | — | — | 99% | CNAF : 4,7 M de familles bénéficiaires |
| Aides au logement | 5.25 M | 5.80 M | 14.4 | 16.0 | 111% | 110% | DREES : APL 7,1 Md€ = 44,3 % des aides au logement, soit ≈ 16 Md€ ; ≈ 5,8 M de foyers |

Lecture : un recours apparent proche de 1 − non-recours publié indique un modèle cohérent ; au-dessus de 100 %, le modèle sous-estime les droits ; très en dessous, il les surestime (ou le non-recours est plus fort qu'estimé).

