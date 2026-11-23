"""Phase 3.1 — estimation de la transmission entre PIB potentiel et demande (paramètres de fermeture ρ et θ) par
inférence indirecte.

1. Moments empiriques (données d'étalonnage, 1982-2019, hors crise sanitaire) : modèle ARDL de l'écart de production
   publié par la Commission européenne (AMECO, AVGDGP) et par le FMI (WEO, NGAP_NPGDP) :
       g_t = c + φ1 g_{t−1} + φ2 g_{t−2} + β0 Δp_t + β1 Δp_{t−1} + e_t,
   où Δp est l'écart de la croissance du PIB potentiel à sa moyenne. φ résume la persistance de l'écart (vitesse de
   retour de la production vers le potentiel), β la façon dont une accélération ou un ralentissement du potentiel se
   transmet à l'écart (β < 0 : la production suit le potentiel avec retard). Écarts-types par bootstrap des résidus.
   Tests de spécifications plus riches : asymétrie (Δp > 0 et Δp < 0), dépendance à l'état (Δp × écart passé),
   stabilité (avant et après 2000).
2. Moments du modèle : à partir des réponses impulsionnelles du modèle (phase31/irf_fermeture.py) à un choc de demande
   transitoire et à un choc d'offre permanent, on construit par superposition (le modèle est quasi linéaire autour de la
   référence) de longues séries synthétiques, dont la variance des deux chocs est fixée pour reproduire les variances
   observées de g et Δp, puis on estime le même ARDL.
3. Estimation : (ρ, θ) minimisant la distance pondérée (inverse des variances bootstrap) entre coefficients du modèle
   et coefficients empiriques ; intervalle : ensemble des configurations non rejetées au seuil de 10 % (test du χ²
   à 4 degrés de liberté sur la distance).
Limites : l'écart de production publié est lui-même estimé (fonction de production et filtres) ; sa persistance est
en partie un produit de la méthode. La comparaison AMECO / FMI en donne une idée.
Sortie : phase31/resultats/estimation_theta.json
"""
import json
import pathlib
import sys

import numpy as np

R = pathlib.Path(__file__).resolve().parents[1]
RAW = R / "data" / "raw"
OUT = R / "phase31" / "resultats"
OUT.mkdir(parents=True, exist_ok=True)


def serie(f):
    d = json.loads((RAW / f).read_text())["series"]["docs"][0]
    return {int(p): float(v) for p, v in zip(d["period"], d["value"]) if v not in (None, "NA") and str(v) != "nan"}


def donnees(source):
    if source == "AMECO":
        g = serie("dbnomics_AMECO_AVGDGP_FRA.1.0.0.0.AVGDGP.json")
        pot = json.loads((RAW / "dbnomics_AMECO_OVGDP_FRA.json").read_text())["series"]["docs"][0]
        pot = {int(p): float(v) for p, v in zip(pot["period"], pot["value"]) if v not in (None, "NA")}
    else:
        g = serie("dbnomics_IMF_WEO_2025-04_FRA.NGAP_NPGDP.pcent_potential_gdp.json")
        # le FMI ne publie pas le niveau du potentiel dans cette série : potentiel = PIB réel / (1 + g/100)
        y = serie("dbnomics_AMECO_OVGD_FRA.1.1.0.0.OVGD.json")
        pot = {t: y[t] / (1 + g[t] / 100) for t in g if t in y}
    gp = {t: 100 * np.log(pot[t] / pot[t - 1]) for t in pot if t - 1 in pot}
    return g, gp


def matrice(g, gp, ans, specif="base"):
    moy = np.mean([gp[t] for t in ans])
    dp = {t: gp[t] - moy for t in gp}
    Y, Xs = [], []
    for t in ans:
        x = [1.0, g[t - 1], g[t - 2], dp[t], dp[t - 1]]
        if specif == "asymetrie":
            x = [1.0, g[t - 1], g[t - 2], max(dp[t], 0), min(dp[t], 0), dp[t - 1]]
        if specif == "etat":
            x = [1.0, g[t - 1], g[t - 2], dp[t], dp[t - 1], dp[t] * g[t - 1]]
        Y.append(g[t])
        Xs.append(x)
    return np.array(Y), np.array(Xs)


