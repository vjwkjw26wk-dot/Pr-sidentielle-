"""Lot 7 — Équations de comportement estimées sur séries françaises (1996-2019, hors années Covid).

Forme commune : modèle à correction d'erreur (MCE) en une étape,
    Δy_t = a + Σ β Δx_t + λ (y − θ·x)_{t−1} + ε_t ,   λ < 0 : vitesse de retour vers la cible de long terme.
Il est estimé par moindres carrés ordinaires sur le niveau retardé (y_{t−1}, x_{t−1}) ; θ = −coef(x_{t−1}) / λ.
Équations de branche : panel des 25 branches marchandes (`m7_series.BRANCHES`), effets fixes de branche (et tendances
de branche pour l'emploi), pentes communes ; écarts types robustes groupés par année (chocs communs).
Équations macroéconomiques (salaires, consommation, commerce extérieur) : séries agrégées.
Critère de cointégration : t de λ comparé aux valeurs critiques du test de Banerjee, Dolado et Mestre (≈ −3,5 à 5 %
pour 2-3 régresseurs ; pour les panels, valeur indicative).

Chaque équation renvoie un objet `Equation` (coefficients, écarts types, élasticités de long terme, diagnostics) et une
fonction de simulation dynamique utilisée dans les tests rétrospectifs.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.diagnostic import acorr_breusch_godfrey

import m7_series as S

DEBUT, FIN = 1997, 2019


@dataclass
class Equation:
    nom: str
    variable: str
    res: object
    lr: dict = field(default_factory=dict)          # élasticités de long terme
    note: str = ""

    def coef(self, k):
        return float(self.res.params[k])

    def tableau(self, garder) -> list:
        L = []
        for k in garder:
            if k in self.res.params:
                L.append((k, self.res.params[k], self.res.bse[k], self.res.tvalues[k]))
        return L


def _ols(y, X, groupes=None):
    X = sm.add_constant(X, has_constant="skip")
    if groupes is None:
        return sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": 1})
    return sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": groupes})


def _prep_panel(p: pd.DataFrame, debut=DEBUT, fin=FIN) -> pd.DataFrame:
    d = p.sort_values(["branche", "annee"]).copy()
    L = lambda c: np.log(d[c])  # noqa: E731
    d["cn"] = d.wb / d.ns                        # coût par salarié
    for c in ("q", "h", "n", "cs", "cn", "pva", "clu", "i", "k", "y"):
        d["l" + c] = L(c)
    g = d.groupby("branche")
    for c in ("lq", "lh", "ln", "lcs", "lcn", "lpva", "lclu", "li", "lk"):
        d["d" + c] = g[c].diff()
        d[c + "_1"] = g[c].shift(1)
        d["d" + c + "_1"] = g["d" + c].shift(1)
    d["lrc_1"] = (d.lcs - d.lpva).groupby(d.branche).shift(1)       # coût réel horaire du travail (en prix de la VA)
    d["lrcn_1"] = (d.lcn - d.lpva).groupby(d.branche).shift(1)      # coût réel par tête
    tau = S.taux_is()
    d["pm_net"] = d.pm.clip(lower=0.02) * (1 - d.annee.map(tau) / 100)
    d["lpmnet_1"] = np.log(d.pm_net).groupby(d.branche).shift(1)
    d["t"] = d.annee - 2010
    d["rupture_2008"] = (d.annee - 2008).clip(lower=0)        # ralentissement commun de la productivité après 2008
    return d[(d.annee >= debut) & (d.annee <= fin)].dropna(subset=["dlq", "lq_1", "dlh"])


# --------------------------------------------------------------------------------------------------------------
# 1. Demande de travail (heures) par branche
#    Δln h = a_i + b_i t + β0 Δln q + β1 Δln h_{t−1} + λ [ln h − ln q + σ ln(cs/pva)]_{t−1}
# --------------------------------------------------------------------------------------------------------------
SIGMA_TRAVAIL = 0.4   # élasticité de substitution capital-travail (calibrée : non identifiée sur ces données, voir doc)


def _poids_branche(d):
    w = d.groupby("branche").h.transform("mean")
    return w / w.mean()


def emploi(p, debut=DEBUT, fin=FIN, sigma=SIGMA_TRAVAIL, mesure="n") -> Equation:
    """Long terme contraint à rendements constants : ln N = ln q − σ ln(coût/pva) + tendance de productivité de branche.
    Mesure retenue : l'emploi en personnes (`n`) ; la durée du travail par personne est traitée à part (exogène, car
    largement réglementaire : réduction du temps de travail de 1998-2002). Variante `mesure="h"` : heures.
    Estimé en moindres carrés pondérés par la taille de la branche (heures moyennes)."""
    d = _prep_panel(p, debut, fin)
    if mesure == "n":
        d = d.assign(lh=d.ln, dlh=d.dln, lh_1=d.ln_1, dlh_1=d.dln_1, lrc_1=d.lrcn_1)
    ecm = d.lh_1 - d.lq_1 + sigma * d.lrc_1
    X = pd.DataFrame({"dlq": d.dlq, "dlq_1": d.dlq_1, "dlh_1": d.dlh_1, "ecm_1": ecm, "rupture_2008": d.rupture_2008})
    X = pd.concat([X, pd.get_dummies(d.branche, prefix="fe", drop_first=True, dtype=float),
                   pd.get_dummies(d.branche, prefix="tr", dtype=float).mul(d.t, axis=0)], axis=1)
    ok = X.notna().all(axis=1)
    Xc = sm.add_constant(X[ok])
    r = sm.WLS(d.dlh[ok], Xc, weights=_poids_branche(d)[ok]).fit(cov_type="cluster", cov_kwds={"groups": d.annee[ok]})
    # test de la contrainte : version libre
    Xl = pd.concat([pd.DataFrame({"dlq": d.dlq, "dlq_1": d.dlq_1, "dlh_1": d.dlh_1, "lh_1": d.lh_1, "lq_1": d.lq_1, "lrc_1": d.lrc_1}),
                    X.filter(regex="^(fe|tr)_")], axis=1)
    rl = sm.WLS(d.dlh[ok], sm.add_constant(Xl[ok]), weights=_poids_branche(d)[ok]).fit()
    e = Equation("Demande de travail (" + ("emploi en personnes" if mesure == "n" else "heures") + "), 25 branches",
                 "Δln emploi" if mesure == "n" else "Δln heures", r,
                 {"élasticité de court terme aux volumes": r.params["dlq"], "vitesse d'ajustement λ": r.params["ecm_1"],
                  "élasticité de long terme aux volumes (contrainte)": 1.0,
                  "élasticité de long terme au coût réel (calibrée)": -sigma,
                  "version libre : élasticité de long terme aux volumes": -rl.params["lq_1"] / rl.params["lh_1"],
                  "version libre : élasticité au coût réel": -rl.params["lrc_1"] / rl.params["lh_1"]})
    e.mesure = mesure
    return e


# --------------------------------------------------------------------------------------------------------------
# 2. Prix de la valeur ajoutée (taux de marge) par branche
#    Δln pva = a_i + α0 Δln clu + α1 Δln q + λ [ln pva − ln clu]_{t−1}
#    Long terme : prix = coût salarial unitaire × marge propre à la branche (homogénéité testée).
# --------------------------------------------------------------------------------------------------------------
def prix_va(p, debut=DEBUT, fin=FIN) -> Equation:
    d = _prep_panel(p, debut, fin)
    X = pd.DataFrame({"dlclu": d.dlclu, "dlq": d.dlq, "ecm_1": d.lpva_1 - d.lclu_1})
    X = pd.concat([X, pd.get_dummies(d.branche, prefix="fe", drop_first=True, dtype=float)], axis=1)
    ok = X.notna().all(axis=1)
    r = sm.WLS(d.dlpva[ok], sm.add_constant(X[ok]), weights=_poids_branche(d)[ok]).fit(cov_type="cluster", cov_kwds={"groups": d.annee[ok]})
    Xl = pd.concat([pd.DataFrame({"dlclu": d.dlclu, "dlq": d.dlq, "lpva_1": d.lpva_1, "lclu_1": d.lclu_1}), X.filter(regex="^fe_")], axis=1)
    rl = sm.WLS(d.dlpva[ok], sm.add_constant(Xl[ok]), weights=_poids_branche(d)[ok]).fit()
    return Equation("Prix de la valeur ajoutée, 25 branches", "Δln prix VA", r,
                    {"transmission de court terme du coût salarial unitaire": r.params["dlclu"],
                     "effet de court terme de la demande (volume)": r.params["dlq"],
                     "vitesse de retour de la marge λ": r.params["ecm_1"],
                     "version libre : transmission de long terme (1 = homogénéité)": -rl.params["lclu_1"] / rl.params["lpva_1"]})


# --------------------------------------------------------------------------------------------------------------
# 3. Investissement par branche (accélérateur, profitabilité après impôt sur les sociétés, coût du capital)
#    Δln I = a_i + β0 Δln q + β1 Δln q_{t−1} + λ [ln I − ln q]_{t−1} + θ ln(πnet)_{t−1} + φ r_{t−1}
#    πnet = part des profits × (1 − taux normal d'IS) ; r = taux long réel (OAT 10 ans − inflation de la FBCF).
# --------------------------------------------------------------------------------------------------------------
def investissement(p, m, debut=DEBUT, fin=FIN) -> Equation:
    """Branches : accélérateur à correction d'erreur ; cible de long terme ln I = a_i + θq ln q + θk ln k."""
    d = _prep_panel(p, debut, fin)
    X = pd.DataFrame({"dlq": d.dlq, "dlq_1": d.dlq_1, "li_1": d.li_1, "lk_1": d.lk_1, "lq_1": d.lq_1})
    X = pd.concat([X, pd.get_dummies(d.branche, prefix="fe", drop_first=True, dtype=float)], axis=1)
    ok = X.notna().all(axis=1) & np.isfinite(d.dli)
    r = sm.WLS(d.dli[ok], sm.add_constant(X[ok]), weights=_poids_branche(d)[ok]).fit(cov_type="cluster", cov_kwds={"groups": d.annee[ok]})
    lam = r.params["li_1"]
    return Equation("Investissement (FBCF en volume), 25 branches : accélérateur", "Δln FBCF", r,
                    {"élasticité de court terme aux volumes": r.params["dlq"], "vitesse λ": lam,
                     "long terme : élasticité aux volumes": -r.params["lq_1"] / lam,
                     "long terme : élasticité au capital installé": -r.params["lk_1"] / lam})


