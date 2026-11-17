# Validation de M10 — réformes socio-fiscales de la microsimulation au modèle bouclé (version 0.1)

Généré par `tests/validation_M10.py`. Effets statiques sur les revenus 2024 (impôt : 2 % des ménages ; prestations : deux sous-échantillons de 0,5 %), puis effets macroéconomiques dans M8 (base 2022, compte central avec fermeture d'offre).

Législation actuelle : impôt net 92.4 Md€ ; droits simulés RSA 17.8, prime d'activité 15.6, allocations familiales 13.5, aides au logement 14.8 Md€.

## R1 — Impôt sur le revenu : première tranche de 11 % à 14 %

### Effet statique (revenus 2024)

- Impôt sur le revenu net : +13.55 Md€ ;
- prestations versées (droits × recours apparent) : +0.00 Md€ (droits : rsa +0.00, ppa +0.00, af +0.00, aide_logement +0.00 Md€).

| Décile de niveau de vie | Niveau de vie moyen (€/UC/an, approché) | Variation (€/UC/an) | Variation (%) | Part de gagnants | Part de perdants |
|---|---|---|---|---|---|
| 1 | 5 448 | -1 | -0.02 % | 0% | 0% |
| 2 | 10 873 | -3 | -0.03 % | 0% | 2% |
| 3 | 14 578 | -36 | -0.25 % | 0% | 19% |
| 4 | 17 456 | -89 | -0.51 % | 0% | 38% |
| 5 | 20 071 | -196 | -0.98 % | 0% | 66% |
| 6 | 22 761 | -315 | -1.38 % | 0% | 88% |
| 7 | 25 957 | -428 | -1.65 % | 0% | 97% |
| 8 | 30 076 | -511 | -1.70 % | 0% | 99% |
| 9 | 36 383 | -563 | -1.55 % | 0% | 100% |
| 10 | 71 573 | -585 | -0.82 % | 0% | 100% |

### Effets macroéconomiques (écarts au compte central)

| Année | PIB | Consommation | Emploi (milliers) | Prix conso. | Revenu disponible | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|
| 2024 | -0.23 % | -0.79 % | -52 | -0.01 % | -0.86 % | +0.30 | -0.35 |
| 2026 | -0.18 % | -0.84 % | -55 | -0.13 % | -1.00 % | +0.29 | -0.78 |
| 2030 | -0.09 % | -0.84 % | -33 | -0.28 % | -1.15 % | +0.33 | -1.77 |

## R3 — Impôt sur le revenu : barème non revalorisé (seuils des tranches, décote et plafond du quotient familial −2 %, soit l'équivalent d'un gel face à une indexation de 2 %)

### Effet statique (revenus 2024)

- Impôt sur le revenu net : +2.67 Md€ ;
- prestations versées (droits × recours apparent) : +0.00 Md€ (droits : rsa +0.00, ppa +0.00, af +0.00, aide_logement +0.00 Md€).

| Décile de niveau de vie | Niveau de vie moyen (€/UC/an, approché) | Variation (€/UC/an) | Variation (%) | Part de gagnants | Part de perdants |
|---|---|---|---|---|---|
| 1 | 5 448 | -1 | -0.02 % | 0% | 0% |
| 2 | 10 873 | -1 | -0.01 % | 0% | 1% |
| 3 | 14 578 | -6 | -0.04 % | 0% | 10% |
| 4 | 17 456 | -16 | -0.09 % | 0% | 28% |
| 5 | 20 071 | -30 | -0.15 % | 0% | 59% |
| 6 | 22 761 | -44 | -0.19 % | 0% | 82% |
| 7 | 25 957 | -57 | -0.22 % | 0% | 95% |
| 8 | 30 076 | -84 | -0.28 % | 0% | 99% |
| 9 | 36 383 | -115 | -0.32 % | 0% | 100% |
| 10 | 71 573 | -171 | -0.24 % | 0% | 100% |

### Effets macroéconomiques (écarts au compte central)

| Année | PIB | Consommation | Emploi (milliers) | Prix conso. | Revenu disponible | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|
| 2024 | -0.05 % | -0.16 % | -10 | -0.00 % | -0.17 % | +0.06 | -0.07 |
| 2026 | -0.04 % | -0.17 % | -11 | -0.03 % | -0.20 % | +0.06 | -0.15 |
| 2030 | -0.02 % | -0.17 % | -6 | -0.06 % | -0.23 % | +0.06 | -0.35 |

## R2 — RSA : montant forfaitaire +10 %

### Effet statique (revenus 2024)

- Impôt sur le revenu net : +0.00 Md€ ;
- prestations versées (droits × recours apparent) : +1.93 Md€ (droits : rsa +2.84, ppa +0.00, af +0.00, aide_logement +0.00 Md€).

| Décile de niveau de vie | Niveau de vie moyen (€/UC/an, approché) | Variation (€/UC/an) | Variation (%) | Part de gagnants | Part de perdants |
|---|---|---|---|---|---|
| 1 | 5 448 | +163 | +2.99 % | 36% | 0% |
| 2 | 10 873 | +149 | +1.37 % | 34% | 0% |
| 3 | 14 578 | +27 | +0.19 % | 8% | 0% |
| 4 | 17 456 | +20 | +0.12 % | 6% | 0% |
| 5 | 20 071 | +16 | +0.08 % | 5% | 0% |
| 6 | 22 761 | +13 | +0.06 % | 4% | 0% |
| 7 | 25 957 | +11 | +0.04 % | 4% | 0% |
| 8 | 30 076 | +10 | +0.03 % | 3% | 0% |
| 9 | 36 383 | +8 | +0.02 % | 3% | 0% |
| 10 | 71 573 | +6 | +0.01 % | 2% | 0% |

### Effets macroéconomiques (écarts au compte central)

| Année | PIB | Consommation | Emploi (milliers) | Prix conso. | Revenu disponible | Solde public (pt de PIB) | Dette (pt de PIB) |
|---|---|---|---|---|---|---|---|
| 2024 | +0.03 % | +0.10 % | +7 | +0.00 % | +0.11 % | -0.05 | +0.06 |
| 2026 | +0.02 % | +0.11 % | +7 | +0.02 % | +0.13 % | -0.04 | +0.13 |
| 2030 | +0.01 % | +0.11 % | +4 | +0.04 % | +0.15 % | -0.05 | +0.28 |

## Limites

- Effets statiques : pas de réaction de l'offre de travail ni du recours aux prestations à la réforme.
- Niveau de vie approché à partir du revenu fiscal de référence (avant CSG, hors revenus exonérés), et non du revenu disponible de l'Insee.
- Prestations : erreur d'échantillonnage de l'ordre de 2 % (deux sous-échantillons) ; les petites réformes de prestations sont donc imprécises.
- Le sens macro → micro (revalorisation des revenus de M4 par M8) n'est pas encore fait : le montant statique est indexé sur le PIB nominal.

Durée : 17 s.

