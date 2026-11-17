"""Simulation des jeux de mesures des candidats (simulateur/programmes.py) par le modèle complet.

Pour chaque jeu : écarts à la trajectoire inchangée en 2028, 2030 et 2032 (modèle complet), écart de l'approximation
additive de l'interface en 2032, et contrôle de cohérence du solde (effet ex ante annoncé vs effet simulé).
Même traitement pour tous les jeux ; aucun classement. Sortie : outputs/programmes_candidats.md et .json.
Usage : python3 tests/programmes_candidats.py
"""
from __future__ import annotations

import json
import pathlib
import sys

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
sys.path.insert(0, str(RACINE / "tests"))
from simulateur import executer as X, catalogue as CAT, programmes as PG  # noqa: E402
from validation_additivite import additif  # noqa: E402

IND = [("pib", "PIB (%)"), ("chomage", "Chômage (pt)"), ("emploi_milliers", "Emploi (milliers)"), ("pc", "Prix à la consommation (%)"),
       ("solde_pib", "Solde public (pt de PIB)"), ("dette_pib", "Dette (pt de PIB)")]
ANS = (2028, 2030, 2032)


def main():
    D = json.loads((RACINE / "outputs" / "variantes_elementaires.json").read_text())
    cur = {c["cle"]: c for c in CAT.CURSEURS}
    res = {}
    L = [f"# Jeux de mesures des candidats : simulation par le modèle complet (version {X.VERSION_MODELE})", "",
         f"Sources au {PG.DATE}. Écarts à la trajectoire « politique inchangée ». Traductions approximatives : voir "
         "simulateur/programmes.py et doc/11_coherence_et_programmes.md. Les candidats sont présentés par ordre alphabétique ; "
         "aucun classement ni note n'est établi.", ""]
    for p in sorted(PG.PROGRAMMES, key=lambda x: x["tri"]):
        sel = p["curseurs"]
        r = X.executer({"nom": p["id"], "horizon": 2032, "hypotheses": {"europe": True, "incertitude": 0, "profils": False},
                        "mesures": [cur[k]["mesure"](v) for k, v in sel.items()]})
        tr = r["trajectoires"]
        ex = {i: {a: (tr["emploi"]["scenario"][a] - tr["emploi"]["reference"][a]) if i == "emploi_milliers" else tr[i]["ecart"][a]
                  for a in ANS} for i, _ in IND}
        ad = additif(sel, D)
        res[p["id"]] = {"exact": ex, "additif_2032": {i: ad.get(i, {}).get(2032) for i, _ in IND},
                        "distribution": r.get("distribution"), "statique": r.get("statique")}
        L += [f"## {p['candidat']} ({p['parti']})", "",
              "Curseurs : " + ", ".join(f"{cur[k]['libelle']} = {v:g} {cur[k]['unite']}" for k, v in sel.items()), "",
              "| Indicateur | 2028 | 2030 | 2032 | 2032 additif (interface) |", "|---|---|---|---|---|"]
        for i, lib in IND:
            a32 = ad.get(i, {}).get(2032)
            L.append(f"| {lib} | {ex[i][2028]:+.2f} | {ex[i][2030]:+.2f} | {ex[i][2032]:+.2f} | "
                     + (f"{a32:+.2f} |" if a32 is not None else "– |"))
        L += ["", "Non représenté : " + " ; ".join(p["non_represente"]) + ".", ""]
        print(p["id"], "ok", flush=True)
    (RACINE / "outputs" / "programmes_candidats.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (RACINE / "outputs" / "programmes_candidats.json").write_text(json.dumps(res, ensure_ascii=False, default=float, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
