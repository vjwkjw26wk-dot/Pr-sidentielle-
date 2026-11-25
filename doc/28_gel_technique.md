# 28 — Gel technique (version 1.0, 25 novembre 2026) : capacités, limites résiduelles, mises à jour attendues

Configuration de référence, versions et commandes : `GEL.md` à la racine du dépôt.

## 1. Capacités de simulation (toutes exécutables par `phase7/campagne.py`)

| Capacité | Mise en œuvre | Sortie |
|---|---|---|
| Mesures isolées | chaque mesure du corpus traduite et évaluée seule | `resultats["mesure:<id>"]` |
| Programmes complets, lecture A (mesures documentées) | `m27_corpus.mesures(candidat, ref, "conforme")` → M25 → M23 | `resultats["A"]` |
| Trajectoires budgétaires annoncées, lecture B | `ObjectifBudgetaire` : effort supplémentaire suivant la cible de solde, composition [H] | `resultats["B"]`, écart à la cible |
| Mise en œuvre partielle (50 %) ou retardée (+2 ans) | `modifier(liste, facteur, retard)` | `mise_en_oeuvre:*` |
| Régimes budgétaires et monétaires | 10 régimes (`REGIMES_ROBUSTESSE`) | `regime:*` |
| Conformité / tension européennes | M26 : conforme, contentieux, tension (amendes PDE, prime) | `europe:*` |
| Environnements alternatifs | σ 0,3 / 0,6, équation de prix v0.9 | `environnement:*` |
| Hypothèse de taux longs | OAT 4,89 % ou 3,82 % | `A:oat_382`, `B:oat_382` |
| Additionnalité de l'investissement hors APU (LFI) | 100 / 50 / 25 / 0 % | `additionnalite:*` |
| Horizons | 5 et 10 ans ; 20 ans sous hypothèses explicites | 2031, 2036, 2046 |
| Retraites | âge, mode de montée, durée d'assurance requise, groupe de départ anticipé, effets générationnels | M9 (`regle_age`, `effets_generationnels`) |
| Distribution statique | microsimulation OpenFisca par décile, groupes | `traductions["A"]` |

## 2. Développements de la finalisation

1. **Retraites (M9)** : durée d'assurance requise (calendriers 2014 et LFSS 2026, réformes « cible@début[:mode] ») ;
   report de l'âge effectif par année de durée (9 mois hommes, 5 mois femmes, Bozio 2011) ; décote et proratisation
   sur la part de base de la pension [H] ; groupe de départ anticipé (carrières longues, part 17 % CNAV 2024, ou
   maintien des conditions actuelles pour une fraction) ; effets générationnels (âge pivot, durée de retraite,
   facteur de pension). La référence estimée est exactement reproduite sans option.
2. **Lecture B** (`ObjectifBudgetaire`, `simuler_objectif`) : trajectoire de solde cible, effort réparti sur les
   instruments de M23, correction itérative de la cible.
3. **Correction** : une variante d'environnement sur les taux (OAT) était écrasée par l'appliqueur monétaire à partir
   de 2027 ; corrigé et testé.
4. **Investissement hors APU** : contrôle de non-double-compte (test : effet ex ante égal au montant, aucune dépense
   publique directe, pas de hausse directe de la dette) ; variantes d'additionnalité.
5. **Correction de la variante « tension »** : le choc de prime souveraine figurait aussi dans la référence et
   s'annulait dans l'écart ; la référence est désormais simulée sans le choc (`phase7/campagne.py`,
   `phase7/complement_europe.py`).
6. **Reproductibilité** : la campagne relancée le 25 novembre 2026 reproduit à l'identique les lectures A et B
   calculées la veille pour les trois candidats.
7. **Contrôles** : identité dette-solde dans toutes les simulations de programmes ; transfert exact des programmes.

## 3. Double comptabilisations : points vérifiés

| Risque | Traitement |
|---|---|
| Investissement hors APU compté aussi en investissement public | non : canal `autres_investissements` sans dépense publique ; test dédié |
| Investissement hors APU et FBCF des branches | la FBCF des branches ne réagit qu'à la demande induite (accélérateur) ; pas d'ajout direct |
| Financement du pôle public par l'épargne réglementée | non représenté : aucune baisse de consommation ni hausse de taux associée (limite, pas double compte) |
| Coût des retraites annoncé et coût M9 | seul le coût M9 entre dans le modèle ; le montant annoncé sert de contrôle |
| Économies RN « retraites » (P09) et réforme P08 | P09 non simulée (mesures non détaillées) |
| Composantes P06-P07 de P05 | non additionnées |
| Aides aux entreprises (H11) | deux canaux exclusifs (moitié impôts de production, moitié cotisations) |
| Microsimulation et mesures macro | une même mesure passe soit par la microsimulation (montant statique transmis à M8), soit par un canal macro, jamais les deux |
| Lecture B et règle budgétaire | effort de la règle figé (référence) ; effort de l'objectif distinct et journalisé |

## 4. Limites résiduelles (principales)

- Chômage : ampleur peu fiable pour les grands chocs d'offre de travail (population active en partie exogène).
- Référence à politique inchangée explosive (dette > 200 % du PIB en 2046) : les niveaux à 20 ans sont conditionnels.
- Recettes sans canal propre (Zucman, multinationales, TTF, fraude, contribution UE) : sans effet de demande, bornes
  hautes de rendement.
- Pas d'effets de crédibilité, de confiance ou d'incertitude politique ; prime souveraine seulement dans les variantes.
- Énergie non distinguée dans la TVA ; capitalisation (RN, Horizons), durée d'indemnisation du chômage, jours de carence,
  priorité nationale, contrôle des capitaux non représentés.
- Microsimulation statique (revenus 2024 indexés), sans dynamique individuelle ni territoires.

## 5. À actualiser après les publications des candidats

| Élément attendu | Candidat | Fichiers à modifier |
|---|---|---|
| Chiffrage complet de *L'Avenir en commun* (annoncé début 2027) ; barème de l'IR à 14 tranches ; périmètre de la revalorisation de 10 % (L21) | Mélenchon | `m27_corpus.py` (L05, L21, nouvelles mesures), `OBJECTIFS` |
| « Volume 2 » (janvier 2027) : ventilation des ~150 Md€, barème de l'allocation de 350 €, durée d'indemnisation, enseignants | Philippe | H01, H04, H07, H10 ; `OBJECTIFS` |
| Composition des 140 Md€ ; économies retraites (15-20 Md€) ; coût de la TVA énergie ; impôts de production | Le Pen | P01, P03, P05, P09, P10, P15 ; `OBJECTIFS` |
| Programme détaillé de G. Attal ou d'un autre candidat du centre | — | réévaluer le choix du candidat (ajout au corpus sans changement de code) |
| Nouvelles données (comptes 2025, prévisions FMI d'avril 2027, taux) | — | recalibration des environnements |

Procédure : modifier le corpus → `pytest tests/test_phase6.py tests/test_finalisation.py` → campagne du candidat →
`etude/generer.py` → `etude/compiler.sh`.