DELTA_USAGE = 0.07    # taux de dépréciation retenu dans le coût d'usage (FBCF / capital net, moyenne 1995-2019 ≈ 7 %)


def serie_snf(m) -> pd.DataFrame:
    import json
    from telechargement import jsonstat_dict
    s = pd.Series(jsonstat_dict(json.loads(S.telecharger(
        S.B + "nasa_10_nf_tr?format=JSON&geo=FR&unit=CP_MEUR&sector=S11&direct=PAID&direct=RECV&na_item=B2A3G&na_item=D51&na_item=B1G&na_item=P51G&sinceTimePeriod=1995",
        "eurostat_nasa_10_nf_tr_S11_FR.json").read_text())))
    an = list(range(1995, 2026))
    g = lambda it: pd.Series([float(s.get(("PAID", it, str(t)), s.get(("RECV", it, str(t)), np.nan))) for t in an], index=an)  # noqa: E731
    pfb = (m.fbcf_cp / m.fbcf).reindex(an)
    ppib = (m.pib_cp / m.pib).reindex(an)
    d = pd.DataFrame({"va": g("B1G"), "ebe": g("B2A3G"), "fbcf": g("P51G"), "is": g("D51")})
    d["iv"] = d.fbcf / pfb
    d["qv"] = d.va / ppib
    d["taux_marge"] = d.ebe / d.va
    infl = np.log(pfb).diff() * 100        # inflation réalisée du prix de la FBCF (la variante anticipée, moyenne des
    #                                        3 années passées, dégrade la prévision hors échantillon : voir doc)
    d["r_reel"] = m.taux_long.reindex(an) - infl
    d["tau_is"] = S.taux_is().reindex(an)
    d["cout_usage"] = (d.r_reel.clip(lower=-5) / 100 + DELTA_USAGE) * pfb / ppib / (1 - d.tau_is / 100)
    return d