def ols(Y, X):
    b, *_ = np.linalg.lstsq(X, Y, rcond=None)
    e = Y - X @ b
    s2 = e @ e / (len(Y) - X.shape[1])
    V = s2 * np.linalg.inv(X.T @ X)
    return b, np.sqrt(np.diag(V)), e


def bootstrap(Y, X, b, e, n=2000, graine=0):
    rng = np.random.default_rng(graine)
    B = []
    for _ in range(n):
        Yb = X @ b + rng.choice(e, size=len(e), replace=True)
        bb, *_ = np.linalg.lstsq(X, Yb, rcond=None)
        B.append(bb)
    return np.array(B)


def empirique():
    res = {}
    ans = [t for t in range(1982, 2020)]
    for src in ("AMECO", "FMI"):
        g, gp = donnees(src)
        Y, X = matrice(g, gp, ans)
        b, se, e = ols(Y, X)
        Bt = bootstrap(Y, X, b, e)
        r = {"coef": dict(zip(["c", "phi1", "phi2", "beta0", "beta1"], map(float, b))),
             "se": dict(zip(["c", "phi1", "phi2", "beta0", "beta1"], map(float, se))),
             "cov_boot": np.cov(Bt[:, 1:].T).tolist(), "var_g": float(np.var([g[t] for t in ans])),
             "var_dp": float(np.var([gp[t] for t in ans])), "n": len(ans)}
        # demi-vie de l'écart après un choc de demande (AR(2))
        x = [0.0, 1.0]
        for h in range(1, 30):
            x.append(b[1] * x[-1] + b[2] * x[-2])
            if abs(x[-1]) < 0.5:
                r["demi_vie_ans"] = h
                break
        for sp in ("asymetrie", "etat"):
            Y2, X2 = matrice(g, gp, ans, sp)
            b2, se2, e2 = ols(Y2, X2)
            r[sp] = {"coef": b2.tolist(), "se": se2.tolist(), "t_supplementaire": float((b2[-1] if sp == "etat" else b2[3] - b2[4]) /
                                                                                            (se2[-1] if sp == "etat" else np.sqrt(se2[3] ** 2 + se2[4] ** 2)))}
        # stabilité : deux sous-périodes
        for nom, sous in (("1982-1999", list(range(1982, 2000))), ("2000-2019", list(range(2000, 2020)))):
            Y3, X3 = matrice(g, gp, sous)
            b3, se3, _ = ols(Y3, X3)
            r[nom] = {"coef": b3.tolist(), "se": se3.tolist()}
        res[src] = r
    return res


def coefs_modele(irf, var_g, var_dp, n=6000, graine=1):
    """ARDL estimé sur des séries synthétiques construites par superposition des réponses impulsionnelles."""
    gd, pd_ = np.array(irf["demande"]["gap"]) * 100, np.diff([0.0] + irf["demande"]["pot"])
    gs, ps = np.array(irf["offre"]["gap"]) * 100, np.diff([0.0] + irf["offre"]["pot"])
    gd, gs = gd / 100, gs / 100                     # écart de production du modèle déjà en points de pourcentage
    # variances des chocs pour reproduire var(g) et var(Δp)
    A = np.array([[np.sum(gd ** 2), np.sum(gs ** 2)], [np.sum(pd_ ** 2), np.sum(ps ** 2)]])
    sig2 = np.linalg.solve(A, np.array([var_g, var_dp]))
    if np.any(sig2 <= 0):
        sig2 = np.clip(sig2, 1e-6, None)
    rng = np.random.default_rng(graine)
    L = len(gd)
    ed, es = rng.normal(0, np.sqrt(sig2[0]), n + L), rng.normal(0, np.sqrt(sig2[1]), n + L)
    g = np.convolve(ed, gd)[:n + L] + np.convolve(es, gs)[:n + L]
    p = np.convolve(ed, pd_)[:n + L] + np.convolve(es, ps)[:n + L]
    g, p = g[L:], p[L:]
    Y = g[2:]
    X = np.column_stack([np.ones(len(Y)), g[1:-1], g[:-2], p[2:] - p.mean(), p[1:-1] - p.mean()])
    b, *_ = np.linalg.lstsq(X, Y, rcond=None)
    return b[1:], sig2


