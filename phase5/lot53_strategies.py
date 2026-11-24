"""Phase 5, lot 5.3 : stratégies S1-S5 dans le moteur à régimes — tableau de robustesse (10 régimes), effets robustes,
sensibilités, changements de classement. Environnement P4 / part_constante. Résultats : phase5/resultats/lot53_*.csv"""
import json, pathlib, pickle, sys, time, warnings
warnings.filterwarnings("ignore")
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src"), str(R)]
import numpy as np, pandas as pd
import m23_regimes as G
import m25_programmes as P

OUT = pathlib.Path(__file__).parent / "resultats"; OUT.mkdir(exist_ok=True)
pd.set_option("display.width", 260); pd.set_option("display.max_rows", 500)
t0 = time.time()
S = P.strategies()
env_h = G.Environnement.charger("p4", "historique")
TR = {k: P.traduire(v["curseurs"], env_h, k) for k, v in S.items()}
pickle.dump(TR, open(OUT / "lot53_traductions.pkl", "wb"))

# contrôle du transfert : sur l'environnement historique, programme transféré = exogènes construites par le simulateur
import sys as _s
_s.path[:0] = [str(R / "rapport")]
from simulateur import executer as X, catalogue as CAT
import m14_heterogeneite as H14
env_h.activer()
CUR = {c["cle"]: c for c in CAT.CURSEURS}
sc = {"nom": "S2_emploi", "horizon": 2047, "hypotheses": {"europe": False, "distribution_dynamique": False},
      "mesures": [CUR[a]["mesure"](v) for a, v in S["S2_emploi"]["curseurs"].items()]}
sauv = _s.modules.get("m10_couplage"); _s.modules["m10_couplage"] = P._module_microsimulation_fige(); aj = H14.ajustement_conso; H14.ajustement_conso = lambda *a, **k: 0.0
ref, var, ans, info = X.construire(sc, env_h.mod, central=env_h.reference)
_s.modules["m10_couplage"] = sauv; H14.ajustement_conso = aj
var.mesure_menages = TR["S2_emploi"]["mesure_menages"]
direct = env_h.mod.simuler(env_h.annees, var)
transf = G.simuler(env_h, G.regime("R0", monetaire={"taux_court_reference": "derive"}), P.programme(TR["S2_emploi"]))["trajectoire"]
ecart_transfert = max(float(((transf[c] - direct[c]).abs() / direct[c].abs().max()).max()) for c in ("pib", "pc", "dette", "emploi"))
print(f"Contrôle du transfert (S2, environnement historique) : écart relatif maximal {ecart_transfert:.1e}")

env = G.Environnement.charger("p4", "part_constante")
tabs = {}
for k in S:
    tabs[k] = G.robustesse(env, P.programme(TR[k]), horizons=(5, 10, 20))
    print("fait", k, round(time.time() - t0), "s", flush=True)
rob = pd.concat(tabs, names=["stratégie"])
rob.to_csv(OUT / "lot53_robustesse_S1_S5.csv")

# synthèse : principal, min et max sur les régimes, accord des signes ; classements par régime
var_ = ["PIB (%)", "emploi (milliers)", "chômage (pt)", "prix (%)", "solde (pt PIB)", "dette (pt PIB)"]
syn = {}
for (k, h), g in rob.groupby(level=["stratégie", "horizon"]):
    g = g.droplevel([0, 2])
    pr = g.loc["principal (R2 figé, taux exogènes, central)"]
    for v in var_:
        x = g[v]
        syn[(k, h, v)] = {"principal": pr[v], "min": x.min(), "max": x.max(), "régime min": x.idxmin(), "régime max": x.idxmax(),
                          "signe robuste": bool((np.sign(x) == np.sign(pr[v])).all() or x.abs().max() < 0.05)}
syn = pd.DataFrame(syn).T; syn.index.names = ["stratégie", "horizon", "variable"]
syn.to_csv(OUT / "lot53_synthese_S1_S5.csv")
print(syn[syn.index.get_level_values(1).isin([10, 20])].round(2).to_string())
cl = {}
for v, asc in (("PIB (%)", False), ("chômage (pt)", True), ("dette (pt PIB)", True), ("prix (%)", True)):
    for h in (10, 20):
        x = rob.xs(h, level="horizon")[v].unstack("stratégie")
        cl[(v, h)] = x.rank(axis=1, ascending=asc).astype(int).apply(lambda r: " > ".join(r.sort_values().index.str.split("_").str[0]), axis=1)
cl = pd.DataFrame(cl)
cl.to_csv(OUT / "lot53_classements_S1_S5.csv")
print(cl.to_string())
(OUT / "lot53_bilan.json").write_text(json.dumps({"controle_transfert": ecart_transfert, "duree_s": time.time() - t0,
                                                   "microsimulation_reprise": {k: v["microsimulation_reprise"] for k, v in TR.items()}}, indent=1))
