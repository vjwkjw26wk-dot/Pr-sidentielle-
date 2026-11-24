"""Phase 5 — audit ciblé avant les lots 5.1-5.3 : (1) taux d'intérêt et dette ; (2) composition de l'ajustement ;
(3) dynamique (écart de production, chômage, retour au potentiel). Environnement P4 / part_constante en cache, aucune
recalibration (vérifiée). Résultats : phase5/resultats/audit_*.csv, audit_bilan.json."""
import json, pathlib, sys, time, warnings
warnings.filterwarnings("ignore")
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src"), str(R)]
import numpy as np, pandas as pd
import m8_reference as RF
import m23_regimes as G

OUT = pathlib.Path(__file__).parent / "resultats"; OUT.mkdir(exist_ok=True)
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 300)
t_debut = time.time()
env = G.Environnement.charger("p4", "part_constante")
def _interdit(*a, **k):
    raise RuntimeError("recalibration interdite")
RF.caler = RF.compte_reference = _interdit
bilan = {}
TC = G.variante_taux_court_observe(2026)
TC27 = G.variante_taux_court_observe(2027)
FAV = G.variante_oat(avec=TC)
AN = (2027, 2031, 2036, 2046)                       # 1, 5, 10, 20 ans


def portefeuille(env, t0=2026):
    """Après une simulation : part de l'encours émise après t0, taux marginal (coupon moyen des émissions de l'année)
    et coupon moyen de l'encours."""
    P = env.mod._pf_etat
    anciens = {(c[0], round(c[1], 6), round(c[2], 9)) for c in P[t0].cohortes}
    out = {}
    for t in sorted(P):
        if t <= t0:
            continue
        cs = P[t].cohortes
        enc = sum(c[1] for c in cs) + P[t].btf
        neuf = sum(c[1] for c in cs if (c[0], round(c[1], 6), round(c[2], 9)) not in anciens) + P[t].btf
        nouv = [c for c in cs if c[0] - t in set(int(m) for m in [2, 3, 5, 7, 10, 15, 20, 30, 50]) and (c[0], round(c[1], 6), round(c[2], 9)) not in anciens]
        em = [c for c in cs if (c[0], round(c[1], 6), round(c[2], 9)) not in anciens and c[0] - t in (2, 3, 5, 7, 10, 15, 20, 30, 50)]
        w = sum(c[1] for c in em)
        out[t] = {"part de l'encours émise après 2026 (%)": 100 * neuf / enc,
                  "coupon marginal des émissions MLT (%)": (sum(c[1] * (c[2] + (P[t]._infl(t) if c[3] else 0)) for c in em) / w) if w else np.nan,
                  "taux des BTF (%)": P[t].taux_btf}
    return pd.DataFrame(out).T


def dynamique_dette(tr):
    """Décomposition Δd = (i − g)/(1 + g) d₋₁ − solde primaire + résidu (flux de créances, en points de PIB)."""
    d = tr.dette_pib; g = tr.pib_nominal.pct_change(); i = tr.interets / tr.dette.shift(1)
    sp = tr.solde_pib + 100 * tr.interets / tr.pib_nominal
    effet = 100 * (i - g) / (1 + g) * d.shift(1) / 100
    return pd.DataFrame({"Δ dette": d.diff(), "effet boule de neige": effet, "−solde primaire": -sp,
                         "résidu": d.diff() - effet + sp, "taux apparent (%)": 100 * i, "croissance nominale (%)": 100 * g,
                         "i − g (pt)": 100 * (i - g)})


# ======================================================================================================== 1. TAUX
print("=" * 30, "1. TAUX D'INTÉRÊT ET DETTE")
sims = {}
for nom, var, reg in [("R0 central", None, "R0"), ("R0 taux court observé (2026)", TC, "R0"), ("R0 taux court observé (2027)", TC27, "R0"),
                      ("R0 taux court observé + OAT 3,82 %", FAV, "R0"),
                      ("R2 central", None, "R2"), ("R2 taux court observé", TC, "R2"), ("R2 taux court observé + OAT 3,82 %", FAV, "R2")]:
    s = G.simuler(env, G.regime(reg), variante_env=var)
    sims[nom] = s
    if nom in ("R0 central", "R0 taux court observé (2026)", "R0 taux court observé + OAT 3,82 %"):
        pf = portefeuille(env)
        pf.to_csv(OUT / f"audit_portefeuille_{nom.split(' ', 1)[1].replace(' ', '_').replace(',', '').replace('%', 'pc').replace('+', 'et')}.csv")
        print(f"\n{nom} — portefeuille :"); print(pf.loc[[2027, 2028, 2031, 2036, 2046]].round(2).to_string())
    dd = dynamique_dette(s["trajectoire"])
    dd.to_csv(OUT / f"audit_dynamique_dette_{len(sims)}.csv")
    if nom in ("R0 central", "R0 taux court observé (2026)"):
        print(f"\n{nom} — dynamique de la dette :"); print(dd.loc[[2027, 2028, 2031, 2036, 2046]].round(2).to_string())

