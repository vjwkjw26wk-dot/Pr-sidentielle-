"""M20 — Boucle prix-salaires estimée en trimestriel (phase 4.2, A.2).

Secteur marchand = ensemble − administrations, enseignement, santé et action sociale (O-Q). Séries CVS (« SA ») :
  Eurostat namq_10_a10 (D1, B1G en CP_MEUR et CLV15_MEUR), namq_10_a10_e (salariés, milliers),
  namq_10_fcs (P31_S14 : déflateur de la consommation des ménages), namq_10_gdp (P7 : déflateur des importations),
  Insee BDM 001688526 (taux de chômage BIT, France hors Mayotte, trimestriel),
  Commission européenne (Eurostat ei_bsco_m BS-PT-NY : anticipations de prix des consommateurs à 12 mois, solde ;
  ei_bsin_m_r2 BS-ISPE : anticipations de prix de vente des industriels, solde), moyennes trimestrielles.
Limites : volumes chaînés non additifs (VA marchande = total − O-Q en CLV : approximation) ; salariés seulement (pas
d'heures trimestrielles par branche dans cette extraction) ; productivité par salarié.

Équations (correction d'erreur, homogénéité de long terme imposée) :
  W : Δln w   = c + Σ_{i=0..4} b_i Δln pc_{t−i} + d Δln prod + λw (ln w − ln pva − ln prod)_{t−1} + γ (u − u*)_{t−1}
               [+ e · anticipations_{t−1}]
  P : Δln pva = c + Σ_{i=0..2} a_i Δln csu_{t−i} + λp (ln pva − ln csu)_{t−1} [+ κ (u − u*)_{t−1}]
      csu = w / prod (coût salarial unitaire par salarié)
  C : Δln pc  = c + β Δln pva + Σ_{i=0..2} m_i Δln pm_{t−i} + λc (ln pc − s ln pva − (1 − s) ln pm)_{t−1}
      s = part domestique, estimée librement dans une régression de long terme puis imposée.
"""
from __future__ import annotations

import json
import pathlib

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.filters.hp_filter import hpfilter

import m7_series as S

RACINE = pathlib.Path(__file__).resolve().parents[1]


def _L(f):
    from telechargement import jsonstat_dict
    return pd.Series(jsonstat_dict(json.loads((RACINE / "data" / "raw" / f).read_text())))


def _q(s, *k):
    return pd.Series({kk[-1]: v for kk, v in s.items() if tuple(kk[:-1]) == k}, dtype=float).sort_index()


def _trim_mensuel(s):
    s.index = pd.PeriodIndex(s.index, freq="M")
    return s.groupby(s.index.asfreq("Q")).mean()


def donnees() -> pd.DataFrame:
    a, a1, e, c, g = (_L(f) for f in ("eurostat_namq_10_a10_FR.json", "eurostat_namq_10_a10_D1_FR.json", "eurostat_namq_10_a10_e_FR.json",
                                      "eurostat_namq_10_fcs_FR.json", "eurostat_namq_10_gdp_P7_FR.json"))
    D1 = _q(a1, "SA", "TOTAL") - _q(a1, "SA", "O-Q")
    VA = _q(a, "CP_MEUR", "TOTAL", "B1G") - _q(a, "CP_MEUR", "O-Q", "B1G")
    VAv = _q(a, "CLV15_MEUR", "TOTAL", "B1G") - _q(a, "CLV15_MEUR", "O-Q", "B1G")
    SAL = _q(e, "TOTAL", "SA") - _q(e, "O-Q", "SA")
    PC = _q(c, "CP_MEUR") / _q(c, "CLV15_MEUR")
    PM = _q(g, "CP_MEUR", "SCA", "P7") / _q(g, "CLV15_MEUR", "SCA", "P7")
    idx = sorted(set(D1.index) & set(SAL.index) & set(PC.index) & set(VAv.index) & set(PM.index))
    d = pd.DataFrame({"lw": np.log(D1 / SAL), "lpva": np.log(VA / VAv), "lprod": np.log(VAv / SAL), "lpc": np.log(PC),
                      "lpm": np.log(PM)}).loc[idx]
    d.index = pd.PeriodIndex(d.index, freq="Q")
    u = S.bdm("001688526").astype(float)
    u.index = pd.PeriodIndex(u.index, freq="Q")
    cyc, _ = hpfilter(u.loc["1980Q1":], lamb=1600)
    d["u"] = u.reindex(d.index)
    d["ugap"] = cyc.reindex(d.index)
    co, ind = _L("eurostat_ei_bsco_m_FR.json"), _L("eurostat_ei_bsin_m_r2_FR.json")
    d["anticip_conso"] = _trim_mensuel(_q(co, "BS-PT-NY", "SA")).reindex(d.index)
    d["anticip_ind"] = _trim_mensuel(_q(ind, "BS-ISPE", "SA")).reindex(d.index)
    d["lcsu"] = d.lw - d.lprod
    for k in ("lw", "lpva", "lprod", "lpc", "lpm", "lcsu"):
        d["d" + k] = d[k].diff()
    for i in range(1, 5):
        d[f"dlpc_{i}"] = d.dlpc.shift(i)
        d[f"dlcsu_{i}"] = d.dlcsu.shift(i)
        d[f"dlpm_{i}"] = d.dlpm.shift(i)
    d["ecm_w"] = (d.lw - d.lpva - d.lprod).shift(1)
    d["ecm_p"] = (d.lpva - d.lcsu).shift(1)
    d["ugap_1"] = d.ugap.shift(1)
    d["anticip_conso_1"] = (d.anticip_conso / 100).shift(1)
    d["anticip_ind_1"] = (d.anticip_ind / 100).shift(1)
    return d


