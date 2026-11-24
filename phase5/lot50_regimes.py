"""Phase 5, lot 5.0 : environnement calibré une fois, régimes appliqués sans recalibration, programmes ; temps de
calcul, identités, comparaison des références. Résultats : phase5/resultats/lot50_*.csv / .json"""
import copy, json, pathlib, sys, time, warnings
warnings.filterwarnings("ignore")
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src"), str(R)]
import numpy as np, pandas as pd
import m8_reference as RF
import m23_regimes as G

OUT = pathlib.Path(__file__).parent / "resultats"; OUT.mkdir(exist_ok=True)
AN = [2025, 2027, 2031, 2035, 2040, 2047]
pd.set_option("display.width", 250)
bilan = {}

# 1. environnements (cache) ------------------------------------------------------------------------------------------
t0 = time.time(); env = G.Environnement.charger("p4", "part_constante"); bilan["chargement_env_part_constante_s"] = time.time() - t0
t0 = time.time(); env_h = G.Environnement.charger("p4", "historique"); bilan["chargement_env_historique_s"] = time.time() - t0


# interdiction de recalibrer pendant les simulations de régimes
def _interdit(*a, **k):
    raise RuntimeError("recalibration interdite pendant l'application d'un régime")
RF.caler = _interdit
RF.compte_reference = _interdit

# 2. références par régime -------------------------------------------------------------------------------------------
REG = {"R0": G.regime("R0"), "R1": G.regime("R1"), "R2": G.regime("R2"), "R2 symétrique": G.regime("R2_sym"),
       "R2 cible 60 %": G.regime("R2", dette_cible=60.0), "R2 cible 100 %": G.regime("R2", dette_cible=100.0),
       "R2 ancrage faible": G.regime("R2", parametres="ancrage_faible"), "R2 ancrage fort": G.regime("R2", parametres="ancrage_fort")}
res, durees, tab = {}, {}, {}
for nom, reg in REG.items():
    s = G.simuler(env, reg)
    res[nom], durees[nom] = s, s["duree_s"]
    tr = s["trajectoire"]
    for t in AN:
        tab[(nom, t)] = {"PIB (Md€ 2022)": tr.pib[t] / 1e3, "chômage": tr.chomage[t], "prix": tr.pc[t], "effort imposé": tr.impose_effort[t],
                         "solde primaire": tr.solde_primaire_pib[t], "solde": tr.solde_pib[t], "dette": tr.dette_pib[t], "taux apparent": tr.taux_apparent[t]}
s_h = G.simuler(env_h, G.regime("R0"))
for t in AN:
    tr = s_h["trajectoire"]
    tab[("R0 convention historique", t)] = {"PIB (Md€ 2022)": tr.pib[t] / 1e3, "chômage": tr.chomage[t], "prix": tr.pc[t], "effort imposé": 0.0,
                                            "solde primaire": tr.solde_primaire_pib[t], "solde": tr.solde_pib[t], "dette": tr.dette_pib[t], "taux apparent": tr.taux_apparent[t]}
df = pd.DataFrame(tab).T; df.index.names = ["régime", "année"]
df.to_csv(OUT / "lot50_references.csv")
print(df.round(2).to_string())
bilan["durees_regimes_s"] = durees

# 3. contrôles -------------------------------------------------------------------------------------------------------
ctl = {}
r0 = res["R0"]["trajectoire"]
cols = ["pib", "pc", "chomage", "dette", "solde", "emploi"]
ctl["R0 = trajectoire de l'environnement (max écart relatif)"] = float(max((r0[c] - env.reference[c]).abs().max() / env.reference[c].abs().max() for c in cols))
for nom, s in res.items():
    tr = s["trajectoire"]
    d = tr.dette.diff() + tr.solde
    ctl[f"{nom} : identité de la dette 2026-2047 (M€)"] = float(d.loc[2026:].abs().max())
    ctl[f"{nom} : identités du compte des sociétés (M€)"] = float(max(tr._identite_b8g.abs().max(), tr._identite_b9.abs().max()))
    somme = sum(tr[f"impose_effort_{k}"] for k in G.INSTRUMENTS)
    ctl[f"{nom} : effort = somme des instruments"] = float((somme - tr.impose_effort).abs().max())
    if nom != "R0" and "sym" not in nom:
        de = tr.impose_effort.diff().loc[2027:]
        ctl[f"{nom} : 0 ≤ Δeffort ≤ plafond"] = bool((de >= -1e-12).all() and (de <= 0.5 + 1e-12).all())
