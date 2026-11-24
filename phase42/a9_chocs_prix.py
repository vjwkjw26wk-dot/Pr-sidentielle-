"""Phase 4.2, chantier A (A.4) : chocs sur les prix et les marges, en écart à une trajectoire de base (backtest,
origine 2010, exogènes observées), pour v0.8, v0.9 et la candidate A (v0.9 + coûts intermédiaires + rattrapage).
Chocs à partir de 2012. Écarts en 2012, 2014 et 2019."""
import copy, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent)); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "phase34"))
import numpy as np, pandas as pd
import lab
import m8_modele as M
from lab import V09
CONF = {"v0.8": {}, "v0.9": V09, "candidate A": {**V09, "prix_va": "ci_hausse", "indexation_retard": 0.17}}
T0, ANS = 2012, (2012, 2014, 2019)
EN = ["CPA_B", "CPA_C19", "CPA_D"]

def choc(nom):
    def f(mod, ex):
        ex = ex
        if nom.startswith("pétrole"):
            fac = 1.5 if "+" in nom else 0.7
            pi = ex.prix_import.copy()
            for c in EN:
                if c in pi.columns:
                    pi.loc[T0:, c] = pi.loc[T0:, c] * fac
            ex.prix_import = pi
        elif nom.startswith("salaires"):
            ex.choc_salaire = pd.Series({t: (0.02 if t == T0 else 0.0) for t in range(2011, 2020)})
            niv = dict(ex.niveaux or {}); niv["ancre_salaire"] = pd.Series({t: (0.02 if t >= T0 else 0.0) for t in range(2011, 2020)}); ex.niveaux = niv
        elif nom.startswith("cotisations"):
            base = ex.subvention_salaires if ex.subvention_salaires is not None else pd.Series(0.0, index=range(1995, 2031))
            ex.subvention_salaires = base + pd.Series({t: (0.02 if t >= T0 else 0.0) for t in base.index})
            ex.subvention_en_depense = True
        elif nom.startswith("consommations"):
            pi = ex.prix_import.copy()
            for c in pi.columns:
                if c not in EN:
                    pi.loc[T0:, c] = pi.loc[T0:, c] * 1.10
            ex.prix_import = pi
        elif nom.startswith("demande"):
            cp = ex.conso_publique.copy(); cp.loc[T0:] = cp.loc[T0:] * 1.05; ex.conso_publique = cp
        elif nom.startswith("productivité"):
            ex.productivite = pd.Series({t: (0.01 if t == T0 else 0.0) for t in range(2011, 2020)})
    return f

CHOCS = ["pétrole +50 %", "pétrole −30 %", "salaires +2 % durable", "cotisations employeurs −2 % de la masse salariale (coût)",
         "consommations intermédiaires importées hors énergie +10 %", "demande publique +5 % (≈ +1,2 pt de PIB)", "productivité +1 % (permanente)"]
VARS = {"PIB": ("pib", "pct"), "prix conso": ("pc", "pct"), "prix VA marchand": ("pva_m", "pct"), "salaire": ("salaire", "pct"),
        "emploi (milliers)": ("emploi", "diff"), "taux de marge (pt)": ("taux_marge", "diff"), "solde (pt PIB)": ("solde_pib", "diff")}
rows = {}
for cnom, spec in CONF.items():
    base = lab.run(2010, 2019, "v08", spec, retour=True)[1]
    for ch in CHOCS:
        _, r, mod, _ = lab.run(2010, 2019, "v08", spec, exp_mod=choc(ch), retour=True)
        for t in ANS:
            row = {}
            for k, (v, typ) in VARS.items():
                row[k] = 100 * (r[v][t] / base[v][t] - 1) if typ == "pct" else (r[v][t] - base[v][t])
            rows[(ch, cnom, t)] = row
df = pd.DataFrame(rows).T
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200)
print(df.round(2).to_string())
df.to_csv(pathlib.Path(__file__).parent / "resultats" / "a9_chocs_prix.csv")
