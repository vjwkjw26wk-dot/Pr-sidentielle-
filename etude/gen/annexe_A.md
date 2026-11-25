### Paramètres structurels modifiables sans recalibration (M23)

| paramètre | catégorie | valeur centrale | basse | haute | statut | source, justification |
|---|---|---|---|---|---|---|
| `PSI_TAUX` | comportements | 0.2 | 0.1 | 0.4 | [L] | consommation : −% par point de taux réel (FR-BDF, Mésange : 0,1-0,4) |
| `PSI_CHOMAGE` | comportements | 0.3 | 0.1 | 0.5 | [H/L] | épargne de précaution : −% de consommation par point de chômage |
| `SEMI_ELAST_IS` | comportements | 0.8 | 0.2 | 1.5 | [L] | transfert de bénéfices : semi-élasticité de la base de l'IS (Heckemeyer et Overesch 2017) |
| `PART_IS_MULTINAT` | comportements | 0.5 | 0.3 | 0.7 | [C] | part de l'IS acquittée par les groupes multinationaux |
| `THETA_TRESORERIE` | comportements | 0.1 | 0.0 | 0.3 | [H] | part des profits conservés réinvestie (contrainte de trésorerie) |
| `THETA_ANTICIPATION` | comportements | 0.75 | 0.5 | 1.0 | [E] | anticipation du potentiel (phase 3.1, inférence indirecte) |
| `mu_taux` | societes | estimé (M24) | 0.35 | 0.83 | [E] | vitesse de renouvellement du taux apparent des SNF (0,60 estimé 1999-2024) |
| `phi_dette` | societes | estimé (M24) | 0.5 | 1.5 | [E] | dette des SNF / besoin de financement (1,06 ± 0,31) |
| `div_lissage` | societes | 1.0 | 0.3 | None | [H] | vitesse d'ajustement des dividendes au taux de distribution (Lintner non identifié) |
| `fiscalite_dividendes` | societes | False | None | True | [E fragile] | effets de la contribution de 3 % et du PFU sur la distribution |
| `bund_transmission` | monetaire | estimé (M24) | 0.2 | 0.6 | [E] | Δ Bund / Δ Euribor (0,39 ± 0,09) |
| `menages_vitesse` | monetaire | estimé (M24) | 0.25 | 0.6 | [E] | vitesse d'ajustement des taux des crédits à l'habitat (0,43 ± 0,07) |
| `entreprises_vitesse` | monetaire | estimé (M24) | 0.6 | 1.0 | [E] | vitesse d'ajustement du coût du crédit aux SNF (0,93 ± 0,02) |
| `bce_inflation` | monetaire | estimé (M24) | 0.2 | 0.6 | [E] | réponse de court terme de la BCE à l'inflation (0,39 ± 0,18) |
| `bce_activite` | monetaire | estimé (M24) | 0.1 | 0.5 | [E] | réponse de court terme de la BCE à l'activité (0,30 ± 0,09) |
| `prime_dette` | monetaire | estimé (M24) | 0.007 | 0.03 | [E]/[L] | prime souveraine par point de dette (1,3 pb ; France seule 0,7 pb ; littérature 3 pb) |
| `prime_solde` | monetaire | estimé (M24) | 0.0 | -0.118 | [E fragile] | prime par point de solde (−1,5 pb hors crise ; −11,8 pb avec la crise) |

### Politique monétaire et conditions financières (M24, estimés)

| paramètre (M24) | valeur | statut |
|---|---|---|
| `bce_lissage` | 0,7278 | [E] |
| `bce_inflation` | 0,3928 | [E] |
| `bce_activite` | 0,3022 | [E] |
| `bce_forme` | contemporaine appliquée à t − 1 [E*] | [E] |
| `bund_transmission` | 0,3858 | [E] |
| `menages_vitesse` | 0,4294 | [E] |
| `menages_court` | 0,2167 | [E] |
| `menages_long` | 0,1679 | [E] |
| `menages_transmission_lt` | 0,8957 | [E] |
| `entreprises_vitesse` | 0,9263 | [E] |
| `entreprises_court` | 0,6781 | [E] |
| `entreprises_long` | 0,0440 | [E] |
| `entreprises_transmission_lt` | 0,7796 | [E] |
| `prime_dette` | 0,0130 | [E] |
| `prime_solde` | −0,0148 | [E] |
| `prime_dette_avec_crise` | 0,0122 | [E] |
| `prime_solde_avec_crise` | −0,1184 | [E] |

### Retraites (M9, finalisation)

