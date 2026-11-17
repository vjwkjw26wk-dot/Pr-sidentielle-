"""Validation rétrospective des équations de comportement (lot 7).

Pour chaque équation : simulation dynamique (la variable expliquée est recalculée année après année à partir de sa
propre valeur simulée, les autres variables étant observées), sur deux périodes hors échantillon :
  A. estimation 1997-2012, simulation 2013-2019 (7 ans) ;
  B. estimation 1997-2019, simulation 2022-2025 à partir des valeurs observées de 2021 (après la crise sanitaire,
     période du choc d'inflation, jamais vue par l'estimation).
Mesures : erreur sur le niveau en fin de période et erreur absolue moyenne sur les taux de croissance annuels,
comparées à une prévision naïve (croissance moyenne de la période d'estimation prolongée).
Sortie : outputs/validation_M7.md
"""
from __future__ import annotations

import pathlib
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
import m7_equations as E  # noqa: E402
import m7_series as S  # noqa: E402


def _effets(res, b, t):
    """Constante + effet fixe + tendance de branche."""
    c = res.params.get("const", 0.0) + res.params.get(f"fe_{b}", 0.0) + res.params.get(f"tr_{b}", 0.0) * (t - 2010)
    return c


def sim_branches(nom, eq, p, debut, fin, sigma=E.SIGMA_TRAVAIL):
    """Simulation dynamique par branche ; renvoie le total simulé et observé (heures, FBCF) ou le prix agrégé."""
    d = p.sort_values(["branche", "annee"]).set_index(["branche", "annee"])
    r = eq.res
    out = []
    for b in S.BRANCHES:
        x = d.loc[b]
        lq, lh, lclu, lpva = np.log(x.q), np.log(x.n if eq.__dict__.get("mesure", "h") == "n" else x.h), np.log(x.clu), np.log(x.va_cp / x.q)
        lrc = np.log((x.wb / x.ns) if eq.__dict__.get("mesure", "h") == "n" else x.cs) - lpva
        li, lk = np.log(x.i), np.log(x.k)
        sim = {}
        if nom == "emploi":
            v = lh.copy()
            for t in range(debut, fin + 1):
                dl1 = v[t - 1] - v[t - 2]
                dv = (_effets(r, b, t) + r.params["dlq"] * (lq[t] - lq[t - 1]) + r.params["dlq_1"] * (lq[t - 1] - lq[t - 2])
                      + r.params["dlh_1"] * dl1 + r.params["ecm_1"] * (v[t - 1] - lq[t - 1] + sigma * lrc[t - 1])
                      + r.params.get("rupture_2008", 0.0) * max(t - 2008, 0))
                v[t] = v[t - 1] + dv
            sim = np.exp(v)
            obs = np.exp(lh)
        elif nom == "prix_va":
            v = lpva.copy()
            for t in range(debut, fin + 1):
                dv = (_effets(r, b, t) + r.params["dlclu"] * (lclu[t] - lclu[t - 1]) + r.params["dlq"] * (lq[t] - lq[t - 1])
                      + r.params["ecm_1"] * (v[t - 1] - lclu[t - 1]))
                v[t] = v[t - 1] + dv
            sim = np.exp(v) * x.q          # VA nominale simulée (pour agréger les prix avec des poids en volume)
            obs = x.va_cp
        elif nom == "investissement":
            v = li.copy()
            for t in range(debut, fin + 1):
                dv = (_effets(r, b, t) + r.params["dlq"] * (lq[t] - lq[t - 1]) + r.params["dlq_1"] * (lq[t - 1] - lq[t - 2])
                      + r.params["li_1"] * v[t - 1] + r.params["lk_1"] * lk[t - 1] + r.params["lq_1"] * lq[t - 1])
                v[t] = v[t - 1] + dv
            sim = np.exp(v)
            obs = x.i
        out.append(pd.DataFrame({"sim": sim, "obs": obs}).loc[debut - 1:fin])
    tot = sum(out)
    if nom == "prix_va":
        q = d.groupby("annee").q.sum().loc[debut - 1:fin]
        tot = tot.div(q, axis=0)
    return tot


