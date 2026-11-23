# 16 — Registre des paramètres de comportement (v0.7)

Légende du statut : **E** estimé sur données françaises ; **L** repris de la littérature (valeur
centrale et fourchette) ; **H** hypothèse de modélisation, à défaut de mieux ; **X** exploratoire
(levier dont l'effet n'est pas établi). Chaque paramètre a trois niveaux (basse / centrale / haute),
activés par l'option `comportements_v07` du simulateur.

Avertissement sur la causalité : la plupart des élasticités viennent d'études quasi expérimentales
locales (une réforme, un secteur, une période). Leur transposition à une réforme de grande ampleur
en équilibre général est une extrapolation.

## 1. Bouclage macroéconomique

| Paramètre | Code | Basse | Centrale | Haute | Statut | Source / justification |
|---|---|---|---|---|---|---|
| Part du capital (PIB potentiel) | `ALPHA_K` | — | 0,35 | — | E | Partage de la valeur ajoutée (comptes nationaux) |
| Chômage structurel u\* | `chomage_structurel` | — | 7,5 → 7,0 % (2026-2031) | — | H | Cohérence avec la référence (hypothèses COR / FMI) |
| Fermeture : force de rappel ρ | `RHO` | 0 | 0,15 | 0,3 | H | Demi-vie de l'écart de production de 3-5 ans |
| Amortissement | `AMORTI` | — | 0,3 | — | H | Évite l'oscillation |
| Phillips prix (hors industrie) | `KAPPA_PRIX` | 0,05 | 0,10 | 0,18 | L | Banque de France (0,18 pt par point d'écart, États-Unis) ; valeur centrale réduite pour la France |
| Importations / tensions | `MU_IMPORT` | 0,5 | 1,0 | 1,5 | H | Fuite de la demande quand les capacités sont saturées |

## 2. Ménages

| Paramètre | Code | Basse | Centrale | Haute | Statut | Source |
|---|---|---|---|---|---|---|
| Épargne de précaution (Δ chômage) | `PSI_CHOMAGE` | 0,1 | 0,3 | 0,6 | L | Littérature sur l'épargne de précaution ; hausse de l'épargne en 2020-2021 |
| Effet du taux réel sur la consommation | `PSI_TAUX` | 0 | 0,2 | 0,5 | L | Élasticité de substitution intertemporelle faible (Havranek 2015) |
| Offre de travail, marge extensive | `ETA_EXT` (M15) | 0,1 | 0,2 | 0,4 | L | Revue OFCE (0,19-1,13), enquête DARES ; 27 études sur 35 > 0,1 |
| Offre de travail, marge intensive | `ETA_INT` (M15) | 0,05 | 0,1 | 0,2 | L | Idem ; Cabannes-Houdré-Landais (revenu imposable 0,02 en moyenne) |
| Assurance chômage → u\* (pt par 10 % d'allocation) | `EFFET_AC` | 0 | 0,063 | 0,13 | L | Le Barbanchon et al. : élasticité de durée à la durée d'indemnisation 0,3 |

## 3. Entreprises

| Paramètre | Code | Basse | Centrale | Haute | Statut | Source |
|---|---|---|---|---|---|---|
| Semi-élasticité des bénéfices à l'IS | `SEMI_ELAST_IS` | 0,2 | 0,8 | 1,5 | L | Heckemeyer-Overesch (~0,8) ; Beer-de Mooij-Liu (~1, ≈1,5 récent) ; Merlo-Wamser (0,22) |
| Part des bénéfices multinationaux | `PART_IS_MULTINAT` | — | 0,5 | — | H | Concentration de l'IS sur les grands groupes |
| Réinvestissement de la trésorerie | `THETA_TRESORERIE` | 0 | 0,10 | 0,30 | L | CICE : pas d'effet concluant sur l'investissement (France Stratégie 2020) ; dividendes 2013 (Bach et al., Boissel-Matray) |
| Délocalisation énergo-intensive | `ELAST_DELOC_ENERGIE` | 0 | 0,15 | 0,4 | L | Dussaux 2020 (OCDE) ; Dechezleprêtre et al. ; Marin-Vona |
| Additionnalité de l'aide à la R&D (€ privé par € public) | `ADDITIONNALITE_RD` | 0,3 | 0,7 | 1,2 | L / X | CNEPI 2021 (0,9-1,5 pour les PME, pas de levier pour les grandes) |
| Élasticité de la production au stock de R&D | `ELAST_STOCK_RD` | 0,03 | 0,08 | 0,15 | L / X | Hall-Mairesse-Mohnen 2010 |
| Formation → u\* (pt par Md€ et par an) | `EFFET_FORMATION` | 0 | 0,02 | 0,05 | X | Effets modestes des programmes de formation des demandeurs d'emploi |

## 4. Prix et salaires

| Paramètre | Code | Valeur | Statut | Source |
|---|---|---|---|---|
| Répercussion TVA normale, hausse / baisse | `REPERCUSSION_TVA_V07` | 0,95 / 0,50 | L | Benzarti-Carloni-Harju-Kosonen (JPE 2020) : hausses répercutées deux fois plus que les baisses |
| Répercussion TVA réduite, hausse / baisse | idem | 0,50 / 0,25 | L | Restauration en France : 2009 peu répercutée ; 2012 ≈ 50 % ; 2014 ≈ 38 % |
| Rythme de répercussion (première année) | `PROFIL_REPERCUSSION` | 0,6 | H | Répercussion étalée sur deux ans |
| Rigidité des salaires à la baisse | `ASYM_SALAIRES` | 0,5 (basse 1,0 ; haute 0,25) | L | Littérature sur la rigidité nominale à la baisse |
| Stabilisateur chômage (dépense de base) | `DEPENSE_ARE_BASE` | 1,5 % du PIB | E | Dépense d'indemnisation ≈ 40 Md€ |

## 5. Paramètres conservés de la v0.6

Les élasticités des équations à correction d'erreur (consommation, investissement, commerce, emploi,
salaires, prix) restent estimées sur données françaises (documents M7-M8). Les comportements des
hauts revenus (M13) et l'hétérogénéité (M14) sont inchangés.
