"""Multiplicateurs simulés de chocs budgétaires standard (≈ 0,5 point de PIB, permanents à partir de 2028), sous le
régime principal (taux exogènes) et sous le régime BCE + prime. Multiplicateur = ΔPIB (Md€) / coût ex ante (Md€).
Sortie : phase7/resultats/multiplicateurs.csv"""
import pathlib, sys, time, warnings
warnings.filterwarnings("ignore")
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src"), str(R)]
import numpy as np, pandas as pd
import m23_regimes as G, m25_programmes as P

OUT = pathlib.Path(__file__).parent / "resultats"; OUT.mkdir(exist_ok=True)
env_h = G.Environnement.charger("p4", "historique")
env = G.Environnement.charger("p4", "part_constante")
MD = 16.0                                    # ≈ 0,5 point de PIB
CHOCS = {
    "consommation publique (+16 Md€)": ({"autres_depenses": MD}, MD),
    "investissement public (+16 Md€)": ({"investissement_public": MD}, MD),
    "transferts aux ménages (+0,5 pt)": ({"transferts_menages": 0.5}, MD),
    "cotisations employeurs (−16 Md€)": ({"cotisations_employeurs": -MD}, MD),
    "impôts de production (−16 Md€)": ({"impots_production": -MD}, MD),
    "TVA taux normal (−2 pt)": ({"tva": -2.0}, 2 * 8.2),
}
REGIMES = {"principal (taux exogènes)": G.regime("R2"),
           "BCE + prime": G.regime("R2", monetaire={"type": "bce", "prime": "ecart_reference"})}
rows = []
t0 = time.time()
for nom, (cur, cout) in CHOCS.items():
    tr = P.traduire(cur, env_h, nom, microsimulation="calcul", debuts={k: 2028 for k in cur})
    for rn, reg in REGIMES.items():
        e = G.evaluer(env, reg, P.programme(tr))
        a, b = e["variante"]["trajectoire"], e["reference"]["trajectoire"]
        for h in (1, 2, 3, 5, 10, 19):
            t = 2027 + h
            part = 0.005 if "transferts" in nom else cout * 1e3 / float(b.pib_nominal[2025])   # coût ex ante / PIB
            rows.append({"choc": nom, "régime": rn, "horizon (ans)": h,
                         "PIB (%)": 100 * np.log(a.pib[t] / b.pib[t]),
                         "multiplicateur": (a.pib[t] / b.pib[t] - 1) / part,
                         "emploi (milliers)": a.emploi[t] - b.emploi[t],
                         "prix (%)": 100 * np.log(a.pc[t] / b.pc[t]),
                         "solde (pt PIB)": a.solde_pib[t] - b.solde_pib[t],
                         "dette (pt PIB)": a.dette_pib[t] - b.dette_pib[t]})
    print(nom, round(time.time() - t0), flush=True)
df = pd.DataFrame(rows)
df.to_csv(OUT / "multiplicateurs.csv", index=False)
print(df[df["horizon (ans)"].isin([1, 5, 10])].round(2).to_string())
