"""Phase 4.4 : vérification de l'intégration — batterie de chocs sur la trajectoire de référence 2023-2047 (base 2022),
chocs à partir de 2027, écarts à la référence à 1, 3, 5, 10, 15 et 20 ans (2027 … 2046), contrôles automatiques
(stabilité, signes attendus, cohérence d'Okun, identités du compte des sociétés, coût ex post des mesures) et
décomposition par gel des boucles pour deux chocs.
Usage : python3 phase43/d1_chocs_integration.py v09|p4 [--gel]"""
import copy, json, pathlib, sys, time, warnings
warnings.filterwarnings("ignore")
H = pathlib.Path(__file__).resolve(); sys.path[:0] = [str(H.parents[1] / "src"), str(H.parents[1]), str(H.parent)]
import numpy as np, pandas as pd
from d0_reference import reference
import m8_modele as M8

T0 = 2027
AN = (2027, 2029, 2031, 2036, 2041, 2046)
EN = ["CPA_B", "CPA_C19", "CPA_D"]


def _ajout(s, d):
    return (s if s is not None else pd.Series(dtype=float)).add(pd.Series(d), fill_value=0.0)


def appliquer(nom, mod, ex, ans):
    pibB = float(mod.macro.pib_cp[mod.B])
    perm = {t: 1.0 for t in ans if t >= T0}
    if nom == "demande publique +1 pt de PIB":
        g_part = mod.T.Fd.loc[mod.P, ["P3_S13", "P3_S15"]].values.sum() + mod.T.Fm.loc[mod.P, ["P3_S13", "P3_S15"]].values.sum()
        ex.conso_publique = ex.conso_publique * pd.Series({t: 1 + (0.01 * pibB / g_part if t >= T0 else 0.0) for t in ex.conso_publique.index})
    elif nom == "impôts des ménages +1 pt de PIB":
        niv = dict(ex.niveaux or {}); niv["impots_menages_pib"] = _ajout(niv.get("impots_menages_pib"), {t: 1.0 for t in perm}); ex.niveaux = niv
    elif nom == "impôts sur les produits +10 %":
        niv = dict(ex.niveaux or {}); niv["impots_produits"] = _ajout(niv.get("impots_produits"), {t: 0.10 for t in perm})
        niv["prix_conso"] = _ajout(niv.get("prix_conso"), {t: 0.9 * np.log1p(0.10 * 0.12) for t in perm}); ex.niveaux = niv
    elif nom == "coût du travail −2 % (allègement)":
        ex.subvention_salaires = _ajout(ex.subvention_salaires, {t: 0.02 for t in range(T0, 2061)}); ex.subvention_en_depense = True
    elif nom == "IS −5 points":
        ex.taux_is = ex.taux_is.copy().astype(float); ex.taux_is.loc[T0:] = ex.taux_is.loc[T0:] - 5.0
    elif nom == "taux d'intérêt +1 pt":
        ex.taux_long = ex.taux_long.copy().astype(float); ex.taux_long.loc[T0:] = ex.taux_long.loc[T0:] + 1.0
        if ex.taux_court is not None:
            ex.taux_court = ex.taux_court.copy().astype(float); ex.taux_court.loc[T0:] = ex.taux_court.loc[T0:] + 1.0
    elif nom == "demande mondiale +5 %":
        ex.demande_mondiale = ex.demande_mondiale.copy().astype(float); ex.demande_mondiale.loc[T0:] = ex.demande_mondiale.loc[T0:] * 1.05
    elif nom == "énergie importée +50 %":
        pi = ex.prix_import.copy()
        for c in EN:
            if c in pi.columns:
                pi.loc[pi.index >= T0, c] = pi.loc[pi.index >= T0, c] * 1.5
        ex.prix_import = pi
    elif nom == "productivité +1 %":
        ex.productivite = _ajout(ex.productivite, {T0: 0.01})
    elif nom == "salaires +2 % (temporaire)":
        ex.choc_salaire = _ajout(ex.choc_salaire, {T0: 0.02})
    return ex


CHOCS = ["demande publique +1 pt de PIB", "impôts des ménages +1 pt de PIB", "impôts sur les produits +10 %",
         "coût du travail −2 % (allègement)", "IS −5 points", "taux d'intérêt +1 pt", "demande mondiale +5 %",
         "énergie importée +50 %", "productivité +1 %", "salaires +2 % (temporaire)"]

