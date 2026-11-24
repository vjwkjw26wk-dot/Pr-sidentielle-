"""Phase 4.3, chantier C, niveau 4 : évaluation d'un choc de politique identifié — le CICE (2013-2018).
Effet du modèle = rétrosimulation conditionnelle avec le CICE observé − même rétrosimulation sans CICE (subvention nulle),
origine 2012. Comparaison aux évaluations ex post : France Stratégie (2020) ≈ 100 000 emplois (micro-économétrie, 2013-
2016) et ≈ 160 000 (évaluation macro-sectorielle, 2013-2017) ; comité de suivi (2018) : « proche de 100 000 »."""
import json, pathlib, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lab43 import *  # noqa
import lab as _lab
import numpy as np, pandas as pd
import m8_modele as M
CFG = ["v0.9", "T1", "P4 (T1 + compte des sociétés)"]
B, FIN = 2012, 2018
res = {}
for nom in CFG:
    out = {}
    for avec in (True, False):
        mod, ex, ans = _lab.construire(B, FIN, "v08", CONFIGS[nom])
        # coût budgétaire : le CICE observé figure déjà dans les autres dépenses observées des deux rétrosimulations ; on
        # l'ajoute en dépense (subvention_en_depense) dans les deux, de sorte que la différence avec − sans compte une
        # fois le coût du dispositif (sans quoi l'effet sur le solde serait celui d'un CICE gratuit)
        ex.subvention_en_depense = True
        if not avec:
            ex.subvention_salaires = pd.Series({t: 0.0 for t in ex.subvention_salaires.index})
        r = mod.simuler(ans, ex)
        out[avec] = r
        M.configurer_v08()
    a, s = out[True], out[False]
    d = pd.DataFrame({"emploi (milliers)": a.emploi - s.emploi, "emploi marchand (milliers)": (a.emploi - a.emploi_non_marchand) - (s.emploi - s.emploi_non_marchand),
                      "PIB (%)": 100 * (a.pib / s.pib - 1), "prix conso (%)": 100 * (a.pc / s.pc - 1), "salaire (%)": 100 * (a.salaire / s.salaire - 1),
                      "taux de marge (pt)": a.taux_marge - s.taux_marge, "solde public (pt PIB)": a.solde_pib - s.solde_pib})
    if "dividendes_distribues" in a:
        d["dividendes (Md€)"] = (a.dividendes_distribues - s.dividendes_distribues) / 1e3
    res[nom] = d
    print(f"\n=== {nom} : effet du CICE (avec − sans)")
    print(d.round(2).to_string())
json.dump({k: v.round(3).to_dict() for k, v in res.items()}, open(pathlib.Path(__file__).parent / "resultats" / "c2_choc_cice.json", "w"), default=float, indent=1)
