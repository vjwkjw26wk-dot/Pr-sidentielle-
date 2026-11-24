"""Phase 4.4 : sensibilité de la configuration candidate P4 aux paramètres non identifiés ou fragiles.
Base : rétrosimulation 2010-2025 (exogènes observées) ; chocs ADDITIFS en 2011 (demande publique +5 % permanente, coût du
travail −2 % permanent, taux +1 pt permanent) ; écarts à la base à 5 et 15 ans, pour chaque variante de paramètre.
Une variante ne change qu'un paramètre à la fois (les autres au central)."""
import json, pathlib, sys, warnings
warnings.filterwarnings("ignore")
H = pathlib.Path(__file__).resolve(); sys.path[:0] = [str(H.parent), str(H.parents[1] / "phase42" / "a2")]
from lab43 import *  # noqa
from lab43 import P4, run
import numpy as np, pandas as pd
import m7_equations as E
import m8_modele as M
from b5_chocs_ancrage import choc

CHOCS = ["demande publique +5 % permanente", "coût du travail −2 % permanent (subvention)", "taux d'intérêt +1 pt permanent"]
PH0, KP0 = E.PHILLIPS, M.KAPPA_PRIX
VARIANTES = {
    "central": ({}, {}),
    "σ = 0,3": ({"sigma": 0.3}, {}), "σ = 0,6": ({"sigma": 0.6}, {}),
    "Phillips salaires × 0,5": ({}, {"phillips": PH0 * 0.5}), "Phillips salaires × 2": ({}, {"phillips": PH0 * 2}),
    "pente des prix κ × 0,5": ({}, {"kappa": KP0 * 0.5}), "pente des prix κ × 2": ({}, {"kappa": KP0 * 2}),
    "rattrapage salarial 0,17 (T2)": ({"indexation_retard": 0.17}, {}),
    "renouvellement dette SNF μ = 0,35": ({}, {"soc": {"mu_taux": 0.35}}),
    "dette SNF φ = 0,5": ({}, {"soc": {"phi_dette": 0.5}}), "dette SNF φ = 1,5": ({}, {"soc": {"phi_dette": 1.5}}),
    "lissage des dividendes 0,3": ({}, {"soc": {"div_lissage": 0.3}}),
    "fermeture v0.6 (chômage)": ({}, {"clos": "v06"}),
}


def lancer(nom):
    sp, opt = VARIANTES[nom]
    spec = {**P4, **sp}

    def prep(f=None):
        def g(mod, ex):
            E.PHILLIPS = opt.get("phillips", PH0)
            if "kappa" in opt:
                ex.kappa_prix = opt["kappa"]
            if "soc" in opt:
                ex.variante_societes = opt["soc"]
            if f:
                f(mod, ex)
        return g
    clos = opt.get("clos", "v08")
    b = run(2010, 2025, clos, spec, exp_mod=prep(), retour=True)[1]
    out = {}
    for ch in CHOCS:
        v = run(2010, 2025, clos, spec, exp_mod=prep(choc(ch)), retour=True)[1]
        for t in (2015, 2025):
            out[(ch, t - 2010)] = {"PIB (%)": 100 * np.log(v.pib[t] / b.pib[t]), "emploi (milliers)": v.emploi[t] - b.emploi[t],
                                   "prix (%)": 100 * np.log(v.pc[t] / b.pc[t]), "solde (pt PIB)": v.solde_pib[t] - b.solde_pib[t],
                                   "dividendes (%)": 100 * np.log(v.dividendes_distribues[t] / b.dividendes_distribues[t])}
    E.PHILLIPS = PH0
    return out


if __name__ == "__main__":
    noms = sys.argv[1].split("|") if len(sys.argv) > 1 else list(VARIANTES)
    rows = {}
    for n in noms:
        for k, v in lancer(n).items():
            rows[(n,) + k] = v
        print("fait", n, flush=True)
    df = pd.DataFrame(rows).T; df.index.names = ["variante", "choc", "année"]
    suf = "" if len(sys.argv) <= 1 else "_" + str(abs(hash(sys.argv[1])) % 10000)
    df.to_csv(H.parent / "resultats" / f"e1_sensibilite{suf}.csv")
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 400)
    print(df.round(2).to_string())