# signes attendus (à 5 ans ; 0 = pas de contrainte) : PIB, emploi, chômage, prix conso, solde public
SIGNES = {"demande publique +1 pt de PIB": (+1, +1, -1, +1, -1), "impôts des ménages +1 pt de PIB": (-1, -1, +1, 0, +1),
          "impôts sur les produits +10 %": (-1, -1, +1, +1, +1), "coût du travail −2 % (allègement)": (+1, +1, -1, -1, -1),
          "IS −5 points": (0, 0, 0, 0, -1), "taux d'intérêt +1 pt": (-1, -1, +1, -1, -1), "demande mondiale +5 %": (+1, +1, -1, 0, +1),
          "énergie importée +50 %": (-1, -1, +1, +1, 0), "productivité +1 %": (+1, 0, 0, -1, 0), "salaires +2 % (temporaire)": (0, 0, 0, +1, 0)}

COLS = ["PIB (%)", "emploi (milliers)", "chômage (pt)", "prix conso (%)", "salaire réel (%)", "taux de marge (pt)", "consommation (%)",
        "FBCF (%)", "exportations (%)", "importations (%)", "taux d'épargne (pt)", "solde public (pt PIB)", "dette publique (pt PIB)",
        "solde extérieur (pt PIB)", "dividendes distribués (%)", "dette des SNF (pt PIB)", "autofinancement (pt)"]


def ecarts(v, b):
    lp = np.log(v.pc / b.pc)
    d = pd.DataFrame({
        "PIB (%)": 100 * np.log(v.pib / b.pib), "emploi (milliers)": v.emploi - b.emploi, "chômage (pt)": v.chomage - b.chomage,
        "prix conso (%)": 100 * lp, "salaire réel (%)": 100 * (np.log(v.salaire / b.salaire) - lp), "taux de marge (pt)": v.taux_marge - b.taux_marge,
        "consommation (%)": 100 * np.log(v.c / b.c), "FBCF (%)": 100 * np.log(v.fbcf / b.fbcf), "exportations (%)": 100 * np.log(v.x / b.x),
        "importations (%)": 100 * np.log(v.m / b.m), "taux d'épargne (pt)": v.taux_epargne - b.taux_epargne,
        "solde public (pt PIB)": v.solde_pib - b.solde_pib, "dette publique (pt PIB)": v.dette_pib - b.dette_pib,
        "solde extérieur (pt PIB)": 100 * (v.solde_exterieur / v.pib_nominal - b.solde_exterieur / b.pib_nominal)})
    if "dividendes_distribues" in v:
        d["dividendes distribués (%)"] = 100 * np.log(v.dividendes_distribues / b.dividendes_distribues)
        d["dette des SNF (pt PIB)"] = 100 * (v.dette_s11 / v.pib_nominal - b.dette_s11 / b.pib_nominal)
        d["autofinancement (pt)"] = v.taux_autofinancement - b.taux_autofinancement
    return d


def controles(nom, d, v, b, ex):
    """Contrôles automatiques. Renvoie une liste de (contrôle, réussi, détail)."""
    out = []
    out.append(("pas de valeur manquante", bool(np.isfinite(d.loc[T0:, ["PIB (%)", "prix conso (%)", "dette publique (pt PIB)"]].values).all()), ""))
    # stabilité : écart annuel moyen des 5 dernières années (variation d'une année sur l'autre) borné
    var = d[["PIB (%)", "prix conso (%)"]].diff().loc[2042:2046].abs().max()
    out.append(("stabilité (variation annuelle des écarts de PIB et de prix < 0,25 pt sur 2042-2046)", bool((var < 0.25).all()), f"{var.round(3).to_dict()}"))
    sg = SIGNES[nom]
    for k, (col, s) in enumerate(zip(["PIB (%)", "emploi (milliers)", "chômage (pt)", "prix conso (%)", "solde public (pt PIB)"], sg)):
        if s:
            x = float(d[col][2031])
            out.append((f"signe attendu à 5 ans : {col} {'+' if s > 0 else '−'}", bool(np.sign(x) == s or abs(x) < 1e-3), f"{x:.3f}"))
    # Okun / comptabilité du chômage : Δu ≈ −Δemploi / population active (même population active)
    pa = float(ex.population_active[2031])
    du_cpt = -100 * float(d["emploi (milliers)"][2031]) / pa
    out.append(("cohérence chômage-emploi (écart < 0,05 pt)", abs(du_cpt - float(d["chômage (pt)"][2031])) < 0.05, f"{du_cpt:.3f} vs {float(d['chômage (pt)'][2031]):.3f}"))
    if "_identite_b8g" in v:
        m = float(max(v["_identite_b8g"].abs().max(), v["_identite_b9"].abs().max()))
        out.append(("identités du compte des sociétés (< 1e-6 M€)", m < 1e-6, f"{m:.1e}"))
    return out


