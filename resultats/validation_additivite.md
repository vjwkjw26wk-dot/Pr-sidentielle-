# Validation de l'approximation additive de l'interface (version 0.4)

Écarts à la trajectoire inchangée en 2028 et 2032 : modèle complet (exact) et somme des variantes élémentaires interpolées (interface). Scénarios illustratifs, non attribués à un programme.

## A — redistribution et dépense

Mesures : RSA (montant forfaitaire) = 25 %, Coup de pouce au SMIC = 10 %, Impôt sur la fortune (taux moyen, remplace l'IFI) = 1 %, Impôt sur le revenu : taux de la tranche supérieure = 50 %, Âge légal : retour immédiat (sans transition) = 62 ans, Emplois publics = 100 milliers

| Indicateur | 2028 exact | 2028 additif | 2032 exact | 2032 additif | écart 2032 |
|---|---|---|---|---|---|
| PIB (%) | +0.24 | +0.25 | -0.92 | -0.92 | +0.01 |
| Chômage (pt) | -1.34 | -1.35 | -1.76 | -1.77 | -0.00 |
| Solde public (pt de PIB) | -0.02 | -0.03 | -0.58 | -0.59 | -0.01 |
| Dette (pt de PIB) | -1.50 | -1.51 | -1.10 | -1.08 | +0.01 |
| Prix (%) | +0.75 | +0.75 | +2.48 | +2.46 | -0.02 |

## B — baisse des prélèvements et des dépenses

Mesures : Cotisations patronales = -20 Md€/an, Taux de l'impôt sur les sociétés = 20 %, Autres dépenses de fonctionnement = -30 Md€/an, Âge légal de départ (cible) = 65 ans, Allocations chômage = -10 %

| Indicateur | 2028 exact | 2028 additif | 2032 exact | 2032 additif | écart 2032 |
|---|---|---|---|---|---|
| PIB (%) | -0.75 | -0.74 | -0.08 | -0.07 | +0.01 |
| Chômage (pt) | +0.76 | +0.76 | +0.40 | +0.40 | -0.00 |
| Solde public (pt de PIB) | -0.63 | -0.62 | -0.31 | -0.30 | +0.01 |
| Dette (pt de PIB) | +3.12 | +3.10 | +5.32 | +5.22 | -0.10 |
| Prix (%) | -0.95 | -0.95 | -1.73 | -1.75 | -0.02 |

## C — protection commerciale et production

Mesures : Droits de douane hors UE (avec riposte) = 10 %, Objectif de relocalisation industrielle = 10 % des importations, Taux normal de TVA = -2 points, Âge légal de départ (cible) = 62 ans, Prix de l'énergie importée (hypothèse) = 20 %

| Indicateur | 2028 exact | 2028 additif | 2032 exact | 2032 additif | écart 2032 |
|---|---|---|---|---|---|
| PIB (%) | -0.92 | +0.03 | -1.27 | -0.15 | +1.11 |
| Chômage (pt) | -0.73 | -1.00 | -1.10 | -1.87 | -0.77 |
| Solde public (pt de PIB) | -0.33 | -0.17 | -1.47 | -0.80 | +0.67 |
| Dette (pt de PIB) | +0.74 | -0.14 | +4.22 | -0.36 | -4.58 |
| Prix (%) | +1.02 | +0.87 | +3.38 | +4.11 | +0.73 |

## D — transition et investissement

Mesures : Taxe carbone (hausse) = 100 €/t CO2, Investissement public = 30 Md€/an, Logements sociaux supplémentaires = 50 milliers/an, Taux réduits de TVA = -2 points, CSG sur les revenus d'activité = 1 points

| Indicateur | 2028 exact | 2028 additif | 2032 exact | 2032 additif | écart 2032 |
|---|---|---|---|---|---|
| PIB (%) | +0.27 | +0.26 | +0.37 | +0.36 | -0.01 |
| Chômage (pt) | -0.00 | +0.00 | +0.11 | +0.12 | +0.01 |
| Solde public (pt de PIB) | -0.36 | -0.36 | -0.59 | -0.60 | -0.00 |
| Dette (pt de PIB) | -0.15 | -0.14 | +2.00 | +2.03 | +0.02 |
| Prix (%) | +0.92 | +0.93 | +0.76 | +0.76 | -0.00 |

## Synthèse

Écart absolu moyen en 2032 entre l'approximation additive et le modèle complet : 0.41 (maximum 4.58) ; écart relatif médian : 2 %.

Les interactions viennent surtout du bouclage macroéconomique (fermeture d'offre, indexation des prix et salaires) et du cumul de mesures sur les mêmes ménages ; le calcul exact (`python3 -m simulateur.serveur`) reste la référence.
