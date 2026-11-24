# 27 — Conditions de passage au rapport comparatif : critères objectifs et évaluation

Chaque critère a un indicateur mesurable, un seuil explicite et une source de vérification (script ou test). Les
seuils sont des conventions du projet, modifiables, mais l'évaluation ci-dessous les applique tels quels. Un critère non atteint n'interdit pas le rapport s'il est **présenté comme limite** ; un critère
bloquant (B) l'interdit.

## 1. Critères

| # | Critère | Indicateur | Seuil | Bloquant | Vérification |
|---|---|---|---|---|---|
| C1 | Capacité à simuler les programmes | paquets des trois candidats traduits et simulés sous le régime principal et les trois variantes européennes, trajectoires finies | 3/3 candidats × 3 variantes | B | `phase6/simulabilite.py` |
| C2 | Couverture des montants annoncés | part des montants chiffrés (hors enveloppes et composantes) entrant dans le modèle par un canal identifié | ≥ 80 % par candidat | non (limite à présenter) | `doc/25` §5 |
| C3 | Couverture des enveloppes globales | part de l'effort global annoncé (économies nettes, objectif de déficit) ventilée en mesures | ≥ 50 % ; sinon lecture « programme = régime » obligatoire en complément | non | `doc/25` §5 |
| C4 | Cohérence comptable | contrôles d'intégration ; identité dette-solde des simulations de programmes (années ≥ 2027) ; transfert des programmes entre environnements | 142/142 ; écart relatif < 1e-6 ; écart nul | B | doc 21 §8 ; `simulabilite.json` ; `lot53_bilan.json` |
| C5 | Reproductibilité | v0.8 et v0.9 reproduits ; revalidation du cache par empreinte des paramètres ; suites de tests des phases 4.3 à 6 | 100 % (hors échecs v0.8 documentés) | B | `tests/` |
| C6 | Robustesse des conclusions qualitatives | part des couples (stratégie, variable PIB ou dette, horizon 10 ou 20 ans) dont le signe est identique dans les 10 régimes | ≥ 80 % | non (cas non robustes à signaler) | `lot53_synthese_S1_S5.csv` |
| C7 | Sensibilité structurelle | amplitude maximale de l'effet à 20 ans due à un paramètre structurel isolé, comparée à l'écart entre stratégies voisines | < écart entre stratégies voisines pour la dette et le PIB | non | `lot53_structurels*.csv`, `lot53_environnements*.csv` |
| C8 | Traçabilité des hypothèses | mesures du corpus avec source ; conversions écrites ; paramètres avec statut [D]/[E]/[C]/[H] | 100 % | B | `tests/test_phase6.py` ; docs 20, 25, 26 |
| C9 | Couverture documentaire | équations, théorie, données, méthodes, calibrations, hypothèses, tests, limites, alternatives, mécanismes manquants | 10/10 rubriques | B | doc 26 |
| C10 | Qualification européenne | mesures du corpus ayant une qualification (niveau) ou explicitement « à instruire » | 100 % des mesures concernées | non | doc 24 |

## 2. Évaluation au 24 novembre 2026