# régime figé = régime actif pour un programme nul ; effet du programme nul = 0
prog_nul = G.evaluer(env, G.regime("R2"), G.PROGRAMME_NUL, ref=res["R2"])
ctl["programme nul : effet maximal (PIB %, dette pt)"] = float(prog_nul["ecart"][["PIB (%)", "dette (pt PIB)"]].abs().max().max())

# 4. programme test : baisse d'impôts des ménages de 0,5 point de PIB à partir de 2028, non financée
def baisse_impots(mod, ex):
    niv = dict(ex.niveaux or {}); s = niv.get("impots_menages_pib", pd.Series(dtype=float)).copy()
    for t in range(2028, 2048):
        s[t] = float(s.get(t, 0.0)) - 0.5
    niv["impots_menages_pib"] = s.sort_index(); ex.niveaux = niv
P = G.Programme("baisse d'impôts des ménages −0,5 pt de PIB (2028)", baisse_impots)
eff = {}
for nom in ("R0", "R2"):
    t0 = time.time()
    e = G.evaluer(env, G.regime(nom), P, ref=res[nom]); eff[f"{nom} figée"] = e["ecart"]; durees[f"programme sous {nom}"] = time.time() - t0
e = G.evaluer(env, G.regime("R2_actif"), P); eff["R2 active"] = e["ecart"]
rows = {(k, t): v.loc[t].to_dict() for k, v in eff.items() for t in (2028, 2032, 2037, 2047)}
dp = pd.DataFrame(rows).T; dp.index.names = ["régime", "année"]
dp.to_csv(OUT / "lot50_programme_test.csv")
print("\nProgramme test :", P.nom); print(dp.round(2).to_string())

# 5. rendement ex post de l'effort, par instrument (effort imposé de 1 point de 2027 à 2047, régime sans règle)
rend = {}
for ins in G.INSTRUMENTS:
    reg = G.Regime(budgetaire=G.RegleBudgetaire(type="ajustement", parts={ins: 1.0}), nom=ins)
    v = G.simuler(env, reg, effort_impose={t: 1.0 for t in range(2027, 2048)})["trajectoire"]
    for t in (2027, 2031, 2037):
        rend[(ins, t - 2026)] = {"PIB (%)": 100 * np.log(v.pib[t] / r0.pib[t]), "solde (pt)": v.solde_pib[t] - r0.solde_pib[t],
                                 "solde primaire (pt)": v.solde_primaire_pib[t] - r0.solde_primaire_pib[t], "dette (pt)": v.dette_pib[t] - r0.dette_pib[t]}
dr = pd.DataFrame(rend).T; dr.index.names = ["instrument", "année"]
dr.to_csv(OUT / "lot50_rendement_instruments.csv")
print("\nEffort imposé de 1 point par instrument :"); print(dr.round(2).to_string())

bilan["controles"] = ctl
(OUT / "lot50_bilan.json").write_text(json.dumps(bilan, indent=1, default=float, ensure_ascii=False))
print("\nContrôles :"); [print(f"  {k} : {v}") for k, v in ctl.items()]
print("\nDurées (s) :", {k: round(v, 1) for k, v in durees.items()}, "chargements :", round(bilan["chargement_env_part_constante_s"], 1), round(bilan["chargement_env_historique_s"], 1))