| paramètre (M9) | valeur | statut | source |
|---|---|---|---|
| report par année de durée requise, hommes | 0.75 an | [E, littérature] | Bozio (2011) |
| report par année de durée requise, femmes | 0,417 an | [E, littérature] | Bozio (2011) |
| part de la pension soumise à proratisation et décote | 0.5 | [H] | ordre de grandeur |
| décote par année manquante | 0.05 | [D] | code de la sécurité sociale |
| part des carrières longues | 0.17 | [D] | CNAV, données 2024 |
| coefficient sur l'écart de masse des pensions | 0.55 | [C] | étude d'impact 2023, Institut Montaigne |

### Règle budgétaire R2 (M23)

| paramètre de régime | valeur | statut |
|---|---|---|
| `debut` | 2027 | [H] |
| `alpha` | 0.5 | [H] |
| `beta` | 0.02 | [H] |
| `dette_cible` | 90.0 | [H] |
| `plafond` | 0.5 | [H] |
| `ecart_suspension` | 1.5 | [H] |
| `epsilon` | 0.5 | [H] |
| répartition de l'effort | {'conso_publique': 0.3, 'prestations': 0.2, 'impots_menages': 0.3, 'impots_produits': 0.2} | [H] |

### Registre détaillé de la version 0.8 (toujours en vigueur pour ces paramètres)

### Bouclage macroéconomique

| Paramètre | Définition | Valeur | Intervalle | Source et méthode | Confiance | Date |
|---|---|---|---|---|---|---|
| α | Part du capital (fonction de production) | 0,35 | 0,30-0,40 | Partage de la valeur ajoutée, comptes nationaux | A | 2024 |
| ρ | Rappel annuel de la demande vers le potentiel | 0,2 | 0,1-0,3 | Inférence indirecte : durée des écarts de production (AMECO, FMI 1982-2019) | B | 2026 |
| θ | Anticipation des révisions du potentiel par la demande | 0,75 | 0,5-1,0 | Même méthode + ancrage sur la réponse de la consommation à un choc permanent (Blundell, Pistaferri, Preston 2008) | C | 2026 |
| a | Terme proportionnel de la fermeture | 0 | 0-0,15 | Retiré : oscillations non observées | C | 2026 |
| μ | Effet des tensions sur les importations | 0 | 0-0,3 | Retiré : oscillations non observées ; non estimé | D | 2026 |
| Part du capital dans l'anticipation | Part de l'écart de potentiel dû au capital prise en compte | 1 | 0-1 | Non identifiable ; incertitude de structure | D | 2026 |
| κ | Pente de Phillips sur les prix hors industrie | 0,10 | 0,05-0,18 | Banque de France (États-Unis 0,18) ; ancrage des anticipations | C | 2024 |
| u* | Chômage structurel | 7,5 → 7,0 % | — | Hypothèses de la référence (FMI, COR) | C | 2026 |

### Ménages