def investissement_snf(m, debut=DEBUT, fin=FIN) -> Equation:
    """Sociétés non financières (agrégat) : effets du coût d'usage du capital (taux d'intérêt, prix relatif, impôt sur
    les sociétés) et du taux de marge, non identifiables au niveau des branches.
    Δln I = a + β0 Δln Q + β1 Δln Q_{t−1} + λ (ln I − ln Q)_{t−1} + θ taux de marge_{t−1} + φ ln(coût d'usage)_{t−1}"""
    d = serie_snf(m)
    li, lq = np.log(d.iv), np.log(d.qv)
    X = pd.DataFrame({"dlq": lq.diff(), "dlq_1": lq.diff().shift(1), "ecm_1": (li - lq).shift(1),
                      "tm_1": d.taux_marge.shift(1), "lcu_1": np.log(d.cout_usage).shift(1)})
    y = li.diff()
    ok = (d.index >= debut) & (d.index <= fin) & X.notna().all(axis=1)
    r = _ols(y[ok], X[ok])
    lam = r.params["ecm_1"]
    e = Equation("Investissement des sociétés non financières (agrégat)", "Δln FBCF des SNF", r,
                 {"élasticité de court terme à la valeur ajoutée": r.params["dlq"], "vitesse λ": lam,
                  "long terme : élasticité au coût d'usage du capital": -r.params["lcu_1"] / lam,
                  "long terme : semi-élasticité au taux de marge (par point de VA)": -r.params["tm_1"] / lam / 100,
                  "long terme : effet d'une baisse de 1 point du taux d'IS (≈ 25 %)":
                      (-r.params["lcu_1"] / lam) * np.log((1 - 0.25) / (1 - 0.24))})
    e.data = d
    return e


