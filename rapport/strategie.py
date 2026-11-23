"""Recherche de programmes de redressement par optimisation linéaire sur un métamodèle, puis vérification par le modèle
complet (version 0.6).

1. Métamodèle : l'effet de chaque levier est supposé proportionnel à son ampleur, avec des pentes distinctes à la hausse
   et à la baisse quand deux expériences existent (rapport/simulations.py), et additif entre leviers (erreur d'additivité
   mesurée par les expériences combinées). L'âge légal est une option discrète (62, 64, 65, 66 ans).
2. Optimisation : programme linéaire (scipy.optimize.linprog, méthode HiGHS) pour chaque scénario et chaque option d'âge ;
   fonction objectif et contraintes explicites (OBJECTIFS). Le résultat est l'optimum du métamodèle sous ces contraintes,
   pas un optimum politique ou social.
3. Vérification : chaque programme retenu est simulé par le modèle complet (horizon 2047, microsimulation).
Sortie : rapport/resultats/strategie.json
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
from scipy.optimize import linprog

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
sys.path.insert(0, str(RACINE / "src"))
RES = RACINE / "rapport" / "resultats"
ANNEES = (2029, 2030, 2032, 2037, 2047)

# levier : (actuel, borne basse, borne haute, [(expérience, valeur du curseur)] pour la hausse, idem pour la baisse)
LEVIERS = {
    "tva": (0, -1, 2, [("tva", 1)], []),
    "tva_reduite": (0, 0, 2, [("tva_reduite", 2)], []),
    "csg_activite": (0, -1, 1, [("csg", 1)], []),
    "ir_t1": (11, 11, 13, [("ir_bas", 13)], []),
    "isf": (0, 0, 1, [("isf", 1.0)], []),
    "pfu": (0, 0, 15, [("pfu", 15)], []),
    "successions": (0, 0, 50, [("successions", 50)], []),
    "taxe_carbone": (0, 0, 100, [("carbone", 50)], []),
    # hausses d'IS et d'impôts de production exclues de l'optimisation : leurs effets passent par la délocalisation des
    # bénéfices et des activités, que le modèle ne représente pas (il en sous-estimerait le coût)
    "taux_is": (25.8, 20, 25.8, [("is", 30.5)], [("is_baisse", 20)]),
    "impots_production": (0, -15, 0, [("production", 10)], []),
    "cotisations_employeurs": (0, -20, 10, [("cotisations", 10)], [("cot_moins20", -20)]),
    "emploi_public": (0, -200, 50, [], [("emploi_public", -170)]),
    "autres_depenses": (0, -30, 10, [], [("fonctionnement", -10)]),
    "investissement_public": (0, -10, 30, [("invest_public30", 30)], [("invest_public_moins", -10)]),
    "indexation_pensions": (0, -1, 0, [], [("indexation", -1)]),
    "assurance_chomage": (0, -25, 0, [], [("chomage", -25)]),
    "rsa": (0, 0, 25, [("rsa25", 25)], []),
    "prime_activite": (0, 0, 25, [("ppa25", 25)], []),
    "allocations_familiales": (0, -10, 25, [("af25", 25)], []),
    "aides_logement": (0, -10, 0, [], [("apl_moins10", -10)]),
    "minimum_vieillesse": (0, 0, 25, [("aspa25", 25)], []),
    # la réindustrialisation n'est pas un instrument (c'est un résultat visé, sans coût public dans le simulateur) : exclue
    "temps_travail": (35, 35, 37, [("temps37", 37)], []),
    # SMIC exclu : l'emploi peu qualifié et les allègements dégressifs ne sont pas représentés
    "droits_douane": (0, 0, 10, [("douanes10", 10)], []),
}
AGES = {64: None, 62: "age62", 65: "age65", 66: "age66"}
INDIC = ["pib", "emploi_k", "chomage", "solde", "dette", "ext", "rnb", "industrie", "rdb_reel", "pauvrete", "mediane", "inflation"]


def charger():
    E = {}
    for f in RES.glob("experiences_*.json"):
        E.update(json.loads(f.read_text()))
    return E


def effets(e):
    """Vecteur d'effets d'une expérience : indicateur × année."""
    T = e["traj"]
    g = lambda k, t: T[k]["ecart"].get(str(t), np.nan) if k in T else np.nan  # noqa: E731
    out = {}
    for t in ANNEES:
        emp = T["emploi"]["scenario"][str(t)] - T["emploi"]["reference"][str(t)] if "emploi" in T else np.nan
        out[("pib", t)] = g("pib", t)
        out[("emploi_k", t)] = emp
        out[("chomage", t)] = g("chomage", t)
        out[("solde", t)] = g("solde_pib", t)
        out[("dette", t)] = g("dette_pib", t)
        out[("ext", t)] = g("solde_exterieur_pib", t)
        out[("rnb", t)] = g("rnb", t)
        out[("industrie", t)] = g("part_industrie", t)
        out[("rdb_reel", t)] = g("rdb", t) - g("pc", t) if "pc" in T else np.nan
        out[("inflation", t)] = g("inflation", t)
    ineg = e.get("inegalites") or {}
    for t in ANNEES:
        out[("pauvrete", t)] = (ineg["apres_seuil_fixe"]["taux_pauvrete"] - ineg["avant"]["taux_pauvrete"]) if ineg else 0.0
        out[("mediane", t)] = ((ineg["apres"]["mediane"] / ineg["avant"]["mediane"] - 1) * 100) if ineg else 0.0
    return out


def metamodele(E):
    """Variables du programme linéaire : (levier, sens) avec pente par unité de curseur et borne."""
    var = []
    for k, (act, lo, hi, plus, moins) in LEVIERS.items():
        if hi > act:
            src = plus or moins
            if src:
                nom, v = src[-1]
                ef = effets(E[nom])
                var.append({"levier": k, "sens": +1, "borne": hi - act, "pente": {c: x / (v - act) for c, x in ef.items()},
                            "source": nom, "extrapole": not plus})
        if lo < act:
            src = moins or plus
            if src:
                nom, v = src[-1]
                ef = effets(E[nom])
                var.append({"levier": k, "sens": -1, "borne": act - lo, "pente": {c: x / (act - v) * -1 * -1 if moins else -x / (v - act) for c, x in ef.items()},
                            "source": nom, "extrapole": not moins})
    # pente « par unité de baisse » : effet d'une baisse d'une unité
    for x in var:
        if x["sens"] == -1:
            nom = x["source"]
            act = LEVIERS[x["levier"]][0]
            v = [vv for n, vv in LEVIERS[x["levier"]][4] + LEVIERS[x["levier"]][3] if n == nom][0]
            ef = effets(E[nom])
            x["pente"] = {c: val / abs(v - act) * (1 if v < act else -1) for c, val in ef.items()}
    return var


IMPOTS = {"tva", "tva_reduite", "csg_activite", "ir_t1", "isf", "pfu", "successions", "taxe_carbone", "taux_is", "impots_production",
          "cotisations_employeurs", "droits_douane"}
ECONOMIES = {"emploi_public", "autres_depenses", "investissement_public", "indexation_pensions", "assurance_chomage", "allocations_familiales",
             "aides_logement"}
# Contraintes de faisabilité (hypothèses explicites, identiques pour tous les scénarios) : hausses de prélèvements limitées à
# 1,5 point de PIB et économies de dépenses à 2,5 points de PIB (effet sur le solde en 2030) sur un mandat ; pénalité de
# parcimonie λ (par levier utilisé à pleine amplitude), exprimée dans l'unité de l'objectif.
PLAFOND_IMPOTS, PLAFOND_ECONOMIES = 1.5, 2.5


def resoudre(var, age_ef, objectif, contraintes, penalite=0.0, plafonds=None):
    """objectif : {(indicateur, année): poids} à maximiser ; contraintes : liste ((indicateur, année), '<=' ou '>=', borne)."""
    n = len(var)
    c = -np.array([sum(w * np.nan_to_num(x["pente"].get(k, 0.0)) for k, w in objectif.items()) - penalite / x["borne"] for x in var])
    A, b = [], []
    A.append(np.array([max(0.0, np.nan_to_num(x["pente"].get(("solde", 2030), 0.0))) if x["levier"] in IMPOTS and x["sens"] > 0 else 0.0 for x in var]))
    b.append((plafonds or (PLAFOND_IMPOTS, PLAFOND_ECONOMIES))[0])
    A.append(np.array([max(0.0, np.nan_to_num(x["pente"].get(("solde", 2030), 0.0))) if x["levier"] in ECONOMIES and x["sens"] < 0 else 0.0 for x in var]))
    b.append((plafonds or (PLAFOND_IMPOTS, PLAFOND_ECONOMIES))[1])
    for k, sens, borne in contraintes:
        row = np.array([np.nan_to_num(x["pente"].get(k, 0.0)) for x in var])
        cst = np.nan_to_num(age_ef.get(k, 0.0)) if age_ef else 0.0
        if sens == "<=":
            A.append(row); b.append(borne - cst)
        else:
            A.append(-row); b.append(-(borne - cst))
    r = linprog(c, A_ub=np.array(A) if A else None, b_ub=np.array(b) if b else None, bounds=[(0, x["borne"]) for x in var], method="highs")
    if not r.success:
        return None
    val = -r.fun - penalite * 0 + (sum(w * np.nan_to_num(age_ef.get(k, 0.0)) for k, w in objectif.items()) if age_ef else 0.0)
    return {"x": r.x, "objectif": float(val)}


def effets_programme(var, x, age_ef):
    tot = {}
    for xi, v in zip(x, var):
        for k, p in v["pente"].items():
            tot[k] = tot.get(k, 0.0) + xi * np.nan_to_num(p)
    for k, p in (age_ef or {}).items():
        tot[k] = tot.get(k, 0.0) + np.nan_to_num(p)
    return tot


def curseurs(var, x, age):
    cur = {}
    for xi, v in zip(x, var):
        if xi > 1e-6:
            act = LEVIERS[v["levier"]][0]
            cur[v["levier"]] = round(cur.get(v["levier"], act) + v["sens"] * xi, 2)
    if age != 64:
        cur["age_legal"] = age
    return cur


# Fonctions objectif et contraintes des scénarios (horizon de référence : 2037, soit 10 ans après l'élection)
OBJECTIFS = {
    "A": {"libelle": "Redressement budgétaire prioritaire",
          "objectif": {("dette", 2037): -1.0}, "penalite": 0.5,
          "contraintes": [(("pib", 2030), ">=", -0.5), (("chomage", 2030), "<=", 0.3), (("pauvrete", 2037), "<=", 0.0),
                          (("rdb_reel", 2030), ">=", -1.0)]},
    "B": {"libelle": "Croissance et réindustrialisation prioritaires",
          "objectif": {("pib", 2037): 1.0, ("industrie", 2037): 1.0}, "penalite": 0.05,
          "contraintes": [(("dette", 2037), "<=", 0.0), (("solde", 2030), ">=", 0.0), (("pauvrete", 2037), "<=", 0.2)]},
    "C": {"libelle": "Redressement équilibré",
          "objectif": {("pib", 2037): 1.0, ("emploi_k", 2037): 1 / 200, ("pauvrete", 2037): -2.0, ("rdb_reel", 2037): 1.0}, "penalite": 0.1,
          "contraintes": [(("dette", 2037), "<=", -5.0), (("solde", 2030), ">=", 0.5), (("pauvrete", 2037), "<=", 0.0),
                          (("chomage", 2030), "<=", 0.2)]},
    "D": {"libelle": "Effort maximal sur la dette (plafonds relevés)",
          "objectif": {("dette", 2047): -1.0}, "penalite": 0.5, "plafonds": (2.5, 4.0),
          "contraintes": [(("pib", 2030), ">=", -1.5), (("pauvrete", 2037), "<=", 0.0)]},
}


def main():
    E = charger()
    var = metamodele(E)
    out = {"variables": [{k: v for k, v in x.items() if k != "pente"} for x in var], "scenarios": {}}
    for s, d in OBJECTIFS.items():
        best = None
        essais = {}
        for age, nom in AGES.items():
            age_ef = effets(E[nom]) if nom else {}
            r = resoudre(var, age_ef, d["objectif"], d["contraintes"], d.get("penalite", 0.0), d.get("plafonds"))
            essais[age] = None if r is None else r["objectif"]
            if r is not None and (best is None or r["objectif"] > best["objectif"]):
                best = {**r, "age": age, "age_ef": age_ef}
        if best is None:
            out["scenarios"][s] = {"libelle": d["libelle"], "faisable": False, "essais": essais}
            continue
        eff = effets_programme(var, best["x"], best["age_ef"])
        out["scenarios"][s] = {"libelle": d["libelle"], "faisable": True, "age": best["age"], "essais": essais,
                               "curseurs": curseurs(var, best["x"], best["age"]),
                               "metamodele": {f"{k[0]}|{k[1]}": float(v) for k, v in eff.items()},
                               "objectif": {f"{k[0]}|{k[1]}": w for k, w in d["objectif"].items()},
                               "contraintes": [[f"{k[0]}|{k[1]}", sns, bnd] for k, sns, bnd in d["contraintes"]]}
        print(s, best["age"], out["scenarios"][s]["curseurs"])
    (RES / "strategie.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
