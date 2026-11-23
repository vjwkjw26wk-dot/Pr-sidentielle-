# 20 — Registre des paramètres (version 0.8)

Pour chaque paramètre important : définition, valeur retenue, intervalle, source, méthode, degré de confiance, date de
référence. Confiance : **A** estimé sur données françaises avec diagnostic satisfaisant ; **B** estimé ou repris
d'études causales proches (autre pays, autre période) ; **C** calibré sur la littérature sans estimation propre ;
**D** hypothèse de modélisation ; **X** exploratoire. Les paramètres des équations à correction d'erreur (consommation,
investissement, commerce, emploi, salaires, prix) sont estimés sur données Insee 1997-2019 (documents M7-M8,
confiance A à B) et ne sont pas repris ici.

## Bouclage macroéconomique

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

## Ménages

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

## Entreprises et incidence

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

## Finances publiques

| Paramètre | Définition | Valeur | Intervalle | Source | Confiance | Date |
|---|---|---|---|---|---|---|
| Renouvellement de la dette | Part de la dette renouvelée chaque année au taux de marché | 1/8 | 1/10-1/6 | Durée moyenne de la dette (AFT) | C ; le backtest montre une baisse plus rapide du taux apparent en 2012-2019 que celle simulée | 2024 |
| Dépense d'indemnisation chômage | % du PIB à chômage de base | 1,5 | 1,3-1,7 | Unédic | A | 2024 |

## Données indisponibles et substitutions

| Donnée manquante | Substitution | Perte de précision |
|---|---|---|
| Potentiel en temps réel (millésimes successifs) | Potentiel reconstruit en temps réel par filtrage jusqu'à l'origine | Le potentiel « vintage » d'époque aurait pu être différent |
| Patrimoine des ménages par ménage dans l'échantillon | Revenus non salariaux et non pensions du revenu fiscal | Les ménages à patrimoine non productif de revenu imposable sont sous-représentés |
| Héritages reçus par ménage | Assiette de patrimoine pondérée par l'âge | Distribution des droits de succession approximative |
| Transitions individuelles emploi-chômage (panel) | Probabilités en espérance par risque relatif âge × catégorie | Pas de distribution des pertes individuelles |
| Effets de la crise sanitaire | Période exclue du backtest | Pas de validation sur 2020-2021 |
