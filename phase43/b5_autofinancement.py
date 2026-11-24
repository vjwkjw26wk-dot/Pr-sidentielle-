"""Phase 4.3, chantier B : l'investissement des sociétés dépend-il de leur autofinancement ou de leur profitabilité ?
Test sur les comptes de S11 (1997-2019) : équation d'accélérateur en correction d'erreur augmentée du taux d'épargne
(B8G / VA) ou du taux de profit après intérêts et IS, retardés. Non retenu si non significatif (pas de canal ajouté)."""
import pathlib, sys, warnings
warnings.filterwarnings("ignore")
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src")]
import numpy as np, pandas as pd, statsmodels.api as sm
import m21_societes as S, m7_series as S7
d = S.donnees(); mac = S7.macro()
# volumes : FBCF et VA de S11 déflatées par les prix de la FBCF et du PIB (pas de volumes de secteur publiés)
li = np.log(d.fbcf / mac.p_fbcf.reindex(d.index)); lq = np.log(d.va / mac.p_pib.reindex(d.index))
cu = np.log((d.taux_long / 100 + 0.08) * mac.p_fbcf.reindex(d.index) / mac.p_pib.reindex(d.index))
an = [t for t in range(1998, 2020)]
base = pd.DataFrame({"dlq": lq.diff(), "ecart_1": (li - lq).shift(1), "cu_1": cu.shift(1)})
res = {}
for nom, extra in (("accélérateur seul", None), ("+ taux d'épargne t−1", (d.b8g / d.va).shift(1)), ("+ taux de profit t−1", (d.profit / d.va).shift(1)),
                   ("+ Δ taux d'épargne t−1", (d.b8g / d.va).diff().shift(1))):
    X = base.copy()
    if extra is not None:
        X["z"] = extra
    m = sm.OLS(li.diff().loc[an], sm.add_constant(X.loc[an])).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
    res[nom] = m
    z = f"z = {m.params['z']:+.3f} (± {m.bse['z']:.3f}, p = {m.pvalues['z']:.2f})" if "z" in m.params else ""
    print(f"{nom:28s} R² {m.rsquared:.2f}  dlq {m.params['dlq']:+.2f}  écart {m.params['ecart_1']:+.2f}  coût d'usage {m.params['cu_1']:+.2f}  {z}")