# --------------------------------------------------------------------------------------------------------------
# 4. Salaire horaire du secteur marchand (courbe WS)
#    Δln cs = a + β1 Δln pc + β2 Δln prod + γ u + λ [ln cs − ln pva − ln prod]_{t−1}
# --------------------------------------------------------------------------------------------------------------
def _agreger_marchand_inutilise(p) -> pd.DataFrame:
    g = p.groupby("annee")[["wb", "hs", "h", "va_cp", "q"]].sum(min_count=1)
    g["cs"] = g.wb / g.hs
    g["pva"] = g.va_cp / g.q
    g["productivite"] = g.q / g.h
    return g


PHILLIPS = -0.004   # effet d'un point d'écart du chômage à sa tendance sur la croissance du salaire (calibré, voir doc)


def salaires(p, m, debut=DEBUT, fin=FIN, phillips=PHILLIPS) -> Equation:
    """Salaire moyen par salarié (et non horaire : la réduction du temps de travail de 1998-2002 fausse le salaire
    horaire). Δln w = a + β Δln pc + λ (ln w − ln pva − ln prod)_{t−1} + γ (u − u*) ; γ calibré."""
    from statsmodels.tsa.filters.hp_filter import hpfilter
    g = p.groupby("annee")[["wb", "ns", "n", "va_cp", "q"]].sum(min_count=1)
    lw, lpva, lprod = np.log(g.wb / g.ns), np.log(g.va_cp / g.q), np.log(g.q / g.n)
    lpc = np.log(m.p_c.reindex(g.index))
    cyc, _ = hpfilter(m.chomage.loc[1980:2025].dropna(), lamb=100)
    ugap = cyc.reindex(g.index)
    y = lw.diff() - phillips * ugap
    X = pd.DataFrame({"dlpc": lpc.diff(), "dlprod": lprod.diff(), "ecm_1": (lw - lpva - lprod).shift(1)})
    ok = (g.index >= debut) & (g.index <= fin) & X.notna().all(axis=1)
    r = _ols(y[ok], X[ok])
    rl = _ols(lw.diff()[ok], X.assign(ugap=ugap)[ok])
    e = Equation("Salaire moyen par tête, secteur marchand", "Δln salaire par tête", r,
                 {"indexation de court terme sur les prix à la consommation": r.params["dlpc"],
                  "effet de court terme de la productivité": r.params["dlprod"],
                  "vitesse de retour de la part des salaires λ": r.params["ecm_1"],
                  "effet d'un point d'écart de chômage (calibré)": phillips,
                  "effet estimé librement (biaisé par la composition de l'emploi)": rl.params["ugap"]})
    e.ugap = ugap
    return e


# --------------------------------------------------------------------------------------------------------------
# 5. Consommation des ménages
#    Δln C = a + β Δln RDBr + γ Δu + λ [ln C − ln RDBr]_{t−1}
# --------------------------------------------------------------------------------------------------------------
def consommation(m, debut=DEBUT, fin=FIN) -> Equation:
    rdbr = np.log(m.rdb / m.p_c)
    lc = np.log(m.c)
    y = lc.diff()
    X = pd.DataFrame({"dlrdb": rdbr.diff(), "du": m.chomage.diff(), "ecart_1": (lc - rdbr).shift(1)})
    ok = (m.index >= debut) & (m.index <= fin)
    r = _ols(y[ok], X[ok])
    return Equation("Consommation des ménages (volume)", "Δln consommation", r,
                    {"propension marginale de court terme (élasticité)": r.params["dlrdb"], "vitesse λ": r.params["ecart_1"]})