# écart aux cibles de calage induit par la correction du taux court (la recalibration est-elle nécessaire ?)
H = env.R["hypotheses"]
F = H["fmi"]
b, c = sims["R0 central"]["trajectoire"], sims["R0 taux court observé (2026)"]["trajectoire"]
ec = {}
for t in range(2026, 2032):
    gb, gc = 100 * (b.pib[t] / b.pib[t - 1] - 1), 100 * (c.pib[t] / c.pib[t - 1] - 1)
    pb, pcc = 100 * (b.pc[t] / b.pc[t - 1] - 1), 100 * (c.pc[t] / c.pc[t - 1] - 1)
    ec[t] = {"croissance (pt)": gc - gb, "inflation (pt)": pcc - pb, "chômage (pt)": c.chomage[t] - b.chomage[t],
             "taux d'épargne (pt)": c.taux_epargne[t] - b.taux_epargne[t], "solde (pt PIB)": c.solde_pib[t] - b.solde_pib[t]}
ec = pd.DataFrame(ec).T
print("\nÉcart aux cibles de calage induit par la correction du taux court (corrigé − central) :"); print(ec.round(3).to_string())
bilan["ecart_cibles_correction_taux_court_max"] = {k: float(ec[k].abs().max()) for k in ec}

tab1 = {}
for nom, s in sims.items():
    tr = s["trajectoire"]
    for t in AN:
        tab1[(nom, t)] = {"OAT": float(env.R["exogenes"].taux_long.get(t)) if "OAT" not in nom else np.nan, "taux apparent": tr.taux_apparent[t],
                          "intérêts (pt PIB)": 100 * tr.interets[t] / tr.pib_nominal[t], "effort": tr.impose_effort[t],
                          "solde primaire": tr.solde_primaire_pib[t], "solde": tr.solde_pib[t], "dette": tr.dette_pib[t],
                          "PIB (écart à R0 central, %)": 100 * np.log(tr.pib[t] / b.pib[t]), "chômage": tr.chomage[t]}
t1 = pd.DataFrame(tab1).T; t1.index.names = ["simulation", "année"]
t1.to_csv(OUT / "audit_taux.csv")
print("\nSynthèse taux :"); print(t1.drop(columns="OAT").round(2).to_string())

# ============================================================================================= 2. COMPOSITION
print("\n" + "=" * 30, "2. COMPOSITION DE L'AJUSTEMENT (taux court observé)")
ref0 = sims["R0 taux court observé (2026)"]["trajectoire"]
COMPO = {f"consommation publique {int(100 * x)} %": {"conso_publique": x, "prestations": 0.5 - x, "impots_menages": 0.30, "impots_produits": 0.20}
         for x in (0.0, 0.15, 0.30)}
tab2, csims = {}, {}
for nom, parts in COMPO.items():
    s = G.simuler(env, G.regime("R2", parts=parts), variante_env=TC)
    csims[nom] = s
    tr = s["trajectoire"]
    for t in AN:
        tab2[(nom, t - 2026)] = {"effort (pt PIB)": tr.impose_effort[t], "PIB (%)": 100 * np.log(tr.pib[t] / ref0.pib[t]),
                                 "emploi (milliers)": tr.emploi[t] - ref0.emploi[t], "dont non marchand": tr.emploi_non_marchand[t] - ref0.emploi_non_marchand[t],
                                 "chômage (pt)": tr.chomage[t] - ref0.chomage[t], "prix (%)": 100 * np.log(tr.pc[t] / ref0.pc[t]),
                                 "solde (pt PIB)": tr.solde_pib[t] - ref0.solde_pib[t], "dette (pt PIB)": tr.dette_pib[t] - ref0.dette_pib[t],
                                 "dette 2046 (niveau)": tr.dette_pib[t], "écart de production": tr.ecart_production[t]}
t2 = pd.DataFrame(tab2).T; t2.index.names = ["répartition", "horizon"]
t2.to_csv(OUT / "audit_composition.csv")
print(t2.round(2).to_string())