SPEC = {
    "W": ["dlpc", "dlpc_1", "dlpc_2", "dlpc_3", "dlpc_4", "dlprod", "ecm_w", "ugap_1"],
    "W+anticipations": ["dlpc", "dlpc_1", "dlpc_2", "dlpc_3", "dlpc_4", "dlprod", "ecm_w", "ugap_1", "anticip_conso_1"],
    "P": ["dlcsu", "dlcsu_1", "dlcsu_2", "ecm_p"],
    "P+tension": ["dlcsu", "dlcsu_1", "dlcsu_2", "ecm_p", "ugap_1"],
    "P+anticipations": ["dlcsu", "dlcsu_1", "dlcsu_2", "ecm_p", "anticip_ind_1"],
}


def part_domestique(d, debut="1997Q1", fin="2019Q4"):
    """s dans ln pc = c + s ln pva + (1 − s) ln pm (moindres carrés contraints, niveau)."""
    x = d.loc[debut:fin]
    r = sm.OLS(x.lpc - x.lpm, sm.add_constant(x.lpva - x.lpm)).fit()
    return float(r.params.iloc[1]), r


def regresseurs_c(d, s):
    X = pd.DataFrame({"dlpva": d.dlpva, "dlpm": d.dlpm, "dlpm_1": d.dlpm_1, "dlpm_2": d.dlpm_2,
                      "ecm_c": (d.lpc - s * d.lpva - (1 - s) * d.lpm).shift(1)}, index=d.index)
    return X


def estimer(d, eq, debut="1997Q1", fin="2019Q4", s=None):
    x = d.loc[debut:fin]
    if eq == "C":
        X = regresseurs_c(d, s).loc[debut:fin]
        y = x.dlpc
    else:
        X = x[SPEC[eq]]
        y = x.dlw if eq.startswith("W") else x.dlpva
    ok = X.notna().all(axis=1) & y.notna()
    return sm.OLS(y[ok], sm.add_constant(X[ok])).fit(cov_type="HAC", cov_kwds={"maxlags": 4})


