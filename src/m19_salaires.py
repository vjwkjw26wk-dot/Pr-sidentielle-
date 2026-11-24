"""M19 — Formation des salaires : indexation retardée et canal du SMIC (phase 4.2, chantier A).

Diagnostic (backtest v0.9, origine 2021) : salaires marchands par tête simulés +2,2 / +1,5 / +1,7 % en 2022-2024 contre
+5,0 / +4,5 / +3,0 % observés. L'équation M7 (Δln w = a + β Δln pc + δ Δln prod + λ (ln w − ln pva − ln prod)_{−1}
+ γ (u − u*)) a une indexation de court terme faible et mal identifiée (β = 0,39 ± 0,22 sur 1997-2019, inflation basse)
et aucun canal de rattrapage.

Variantes comparées (estimées sur 1998-2019, testées hors échantillon sur 2021-2024) :
  W0 : M7 (référence v0.9) ;
  W1 : + inflation de l'année précédente ;
  W2 : + croissance du SMIC horaire (Insee BDM 000822484, moyenne annuelle) ;
  W3 : W2 + inflation de l'année précédente.
Le SMIC est rendu endogène par sa règle légale (code du travail, art. L3231-4 à L3231-11), approchée en annuel :
  Δln SMIC_t = Δln pc_t (revalorisations automatiques infra-annuelles dès 2 % d'inflation, d'où une indexation
  quasi contemporaine en période d'inflation) + ½ max(Δln w_{t−1} − Δln pc_{t−1}, 0) (moitié du gain de pouvoir d'achat
  du salaire horaire ouvrier, ici approché par le salaire moyen marchand) + coup de pouce (décision, exogène).
Limites : le salaire ouvrier (SHBOE) et l'indice des prix des ménages du premier quintile ne sont pas dans le modèle ;
l'approximation annuelle de la règle est vérifiée sur 1998-2024 (voir `regle_smic`).
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd
import statsmodels.api as sm

import m7_series as S

IDBANK_SMIC = "000822484"   # Insee BDM : montant du SMIC brut horaire (€), mensuel


def smic_annuel() -> pd.Series:
    """Moyenne annuelle du SMIC horaire brut (€)."""
    s = S.bdm(IDBANK_SMIC)
    s.index = pd.PeriodIndex(s.index, freq="M")
    return s.groupby(s.index.year).mean()


def donnees(p=None, m=None):
    from statsmodels.tsa.filters.hp_filter import hpfilter
    p = S.panel_branches() if p is None else p
    m = S.macro() if m is None else m
    g = p.groupby("annee")[["wb", "ns", "n", "va_cp", "q"]].sum(min_count=1)
    d = pd.DataFrame({"lw": np.log(g.wb / g.ns), "lpva": np.log(g.va_cp / g.q), "lprod": np.log(g.q / g.n)})
    d["lpc"] = np.log(m.p_c.reindex(d.index))
    d["lsmic"] = np.log(smic_annuel().reindex(d.index))
    cyc, _ = hpfilter(m.chomage.loc[1980:2025].dropna(), lamb=100)
    d["ugap"] = cyc.reindex(d.index)
    for c in ("lw", "lpc", "lprod", "lsmic"):
        d["d" + c] = d[c].diff()
    d["dlpc_1"] = d.dlpc.shift(1)
    d["ecm_1"] = (d.lw - d.lpva - d.lprod).shift(1)                 # cible : part des salaires (prix de VA)
    d["ecm_c_1"] = (d.lw - d.lpc - d.lprod).shift(1)                # cible : salaire réel de consommation / productivité
    d["tdc_1"] = (d.lpc - d.lpva).shift(1)                          # termes de l'échange (prix conso / prix de VA)
    return d


SPECS_W = {"W0 M7 (v0.9)": ["dlpc", "dlprod", "ecm_1"], "W1 + inflation passée": ["dlpc", "dlpc_1", "dlprod", "ecm_1"],
           "W2 + SMIC": ["dlpc", "dlsmic", "dlprod", "ecm_1"], "W3 + SMIC + inflation passée": ["dlpc", "dlpc_1", "dlsmic", "dlprod", "ecm_1"],
           # cible de long terme en prix à la consommation (Mésange) ; W5 : poids libre entre prix de VA et prix conso
           "W4 cible prix conso": ["dlpc", "dlprod", "ecm_c_1"], "W5 cible mixte (poids estimé)": ["dlpc", "dlprod", "ecm_1", "tdc_1"],
           "W6 cible prix conso + SMIC": ["dlpc", "dlsmic", "dlprod", "ecm_c_1"]}


def estimer(d, spec, debut=1998, fin=2019, phillips=None):
    """Estimation par MCO (le terme de Phillips est calibré et retiré de la variable expliquée, comme en M7)."""
    import m7_equations as E
    ph = E.PHILLIPS if phillips is None else phillips
    dd = d.loc[debut:fin]
    y = dd.dlw - ph * dd.ugap
    return sm.OLS(y, sm.add_constant(dd[SPECS_W[spec]])).fit()


def regle_smic(d, t, dlpc_t, dlw_1, dlpc_1, coup_de_pouce=0.0):
    """Croissance annuelle du SMIC selon la règle légale approchée."""
    return dlpc_t + 0.5 * max(dlw_1 - dlpc_1, 0.0) + coup_de_pouce


def simuler(d, r, spec, debut, fin, smic_endogene=False):
    """Simulation dynamique du salaire (prix, productivité, VA et chômage observés)."""
    import m7_equations as E
    lw = {debut - 1: float(d.lw[debut - 1])}
    ls = {debut - 1: float(d.lsmic[debut - 1]), debut - 2: float(d.lsmic[debut - 2])}
    lw[debut - 2] = float(d.lw[debut - 2])
    for t in range(debut, fin + 1):
        x = {"dlpc": d.dlpc[t], "dlpc_1": d.dlpc[t - 1], "dlprod": d.dlprod[t],
             "ecm_1": lw[t - 1] - d.lpva[t - 1] - d.lprod[t - 1], "ecm_c_1": lw[t - 1] - d.lpc[t - 1] - d.lprod[t - 1],
             "tdc_1": d.lpc[t - 1] - d.lpva[t - 1]}
        if smic_endogene:
            ls[t] = ls[t - 1] + regle_smic(d, t, d.dlpc[t], lw[t - 1] - lw[t - 2], d.dlpc[t - 1])
        else:
            ls[t] = float(d.lsmic[t])
        x["dlsmic"] = ls[t] - ls[t - 1]
        lw[t] = lw[t - 1] + r.params["const"] + sum(r.params[k] * x[k] for k in SPECS_W[spec]) + E.PHILLIPS * d.ugap[t]
    return pd.Series(lw), pd.Series(ls)
