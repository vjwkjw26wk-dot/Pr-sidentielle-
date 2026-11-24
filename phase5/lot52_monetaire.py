"""Phase 5, lot 5.2 : politique monétaire et conditions financières — estimations (M24), simulations illustratives.
Environnement P4 / part_constante (revalidé sans recalibration). Résultats : phase5/resultats/lot52_*.csv"""
import json, pathlib, sys, time, warnings
warnings.filterwarnings("ignore")
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src"), str(R)]
import numpy as np, pandas as pd
import m23_regimes as G
import m24_monetaire as M

OUT = pathlib.Path(__file__).parent / "resultats"; OUT.mkdir(exist_ok=True)
pd.set_option("display.width", 260); pd.set_option("display.max_rows", 400)
print(M.rapport())
P = M.parametres()
print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in P.items()})
(OUT / "lot52_parametres.json").write_text(json.dumps(P, indent=1, ensure_ascii=False, default=float))

env = G.Environnement.charger("p4", "part_constante")
AN = (2027, 2028, 2031, 2036, 2046)
perm = {t: 1.0 for t in range(2027, 2048)}


def stimulus(mod, ex):
    """Programme test : consommation publique +1 point de PIB à partir de 2027 (non financé)."""
    part = float(mod.macro.g_cp[mod.B] / mod.macro.pib_cp[mod.B])
    ex.conso_publique = ex.conso_publique * pd.Series({t: (1 + 0.01 / part if t >= 2027 else 1.0) for t in ex.conso_publique.index})
STIM = G.Programme("consommation publique +1 pt de PIB", stimulus)

CAS = {
    "1. taux directeur +1 pt permanent (exogène)": (G.regime("R0", monetaire={"chocs_directeur": perm}), None, "R0"),
    "2. taux directeur +1 pt en 2027 (règle BCE)": (G.regime("R0", monetaire={"type": "bce", "chocs_directeur": {2027: 1.0}}), None, "R0"),
    "3. idem, anticipations rationnelles": (G.regime("R0", monetaire={"type": "bce", "anticipations": "rationnelles", "chocs_directeur": {2027: 1.0}}), None, "R0"),
    "4. écart OAT-Bund +1 pt permanent": (G.regime("R0", monetaire={"chocs_ecart_souverain": perm}), None, "R0"),
    "5. inflation du reste de la zone +1 pt (2027-2028), règle BCE": (G.regime("R0", monetaire={"type": "bce", "chocs_inflation_ze": {2026: 1.0, 2027: 1.0}}), None, "R0"),
    "6. stimulus, taux exogènes": (G.regime("R0"), STIM, "R0"),
    "7. stimulus, règle BCE": (G.regime("R0", monetaire={"type": "bce"}), STIM, "R0"),
    "8. stimulus, règle BCE + prime estimée": (G.regime("R0", "bce"), STIM, "R0"),
    "9. stimulus, BCE + prime forte (3 pb/pt de dette, 10 pb/pt de déficit)": (G.regime("R0", monetaire={"type": "bce", "prime": "ecart_reference", "prime_dette": 0.03, "prime_solde": -0.10}), STIM, "R0"),
    "10. R2 avec BCE et prime, écart à R2 à taux exogènes": (G.regime("R2", "bce"), None, "R2"),
    "11. R0, prime « niveau » (1,3 pb/pt de dette depuis 2026)": (G.regime("R0", monetaire={"prime": "niveau"}), None, "R0"),
}
ref = {"R0": G.simuler(env, G.regime("R0")), "R2": G.simuler(env, G.regime("R2"))}
rows, durees = {}, {}
for nom, (reg, prog, base) in CAS.items():
    t0 = time.time()
    b = ref[base]["trajectoire"]
    v = G.simuler(env, reg, prog or G.PROGRAMME_NUL)["trajectoire"]
    durees[nom] = time.time() - t0
    for t in AN:
        rows[(nom, t)] = {
            "PIB (%)": 100 * np.log(v.pib[t] / b.pib[t]), "prix (%)": 100 * np.log(v.pc[t] / b.pc[t]),
            "chômage (pt)": v.chomage[t] - b.chomage[t],
            "taux directeur (pt)": v.mon_taux_directeur[t] - b.mon_taux_directeur[t], "OAT (pt)": v.mon_oat[t] - b.mon_oat[t],
            "écart souverain (pt)": v.mon_ecart_souverain[t] - b.mon_ecart_souverain[t],
            "crédit ménages (pt)": v.mon_ecart_credit_menages[t] - b.mon_ecart_credit_menages[t],
            "crédit SNF (pt)": v.mon_ecart_credit_entreprises[t] - b.mon_ecart_credit_entreprises[t],
            "intérêts APU (Md€)": (v.interets[t] - b.interets[t]) / 1e3, "taux apparent APU (pt)": v.taux_apparent[t] - b.taux_apparent[t],
            "intérêts SNF (Md€)": (v.interets_s11[t] - b.interets_s11[t]) / 1e3, "FBCF (%)": 100 * np.log(v.fbcf[t] / b.fbcf[t]),
            "solde (pt PIB)": v.solde_pib[t] - b.solde_pib[t], "dette (pt PIB)": v.dette_pib[t] - b.dette_pib[t]}
    print("fait", nom, f"{durees[nom]:.1f} s", flush=True)
df = pd.DataFrame(rows).T; df.index.names = ["simulation", "année"]
df.to_csv(OUT / "lot52_simulations.csv")
print(df.round(2).to_string())
print("Durées :", {k[:3]: round(v, 1) for k, v in durees.items()})