| Paramètre | Définition | Valeur | Intervalle | Source et méthode | Confiance | Date |
|---|---|---|---|---|---|---|
| η_ext | Élasticité de participation au gain à l'emploi | 0,2 | 0,1-0,4 | Revues OFCE, DARES ; 27 études sur 35 > 0,1 | B | 2023 |
| η_int | Élasticité des heures au taux marginal net | 0,1 | 0,05-0,2 | Cabannes, Houdré, Landais (2014) ; revues | B | 2014 |
| ψ_u | Épargne de précaution (consommation, % par point de chômage) | 0,3 | 0,1-0,6 | Littérature ; épisode 2020-2021 | C | — |
| ψ_r | Effet du taux réel sur la consommation | 0,2 | 0-0,5 | Havranek (2015) | C | 2015 |
| Rigidité salariale à la baisse | Multiplicateur de la courbe de Phillips quand u > u* | 0,5 | 0,25-1 | Littérature sur la rigidité nominale | C | — |
| Effet de l'assurance chômage sur u* | Points par 10 % d'allocation | 0,063 | 0-0,13 | Le Barbanchon, Rathelot, Roulet (2017) | B | 2017 |
| Salaire d'embauche (M16) | Relatif au salaire moyen | 0,75 | 0,6-0,9 | Insee, salaires d'embauche | C | — |
| Allocation perdue au retour à l'emploi (M16) | € par an, en espérance | 5 200 | 3 000-8 000 | Indemnisation moyenne × part indemnisée (Unédic, ordres de grandeur) | C | 2024 |
| Masse indiciaire nette (M16, point d'indice) | M€ pour +100 % | 187 000 | 170 000-200 000 | Masse indiciaire brute ≈ 220 Md€ (DGAFP, 1 % ≈ 2,2 Md€) × 0,85 | C | 2025 |
| Âges des ménages concernés par l'âge légal (M16) | Âge de la personne de référence | 58-67 ans | — | Hypothèse de pseudo-cohorte | D | — |
| Prime de risque souveraine (M11) | Point de taux long par point de dette | 0,03 | 0-0,05 | Littérature (2 à 5 points de base par point de dette) ; non estimée par le projet | C | — |
| Taux net d'un supplément de salaire (M16) | Part conservée après impôt | 0,88 | 0,8-0,95 | Taux moyen d'IR | D | 2024 |

### Entreprises et incidence

| Paramètre | Définition | Valeur | Intervalle | Source et méthode | Confiance | Date |
|---|---|---|---|---|---|---|
| Semi-élasticité des bénéfices à l'IS | Transfert de bénéfices des groupes | 0,8 | 0,2-1,5 | Heckemeyer-Overesch ; Beer, de Mooij, Liu ; Merlo-Wamser | B | 2017-2020 |
| Part des groupes dans l'IS | — | 0,5 | — | Concentration de l'IS | D | — |
| Trésorerie → investissement | Part des bénéfices conservés investie | 0,10 | 0-0,3 | CICE (France Stratégie 2020) ; dividendes 2013 (Boissel, Matray) | C | 2020-2022 |
| Incidence salariale de l'IS | Part supportée par les salariés à long terme | 0,3 | 0-0,5 | Fuest, Peichl, Siegloch (AER 2018) : ≈ 0,5 (impôt local allemand) | C | 2018 |
| Incidence salariale des impôts de production | idem | 0,2 | 0-0,4 | Pas d'estimation causale française | D | — |
| Répercussion des impôts de production sur les prix | — | 0,5 | 0,3-0,7 | CAE (2019), hypothèse | D | 2019 |
| Transmission des cotisations employeurs aux salaires | Part transmise à long terme | 0,5 | 0,2-1,0 | Bozio, Breda, Grenet (2019) ; Carbonnier et al. (2019) | C | 2019 |
| Répercussion de la TVA (hausse / baisse, taux normal) | — | 0,95 / 0,50 | — | Benzarti et al. (JPE 2020) ; restauration en France | B | 2020 |
| Délocalisation énergo-intensive | Élasticité des importations au prix relatif de l'énergie | 0,15 | 0-0,4 | Dussaux (2020) ; Marin et Vona (2021) | C | 2021 |
| Additionnalité de l'aide à la R&D | € de R&D privée par € d'aide | 0,7 | 0,3-1,2 | CNEPI (2021) : 0,9-1,5 PME, ≈ 0 grandes | C | 2021 |
| Élasticité au stock de R&D | — | 0,08 | 0,03-0,15 | Hall, Mairesse, Mohnen (2010) | C/X | 2010 |
| Formation → u* | Points par Md€ et par an | 0,02 | 0-0,05 | Évaluations des formations de demandeurs d'emploi | X | — |
| Durée du travail | Part des heures supplémentaires convertie en production | 0,3 | — | Hypothèse D de la v0.6 (35 heures) | D | — |

### Finances publiques

| Paramètre | Définition | Valeur | Intervalle | Source | Confiance | Date |
|---|---|---|---|---|---|---|
| Renouvellement de la dette | Part de la dette renouvelée chaque année au taux de marché | 1/8 | 1/10-1/6 | Durée moyenne de la dette (AFT) | C ; le backtest montre une baisse plus rapide du taux apparent en 2012-2019 que celle simulée | 2024 |
| Dépense d'indemnisation chômage | % du PIB à chômage de base | 1,5 | 1,3-1,7 | Unédic | A | 2024 |

### Données indisponibles et substitutions

| Donnée manquante | Substitution | Perte de précision |
|---|---|---|
| Potentiel en temps réel (millésimes successifs) | Potentiel reconstruit en temps réel par filtrage jusqu'à l'origine | Le potentiel « vintage » d'époque aurait pu être différent |
| Patrimoine des ménages par ménage dans l'échantillon | Revenus non salariaux et non pensions du revenu fiscal | Les ménages à patrimoine non productif de revenu imposable sont sous-représentés |
| Héritages reçus par ménage | Assiette de patrimoine pondérée par l'âge | Distribution des droits de succession approximative |
| Transitions individuelles emploi-chômage (panel) | Probabilités en espérance par risque relatif âge × catégorie | Pas de distribution des pertes individuelles |
| Effets de la crise sanitaire | Période exclue du backtest | Pas de validation sur 2020-2021 |