def duree_empirique():
    """Durée moyenne d'un écart de production (somme de la réponse impulsionnelle AR(2) sur 0-10 ans, écart initial = 1),
    avec intervalle bootstrap à 90 %."""
    out = {}
    ans = list(range(1982, 2020))
    for src in ("AMECO", "FMI"):
        g, _ = donnees(src)
        Y = np.array([g[t] for t in ans])
        X = np.column_stack([np.ones(len(ans)), [g[t - 1] for t in ans], [g[t - 2] for t in ans]])
        b, se, e = ols(Y, X)
        B = bootstrap(Y, X, b, e)

        def somme(p1, p2):
            x = [0.0, 1.0]
            for _ in range(1, 11):
                x.append(p1 * x[-1] + p2 * x[-2])
            return float(sum(x[1:]))
        ss = [somme(bb[1], bb[2]) for bb in B]
        out[src] = {"phi": b[1:].tolist(), "se": se[1:].tolist(), "duree": somme(b[1], b[2]), "ic90": np.percentile(ss, [5, 95]).tolist()}
    return out


def main():
    """Sélection des paramètres de fermeture (μ = 0, terme proportionnel a = 0 : voir document 19) :
    - moment empirique : durée moyenne de l'écart de production (AMECO et FMI, 1982-2019) ;
    - moment du modèle : durée de l'écart après un choc d'offre permanent (productivité −1 % en 2028), somme 0-10 ans ;
    - contraintes : pas de dépassement de plus de 10 % ; θ compatible avec la réponse de la consommation à un choc
      permanent de revenu (Blundell, Pistaferri et Preston 2008 : environ 0,6-0,65) et de l'investissement (≈ 1),
      soit une plage a priori de 0,4 à 1,0 ;
    - ensemble plausible : durées dans l'union des intervalles à 90 % des deux sources."""
    emp = empirique()
    dur = duree_empirique()
    lo = min(d["ic90"][0] for d in dur.values())
    hi = max(d["ic90"][1] for d in dur.values())
    cible = float(np.mean([d["duree"] for d in dur.values()]))
    irf = {}
    for f in ("irf_i.json", "irf_j.json", "irf_k.json"):
        if (OUT / f).exists():
            irf.update(json.loads((OUT / f).read_text()))
    conf = {}
    for k, v in irf.items():
        g = v["offre"]["gap"][:11]
        rho, th, pk, am = map(float, k.split("|"))
        d = float(sum(x / g[0] for x in g))
        mn = float(min(x / g[0] for x in g))
        conf[k] = {"rho": rho, "theta": th, "part_k": pk, "a": am, "duree": d, "minimum": mn, "dette_2047_choc_offre": v["offre"]["dette"][19],
                   "plausible": bool(lo <= d <= hi and mn >= -0.1 and 0.4 <= th <= 1.0)}
    res = {"empirique_ardl": emp, "duree_empirique": dur, "intervalle_cible": [lo, hi], "cible_centrale": cible, "configurations": conf,
           "retenu": {"rho": 0.2, "theta": 0.75, "a": 0.0, "mu": 0.0, "part_k": 1.0},
           "plage": {"theta": [0.5, 1.0], "rho": [0.1, 0.3]}}
    (OUT / "estimation_theta.json").write_text(json.dumps(res, indent=1, default=float))
    print("durée empirique", {k: (round(v["duree"], 2), [round(x, 2) for x in v["ic90"]]) for k, v in dur.items()}, "cible", round(cible, 2))
    for k, c in sorted(conf.items(), key=lambda kv: kv[1]["duree"]):
        print(k, round(c["duree"], 2), round(c["minimum"], 2), round(c["dette_2047_choc_offre"], 1), "plausible" if c["plausible"] else "")
    for src in ("AMECO", "FMI"):
        e = emp[src]
        print(src, {k: (round(e["coef"][k], 3), round(e["se"][k], 3)) for k in e["coef"]},
              "asymétrie t =", round(e["asymetrie"]["t_supplementaire"], 2), "état t =", round(e["etat"]["t_supplementaire"], 2))


if __name__ == "__main__":
    main()
