"""Banc d'essai de la phase 3.4 (branche phase34) : backtests et chocs, v0.8 (référence) contre v0.9 (options SPEC).

Chaque configuration est un dict d'options SPEC ; {} = v0.8 à l'identique. Le modèle est ré-instancié (et ses équations
ré-estimées) quand σ change, pour que les coefficients soient cohérents avec σ."""
import json
import pathlib
import sys

import numpy as np
import pandas as pd

R = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R / "src"), str(R), str(R / "phase31")]
import m7_equations as E  # noqa: E402
import m8_modele as M  # noqa: E402
import backtest as BT  # noqa: E402

CLOS = {"v08": ("production", 0.2, 0.0, 0.75), "v06": ("chomage", 0.15, 0.3, 0.0), "demande": ("production", 0.0, 0.0, 0.0)}
V09 = {"demande_travail": "ces_heures", "cible_k": False, "potentiel": "ces_marchand", "sigma": 0.45,
       "non_marchand": "branches", "salaire_public": "instrument", "dette": "cohortes", "cout_travail": "net_subventions"}
V09_SANS_DETTE = {k: v for k, v in V09.items() if k != "dette"}


def appliquer(spec):
    M.configurer_v08()
    if spec:
        M.SPEC.update(spec)
        if spec.get("sigma") is not None:
            E.SIGMA_TRAVAIL = spec["sigma"]


def construire(B, fin, clos="v08", spec=None, **kw):
    appliquer(spec)
    mode, rho, a, th = CLOS[clos]
    mod, ex, ans = BT.construire(B, fin, rho, a, th, mode, **kw)
    if M.SPEC["dette"] == "cohortes":
        import m17_dette as D
        ex.taux_court = D.taux_observes()[1]           # taux court observé : exogène conditionnel, comme le taux long
    if M.SPEC["cout_travail"] == "net_subventions":
        # CICE observé (politique injectée, comme les taux apparents) ; bascule de 2019 : baisse de cotisations employeurs
        # de même ampleur (chute des D39 en 2019, données) → D1 abaissé (choc de salaire) sans rattrapage (ancre)
        sv = M.taux_subvention_salaires()
        ex.subvention_salaires = sv
        if fin >= 2019 and B < 2019:
            from telechargement import jsonstat_dict
            import json as _j
            s_ = pd.Series(jsonstat_dict(_j.loads((R / "data" / "raw" / "eurostat_nasa_D39_D1_S11_S13_FR.json").read_text())))
            g = lambda it, sec, dr: pd.Series({int(k[-1]): v for k, v in s_.items() if dr in k and it in k and sec in k})  # noqa: E731
            bascule = float(g("D39", "S1", "RECV")[2018] - g("D39", "S1", "RECV")[2019])
            d1m = float(g("D1", "S1", "PAID")[2019] - g("D1", "S13", "PAID")[2019])
            lw = float(np.log1p(-bascule / d1m))
            ex.choc_salaire = pd.Series({t: (lw if t == 2019 else 0.0) for t in ans})
            niv = ex.niveaux or {}
            niv["ancre_salaire"] = pd.Series({t: (lw if t >= 2019 else 0.0) for t in ans})
            ex.niveaux = niv
    if M.SPEC["potentiel"] == "ces_marchand":
        # niveau de calage constant : potentiel de l'année de base = PIB × exp(−écart d'Okun de base)
        us = float(ex.chomage_structurel[B])
        gapB = -M.OKUN * (float(mod.macro.chomage[B]) - us) / 100
        ex.lpgf = pd.Series({t: -gapB for t in range(1990, fin + 1)})
        pa = ex.population_active
        gpa = np.log(float(pa[B]) / float(pa[B - 8])) / 8
        ex.ces_ref = {"lk": ex.lk_ref, "nstar": pd.Series({t: float(pa[B]) * np.exp(gpa * (t - B)) * (1 - us / 100) for t in ans})}
        ex.lpot_ref = None
    return mod, ex, ans


def run(B=2010, fin=2019, clos="v08", spec=None, exp_mod=None, retour=False, **kw):
    mod, ex, ans = construire(B, fin, clos, spec, **kw)
    if exp_mod:
        exp_mod(mod, ex)
    r = mod.simuler(ans, ex)
    o = BT.observe(mod)
    em = mod.emp
    t = fin
    mk_obs = sum(mod.hist[b].n for b in mod.BR)
    nm_obs = em.emploi - mk_obs
    n_nm_sim = r["emploi_non_marchand"] if "emploi_non_marchand" in r else None
    rm = lambda k: float(np.sqrt(np.mean([(r[k][y] - o[k][y]) ** 2 for y in ans if y in o[k].index])))  # noqa: E731
    gr = lambda s, y, ref: 100 * (s[y] / (s[y - 1] if y - 1 in s.index else ref[y - 1]) - 1)  # noqa: E731
    rmg = lambda k: float(np.sqrt(np.mean([(gr(r[k], y, o[k]) - gr(o[k], y, o[k])) ** 2 for y in ans])))  # noqa: E731
    us = pd.Series({y: float(ex.chomage_structurel[y]) for y in ans})
    okun = (r.ecart_production.loc[list(ans)] + M.OKUN * (r.chomage.loc[list(ans)] - us))
    res = dict(dette=float(r.dette_pib[t] - o["dette_pib"][t]), solde=float(r.solde_pib[t] - o["solde_pib"][t]),
               pib=float(100 * (r.pib[t] / o["pib"][t] - 1)), emploi=float(100 * (r.emploi[t] / em.emploi[t] - 1)),
               chomage=float(r.chomage[t] - o["chomage"][t]), pc=float(100 * (r.pc[t] / o["pc"][t] - 1)),
               pibn=float(100 * (r.pib_nominal[t] / mod.macro.pib_cp[t] - 1)),
               rmse_pib_g=rmg("pib"), rmse_pc_g=rmg("pc"), rmse_chom=rm("chomage"), rmse_dette=rm("dette_pib"),
               okun_moy=float(okun.mean()), okun_max=float(okun.abs().max()),
               taux_app=float(r.taux_apparent[t] - 100 * mod.apu.d41pay[t] / mod.apu.dette[t - 1]),
               rmse_taux_app=float(np.sqrt(np.mean([(r.taux_apparent[y] - 100 * mod.apu.d41pay[y] / mod.apu.dette[y - 1]) ** 2 for y in ans if y in mod.apu.d41pay.index]))))
    if n_nm_sim is not None:
        res["emploi_nm"] = float(100 * (n_nm_sim[t] / nm_obs[t] - 1))
        res["emploi_m"] = float(100 * ((r.emploi[t] - n_nm_sim[t]) / mk_obs[t] - 1))
    M.configurer_v08()
    return (res, r, mod, o) if retour else res


def table(rows, cols=None):
    df = pd.DataFrame(rows).T
    return (df[cols] if cols else df).round(2).to_string()