# --------------------------------------------------------------------------------------------------------------
# 6-7. Commerce extérieur (biens et services)
#    Importations : Δln M = a + β Δln D + ε Δln(pm/pd) + λ [ln M − ln D − ε_lt ln(pm/pd)]_{t−1} + τ t
#      D = demande totale en volume (consommation, FBC, exportations, pondérées par leur contenu en importations
#      du tableau entrées-sorties 2019) ; pd = prix du PIB.
#    Exportations : Δln X = a + β Δln DM + ε Δln(px/pw) + λ [ln X − ln DM − ε_lt ln(px/pw)]_{t−1}
#      DM = importations en volume de l'Union européenne (proxy de la demande mondiale adressée), pw = leur prix.
# --------------------------------------------------------------------------------------------------------------
CONTENU_IMPORT = {"c": 0.13, "g": 0.06, "fbc": 0.23, "x": 0.33}   # contenu direct et indirect, TES 2019 (voir m5)


def demande_ponderee(m) -> pd.Series:
    return sum(w * m[k] for k, w in CONTENU_IMPORT.items())


def importations(m, debut=DEBUT, fin=FIN) -> Equation:
    D = demande_ponderee(m)
    lm, ld = np.log(m.m), np.log(D)
    lprel = np.log(m.p_m / m.p_pib)
    y = lm.diff()
    X = pd.DataFrame({"dld": ld.diff(), "dlprel": lprel.diff(), "lm_1": lm.shift(1), "ld_1": ld.shift(1),
                      "lprel_1": lprel.shift(1), "t": m.index - 2010})
    ok = (m.index >= debut) & (m.index <= fin)
    r = _ols(y[ok], X[ok])
    lam = r.params["lm_1"]
    return Equation("Importations (volume)", "Δln importations", r,
                    {"élasticité à la demande, court terme": r.params["dld"],
                     "élasticité à la demande, long terme": -r.params["ld_1"] / lam,
                     "élasticité-prix, long terme": -r.params["lprel_1"] / lam,
                     "tendance annuelle de pénétration": -r.params["t"] / lam, "vitesse λ": lam})


def exportations(m, debut=DEBUT, fin=FIN) -> Equation:
    """Aucune relation de long terme n'est identifiée sur données annuelles 1997-2019 (λ non significatif, instable entre
    sous-périodes). Forme retenue en différences : Δln X = a + β Δln DM + ε Δln(px/pw) ; la constante mesure la
    tendance des parts de marché à demande et prix relatifs inchangés.
    DM : importations en volume de l'Union européenne ; pw : leur prix (prix des concurrents, approché).
    Variante testée (`m7_series.demande_mondiale_adressee`, FMI : importations des partenaires pondérées par les
    exportations françaises) : moins bonne hors échantillon sur 2013-2019 (erreur de niveau −9,5 % contre −0,2 %),
    meilleure sur 2022-2024 (−6,6 % contre −10,3 % dans le modèle bouclé). La demande de l'UE reste la référence."""
    lx, ldm = np.log(m.x), np.log(m.ue_m)
    lprel = np.log(m.p_x / m.p_ue_m)
    X = pd.DataFrame({"dldm": ldm.diff(), "dlprel": lprel.diff()})
    ok = (m.index >= debut) & (m.index <= fin)
    r = _ols(lx.diff()[ok], X[ok])
    Xl = X.assign(lx_1=lx.shift(1), ldm_1=ldm.shift(1), lprel_1=lprel.shift(1))
    rl = _ols(lx.diff()[ok], Xl[ok])
    return Equation("Exportations (volume)", "Δln exportations", r,
                    {"élasticité à la demande mondiale": r.params["dldm"], "élasticité-prix": r.params["dlprel"],
                     "tendance des parts de marché (% par an)": (r.params["const"]) * 100,
                     "forme à correction d'erreur : λ (t)": f"{rl.params['lx_1']:.3f} ({rl.tvalues['lx_1']:.1f})"})


