"""A.2 — Batterie de chocs (ancrage nominal) : base = backtest 2010-2025 (exogènes observées), chocs ADDITIFS en 2011,
écarts à la base à 1, 3, 5, 10 et 15 ans (2011, 2013, 2015, 2020, 2025). Configurations : v0.9, v0.9 + rattrapage,
C1 (frontière), C2 (frontière + rattrapage)."""
import copy, pathlib, sys
H = pathlib.Path(__file__).resolve(); sys.path[:0] = [str(H.parents[2] / "phase34"), str(H.parents[2] / "src")]
import numpy as np, pandas as pd
import lab
from lab import V09
CONF = {"v0.9": V09, "v0.9 + rattrapage": {**V09, "indexation_retard": 0.17},
        "C1 frontière": {**V09, "prix_va": "frontiere"}, "C2 frontière + rattrapage": {**V09, "prix_va": "frontiere", "indexation_retard": 0.17}}
if "--sans-tension" in sys.argv:
    CONF = {"v0.9": V09, "T0 v0.9 sans tension": {**V09, "tension_prix": "aucune"},
            "T1 frontière sans tension": {**V09, "prix_va": "frontiere", "tension_prix": "aucune"},
            "T2 frontière sans tension + rattrapage": {**V09, "prix_va": "frontiere", "tension_prix": "aucune", "indexation_retard": 0.17}}
EN = ["CPA_B", "CPA_C19", "CPA_D"]
T0 = 2011
AN = (2011, 2013, 2015, 2020, 2025)

def add(serie, d, index):
    base = serie if serie is not None else pd.Series(0.0, index=index)
    return base.add(pd.Series(d), fill_value=0.0)

def choc(nom):
    def f(mod, ex):
        ans = list(range(2011, 2026))
        if nom.startswith("pétrole"):
            pi = ex.prix_import.copy()
            yrs = [2011, 2012] if "temporaire" in nom else [t for t in pi.index if t >= T0]
            for c in EN:
                if c in pi.columns:
                    pi.loc[yrs, c] = pi.loc[yrs, c] * 1.5
            ex.prix_import = pi
        elif nom.startswith("salaires"):
            ex.choc_salaire = add(ex.choc_salaire, {T0: 0.02}, ans)
        elif nom.startswith("productivité"):
            ex.productivite = add(ex.productivite, {T0: 0.01}, ans)
        elif nom.startswith("coût du travail"):
            ex.subvention_salaires = add(ex.subvention_salaires, {t: 0.02 for t in range(T0, 2031)}, range(1995, 2031))
            ex.subvention_en_depense = True
        elif nom.startswith("demande"):
            cp = ex.conso_publique.copy(); cp.loc[T0:] = cp.loc[T0:] * 1.05; ex.conso_publique = cp
        elif nom.startswith("taux"):
            tl = ex.taux_long.copy(); tl.loc[T0:] = tl.loc[T0:] + 1.0; ex.taux_long = tl
            if ex.taux_court is not None:
                tc = ex.taux_court.copy(); tc.loc[T0:] = tc.loc[T0:] + 1.0; ex.taux_court = tc
        elif nom.startswith("anticipations"):
            # proxy (le modèle n'a pas de variable d'anticipation) : +1 point sur la croissance des salaires et des prix de
            # VA pendant un an, sans déplacement des cibles de long terme
            ex.choc_salaire = add(ex.choc_salaire, {T0: 0.01}, ans)
            cal = dict(ex.calage or {}); cal["prix"] = add(cal.get("prix"), {T0: 0.01}, ans); ex.calage = cal
    return f

CHOCS = ["pétrole +50 % temporaire (2 ans)", "pétrole +50 % permanent", "salaires +2 % temporaire", "productivité +1 % permanente",
         "coût du travail −2 % permanent (subvention)", "demande publique +5 % permanente", "taux d'intérêt +1 pt permanent",
         "anticipations d'inflation +1 pt (1 an, proxy)"]
rows = {}
for cn, spec in CONF.items():
    b = lab.run(2010, 2025, "v08", spec, retour=True)[1]
    for ch in CHOCS:
        v = lab.run(2010, 2025, "v08", spec, exp_mod=choc(ch), retour=True)[1]
        lp = np.log(v.pc / b.pc)
        prod_v, prod_b = v.pib / v.emploi, b.pib / b.emploi
        for t in AN:
            rows[(ch, cn, t - T0 + 1)] = {
                "niveau prix (%)": 100 * lp[t], "inflation (pt)": 100 * (lp[t] - (lp[t - 1] if t - 1 in lp.index else 0.0)),
                "salaire (%)": 100 * np.log(v.salaire[t] / b.salaire[t]), "salaire réel (%)": 100 * (np.log(v.salaire[t] / b.salaire[t]) - lp[t]),
                "prix VA (%)": 100 * np.log(v.pva_m[t] / b.pva_m[t]), "marge (pt)": v.taux_marge[t] - b.taux_marge[t],
                "productivité (%)": 100 * np.log(prod_v[t] / prod_b[t]), "emploi (milliers)": v.emploi[t] - b.emploi[t],
                "PIB (%)": 100 * np.log(v.pib[t] / b.pib[t]), "solde (pt PIB)": v.solde_pib[t] - b.solde_pib[t]}
    print("fait :", cn, flush=True)
df = pd.DataFrame(rows).T
df.index.names = ["choc", "configuration", "année"]
df.to_csv(H.parent / ("b5_chocs_ancrage_sans_tension.csv" if "--sans-tension" in sys.argv else "b5_chocs_ancrage.csv"))
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 400)
print(df.round(2).to_string())
