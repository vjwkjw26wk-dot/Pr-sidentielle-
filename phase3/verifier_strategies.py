"""Phase 3 — vérification des stratégies optimisées (et des points de comparaison A, B, C, D, R de la v0.6) avec le
modèle complet v0.7.

Pour chaque programme :
- simulation complète (microsimulation, zone euro) avec les comportements central, bas et haut ;
- mise en œuvre partielle (curseurs à mi-chemin) ;
- environnements : les chocs de rapport/verification.py (croissance mondiale faible, énergie, taux, inflation importée,
  compétitivité, productivité, démographie) et trois environnements favorables (croissance mondiale forte, taux bas,
  énergie bon marché) ; le choc est appliqué à la référence et au programme.
Sortie : phase3/resultats/verification_v07_<programme>.json

Usage : python3 phase3/verifier_strategies.py [complet|leger] <programme> ...
"""
import copy
import json
import os
import pathlib
import sys
import time

R = pathlib.Path(__file__).resolve().parents[1]
RES = R / "phase3" / "resultats"
os.environ["SORTIE_SIMULATIONS"] = str(RES)
sys.path[:0] = [str(R / "rapport"), str(R / "src"), str(R), str(R / "phase3")]
import verification as V  # noqa: E402
from simulations import simuler  # noqa: E402
import optimisation as O  # noqa: E402

CUR = V.CUR
V.ANNEES = (2029, 2030, 2032, 2037, 2042, 2047)   # horizons 5, 10, 15 et 20 ans


def chocs_favorables():
    def monde_fort(ex):
        V._apres(ex, "demande_mondiale", lambda t, v: v * 1.01 ** (t - V.DEB + 1))

    def taux_bas(ex):
        V._apres(ex, "taux_long", lambda t, v: v - 1.0)

    def energie_bon_marche(ex):
        for p in V.M.NON_CONCURRENTS:
            ex.prix_import[p] = [x * (0.8 if t >= V.DEB + 1 else 1.0) for t, x in zip(ex.prix_import.index, ex.prix_import[p])]
    return {"croissance mondiale plus forte (+1 pt par an)": monde_fort, "taux longs plus bas (−1 point)": taux_bas,
            "énergie importée −20 %": energie_bon_marche}


def programmes():
    P = {}
    f = RES / "optimisation_v07.json"
    if f.exists():
        for k, s in json.loads(f.read_text())["strategies"].items():
            if "leviers" not in s:
                continue
            cur = {}
            for lev, v in s["leviers"].items():
                val = O.VALEUR_ACTUELLE.get(lev, 0.0) + v
                if lev == "age_legal":
                    val = round(val)
                cur[lev] = round(val, 2)
            P[k] = cur
    S = json.loads((R / "rapport" / "resultats" / "strategie.json").read_text())["scenarios"]
    for k, v in S.items():
        if v.get("faisable"):
            P[f"v06_{k}"] = {a: float(b) for a, b in v["curseurs"].items()}
    f = R / "rapport" / "resultats" / "scenario_recommande.json"
    if f.exists():
        for k, v in json.loads(f.read_text()).items():
            P[f"v06_{k}"] = {a: float(b) for a, b in v["curseurs"].items()}
    return P


def demi(cur):
    d = {a: (CUR[a]["actuel"] + (b - CUR[a]["actuel"]) / 2) for a, b in cur.items()}
    if "age_legal" in d:
        d["age_legal"] = round(d["age_legal"])
    return d


def resistance(cur, leger):
    mod = V.X.modele(2022)
    sc = V.X.depuis_curseurs({"nom": "p", "horizon": 2047, "hypotheses": {"europe": True, "profils": False},
                              "mesures": [CUR[k]["mesure"](v) for k, v in cur.items()]})
    ref, var, ans, info = V.X.construire(sc, mod)
    _, _, Eu = V.EU.simuler_couple(mod, ans, ref, var, theta=V.EU.THETA_PRIME)
    if Eu is not None:
        var.taux_long = var.taux_long.add(Eu.taux_long_fr, fill_value=0.0)
        var.demande_mondiale = var.demande_mondiale * (1 + Eu.demande_ue.reindex(var.demande_mondiale.index).fillna(0.0) / 100)
    out = {}
    ch = {**V.chocs(), **chocs_favorables()}
    if leger:
        ch = {k: f for k, f in ch.items() if any(s in k for s in ("mondiale plus faible", "taux longs (+", "productivit", "énergétique"))}
    for nom, f in ch.items():
        r2, v2 = copy.deepcopy(ref), copy.deepcopy(var)
        f(r2)
        f(v2)
        try:
            out[nom] = V.tableau(mod.simuler(ans, r2), mod.simuler(ans, v2))
        except Exception as e:  # noqa: BLE001
            out[nom] = {"erreur": repr(e)}
    return out


def main():
    mode = sys.argv[1]
    P = programmes()
    cible = sys.argv[2:] or list(P)
    for k in cible:
        t0 = time.time()
        cur = P[k]
        out = {"curseurs": cur, "complet": simuler(k, cur)}
        if mode == "complet" or not k.startswith("v06_"):
            out["basse"] = simuler(k, cur, hyp={"comportements_v07": "basse"})
            out["haute"] = simuler(k, cur, hyp={"comportements_v07": "haute"})
            out["mi_chemin"] = simuler(k + "_demi", demi(cur))
        out["resistance"] = resistance(cur, leger=(mode != "complet"))
        (RES / f"verification_v07_{k}.json").write_text(json.dumps(out, ensure_ascii=False, default=float))
        print(k, "ok", round(time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
