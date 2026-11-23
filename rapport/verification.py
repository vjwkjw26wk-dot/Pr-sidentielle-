"""Vérification des programmes par le modèle complet et tests de résistance (version 0.6).

Pour chaque scénario de rapport/resultats/strategie.json (et le scénario recommandé s'il est défini) :
- simulation complète (horizon 2047, microsimulation, zone euro) ;
- tests de résistance : le même choc est appliqué à la référence et au programme ; on mesure l'effet du programme sous
  choc et les niveaux atteints (dette, solde, chômage) avec et sans programme ;
- mise en œuvre à moitié (curseurs à mi-chemin).
Sortie : rapport/resultats/verification.json
"""
from __future__ import annotations

import copy
import json
import pathlib
import sys

import numpy as np
import pandas as pd

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
sys.path.insert(0, str(RACINE / "src"))
from simulateur import executer as X, catalogue as CAT  # noqa: E402
import m11_europe as EU  # noqa: E402
import m8_modele as M  # noqa: E402
sys.path.insert(0, str(RACINE / "rapport"))
from simulations import simuler  # noqa: E402

RES = RACINE / "rapport" / "resultats"
CUR = {c["cle"]: c for c in CAT.CURSEURS}
ANNEES = (2029, 2030, 2032, 2037, 2047)
DEB = 2028


def _apres(ex, attr, f):
    s = getattr(ex, attr)
    setattr(ex, attr, pd.Series({t: (f(t, v) if t >= DEB else v) for t, v in s.items()}))


def chocs():
    def monde(ex):
        _apres(ex, "demande_mondiale", lambda t, v: v * 0.99 ** (t - DEB + 1))

    def energie(ex):
        for p in M.NON_CONCURRENTS:
            ex.prix_import[p] = [x * (1.5 if t >= DEB + 1 else 1.0) for t, x in zip(ex.prix_import.index, ex.prix_import[p])]

    def taux(ex):
        _apres(ex, "taux_long", lambda t, v: v + 1.5)

    def inflation(ex):
        f = lambda t: 1.02 ** (min(t, 2032) - DEB + 1)  # noqa: E731
        ex.prix_import = ex.prix_import.mul(pd.Series({t: (f(t) if t >= DEB else 1.0) for t in ex.prix_import.index}), axis=0)
        _apres(ex, "prix_mondial", lambda t, v: v * f(t))

    def competitivite(ex):
        _apres(ex, "prix_mondial", lambda t, v: v * 0.95)

    def productivite(ex):
        base = ex.productivite if ex.productivite is not None else pd.Series(0.0, index=ex.demande_mondiale.index)
        ex.productivite = pd.Series({t: float(base.get(t, 0.0)) + (-0.003 if t >= DEB else 0.0) for t in ex.demande_mondiale.index})

    def demographie(ex):
        _apres(ex, "population_active", lambda t, v: v * (1 - 0.002 * (t - DEB + 1)))

    return {"croissance mondiale plus faible (−1 pt par an)": monde, "crise énergétique (énergie importée +50 % dès 2029)": energie,
            "hausse des taux longs (+1,5 point)": taux, "inflation importée persistante (+2 % par an, 2028-2032)": inflation,
            "dégradation de la compétitivité (prix concurrents −5 %)": competitivite,
            "productivité plus faible (−0,3 point par an)": productivite, "choc démographique (population active −0,2 % par an)": demographie}


def tableau(c, v):
    out = {}
    for k in ("pib", "chomage", "solde_pib", "dette_pib", "emploi", "solde_exterieur", "rnb", "pc", "rdb"):
        out[k] = {}
        for t in ANNEES:
            if k in ("chomage", "solde_pib", "dette_pib"):
                out[k][t] = {"ref": float(c[k][t]), "prog": float(v[k][t]), "ecart": float(v[k][t] - c[k][t])}
            elif k == "emploi":
                out[k][t] = {"ecart": float(v[k][t] - c[k][t])}
            elif k == "solde_exterieur":
                out[k][t] = {"ecart": float((v[k][t] / v.pib_nominal[t] - c[k][t] / c.pib_nominal[t]) * 100)}
            else:
                out[k][t] = {"ecart": float((v[k][t] / c[k][t] - 1) * 100)}
    return out


def resistance(curseurs):
    mod = X.modele(2022)
    sc = X.depuis_curseurs({"nom": "p", "horizon": 2047, "hypotheses": {"europe": True, "profils": False},
                            "mesures": [CUR[k]["mesure"](v) for k, v in curseurs.items()]})
    ref, var, ans, info = X.construire(sc, mod)
    _, _, Eu = EU.simuler_couple(mod, ans, ref, var, theta=EU.THETA_PRIME)
    if Eu is not None:
        var.taux_long = var.taux_long.add(Eu.taux_long_fr, fill_value=0.0)
        var.demande_mondiale = var.demande_mondiale * (1 + Eu.demande_ue.reindex(var.demande_mondiale.index).fillna(0.0) / 100)
    out = {"central": tableau(mod.simuler(ans, ref), mod.simuler(ans, var))}
    for nom, f in chocs().items():
        r2, v2 = copy.deepcopy(ref), copy.deepcopy(var)
        f(r2)
        f(v2)
        try:
            out[nom] = tableau(mod.simuler(ans, r2), mod.simuler(ans, v2))
        except Exception as e:  # noqa: BLE001
            out[nom] = {"erreur": repr(e)}
    return out


def main():
    S = json.loads((RES / "strategie.json").read_text())["scenarios"]
    extra = json.loads((RES / "scenario_recommande.json").read_text()) if (RES / "scenario_recommande.json").exists() else {}
    progs = {k: v["curseurs"] for k, v in S.items() if v.get("faisable")}
    progs.update({k: v["curseurs"] for k, v in extra.items()})
    cible = sys.argv[1:] or list(progs)
    for k in cible:
        out = {}
        cur = {a: float(b) for a, b in progs[k].items()}
        complet = simuler(k, cur)
        demi = {a: (CUR[a]["actuel"] + (b - CUR[a]["actuel"]) / 2) for a, b in cur.items()}
        if "age_legal" in demi:
            demi["age_legal"] = round(demi["age_legal"])
        out[k] = {"curseurs": cur, "complet": complet, "mi_chemin": simuler(k + "_demi", demi), "resistance": resistance(cur)}
        print(k, "ok", flush=True)
        (RES / f"verification_{k}.json").write_text(json.dumps(out, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main()
