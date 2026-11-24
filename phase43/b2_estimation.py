"""Phase 4.3, chantier B : estimation des comportements du compte des sociétés (M21) et contrôles comptables."""
import pathlib, sys
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src")]
import numpy as np, pandas as pd
import m21_societes as S
pd.set_option("display.width", 250)
d = S.donnees()
cols = ["va", "ebe", "int_nets", "is_", "profit", "div_nets", "b8g", "fbcf", "b9", "dette", "taux_app", "taux_is_app", "taux_long",
        "div_final", "men_d42_recus", "men_d4_nets", "s2_d42_recus"]
t_=d[cols].loc[[1996, 2000, 2005, 2010, 2015, 2019, 2022, 2024]].copy()
for c in cols:
    if not c.startswith('taux'): t_[c]=t_[c]/1e3
print(t_.round(1).to_string())
print("\nContrôle des identités (Md€, max |écart|) :")
chk_b8g = d.b8g - (d.ebe - d.int_nets - d.div_nets - d.d43_nets + d.d44_45_nets - d.is_ + d.autres_courants)
chk_b9 = d.b9 - (d.b8g - d.fbcf - d.autres_capital)
print(f"  B8G : {chk_b8g.abs().max():.2e} (par construction, résidu 'autres courants' : {100*(d.autres_courants/d.va).mean():.2f} % de la VA, écart-type {100*(d.autres_courants/d.va).std():.2f})")
print(f"  B9  : {chk_b9.abs().max():.2e} (résidu 'autres emplois en capital' : {100*(d.autres_capital/d.va).mean():.2f} % de la VA, écart-type {100*(d.autres_capital/d.va).std():.2f})")
est = S.estimer(d)
print("\n" + S.rapport_estimation(est))
# hors échantillon : estimation jusqu'en `fin`, simulation dynamique des dividendes (profit observé, indicatrices connues)
for fin, h in ((2012, range(2013, 2020)), (2014, range(2015, 2020)), (2016, range(2017, 2020)), (2019, range(2022, 2025))):
    e2 = {}   # règle retenue : aucun effet fiscal en central
    a0 = h[0] - 1
    div = {a0: d.div_final[a0]}
    rho0 = d.div_final[a0] / d.profit[a0 - 1]
    Dm = lambda t: (float(t >= 2018), float(2013 <= t <= 2017))
    for t in h:   # règle retenue : taux de distribution de la dernière année observée, effets fiscaux estimés
        rho = rho0 * np.exp(e2.get("pfu", 0.0) * (Dm(t)[0] - Dm(a0)[0]) + e2.get("c3", 0.0) * (Dm(t)[1] - Dm(a0)[1]))
        div[t] = rho * d.profit[t - 1]
    err = [100 * (div[t] / d.div_final[t] - 1) for t in h]
    naif = [100 * (d.div_final[a0] * d.profit[t - 1] / d.profit[a0 - 1] / d.div_final[t] - 1) for t in h]
    print(f"Dividendes, estimation jusqu'en {fin}, simulation {h[0]}-{h[-1]} : erreurs {np.round(err,1)} ; RMSE {np.sqrt(np.mean(np.square(err))):.1f} % "
          f"(règle naïve « part constante du profit de t−1 » : {np.sqrt(np.mean(np.square(naif))):.1f} %)")
# taux apparent hors échantillon (taux court et long observés)
for fin in (2014, 2019):
    p = S.estimer(d, fin=fin, fin_taux=fin)["taux_apparent"].params
    r = {fin: d.taux_app[fin]}
    for t in range(fin + 1, 2025):
        r[t] = r[t - 1] + p["const"] + p["r_court"] * d.taux_court[t] + p["r_long"] * d.taux_long[t] + p["r_app_1"] * r[t - 1]
    print(f"Taux apparent S11, estimé jusqu'en {fin} : erreur (pt) " + ", ".join(f"{t}: {r[t] - d.taux_app[t]:+.2f}" for t in range(fin + 1, 2025)))
    # variante de renouvellement lent μ = 0,35 (mêmes cibles)
    mu, cible = -p["r_app_1"], lambda t: (p["const"] + p["r_court"] * d.taux_court[t] + p["r_long"] * d.taux_long[t]) / -p["r_app_1"]
    r = {fin: d.taux_app[fin]}
    for t in range(fin + 1, 2025):
        r[t] = r[t - 1] + 0.35 * (cible(t) - r[t - 1])
    print(f"   variante μ = 0,35 : " + ", ".join(f"{t}: {r[t] - d.taux_app[t]:+.2f}" for t in range(fin + 1, 2025)))
d.to_csv(pathlib.Path(__file__).parent / "b2_compte_societes_panel.csv")
