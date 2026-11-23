"""Validation du module M17 seul : taux apparent des APU 2011-2019 (taux et déficits observés), contre la règle v0.8."""
import sys, pathlib
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src")]
import numpy as np, pandas as pd
import m17_dette as D
import m8_modele as M
men, apu = M.comptes_menages_apu()
lt, st = D.taux_observes()

rows = {}
for duree in (6.5, 7.0, 7.5):
  for B in (2010, 2014):
      infl = 100 * (M.S.macro().p_c / M.S.macro().p_c.shift(1) - 1)
      P = D.initialiser_historique(apu.dette, B, lt, st, duree_cible=duree, inflation=infl, charge_observee=apu.d41pay)
      P.ecart_initial = P.lam - 1
      ta, ta8 = {}, {}
      t8 = float(apu.d41pay[B] / apu.dette[B - 1])
      for t in range(B + 1, 2020):
          deficit = float(apu.dette[t] - apu.dette[t - 1])     # variation observée de la dette (solde + ajustements)
          r = P.avancer(t, deficit, float(st[t]), float(lt[t]))
          ta[t] = 100 * r["charge"] / float(apu.dette[t - 1])
          t8 += (max(float(lt[t]), 0) / 100 - t8) / 8
          ta8[t] = 100 * t8
      obs = {t: 100 * float(apu.d41pay[t] / apu.dette[t - 1]) for t in ta}
      rows[f"{B} cohortes, durée {duree}"] = ta
      rows[f"{B} règle v0.8 (1/8)"] = ta8
      if B == 2010: rows["observé"] = obs
      print(f"durée {duree} : coefficient de passage comptable λ (2008-2010) = {P.lam:.3f}")
df = pd.DataFrame(rows).T.round(2)
print(df.to_string())
err = {k: float(np.sqrt(np.nanmean([(df.loc[k, t] - df.loc["observé", t]) ** 2 for t in df.columns]))) for k in df.index if k != "observé"}
print("RMSE du taux apparent (points) :", {k: round(v, 2) for k, v in err.items()})
