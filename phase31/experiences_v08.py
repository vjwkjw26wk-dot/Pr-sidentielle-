"""Phase 3.1 — relance de toutes les expériences avec le modèle v0.8 (copie de phase3/experiences_v07.py), et variantes de comportement.

Usage :
    python3 phase3/experiences_v07.py lots <lot1> <lot2> ...      # expériences de rapport/simulations.py
    python3 phase3/experiences_v07.py comportements                # sélection × niveaux basse / haute
Sorties : phase3/resultats/experiences_v08_<lot>.json et experiences_v08_comportements.json.
Les résultats v0.6 restent dans rapport/resultats/ (non modifiés).
"""
import os
import sys
import json
import time
import pathlib

R = pathlib.Path(__file__).resolve().parents[1]
SORTIE = R / "phase31" / "resultats"
SORTIE.mkdir(parents=True, exist_ok=True)
os.environ["SORTIE_SIMULATIONS"] = str(SORTIE)
sys.path[:0] = [str(R / "rapport"), str(R / "src"), str(R)]
import simulations as SIM  # noqa: E402

# expériences dont la sensibilité aux paramètres de comportement est la plus instructive
SELECTION = ["tva_moins1", "tva", "is_baisse", "is_moins_hausse", "cot_moins20", "rsa25", "ppa25", "invest_public20_bis",
             "recherche3", "energie50"]


def lots(noms):
    for lot in noms:
        res = {}
        for l, nom, lib, cur in SIM.EXPERIENCES:
            if l != lot:
                continue
            t0 = time.time()
            try:
                res[nom] = {"libelle": lib, **SIM.simuler(nom, cur)}
            except Exception as e:  # noqa: BLE001
                res[nom] = {"libelle": lib, "erreur": repr(e)}
            print(lot, nom, round(time.time() - t0), flush=True)
        (SORTIE / f"experiences_v08_{lot}.json").write_text(json.dumps(res, ensure_ascii=False, default=float))


def comportements():
    exp = {nom: (lib, cur) for _, nom, lib, cur in SIM.EXPERIENCES}
    res = {}
    for nom in SELECTION:
        if nom not in exp:
            continue
        lib, cur = exp[nom]
        for niv in ("basse", "haute"):
            t0 = time.time()
            try:
                res[f"{nom}|{niv}"] = {"libelle": lib, "niveau": niv, **SIM.simuler(nom, cur, hyp={"comportements_v07": niv})}
            except Exception as e:  # noqa: BLE001
                res[f"{nom}|{niv}"] = {"libelle": lib, "niveau": niv, "erreur": repr(e)}
            print("comportements", nom, niv, round(time.time() - t0), flush=True)
            (SORTIE / "experiences_v08_comportements.json").write_text(json.dumps(res, ensure_ascii=False, default=float))


if __name__ == "__main__":
    if sys.argv[1] == "lots":
        lots(sys.argv[2:])
    else:
        comportements()