def transmission_importations(p, m, debut=1998, fin=2024) -> Equation:
    """Délai de transmission des prix d'importation aux prix à la consommation :
    Δln pc = a + b0 Δln pm + b1 Δln pm_{t−1} + c0 Δln clu + c1 Δln clu_{t−1} + ρ Δln pc_{t−1}.
    Sur 1998-2019, la transmission est immédiate (b1 ≈ 0) ; l'épisode 2021-2024 révèle un délai important (tarifs
    réglementés, bouclier tarifaire, contrats). L'estimation retenue couvre 1998-2024 ; la part transmise l'année même
    θ = b0 / (b0 + b1) sert de paramètre d'ajustement partiel des prix d'importation dans le modèle bouclé."""
    g = p.groupby("annee")[["wb", "ns", "n", "q"]].sum()
    clu = np.log(g.wb / g.ns * g.n / g.q)
    pc, pm = np.log(m.p_c), np.log(m.p_m)
    X = pd.DataFrame({"dlpm": pm.diff(), "dlpm_1": pm.diff().shift(1), "dlclu": clu.diff(), "dlclu_1": clu.diff().shift(1),
                      "dlpc_1": pc.diff().shift(1)})
    ok = (m.index >= debut) & (m.index <= fin) & X.reindex(m.index).notna().all(axis=1)
    r = _ols(pc.diff()[ok], X.reindex(m.index)[ok])
    r19 = _ols(pc.diff()[ok & (m.index <= 2019)], X.reindex(m.index)[ok & (m.index <= 2019)])
    th = r.params["dlpm"] / (r.params["dlpm"] + r.params["dlpm_1"])
    return Equation("Transmission des prix d'importation aux prix à la consommation", "Δln prix de la consommation", r,
                    {"transmission immédiate b0": r.params["dlpm"], "transmission l'année suivante b1": r.params["dlpm_1"],
                     "part transmise l'année même θ": th,
                     "sur 1998-2019 seulement : b0": r19.params["dlpm"], "sur 1998-2019 seulement : b1": r19.params["dlpm_1"]})


def revenus_menages(m, men, poste, debut=DEBUT, fin=FIN) -> Equation:
    """Revenus des ménages hors salaires et prestations (M€ courants) : `d4` revenus de la propriété nets (intérêts,
    dividendes), `ebe` excédent brut et revenu mixte (entrepreneurs individuels, loyers imputés).
    Δln y = a + β Δln PIB nominal + γ Δln pc + λ (ln y − ln PIB nominal)_{t−1} + φ taux long_{t−1}."""
    y = np.log(men[poste])
    pibn = np.log(m.pib_cp.reindex(men.index))
    pc = np.log(m.p_c.reindex(men.index))
    r = m.taux_long.reindex(men.index)
    X = pd.DataFrame({"dpibn": pibn.diff(), "dpc": pc.diff(), "ecm_1": (y - pibn).shift(1), "r_1": r.shift(1)})
    ok = (men.index >= debut) & (men.index <= fin) & X.notna().all(axis=1)
    res = _ols(y.diff()[ok], X[ok])
    nom = {"d4": "Revenus de la propriété nets des ménages", "ebe": "Excédent brut et revenu mixte des ménages"}[poste]
    return Equation(nom, f"Δln {poste}", res, {"élasticité de court terme au PIB nominal": res.params["dpibn"],
                                                "effet des prix": res.params["dpc"], "vitesse λ": res.params["ecm_1"],
                                                "long terme : semi-élasticité au taux long (par point)": -res.params["r_1"] / res.params["ecm_1"]})


def diagnostics(e: Equation) -> dict:
    out = {"n": int(e.res.nobs), "R²": e.res.rsquared, "écart type résiduel": float(np.sqrt(e.res.scale))}
    try:
        out["autocorrélation (BG, p)"] = float(acorr_breusch_godfrey(e.res, nlags=1)[1])
    except Exception:  # noqa: BLE001
        out["autocorrélation (BG, p)"] = np.nan
    return out


def toutes(p=None, m=None, debut=DEBUT, fin=FIN) -> dict:
    p = S.panel_branches() if p is None else p
    m = S.macro() if m is None else m
    return {"emploi": emploi(p, debut, fin), "prix_va": prix_va(p, debut, fin), "investissement": investissement(p, m, debut, fin),
            "investissement_snf": investissement_snf(m, debut, fin),
            "salaires": salaires(p, m, debut, fin), "consommation": consommation(m, debut, fin),
            "importations": importations(m, debut, fin), "exportations": exportations(m, debut, fin),
            "transmission": transmission_importations(p, m)}
