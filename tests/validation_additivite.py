"""Validation de l'approximation additive de l'interface (version 0.4).

Pour des scénarios combinant plusieurs mesures, compare l'écart à la référence calculé par le modèle complet
(`simulateur.executer`) et la somme des variantes élémentaires interpolées (méthode de l'interface).
Les scénarios sont des assemblages illustratifs de mesures, sans attribution à un programme existant.
Sortie : resultats/validation_additivite.md.  Usage : python3 tests/validation_additivite.py
"""
from __future__ import annotations

import json
import pathlib
import sys

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from simulateur import executer as X, catalogue as CAT  # noqa: E402

SCENARIOS = {
    "A — redistribution et dépense": {"rsa": 25, "smic": 10, "isf": 1.0, "ir_t4": 50, "age_legal_immediat": 62, "emploi_public": 100},
    "B — baisse des prélèvements et des dépenses": {"cotisations_employeurs": -20, "taux_is": 20, "autres_depenses": -30, "age_legal": 65, "assurance_chomage": -10},
    "C — protection commerciale et production": {"droits_douane": 10, "reindustrialisation": 10, "tva": -2, "age_legal": 62, "energie_import": 20},
    "D — transition et investissement": {"taxe_carbone": 100, "investissement_public": 30, "logements_sociaux": 50, "tva_reduite": -2, "csg_activite": 1},
}
INDICATEURS = [("pib", "PIB (%)"), ("chomage", "Chômage (pt)"), ("solde_pib", "Solde public (pt de PIB)"), ("dette_pib", "Dette (pt de PIB)"), ("pc", "Prix (%)")]


def poids(c, v, V):
    pts = sorted([(p, f"{p:g}") for p in c["points"] if f"{p:g}" in V] + [(c["actuel"], None)])
    if abs(v - c["actuel"]) < 1e-9:
        return []
    i = next((j for j, (x, _) in enumerate(pts) if x >= v), len(pts) - 1)
    i = max(1, i)
    (xa, ka), (xb, kb) = pts[i - 1], pts[i]
    t = (v - xa) / (xb - xa)
    return [(k, w) for k, w in ((ka, 1 - t), (kb, t)) if k is not None]


def additif(sel, D):
    cur = {c["cle"]: c for c in CAT.CURSEURS}
    out = {i: {} for i, _ in INDICATEURS}
    for cle, v in sel.items():
        for k, w in poids(cur[cle], v, D["variantes"][cle]):
            e = D["variantes"][cle][k]["ecarts"]
            for i, _ in INDICATEURS:
                for a, x in e[i].items():
                    out[i][int(a)] = out[i].get(int(a), 0.0) + w * x
    return out


def main():
    D = json.loads((RACINE / "outputs" / "variantes_elementaires.json").read_text())
    cur = {c["cle"]: c for c in CAT.CURSEURS}
    lignes = ["# Validation de l'approximation additive de l'interface (version 0.4)", "",
              "Écarts à la trajectoire inchangée en 2028 et 2032 : modèle complet (exact) et somme des variantes élémentaires "
              "interpolées (interface). Scénarios illustratifs, non attribués à un programme.", ""]
    synth = []
    for nom, sel in SCENARIOS.items():
        r = X.executer({"nom": nom, "horizon": 2032, "hypotheses": {"europe": True, "incertitude": 0, "profils": False},
                        "mesures": [cur[k]["mesure"](v) for k, v in sel.items()]})
        ad = additif(sel, D)
        lignes += [f"## {nom}", "", "Mesures : " + ", ".join(f"{cur[k]['libelle']} = {v:g} {cur[k]['unite']}" for k, v in sel.items()), "",
                   "| Indicateur | 2028 exact | 2028 additif | 2032 exact | 2032 additif | écart 2032 |", "|---|---|---|---|---|---|"]
        for i, lib in INDICATEURS:
            ex = r["trajectoires"][i]["ecart"]
            e28, e32, a28, a32 = ex[2028], ex[2032], ad[i].get(2028, 0), ad[i].get(2032, 0)
            lignes.append(f"| {lib} | {e28:+.2f} | {a28:+.2f} | {e32:+.2f} | {a32:+.2f} | {a32 - e32:+.2f} |")
            synth.append((nom, lib, e32, a32))
        lignes.append("")
        print(nom, "ok", flush=True)
    ecarts = [abs(a - e) for _, _, e, a in synth]
    rel = [abs(a - e) / max(abs(e), 0.1) for _, _, e, a in synth]
    lignes += ["## Synthèse", "", f"Écart absolu moyen en 2032 entre l'approximation additive et le modèle complet : {sum(ecarts) / len(ecarts):.2f} "
               f"(maximum {max(ecarts):.2f}) ; écart relatif médian : {sorted(rel)[len(rel) // 2] * 100:.0f} %.", "",
               "Les interactions viennent surtout du bouclage macroéconomique (fermeture d'offre, indexation des prix et salaires) "
               "et du cumul de mesures sur les mêmes ménages ; le calcul exact (`python3 -m simulateur.serveur`) reste la référence."]
    (RACINE / "outputs" / "validation_additivite.md").write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print("\n".join(lignes[-4:]))


if __name__ == "__main__":
    main()
