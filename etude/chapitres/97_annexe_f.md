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

- `tests/test_finalisation.py::test_duree_requise_legislation`
- `tests/test_finalisation.py::test_regle_simple_inchangee_et_options_neutres`
- `tests/test_finalisation.py::test_sens_des_effets`
- `tests/test_finalisation.py::test_effets_generationnels`
- `tests/test_finalisation.py::test_objectif_budgetaire_interpolation`
- `tests/test_finalisation.py::test_corpus_retraites_et_objectifs`
- `tests/test_finalisation.py::test_variante_environnement_transmise_au_regime_monetaire`
- `tests/test_finalisation.py::test_investissement_hors_apu_sans_double_compte`
- `tests/test_phase6.py::test_corpus_integrite`
- `tests/test_phase6.py::test_paquet_lfi_recoupe_les_totaux_publies`
- `tests/test_phase6.py::test_conversions_inversent_le_rendement_statique`
- `tests/test_phase6.py::test_variantes_institutionnelles`
- `tests/test_phase6.py::test_amendes_pde_et_regime_monetaire`
- `tests/test_phase6.py::test_qualification_politique_commerciale`
- `tests/test_lot53.py::test_robustesse_programme_nul_et_coherence`
- `tests/test_lot53.py::test_parametres_structurels_appliques_sans_recalibration`
- `tests/test_lot53.py::test_transfert_des_programmes_exact`
- `tests/test_lot53.py::test_revalidation_refuse_un_coefficient_modifie`
- `tests/test_lot52.py::test_estimations_et_statuts`
- `tests/test_lot52.py::test_regime_bce_sans_choc_identique_au_regime_exogene`
- `tests/test_lot52.py::test_choc_permanent_transmission`
- `tests/test_lot52.py::test_regle_bce_lissage`
- `tests/test_lot52.py::test_prime_souveraine`
- `tests/test_phase5.py::test_regles_parametrables`
- `tests/test_phase5.py::test_R0_reproduit_l_environnement`
- `tests/test_phase5.py::test_changer_de_regime_sans_recalibrer_et_rapidement`
- `tests/test_phase5.py::test_identites_et_regle`
- `tests/test_phase5.py::test_programme_nul_et_regle_figee`
- `tests/test_phase5.py::test_programme_figee_effort_identique`
- `tests/test_phase5.py::test_conversion_effort_conso_publique`
- `tests/test_phase43.py::test_identites_compte_societes_donnees`
- `tests/test_phase43.py::test_compte_societes_isole_continuite_et_identites`
- `tests/test_phase43.py::test_hausse_des_taux_augmente_les_interets_et_reduit_les_dividendes`
- `tests/test_phase43.py::test_millesime_fmi_disponible_et_ex_ante_sans_information_future`
- `tests/test_phase43.py::test_v09_reproduite_apres_phase43`
- `tests/test_phase43.py::test_configurations_sans_fuite_d_etat`
- `tests/test_phase43.py::test_v08_reproduite_apres_un_essai_v09`
- `tests/test_phase43.py::test_p4_identites_et_lien_menages`
- `tests/test_phase43.py::test_p4_backtest_proche_de_t1`
- `tests/test_phase43.py::test_p4_choc_de_taux_stable_sur_15_ans`

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
