"""Phase 3 — diagnostic de la fermeture de la v0.6 : chocs d'offre (productivité, population active) appliqués à la
référence, avec et sans fermeture d'offre ; décomposition des effets. Sortie : phase3/resultats/diagnostic_<version>.json"""
from __future__ import annotations
import copy, json, pathlib, sys
import pandas as pd
RACINE = pathlib.Path(__file__).resolve().parents[1]
for p in (RACINE, RACINE / "src", RACINE / "rapport"):
    sys.path.insert(0, str(p))
from simulateur import executer as X  # noqa: E402
import verification as V  # noqa: E402

OUT = RACINE / "phase3" / "resultats"; OUT.mkdir(parents=True, exist_ok=True)
COLS = ["pib", "emploi", "chomage", "pc", "salaire", "pib_nominal", "solde_pib", "dette_pib", "recettes", "depenses", "c", "x", "m", "fbcf"]


def main(version="v06"):
    mod = X.modele(2022)
    sc = X.depuis_curseurs({"nom": "ref", "horizon": 2047, "hypotheses": {"europe": False, "profils": False}, "mesures": []})
    ref, _, ans, _ = X.construire(sc, mod)
    ch = V.chocs()
    out = {}
    for rho in (None, 0.0):
        r0 = copy.deepcopy(ref)
        if rho is not None:
            r0.fermeture_offre = rho
        c0 = mod.simuler(ans, r0)
        for nom in ("productivité plus faible (−0,3 point par an)", "choc démographique (population active −0,2 % par an)"):
            r1 = copy.deepcopy(r0); ch[nom](r1)
            c1 = mod.simuler(ans, r1)
            cle = f"{nom} | rho={'central' if rho is None else rho}"
            out[cle] = {}
            for k in COLS:
                if k not in c0.columns:
                    continue
                out[cle][k] = {int(t): (float(c1[k][t] - c0[k][t]) if k in ("chomage", "solde_pib", "dette_pib") else float((c1[k][t] / c0[k][t] - 1) * 100))
                               for t in (2030, 2032, 2037, 2047)}
            print(cle, {k: round(out[cle][k][2037], 2) for k in out[cle]}, flush=True)
    (OUT / f"diagnostic_{version}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(*(sys.argv[1:] or []))