# pourquoi la consommation publique dégrade le ratio de dette : effort imposé de 1 point par instrument, décomposition
dec = {}
for ins in ("conso_publique", "prestations", "impots_menages"):
    reg = G.Regime(budgetaire=G.RegleBudgetaire(type="ajustement", parts={ins: 1.0}))
    v = G.simuler(env, reg, effort_impose={t: 1.0 for t in range(2027, 2048)}, variante_env=TC)["trajectoire"]
    for t in (2027, 2031, 2036):
        Y0, Y1 = ref0.pib_nominal[t], v.pib_nominal[t]
        num = 100 * (v.dette[t] - ref0.dette[t]) / Y0                     # effet du numérateur (dette en M€)
        den = 100 * v.dette[t] * (1 / Y1 - 1 / Y0)                          # effet du dénominateur (PIB nominal)
        vol = 100 * np.log(v.pib[t] / ref0.pib[t]); prix = 100 * np.log((Y1 / v.pib[t]) / (Y0 / ref0.pib[t]))
        mult = -vol if t == 2027 else np.nan
        dec[(ins, t - 2026)] = {"Δ ratio de dette": v.dette_pib[t] - ref0.dette_pib[t], "effet numérateur": num, "effet dénominateur": den,
                                "PIB volume (%)": vol, "déflateur (%)": prix, "dépenses (pt)": 100 * (v.depenses[t] - ref0.depenses[t]) / Y0,
                                "recettes (pt)": 100 * (v.recettes[t] - ref0.recettes[t]) / Y0, "emploi non marchand (milliers)": v.emploi_non_marchand[t] - ref0.emploi_non_marchand[t]}
t3 = pd.DataFrame(dec).T; t3.index.names = ["instrument (1 pt)", "horizon"]
t3.to_csv(OUT / "audit_decomposition_instruments.csv")
print("\nEffort de 1 point imposé (2027-), décomposition du ratio de dette :"); print(t3.round(2).to_string())
d0, tau = float(ref0.dette_pib[2026]) / 100, float(ref0.recettes[2026] / ref0.pib_nominal[2026])
bilan["seuil_multiplicateur_hausse_ratio_court_terme"] = 1 / (d0 + tau)
print(f"Seuil de multiplicateur au-delà duquel un ajustement relève le ratio de dette à court terme : m* = 1/(d + τ) = {1 / (d0 + tau):.2f} (d = {d0:.2f}, τ = {tau:.2f})")

# ============================================================================================= 3. DYNAMIQUE
print("\n" + "=" * 30, "3. DYNAMIQUE : ÉCART DE PRODUCTION ET CHÔMAGE (taux court observé)")
rampe = {t: min(0.5 * (t - 2026), 3.5) for t in range(2027, 2048)}     # +0,5/an jusqu'à 3,5 pt (2033), puis stable
DYN = {"R2 (règle)": dict(reg=G.regime("R2")),
       "R2 sans clause d'écart": dict(reg=G.regime("R2", ecart_suspension=99.0)),
       "rampe 0,5/an puis stable (2033), composition centrale": dict(reg=G.regime("R2"), impose=rampe),
       "rampe puis stable, sans consommation publique": dict(reg=G.regime("R2", parts=COMPO["consommation publique 0 %"]), impose=rampe)}
tab4 = {}
for nom, o in DYN.items():
    tr = G.simuler(env, o["reg"], effort_impose=o.get("impose"), variante_env=TC)["trajectoire"]
    for t in (2029, 2031, 2033, 2036, 2040, 2046):
        tab4[(nom, t)] = {"effort": tr.impose_effort[t], "Δeffort": tr.impose_effort[t] - tr.impose_effort[t - 1], "écart de production": tr.ecart_production[t],
                          "chômage": tr.chomage[t], "chômage − u*": tr.chomage[t] - 7.0, "emploi NM (Δ, milliers)": tr.emploi_non_marchand[t] - ref0.emploi_non_marchand[t],
                          "emploi marchand (Δ, milliers)": (tr.emploi - tr.emploi_non_marchand)[t] - (ref0.emploi - ref0.emploi_non_marchand)[t],
                          "prix (%)": 100 * np.log(tr.pc[t] / ref0.pc[t]), "salaire réel (%)": 100 * np.log((tr.salaire / tr.pc)[t] / (ref0.salaire / ref0.pc)[t]),
                          "dette": tr.dette_pib[t]}
t4 = pd.DataFrame(tab4).T; t4.index.names = ["simulation", "année"]
t4.to_csv(OUT / "audit_dynamique.csv")
print(t4.round(2).to_string())
bilan["ecart_rampe_theorique"] = "écart stationnaire ≈ −(pente de l'effort × multiplicateur) / ρ"
bilan["duree_totale_s"] = time.time() - t_debut
(OUT / "audit_bilan.json").write_text(json.dumps(bilan, indent=1, default=float, ensure_ascii=False))
print("\nDurée totale :", round(time.time() - t_debut), "s")
