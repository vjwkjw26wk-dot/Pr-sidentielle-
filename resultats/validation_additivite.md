# Validation de l'approximation additive de l'interface (version 0.4)

Écarts à la trajectoire inchangée en 2028 et 2032 : modèle complet (exact) et somme des variantes élémentaires interpolées (interface). Scénarios illustratifs, non attribués à un programme.

## A — redistribution et dépense

Mesures : RSA (montant forfaitaire) = 25 %, Coup de pouce au SMIC = 10 %, Impôt sur la fortune (taux moyen, remplace l'IFI) = 1 %, Impôt sur le revenu : taux de la tranche supérieure = 50 %, Âge légal : retour immédiat (sans transition) = 62 ans, Emplois publics (atteints en 5 ans) = 100 milliers

| Indicateur | 2028 exact | 2028 additif | 2032 exact | 2032 additif | écart 2032 |
|---|---|---|---|---|---|
| PIB (%) | +0.11 | +0.11 | -0.96 | -0.95 | +0.00 |
| Chômage (pt) | -1.24 | -1.24 | -1.73 | -1.73 | -0.00 |
| Solde public (pt de PIB) | -0.08 | -0.08 | -0.53 | -0.54 | -0.01 |
| Dette (pt de PIB) | -1.31 | -1.31 | -1.04 | -1.03 | +0.01 |
| Prix (%) | +0.76 | +0.76 | +2.34 | +2.32 | -0.02 |

## B — baisse des prélèvements et des dépenses

Mesures : Cotisations patronales = -20 Md€/an, Taux de l'impôt sur les sociétés = 20 %, Autres dépenses de fonctionnement = -30 Md€/an, Âge légal de départ (cible) = 65 ans, Allocations chômage = -10 %

| Indicateur | 2028 exact | 2028 additif | 2032 exact | 2032 additif | écart 2032 |
|---|---|---|---|---|---|
| PIB (%) | -0.72 | -0.72 | +0.03 | +0.03 | +0.01 |
| Chômage (pt) | +0.75 | +0.75 | +0.34 | +0.33 | -0.00 |
| Solde public (pt de PIB) | -0.65 | -0.64 | -0.45 | -0.43 | +0.01 |
| Dette (pt de PIB) | +3.11 | +3.08 | +5.35 | +5.25 | -0.10 |
| Prix (%) | -0.95 | -0.95 | -1.69 | -1.71 | -0.02 |

## C — protection commerciale et production

Mesures : Droits de douane hors UE (avec riposte) = 10 %, Objectif de relocalisation industrielle = 10 % des importations, Taux normal de TVA = -2 points, Âge légal de départ (cible) = 62 ans, Prix de l'énergie importée (hypothèse) = 20 %

| Indicateur | 2028 exact | 2028 additif | 2032 exact | 2032 additif | écart 2032 |
|---|---|---|---|---|---|
| PIB (%) | -1.35 | -0.45 | -2.16 | -1.28 | +0.88 |
| Chômage (pt) | -0.60 | -0.87 | -0.58 | -1.26 | -0.68 |
| Solde public (pt de PIB) | -0.32 | -0.16 | -1.57 | -0.96 | +0.61 |
| Dette (pt de PIB) | +1.06 | +0.20 | +6.06 | +1.99 | -4.08 |
| Prix (%) | +1.09 | +0.95 | +3.01 | +3.65 | +0.64 |

## D — transition et investissement

Mesures : Taxe carbone (hausse) = 100 €/t CO2, Investissement public = 30 Md€/an, Logements sociaux supplémentaires = 50 milliers/an, Taux réduits de TVA = -2 points, CSG sur les revenus d'activité = 1 points

| Indicateur | 2028 exact | 2028 additif | 2032 exact | 2032 additif | écart 2032 |
|---|---|---|---|---|---|
| PIB (%) | +0.20 | +0.19 | +0.35 | +0.35 | -0.01 |
| Chômage (pt) | +0.03 | +0.03 | +0.14 | +0.14 | +0.01 |
| Solde public (pt de PIB) | -0.38 | -0.38 | -0.64 | -0.64 | -0.00 |
| Dette (pt de PIB) | -0.06 | -0.05 | +2.27 | +2.30 | +0.03 |
| Prix (%) | +0.93 | +0.95 | +0.72 | +0.72 | -0.00 |

## Synthèse

Écart absolu moyen en 2032 entre l'approximation additive et le modèle complet : 0.36 (maximum 4.08) ; écart relatif médian : 2 %.

Les interactions viennent surtout du bouclage macroéconomique (fermeture d'offre, indexation des prix et salaires) et du cumul de mesures sur les mêmes ménages ; le calcul exact (`python3 -m simulateur.serveur`) reste la référence.
