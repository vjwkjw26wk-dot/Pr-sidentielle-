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
