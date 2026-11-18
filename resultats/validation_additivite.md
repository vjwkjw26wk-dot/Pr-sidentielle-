# Validation de l'approximation additive de l'interface (version 0.4)

Écarts à la trajectoire inchangée en 2028 et 2032 : modèle complet (exact) et somme des variantes élémentaires interpolées (interface). Scénarios illustratifs, non attribués à un programme.

## A — redistribution et dépense

Mesures : RSA (montant forfaitaire) = 25 %, Coup de pouce au SMIC = 10 %, Impôt sur la fortune (taux moyen, remplace l'IFI) = 1 %, Impôt sur le revenu : taux de la tranche supérieure = 50 %, Âge légal : retour immédiat (sans transition) = 62 ans, Emplois publics (atteints en 5 ans) = 100 milliers

| Indicateur | 2028 exact | 2028 additif | 2032 exact | 2032 additif | écart 2032 |
|---|---|---|---|---|---|
| PIB (%) | +0.11 | +0.11 | -0.94 | -0.94 | +0.00 |
| Chômage (pt) | -1.24 | -1.25 | -1.74 | -1.74 | -0.00 |
| Solde public (pt de PIB) | -0.07 | -0.08 | -0.53 | -0.53 | -0.01 |
| Dette (pt de PIB) | -1.31 | -1.31 | -1.08 | -1.07 | +0.01 |
| Prix (%) | +0.76 | +0.76 | +2.36 | +2.34 | -0.02 |

## B — baisse des prélèvements et des dépenses

Mesures : Cotisations patronales = -20 Md€/an, Taux de l'impôt sur les sociétés = 20 %, Autres dépenses de fonctionnement = -30 Md€/an, Âge légal de départ (cible) = 65 ans, Allocations chômage = -10 %

| Indicateur | 2028 exact | 2028 additif | 2032 exact | 2032 additif | écart 2032 |
|---|---|---|---|---|---|
| PIB (%) | -0.78 | -0.77 | -0.11 | -0.10 | +0.01 |
| Chômage (pt) | +0.77 | +0.77 | +0.43 | +0.42 | -0.00 |
| Solde public (pt de PIB) | -0.66 | -0.65 | -0.50 | -0.49 | +0.01 |
| Dette (pt de PIB) | +3.16 | +3.13 | +5.72 | +5.62 | -0.11 |
| Prix (%) | -0.94 | -0.94 | -1.74 | -1.76 | -0.02 |

## C — protection commerciale et production

Mesures : Droits de douane hors UE (avec riposte) = 10 %, Objectif de relocalisation industrielle = 10 % des importations, Taux normal de TVA = -2 points, Âge légal de départ (cible) = 62 ans, Prix de l'énergie importée (hypothèse) = 20 %

| Indicateur | 2028 exact | 2028 additif | 2032 exact | 2032 additif | écart 2032 |
|---|---|---|---|---|---|
| PIB (%) | -1.30 | -0.44 | -2.04 | -1.20 | +0.84 |
| Chômage (pt) | -0.62 | -0.87 | -0.66 | -1.31 | -0.65 |
| Solde public (pt de PIB) | -0.31 | -0.16 | -1.51 | -0.93 | +0.58 |
| Dette (pt de PIB) | +1.02 | +0.19 | +5.68 | +1.78 | -3.91 |
| Prix (%) | +1.08 | +0.95 | +3.03 | +3.66 | +0.63 |

## D — transition et investissement

Mesures : Taxe carbone (hausse) = 100 €/t CO2, Investissement public = 30 Md€/an, Logements sociaux supplémentaires = 50 milliers/an, Taux réduits de TVA = -2 points, CSG sur les revenus d'activité = 1 points

| Indicateur | 2028 exact | 2028 additif | 2032 exact | 2032 additif | écart 2032 |
|---|---|---|---|---|---|
| PIB (%) | +0.28 | +0.24 | +0.42 | +0.39 | -0.02 |
| Chômage (pt) | +0.00 | +0.01 | +0.09 | +0.11 | +0.02 |
| Solde public (pt de PIB) | -0.37 | -0.37 | -0.61 | -0.62 | -0.01 |
| Dette (pt de PIB) | -0.13 | -0.10 | +2.00 | +2.11 | +0.10 |
| Prix (%) | +0.92 | +0.94 | +0.77 | +0.75 | -0.02 |

## Synthèse

Écart absolu moyen en 2032 entre l'approximation additive et le modèle complet : 0.35 (maximum 3.91) ; écart relatif médian : 3 %.

Les interactions viennent surtout du bouclage macroéconomique (fermeture d'offre, indexation des prix et salaires) et du cumul de mesures sur les mêmes ménages ; le calcul exact (`python3 -m simulateur.serveur`) reste la référence.