| # | Résultat | Atteint | Commentaire |
|---|---|---|---|
| C1 | 3 candidats × 3 variantes (conforme, contentieux, tension) simulés sous R2 ; trajectoires finies ; microsimulation calculée (OpenFisca) pour les mesures des ménages | **oui** | durées : 1 à 4 min par candidat |
| C2 | LFI 188,1 / 188,1 Md€ (100 %) ; RN 80,1 / 97,6 Md€ (82 %) ; Horizons 2,0 / 2,0 Md€ (100 %, mais presque aucune mesure n'est chiffrée une à une) | **oui** | RN : économies sur les retraites (15-20 Md€) sans mesure identifiée |
| C3 | LFI : paquet 2027 entièrement ventilé ; RN : environ 45 Md€ ventilés en 2027 pour une enveloppe de 140 Md€ d'ici 2032 (part de 30 % environ si l'enveloppe est un niveau annuel en 2032, indéterminée s'il s'agit d'un cumul : les sources ne le précisent pas) ; Horizons : moins de 15 % des 150 Md€ (essentiellement les 250 000 postes, coût calculé par le modèle) | **non** pour RN et Horizons | la lecture « programme = régime » (objectif de solde atteint par la règle de M23, instruments de dépense) est obligatoire pour ces deux candidats, à côté de la lecture « mesures » |
| C4 | contrôles d'intégration 142/142 (phase 4, doc 21 §8 ; suite de la phase 4.3 rejouée sans échec) ; identité dette-solde dans les 9 simulations de programmes : écart relatif ≤ 1,1e-16 à partir de 2027 ; transfert des programmes : écart nul | **oui** | les années calées 2024-2025 portent des ajustements de stock observés (hors champ) |
| C5 | suites phase 4.3, 5, lots 5.2-5.3, 6 : 32/32 ; reproduction v0.8 / v0.9 / R0 exacte ; revalidation refusant un coefficient modifié | **oui** | deux échecs v0.8 antérieurs, documentés |
| C6 | PIB et dette, 10 et 20 ans : 20/20 signes robustes aux 10 régimes ; toutes variables : 49/60 | **oui** pour PIB et dette | emploi et chômage : 11 cas non robustes (régime actif symétrique, fermetures, σ) à présenter comme tels |
| C7 | amplitude maximale à 20 ans : PIB 0,13 point (réaction de la BCE à l'activité), dette 7,6 points (prime souveraine, sous régime BCE), σ : PIB 0,05 point, dette 7,1 points ; équation de prix v0.9 : PIB 0,05 point, dette 2,6 points ; aucun changement de classement en PIB ni en dette dans aucun test | **oui** | l'effet du régime monétaire lui-même (jusqu'à 15 points de dette) domine : il sera présenté en variante systématique |
| C8 | 66 mesures sourcées (test) ; conversions écrites mesure par mesure ; statuts [D]/[E]/[C]/[H] dans les registres (docs 20, 24, 25, 26) et `STRUCTURELS` | **oui** | |
| C9 | doc 26 : équations, théorie, données, méthodes, calibrations, hypothèses, tests, limites, alternatives, mécanismes manquants | **oui** | détail des estimations dans les documents de module |
| C10 | toutes les mesures du corpus relevant du droit de l'Union qualifiées (niveaux 1 à 4) ; les autres relèvent de la compétence nationale | **oui** | qualification sommaire, non juridique |

**Verdict.** Tous les critères bloquants (C1, C4, C5, C8, C9) sont atteints. Le modèle est en état de servir au
rapport comparatif, sous deux conditions de présentation : (1) pour le RN et Horizons, l'essentiel de l'effort
budgétaire annoncé n'est pas ventilé en mesures : ces programmes doivent être évalués à la fois par leurs mesures
identifiées et comme objectifs de solde (C3) ; (2) les effets sur l'emploi et le chômage sont moins robustes que ceux
sur le PIB et la dette (C6) et doivent être donnés avec leur fourchette de régimes.

## 3. Ce qui reste à faire avant la rédaction (ordre recommandé)

1. **Gel du corpus** à une date annoncée, après la publication du chiffrage complet de LFI (début 2027) et du
   « volume 2 » d'É. Philippe (janvier 2027) ; régénération de la doc 25 (`phase6/generer_doc_corpus.py`).
2. **Retraites (priorité 1 du doc 26)** : durée d'assurance et carrières longues dans M9, ou, à défaut, présentation
   systématique du coût annoncé à côté du coût M9 (L34, P08, H05).
3. **Variantes de composition** pour les enveloppes non ventilées (P03, P05, H01, L11, H11) et passes « programme =
   régime » (R1/R2 actifs) pour le RN et Horizons.
4. **Variantes d'additionnalité** de l'investissement hors APU (L33 : 100 / 50 / 25 %).
5. Si la baisse de TVA sur l'énergie reste centrale dans le programme RN : distinction des produits énergétiques
   (priorité 4 du doc 26).