def sim_macro(nom, eq, m, debut, fin):
    r = eq.res.params
    if nom == "consommation":
        rdbr, lc, u = np.log(m.rdb / m.p_c), np.log(m.c), m.chomage
        v = lc.copy()
        for t in range(debut, fin + 1):
            v[t] = v[t - 1] + r["const"] + r["dlrdb"] * (rdbr[t] - rdbr[t - 1]) + r.get("du", 0.0) * (u[t] - u[t - 1]) + r["ecart_1"] * (v[t - 1] - rdbr[t - 1])
        obs = m.c
    elif nom == "importations":
        ld, lprel, lm = np.log(E.demande_ponderee(m)), np.log(m.p_m / m.p_pib), np.log(m.m)
        v = lm.copy()
        for t in range(debut, fin + 1):
            v[t] = v[t - 1] + (r["const"] + r["dld"] * (ld[t] - ld[t - 1]) + r["dlprel"] * (lprel[t] - lprel[t - 1]) + r["lm_1"] * v[t - 1]
                               + r["ld_1"] * ld[t - 1] + r["lprel_1"] * lprel[t - 1] + r["t"] * (t - 2010))
        obs = m.m
    elif nom == "exportations":
        ldm, lprel, lx = np.log(m.ue_m), np.log(m.p_x / m.p_ue_m), np.log(m.x)
        v = lx.copy()
        for t in range(debut, fin + 1):
            v[t] = v[t - 1] + r["const"] + r["dldm"] * (ldm[t] - ldm[t - 1]) + r["dlprel"] * (lprel[t] - lprel[t - 1])
        obs = m.x
    elif nom == "investissement_snf":
        d = eq.data
        li, lq, cu = np.log(d.iv), np.log(d.qv), np.log(d.cout_usage)
        v = li.copy()
        for t in range(debut, fin + 1):
            v[t] = v[t - 1] + (r["const"] + r["dlq"] * (lq[t] - lq[t - 1]) + r["dlq_1"] * (lq[t - 1] - lq[t - 2]) + r["ecm_1"] * (v[t - 1] - lq[t - 1])
                               + r["tm_1"] * d.taux_marge[t - 1] + r["lcu_1"] * cu[t - 1])
        obs = d.iv
    elif nom == "salaires":
        g = PANEL.groupby("annee")[["wb", "ns", "n", "va_cp", "q"]].sum(min_count=1)
        lw, lpva, lprod = np.log(g.wb / g.ns), np.log(g.va_cp / g.q), np.log(g.q / g.n)
        lpc = np.log(m.p_c.reindex(g.index))
        v = lw.copy()
        for t in range(debut, fin + 1):
            v[t] = v[t - 1] + (r["const"] + r["dlpc"] * (lpc[t] - lpc[t - 1]) + r["dlprod"] * (lprod[t] - lprod[t - 1])
                               + r["ecm_1"] * (v[t - 1] - lpva[t - 1] - lprod[t - 1]) + E.PHILLIPS * eq.ugap[t])
        obs = np.exp(lw)
        return pd.DataFrame({"sim": np.exp(v), "obs": obs}).loc[debut - 1:fin]
    return pd.DataFrame({"sim": np.exp(v), "obs": obs}).loc[debut - 1:fin]


def mesures(df, obs_est):
    g_sim, g_obs = np.log(df.sim).diff().iloc[1:], np.log(df.obs).diff().iloc[1:]
    naif = np.log(obs_est).diff().mean()
    niveau = df.sim.iloc[-1] / df.obs.iloc[-1] - 1
    niveau_naif = np.exp(np.log(df.obs.iloc[0]) + naif * (len(df) - 1)) / df.obs.iloc[-1] - 1
    return dict(croiss_obs=g_obs.mean() * 100, croiss_sim=g_sim.mean() * 100, eam=(g_sim - g_obs).abs().mean() * 100,
                eam_naif=(naif - g_obs).abs().mean() * 100, niveau=niveau * 100, niveau_naif=niveau_naif * 100)


