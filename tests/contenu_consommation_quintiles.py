"""Contenu domestique de la consommation par quintile de niveau de vie (contre-expertise, version 0.6).

Pour un euro de dépense (prix d'acquisition) de chaque quintile : impôts sur les produits, importations directes et
indirectes, valeur ajoutée produite en France (dont commerce et transport), emplois en France, répartition sectorielle
de la valeur ajoutée. Méthode : tableau entrées-sorties 2022 du modèle (M5/M8), passerelle fonctions de consommation
(COICOP) → produits (CPA) avec marges de commerce et impôts (hypothèse documentée, niveau H), structures de consommation
par quintile de l'Insee (Focus n° 338, 2022). Analyse statique (sans bouclage macroéconomique).
Sortie : outputs/contenu_consommation_quintiles.md et .json.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
import m8_modele as M  # noqa: E402

# passerelle : part du prix d'acquisition par produit ; "taxe" = impôts nets sur les produits (TVA, accises)
PASSERELLE = {
    "alimentation": {"CPA_A01": .22, "CPA_C10-12": .50, "CPA_G47": .18, "CPA_G46": .04, "taxe": .06},
    "alcool_tabac": {"CPA_C10-12": .33, "CPA_G47": .14, "taxe": .53},
    "habillement": {"CPA_C13-15": .42, "CPA_G47": .40, "taxe": .18},
    "logement_energie": {"CPA_L68A": .45, "CPA_L68B": .17, "CPA_D": .16, "CPA_E36": .04, "CPA_F": .08, "CPA_C19": .03, "taxe": .07},
    "equipement": {"CPA_C31_32": .25, "CPA_C27": .15, "CPA_C28": .05, "CPA_C22": .05, "CPA_G47": .33, "taxe": .17},
    "sante": {"CPA_Q86": .50, "CPA_C21": .30, "CPA_G47": .12, "taxe": .08},
    "transport": {"CPA_C29": .22, "CPA_C19": .12, "CPA_H49": .10, "CPA_H51": .05, "CPA_G45": .16, "CPA_G47": .05, "CPA_K65": .05, "taxe": .25},
    "communication": {"CPA_J61": .68, "CPA_C26": .10, "CPA_G47": .06, "taxe": .16},
    "loisirs_culture": {"CPA_R90-92": .15, "CPA_R93": .10, "CPA_J58": .10, "CPA_J59_60": .10, "CPA_C26": .10, "CPA_C32": 0.0,
                        "CPA_C31_32": .08, "CPA_N79": .07, "CPA_G47": .15, "taxe": .15},
    "education": {"CPA_P": .95, "taxe": .05},
    "restauration_hotels": {"CPA_I": .85, "taxe": .15},
    "divers": {"CPA_K65": .22, "CPA_K64": .10, "CPA_S96": .20, "CPA_C20": .10, "CPA_Q87_88": .10, "CPA_G47": .12, "taxe": .16},
}
# structures de consommation par quintile (%, Insee Focus n° 338, 2022 ; arrondies)
STRUCT = {"Q1": [13, 4, 3, 34, 3, 4, 11, 5, 5, 1, 6, 11], "Q2": [13, 4, 3, 30, 4, 5, 12, 4, 5, 1, 6, 12],
          "Q3": [13, 4, 3, 30, 4, 4, 13, 4, 6, 0, 7, 13], "Q4": [12, 3, 3, 27, 4, 4, 13, 4, 8, 1, 8, 13],
          "Q5": [11, 3, 3, 25, 5, 3, 13, 3, 9, 1, 10, 13]}
REGROUPE = {"industrie": lambda b: b.startswith("C") or b in ("B", "D", "E"), "agriculture": lambda b: b == "A",
            "construction": lambda b: b == "F", "commerce_transport": lambda b: b in ("G", "H"),
            "services_marchands": lambda b: b in ("I", "J", "K", "M_N", "R-U"), "non_marchand_logement": lambda b: b == "NM"}


def main():
    mod = M.Modele(2022)
    P = list(mod.P)
    n = len(P)
    L = np.linalg.inv(np.eye(n) - mod.Ad0)
    mi = mod.Am0.sum(axis=0)
    sh = mod.part_imp["C"]
    # emplois par M€ de production, par produit (branche de rattachement)
    br = mod.br_prod
    pb = mod.panel[mod.panel.annee == mod.B].set_index("branche")
    emp_br = {b: float(pb.n[b]) for b in pb.index}
    emp_br["NM"] = float(mod.emp.emploi[mod.B]) - sum(emp_br.values())
    x0 = mod.x0
    prod_br = {b: x0[br == b].sum() for b in set(br)}
    e_coef = np.array([emp_br.get(b, np.nan) / prod_br[b] if prod_br.get(b) else np.nan for b in br])
    e_coef = np.nan_to_num(e_coef, nan=np.nanmedian(e_coef))
    res = {}
    for q, w in STRUCT.items():
        tot = {"taxe": 0.0, "import": 0.0, "va": 0.0, "emplois": 0.0}
        va_secteur = {k: 0.0 for k in REGROUPE}
        for (f, part), wf in zip(PASSERELLE.items(), w):
            wf = wf / sum(w)
            for p, s in part.items():
                if p == "taxe":
                    tot["taxe"] += wf * s
                    continue
                if p not in P:
                    continue
                j = P.index(p)
                d = np.zeros(n)
                d[j] = wf * s * (1 - sh[j])                    # demande adressée à la production nationale
                imp_dir = wf * s * sh[j]
                xx = L @ d
                imp_ind = float(mi @ xx)
                va = mod.av * xx
                tot["import"] += imp_dir + imp_ind
                tot["va"] += float(va.sum())
                tot["emplois"] += float((e_coef * xx).sum())
                for k, fn in REGROUPE.items():
                    va_secteur[k] += float(va[[fn(b) for b in br]].sum())
        res[q] = {**{k: v for k, v in tot.items()}, "va_secteurs": va_secteur}
    # 1 Md€ de dépense : emplois (milliers)
    Lm = ["# Contenu domestique d'un euro de consommation par quintile de niveau de vie (version 0.6)", "",
          "Analyse entrées-sorties statique, tableau 2022 ; passerelle fonctions → produits avec marges et impôts (hypothèse) ; "
          "structures de consommation par quintile de l'Insee (2022). Les marges de commerce et de transport sont de la valeur "
          "ajoutée nationale même quand le produit est importé.", "",
          "| Quintile | Impôts sur les produits | Importations (directes + indirectes) | VA produite en France | dont commerce et transport | "
          "dont industrie | Emplois pour 1 Md€ dépensé |", "|---|---|---|---|---|---|---|"]
    for q, r in res.items():
        Lm.append(f"| {q} | {r['taxe'] * 100:.1f} % | {r['import'] * 100:.1f} % | {r['va'] * 100:.1f} % | "
                  f"{r['va_secteurs']['commerce_transport'] * 100:.1f} % | {r['va_secteurs']['industrie'] * 100:.1f} % | {r['emplois'] * 1e3:.1f} k |")
    Lm += ["", "Somme impôts + importations + VA ≈ 100 % (écart : arrondis et produits hors passerelle).", "",
           "Lecture : l'écart de contenu importé entre quintiles reste faible ; les différences portent davantage sur la composition "
           "sectorielle (logement et énergie chez les modestes, services marchands chez les aisés) et sur le contenu en emplois "
           "par euro (plus élevé dans les services de proximité, plus faible dans le logement, très capitalistique)."]
    (RACINE / "outputs" / "contenu_consommation_quintiles.md").write_text("\n".join(Lm) + "\n", encoding="utf-8")
    (RACINE / "outputs" / "contenu_consommation_quintiles.json").write_text(json.dumps(res, indent=1))
    print("\n".join(Lm[5:11]))


if __name__ == "__main__":
    main()
