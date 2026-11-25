# Tests, contrôles comptables et validations {#sec:annexe-f}

## F.1 Contrôles comptables

| Contrôle | Résultat | Source |
|---|---|---|
| 142 contrôles d'intégration (comptes d'agents, TES, flux-stocks) | 142/142 | phase 4, doc 21 §8 |
| Identité dette-solde dans les simulations des programmes (années ≥ 2027) | écart relatif ≤ 1,1e-16 | `phase6/resultats/simulabilite.json` |
| Transfert des programmes entre environnements (historique → part constante) | écart nul | `phase5/resultats/lot53_bilan.json` |
| Recoupement des totaux publiés par LFI (106,4 et 81,7 Md€) | exact | `tests/test_phase6.py` |
| Reproduction de la v0.8, de la v0.9 et de la référence R0 | exacte | `tests/test_phase5.py` |
| Revalidation du cache (empreinte des paramètres calibrés) | refuse un coefficient modifié | `tests/test_lot53.py` |

## F.2 Validations économiques

Voir le chapitre \ref{sec:donnees} : tests équation par équation, rétrosimulations conditionnelles (2010-2019,
2014-2019, 2019-2024), prévisions ex ante contre les millésimes du FMI, choc identifié du CICE.

## F.3 Liste des tests automatisés

Suites de la finalisation, de la phase 6, des lots 5.2 et 5.3, de la phase 5 et de la phase 4.3 (collecte pytest au
moment de la génération) :

{{inc:annexe_F_tests}}

Échecs antérieurs connus et documentés (suite v0.8, configurations historiques conservées en l'état) :
`test_offre_travail_heterogene` (clés obsolètes) et `test_choc_de_productivite_defavorable` (signe de la dette dans la
référence explosive).

## F.4 Défauts corrigés pendant la finalisation

| Défaut | Effet | Correction |
|---|---|---|
| Une variante d'environnement portant sur les taux (OAT 3,82 %) était écrasée par l'appliqueur monétaire à partir de 2027 | les premières simulations « OAT 3,82 % » étaient identiques aux simulations de base | base des taux du régime monétaire calculée après la variante ; test de non-régression ajouté ; variantes recalculées |
| Sensibilité des paramètres monétaires évaluée à taux exogènes (lot 5.3) | effet nul par construction | évaluation sous le régime BCE + prime |
| Pacte impôts de production / aides (Horizons) d'abord traduit en baisse de consommation publique | effet de demande erroné | traduction par les canaux des prélèvements sur les entreprises (deux variantes) |
| Variante européenne « tension » : le choc de prime souveraine figurait aussi dans la simulation de référence | le choc s'annulait dans l'écart ; seules les amendes étaient mesurées | référence simulée sans le choc (le choc est une réponse au programme) ; variantes européennes recalculées pour les trois candidats (`phase7/complement_europe.py`) |
| Variantes d'additionnalité de l'investissement hors budget non simulées | effet déduit approximativement de la mesure isolée | variantes 50 %, 25 %, 0 % ajoutées à la campagne |

**Reproductibilité constatée.** La campagne complète a été relancée le 25 novembre 2026 avec le code gelé : les
résultats de la lecture A, de la lecture B et des variantes déjà calculées la veille ont été reproduits à l'identique
(écart maximal nul) pour les trois candidats.
