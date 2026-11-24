"""Phase 4.3, chantier C : rétrosimulations conditionnelles (niveau 2) et prévisions ex ante (niveau 3) aux mêmes
origines, comparées aux prévisions du FMI du même millésime (octobre de l'origine) et à une prévision naïve.
Usage : python3 phase43/c1_ex_ante.py [configurations séparées par des virgules]"""
import json, pathlib, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from lab43 import *  # noqa
import lab as _lab
import numpy as np, pandas as pd
import m22_validation as V
import m8_modele as M

ORIGINES = [(2010, 2015), (2012, 2017), (2014, 2019), (2016, 2019), (2021, 2025)]
HORIZONS = (1, 3, 5)
CFG = sys.argv[1].split(",") if len(sys.argv) > 1 else ["v0.9", "T1", "P4 (T1 + compte des sociétés)"]
SORTIE = pathlib.Path(__file__).parent / "resultats"; SORTIE.mkdir(exist_ok=True)


def mesures(r, o, B, fin, pc_obs=None):
    out = {}
    for h in HORIZONS:
        t = B + h
        if t > fin:
            continue
        g_s = 100 * ((r.pib[t] / o["pib"][B]) ** (1 / h) - 1); g_o = 100 * ((o["pib"][t] / o["pib"][B]) ** (1 / h) - 1)
        p_s = 100 * ((r.pc[t] / o["pc"][B]) ** (1 / h) - 1); p_o = 100 * ((o["pc"][t] / o["pc"][B]) ** (1 / h) - 1)
        out[h] = {"pib_g": g_s - g_o, "inflation": p_s - p_o, "chomage": float(r.chomage[t] - o["chomage"][t]),
                  "solde_pib": float(r.solde_pib[t] - o["solde_pib"][t]), "dette_pib": float(r.dette_pib[t] - o["dette_pib"][t])}
    return out


def fmi(B, fin, obs_fmi):
    p = V.previsions_fmi(B)
    out = {}
    for h in HORIZONS:
        t = B + h
        if t > fin:
            continue
        g = lambda df, c: 100 * (np.prod([1 + df[c][a] / 100 for a in range(B + 1, t + 1)]) ** (1 / h) - 1)  # noqa: E731
        out[h] = {"pib_g": g(p, "pib_g") - g(obs_fmi, "pib_g"), "inflation": g(p, "inflation") - g(obs_fmi, "inflation"),
                  "chomage": float(p.chomage[t] - obs_fmi.chomage[t]), "solde_pib": float(p.solde_pib[t] - obs_fmi.solde_pib[t]),
                  "dette_pib": float(p.dette_pib[t] - obs_fmi.dette_pib[t])}
    return out


def naif(o, B, fin):
    out = {}
    for h in HORIZONS:
        t = B + h
        if t > fin:
            continue
        g5 = 100 * ((o["pib"][B] / o["pib"][B - 5]) ** 0.2 - 1); p5 = 100 * ((o["pc"][B] / o["pc"][B - 5]) ** 0.2 - 1)
        g_o = 100 * ((o["pib"][t] / o["pib"][B]) ** (1 / h) - 1); p_o = 100 * ((o["pc"][t] / o["pc"][B]) ** (1 / h) - 1)
        out[h] = {"pib_g": g5 - g_o, "inflation": p5 - p_o, "chomage": float(o["chomage"][B] - o["chomage"][t]),
                  "solde_pib": float(o["solde_pib"][B] - o["solde_pib"][t]),
                  "dette_pib": float(o["dette_pib"][B] + h * (o["dette_pib"][B] - o["dette_pib"][B - 5]) / 5 - o["dette_pib"][t])}
    return out


obs_fmi = V.previsions_fmi(2025 - 1)          # dernières valeurs observées publiées par le FMI (octobre 2024)
res = {}
for B, fin in ORIGINES:
    for nom in CFG:
        spec = CONFIGS[nom]
        for mode in ("conditionnel", "ex_ante"):
            mod, ex, ans = _lab.construire(B, fin, "v08", spec)
            if mode == "ex_ante":
                V.exogenes_ex_ante(mod, ex, B, fin)
            r = mod.simuler(ans, ex)
            import backtest as BT
            o = BT.observe(mod)
            res[f"{nom}|{B}|{mode}"] = mesures(r, o, B, fin)
            M.configurer_v08()
            print(nom, B, mode, {h: {k: round(v, 2) for k, v in d.items()} for h, d in res[f"{nom}|{B}|{mode}"].items()}, flush=True)
    res[f"FMI|{B}|ex_ante"] = fmi(B, fin, obs_fmi)
    res[f"naïf|{B}|ex_ante"] = naif(o, B, fin)
    print("FMI", B, res[f"FMI|{B}|ex_ante"], flush=True)
    (SORTIE / f"c1_ex_ante_{'_'.join(c.split(' ')[0] for c in CFG)}.json").write_text(json.dumps(res, indent=1, default=float))
