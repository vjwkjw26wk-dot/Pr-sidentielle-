"""Contre-expertise (version 0.6) : sensibilités univariées, criblage de Morris, incertitude statistique et scénarios
cohérents pour les jeux de mesures des candidats et pour des variantes de contrôle.

Usage : python3 tests/contre_expertise.py <id> [<id> ...]   (ids de simulateur/programmes.py, ou « controle_* »)
Sortie : outputs/contre_expertise/<id>.json
"""
from __future__ import annotations

import json
import pathlib
import sys
import time

import numpy as np

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
sys.path.insert(0, str(RACINE))
from simulateur import sensibilite as S, programmes as PG, catalogue as CAT  # noqa: E402

SORTIE = RACINE / "outputs" / "contre_expertise"
SORTIE.mkdir(parents=True, exist_ok=True)
CUR = {c["cle"]: c for c in CAT.CURSEURS}
CONTROLES = {   # variantes élémentaires de contrôle (une mesure), mêmes méthodes
    "controle_rsa": {"rsa": 25}, "controle_is": {"taux_is": 20}, "controle_depense": {"autres_depenses": 30},
    "controle_tva": {"tva": 2}, "controle_age": {"age_legal_immediat": 62}, "controle_emploi_public": {"emploi_public": -100},
}


def scenario(id_):
    sel = CONTROLES.get(id_) or next(p for p in PG.PROGRAMMES if p["id"] == id_)["curseurs"]
    return {"nom": id_, "horizon": 2032, "hypotheses": {"europe": True, "incertitude": 0, "profils": False},
            "mesures": [CUR[k]["mesure"](v) for k, v in sel.items()]}, sel


def mesures_isolees(id_, sel, mod):
    """Contribution de chaque mesure (simulée seule, jeu central) et sa sensibilité univariée maximale : identifie les
    mesures responsables de l'incertitude."""
    out = {}
    for k, v in sel.items():
        sc = {"nom": k, "horizon": 2032, "hypotheses": {"europe": True, "incertitude": 0, "profils": False},
              "mesures": [CUR[k]["mesure"](v)]}
        prep = S.Preparation(sc, mod)
        c = S.evaluer(prep, {})
        U = {}
        B = S.bornes(mod)
        for nom in ("fermeture_offre", "phillips", "pmc_echelle", "comportements_hauts_revenus", "conso_rappel", "salaire_indexation"):
            b, _, h = B[nom]
            U[nom] = {"bas": S.evaluer(prep, {nom: b}), "haut": S.evaluer(prep, {nom: h})}
        out[k] = {"valeur": v, "central": c, "univarie": U}
    return out


def main(ids):
    for id_ in ids:
        t0 = time.time()
        sc, sel = scenario(id_)
        prep = S.Preparation(sc)
        res = {"id": id_, "curseurs": sel, "bornes": {k: list(v) for k, v in S.bornes(prep.mod).items()}}
        res["central"] = S.evaluer(prep, {})
        res["univarie"] = S.univarie(prep)
        print(id_, "univarié", round(time.time() - t0), flush=True)
        res["coherents"], res["scenarios_definis"] = S.scenarios_coherents(prep)
        evals, stats = S.morris(prep, r=4 if id_.startswith("controle_") else 6)
        res["morris"] = {"evaluations": evals, "indices": stats}
        print(id_, "Morris", round(time.time() - t0), flush=True)
        stat = []
        for d in S.tirages_statistiques(prep.mod, n=50):
            try:
                y = S.evaluer(prep, {}, coefs=d)
                if all(np.isfinite(y[k][2032]) for k in ("pib", "solde_pib", "dette_pib")):
                    stat.append(y)
            except Exception as e:  # noqa: BLE001
                print("tirage écarté :", e)
        res["statistique"] = stat
        res["tirages_rejetes"] = getattr(S.tirages_statistiques, "rejets", None)
        print(id_, "statistique", len(stat), round(time.time() - t0), flush=True)
        if not id_.startswith("controle_"):
            res["mesures"] = mesures_isolees(id_, sel, prep.mod)
            print(id_, "mesures", round(time.time() - t0), flush=True)
        (SORTIE / f"{id_}.json").write_text(json.dumps(res, ensure_ascii=False, default=float))


if __name__ == "__main__":
    main(sys.argv[1:])
