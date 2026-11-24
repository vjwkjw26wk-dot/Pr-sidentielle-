# Phase 4.3-4.4 — compte des sociétés, validation prédictive, validation intégrée

Rapport complet de la phase 4 : `doc/21_phase4_rapport.md`. Notes : `NOTE_B.md` (chantier B), `NOTE_C.md` (chantier C).

## Configurations

```python
import m8_modele as M
M.configurer_v09()      # référence reproductible (défaut des interrupteurs)
M.configurer_phase4()   # P4 = v0.9 + frontière des prix de facteurs + sans effet TUC + compte des sociétés
```

## Reproduction (dans l'ordre ; durées sur 1 cœur)

| Script | Contenu | Durée |
|---|---|---|
| `b2_estimation.py` | estimations du compte des sociétés, tests hors échantillon | < 1 min |
| `b4_compte_isole.py` | compte des sociétés à moteurs observés | < 1 min |
| `b5_autofinancement.py` | lien investissement-autofinancement | < 1 min |
| `b3_backtest_societes.py` | rétrosimulations v0.9, T1, v0.9 + compte, P4 (4 origines) | ≈ 10 min |
| `c1_ex_ante.py`, `c1_synthese.py` | conditionnel et ex ante, 5 origines × 3 configurations, FMI, naïf | ≈ 10 min |
| `c2_choc_cice.py` | effet du CICE (avec − sans) | ≈ 3 min |
| `d0_reference.py v09` / `p4` | référence 2023-2047 (mise en cache dans `outputs/`) | ≈ 50 min chacune |
| `d1_chocs_integration.py p4 --gel` / `v09` | 10 chocs sur 20 ans, contrôles, gel des boucles | ≈ 5 min |
| `e1_sensibilite.py` | 13 variantes × 3 chocs | ≈ 20 min |

Tests : `python3 -m pytest tests/test_phase43.py tests/test_phase42.py` (16 tests, ≈ 2 min).

Données ajoutées (ouvertes) : Eurostat `nasa_10_f_bs` consolidé S11 ; FMI WEO, millésimes d'octobre 2010, 2012,
2014, 2016, 2021 et 2024 via DBnomics (`data/raw/dbnomics_imf_weo_*`).