LIBELLES = {"emploi": "Emploi (25 branches)", "prix_va": "Prix de la valeur ajoutée (25 branches)",
            "investissement": "FBCF des branches marchandes", "investissement_snf": "FBCF des sociétés non financières",
            "salaires": "Salaire moyen par tête", "consommation": "Consommation des ménages",
            "importations": "Importations", "exportations": "Exportations"}
PANEL = None


def main():
    global PANEL
    p, m = S.panel_branches(), S.macro()
    PANEL = p
    L = ["# Validation des équations de comportement (lot 7)", "",
         "Généré par `tests/validation_M7.py`. Simulations dynamiques : chaque équation recalcule sa variable année après année "
         "à partir de ses propres valeurs simulées ; les autres variables sont observées (équation par équation, sans bouclage). "
         "Erreur absolue moyenne (EAM) sur les croissances annuelles, en points ; erreur sur le niveau en fin de période, en %. "
         "La prévision naïve prolonge la croissance moyenne de la période d'estimation.", ""]
    eqs_full = E.toutes(p, m)
    L += ["## 1. Coefficients estimés (1997-2019)", ""]
    for k, e in eqs_full.items():
        dg = E.diagnostics(e)
        L += [f"### {e.nom}", "", f"Variable expliquée : {e.variable} ; {dg['n']} observations ; R² = {dg['R²']:.2f} ; "
              f"écart type résiduel = {dg['écart type résiduel'] * 100:.1f} %"
              + (f" ; autocorrélation des résidus (Breusch-Godfrey, p) = {dg['autocorrélation (BG, p)']:.2f}" if k not in ("emploi", "prix_va", "investissement") else "")
              + (" ; estimé sur 1998-2024" if k == "transmission" else "")
              + ".", "", "| Variable | Coefficient | Écart type | t |", "|---|---|---|---|"]
        for nom, c, se, t in e.tableau([c for c in e.res.params.index if not c.startswith(("fe_", "tr_"))]):
            L.append(f"| {nom} | {c:.3f} | {se:.3f} | {t:.1f} |")
        L += ["", "Grandeurs dérivées : " + " ; ".join(f"{a} = {b:.3f}" if not isinstance(b, str) else f"{a} = {b}" for a, b in e.lr.items()) + ".", ""]
    L += ["## 2. Tests rétrospectifs", ""]
    for titre, (d_est, f_est, d_sim, f_sim) in {"A. Estimation 1997-2012, simulation 2013-2019": (1997, 2012, 2013, 2019),
                                                 "B. Estimation 1997-2019, simulation 2022-2024": (1997, 2019, 2022, 2024)}.items():
        eqs = E.toutes(p, m, d_est, f_est) if f_est != 2019 else eqs_full
        L += [f"### {titre}", "", "| Équation | Croissance annuelle observée | Simulée | EAM | EAM naïve | Erreur de niveau en fin de période | Naïve |",
              "|---|---|---|---|---|---|---|"]
        for k, e in eqs.items():
            if k in ("transmission", "logement"):     # logement : équation de M14, validée dans 12_audit_mecanismes.md
                continue
            if k in ("emploi", "prix_va", "investissement"):
                df = sim_branches(k, e, p, d_sim, f_sim)
                est = sim_branches(k, e, p, d_est, f_est).obs
            else:
                df = sim_macro(k, e, m, d_sim, f_sim)
                est = sim_macro(k, e, m, d_est, f_est).obs
            r = mesures(df, est)
            L.append(f"| {LIBELLES[k]} | {r['croiss_obs']:+.1f} % | {r['croiss_sim']:+.1f} % | {r['eam']:.1f} | {r['eam_naif']:.1f} | "
                     f"{r['niveau']:+.1f} % | {r['niveau_naif']:+.1f} % |")
        L.append("")
    (RACINE / "outputs" / "validation_M7.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