def simuler_systeme(d, rw, rp, rc, s, debut, fin, eqw="W", eqp="P"):
    """Simulation dynamique conjointe : salaires, prix de VA et prix à la consommation endogènes ; productivité,
    prix d'importation, chômage et anticipations observés (conditionnel)."""
    per = pd.period_range(debut, fin, freq="Q")
    lw, lpva, lpc = {}, {}, {}
    for t in pd.period_range(per[0] - 6, per[0] - 1, freq="Q"):
        lw[t], lpva[t], lpc[t] = float(d.lw[t]), float(d.lpva[t]), float(d.lpc[t])
    for t in per:
        # résolution simultanée (point fixe) des trois équations
        lw[t], lpva[t], lpc[t] = lw[t - 1], lpva[t - 1], lpc[t - 1]
        for _ in range(50):
            dlpc = {i: lpc[t - i] - lpc[t - i - 1] for i in range(5)}
            csu = {i: lw[t - i] - float(d.lprod[t - i]) for i in range(4)}
            xw = {"dlpc": dlpc[0], "dlpc_1": dlpc[1], "dlpc_2": dlpc[2], "dlpc_3": dlpc[3], "dlpc_4": dlpc[4],
                  "dlprod": float(d.dlprod[t]), "ecm_w": lw[t - 1] - lpva[t - 1] - float(d.lprod[t - 1]),
                  "ugap_1": float(d.ugap_1[t]), "anticip_conso_1": float(d.anticip_conso_1[t])}
            nw = lw[t - 1] + rw.params["const"] + sum(rw.params[k] * xw[k] for k in SPEC[eqw])
            csu[0] = nw - float(d.lprod[t])
            xp = {"dlcsu": csu[0] - csu[1], "dlcsu_1": csu[1] - csu[2], "dlcsu_2": csu[2] - csu[3],
                  "ecm_p": lpva[t - 1] - csu[1], "ugap_1": float(d.ugap_1[t]), "anticip_ind_1": float(d.anticip_ind_1[t])}
            np_ = lpva[t - 1] + rp.params["const"] + sum(rp.params[k] * xp[k] for k in SPEC[eqp])
            xc = {"dlpva": np_ - lpva[t - 1], "dlpm": float(d.dlpm[t]), "dlpm_1": float(d.dlpm_1[t]), "dlpm_2": float(d.dlpm_2[t]),
                  "ecm_c": lpc[t - 1] - s * lpva[t - 1] - (1 - s) * float(d.lpm[t - 1])}
            nc = lpc[t - 1] + rc.params["const"] + sum(rc.params[k] * xc[k] for k in xc)
            if max(abs(nw - lw[t]), abs(np_ - lpva[t]), abs(nc - lpc[t])) < 1e-10:
                break
            lw[t], lpva[t], lpc[t] = nw, np_, nc
    return pd.DataFrame({"lw": pd.Series(lw), "lpva": pd.Series(lpva), "lpc": pd.Series(lpc)}).loc[per]


def reponse_choc(rw, rp, rc, s, choc="salaire", horizon=60, eqw="W", eqp="P"):
    """Réponses du système homogène (sans tendance) : choc salarial temporaire de 1 % au trimestre 1 (« salaire »),
    ou hausse permanente de 1 % des prix d'importation (« import »). Productivité, chômage, anticipations fixes."""
    n = horizon + 8
    lw, lpva, lpc, lpm = [0.0] * n, [0.0] * n, [0.0] * n, [0.0] * n
    for t in range(6, n):
        lpm[t] = 0.01 if (choc == "import" and t >= 8) else 0.0
        lw[t], lpva[t], lpc[t] = lw[t - 1], lpva[t - 1], lpc[t - 1]
        for _ in range(60):
            dlpc = [lpc[t - i] - lpc[t - i - 1] for i in range(5)]
            xw = dict(zip(["dlpc", "dlpc_1", "dlpc_2", "dlpc_3", "dlpc_4"], dlpc)); xw.update(dlprod=0.0, ecm_w=lw[t - 1] - lpva[t - 1], ugap_1=0.0, anticip_conso_1=0.0)
            nw = lw[t - 1] + sum(rw.params[k] * xw[k] for k in SPEC[eqw]) + (0.01 if (choc == "salaire" and t == 8) else 0.0)
            csu = [nw, lw[t - 1], lw[t - 2], lw[t - 3]]
            xp = {"dlcsu": csu[0] - csu[1], "dlcsu_1": csu[1] - csu[2], "dlcsu_2": csu[2] - csu[3], "ecm_p": lpva[t - 1] - lw[t - 1], "ugap_1": 0.0, "anticip_ind_1": 0.0}
            np_ = lpva[t - 1] + sum(rp.params[k] * xp[k] for k in SPEC[eqp])
            xc = {"dlpva": np_ - lpva[t - 1], "dlpm": lpm[t] - lpm[t - 1], "dlpm_1": lpm[t - 1] - lpm[t - 2], "dlpm_2": lpm[t - 2] - lpm[t - 3],
                  "ecm_c": lpc[t - 1] - s * lpva[t - 1] - (1 - s) * lpm[t - 1]}
            nc = lpc[t - 1] + sum(rc.params[k] * xc[k] for k in xc)
            if max(abs(nw - lw[t]), abs(np_ - lpva[t]), abs(nc - lpc[t])) < 1e-12:
                break
            lw[t], lpva[t], lpc[t] = nw, np_, nc
    return pd.DataFrame({"salaire": lw[8:], "prix VA": lpva[8:], "prix conso": lpc[8:]}) * 100
