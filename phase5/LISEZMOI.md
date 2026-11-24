# Phase 5 — lot 5.0 : environnement, régimes, programmes

Code : `src/m23_regimes.py` (Environnement, Regime, RegleBudgetaire, Programme, simuler, evaluer) ; crochet
`Exogenes.regime_hook` dans `src/m8_modele.py` (appelé au début de chaque année, n'utilise que les années passées) ;
convention de dépense dans `src/m8_reference.py` (`convention="historique"` par défaut, inchangé ; `"part_constante"`).

```python
import m23_regimes as G
env = G.Environnement.charger("p4", "part_constante")     # calibré une fois (≈ 53 min), ensuite ≈ 13 s depuis le cache
ref = G.simuler(env, G.regime("R2"))                        # ≈ 9 s, sans recalibration
eff = G.evaluer(env, G.regime("R2"), G.Programme("nom", fonction_qui_modifie_les_exogenes), ref=ref)
```

Régimes nommés : R0 (aucune règle), R1 (stabilisation), R2 (ajustement vers d* = 90 %, régime principal, figé),
R2_actif, R2_sym ; tous les paramètres sont des arguments (`G.regime("R2", alpha=…, beta=…, plafond=…, dette_cible=…,
parts={…}, parametres="ancrage_faible")`).

Scripts : `construire_environnement.py p4 part_constante|historique` ; `lot50_regimes.py` (références, contrôles,
programme test, rendement des instruments, durées). Tests : `tests/test_phase5.py` (7 tests).

## Lot 5.2 — politique monétaire et conditions financières (`src/m24_monetaire.py`)

```python
G.simuler(env, G.regime("R2", monetaire="bce"))                       # règle de la BCE + prime souveraine estimée
G.simuler(env, G.regime("R0", monetaire={"chocs_directeur": {2027: 1.0}, "anticipations": "rationnelles"}))
G.simuler(env, G.regime("R0", monetaire={"prime": "niveau", "prime_dette": 0.03}))   # hypothèse de scénario
```
Défaut : taux exogènes, avec le taux directeur de référence observé (Euribor 3 mois d'octobre 2026, 2,63 %, à partir de
2027) au lieu du taux déduit du taux long (4,13 %). Le régime « bce » sans choc reproduit exactement le régime exogène.
Revalidation du cache par resimulation : une modification du code qui ne change pas la référence ne déclenche plus la
recalibration de 53 min.
Simulations : `lot52_monetaire.py` ; tests : `tests/test_lot52.py`.

## Lot 5.3 (préparation) — robustesse

`G.robustesse(env, programme)` : effets à 5 et 15 ans dans 10 régimes (règles budgétaires, BCE, ancrage, fermeture).
Paramètres structurels qui demandent un environnement distinct (calibration de 53 min chacun) : σ (0,3 ; 0,6) et
l'équation des prix de VA (v0.9 ; T1). Script : `lot53_robustesse.py` ; test : `tests/test_lot53.py`.
