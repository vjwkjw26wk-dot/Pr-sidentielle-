# 27 — Conditions de passage au rapport comparatif : critères objectifs et évaluation

Chaque critère a un indicateur mesurable, un seuil fixé avant l'évaluation et une source de vérification
(script ou test). Un critère non atteint n'interdit pas le rapport s'il est **présenté comme limite** ; un critère
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

{EVAL}

## 3. Ce qui reste à faire avant la rédaction (ordre recommandé)

{RESTE}