def lancer(conf, gel=False):
    mod, R = reference(conf)
    ans = list(R["trajectoire"].index)
    b = R["trajectoire"]
    tab, ctl, irf = {}, [], {}
    for nom in CHOCS:
        t0 = time.time()
        ex = appliquer(nom, mod, copy.deepcopy(R["exogenes"]), ans)
        v = mod.simuler(ans, ex)
        d = ecarts(v, b)
        irf[nom] = d
        for t in AN:
            tab[(nom, t - T0 + 1)] = d.loc[t].to_dict()
        for c, ok, det in controles(nom, d, v, b, ex):
            ctl.append(dict(configuration=conf, choc=nom, controle=c, reussi=bool(ok), detail=det))
        print(f"{nom} ({time.time() - t0:.0f} s) : PIB à 5 ans {d['PIB (%)'][2031]:+.2f} %, prix {d['prix conso (%)'][2031]:+.2f} %, "
              f"solde {d['solde public (pt PIB)'][2031]:+.2f} pt", flush=True)
    df = pd.DataFrame(tab).T; df.index.names = ["choc", "année"]
    out = H.parent / "resultats"; out.mkdir(exist_ok=True)
    df.to_csv(out / f"d1_chocs_{conf}.csv")
    pd.DataFrame(ctl).to_csv(out / f"d1_controles_{conf}.csv", index=False)
    pd.concat(irf, names=["choc", "annee"]).to_csv(out / f"d1_reponses_{conf}.csv")
    if gel:
        decomposition(mod, R, ans, conf)
    return df, pd.DataFrame(ctl)


BOUCLES = ["C", "prix_salaires", "emploi", "Z"]


def decomposition(mod, R, ans, conf):
    """Gel des boucles (phase 4.1) : contribution de chaque boucle à l'effet sur le PIB et les prix à 1, 5 et 20 ans."""
    mod.simuler(ans, copy.deepcopy(R["exogenes"]))
    g = mod.trajectoires_gel(ans)
    b = R["trajectoire"]
    rows = {}
    for nom in ("demande publique +1 pt de PIB", "coût du travail −2 % (allègement)", "taux d'intérêt +1 pt"):
        for cas, gl in [("tout gelé", BOUCLES)] + [(f"seule active : {x}", [y for y in BOUCLES if y != x]) for x in BOUCLES] + [("complet", [])]:
            ex = appliquer(nom, mod, copy.deepcopy(R["exogenes"]), ans)
            ex.gel = {k: g[k] for k in gl} or None
            v = mod.simuler(ans, ex)
            d = ecarts(v, b)
            for t in (2027, 2031, 2046):
                rows[(nom, cas, t - T0 + 1)] = {k: d[k][t] for k in ("PIB (%)", "emploi (milliers)", "prix conso (%)", "solde public (pt PIB)")}
            print("gel", nom, cas, flush=True)
    df = pd.DataFrame(rows).T; df.index.names = ["choc", "boucles", "année"]
    df.to_csv(H.parent / "resultats" / f"d1_gel_{conf}.csv")
    print(df.round(2).to_string())


if __name__ == "__main__":
    conf = sys.argv[1]
    df, ctl = lancer(conf, gel="--gel" in sys.argv)
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 500)
    print(df[[c for c in COLS if c in df]].round(2).to_string())
    print(ctl.groupby("reussi").size())
    print(ctl[~ctl.reussi].to_string())
