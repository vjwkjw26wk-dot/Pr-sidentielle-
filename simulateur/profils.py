"""Profils de ménages types (cas types) : impôt sur le revenu et prestations, législation actuelle et après réforme.

Les profils sont fictifs (pas de données individuelles) ; calcul OpenFisca-France, revenus 2024, prestations
d'octobre 2024 × 12. Chaque calcul tourne dans un processus séparé pour pouvoir appliquer la réforme (variable
d'environnement M4_REFORME).
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import tempfile

RACINE = pathlib.Path(__file__).resolve().parents[1]
SMIC_ANNUEL_NET_IMPOSABLE_2024 = 17_900   # ordre de grandeur (SMIC net imposable annuel, temps plein)

PROFILS = {
    "celibataire_smic": ("Personne seule, SMIC à temps plein, locataire", [{"age": 30, "salaire": SMIC_ANNUEL_NET_IMPOSABLE_2024}], False, 0),
    "parent_isole_mi_temps": ("Parent isolé, un enfant de 6 ans, mi-temps au SMIC", [{"age": 35, "salaire": SMIC_ANNUEL_NET_IMPOSABLE_2024 / 2}], False, 1),
    "couple_2_smic_2_enfants": ("Couple, deux SMIC, deux enfants", [{"age": 38, "salaire": SMIC_ANNUEL_NET_IMPOSABLE_2024}, {"age": 36, "salaire": SMIC_ANNUEL_NET_IMPOSABLE_2024}], True, 2),
    "couple_cadres_2_enfants": ("Couple de cadres (2 × 50 000 € imposables), deux enfants", [{"age": 45, "salaire": 50_000}, {"age": 44, "salaire": 50_000}], True, 2),
    "retraite_seul": ("Retraité seul, pension de 20 000 € imposables", [{"age": 72, "retraite": 20_000}], False, 0),
    "sans_revenu": ("Personne seule sans revenu d'activité", [{"age": 40}], False, 0),
}


def _calcul(cle: str) -> dict:
    """Exécuté dans le processus fils."""
    sys.path.insert(0, str(RACINE / "src"))
    import m4_openfisca as mo
    from openfisca_core.simulation_builder import SimulationBuilder
    lib, adultes, couple, n_enf = PROFILS[cle]
    T = mo.tbs()
    ind = {}
    for i, a in enumerate(adultes):
        d = {"date_naissance": {"ETERNITY": f"{2024 - a['age']}-01-01"}}
        if a.get("salaire"):
            d["salaire_imposable"] = {"2024": a["salaire"]}
            d["salaire_net"] = {f"2024-{m:02d}": a["salaire"] / 12 * 0.98 for m in range(1, 13)}
            d["salaire_net"].update({"2023": a["salaire"] * 0.98, "2022": a["salaire"] * 0.98})
        if a.get("retraite"):
            d["retraite_imposable"] = {"2024": a["retraite"]}
            d["retraite_nette"] = {f"2024-{m:02d}": a["retraite"] / 12 * 0.93 for m in range(1, 13)}
            d["retraite_nette"].update({"2023": a["retraite"] * 0.93, "2022": a["retraite"] * 0.93})
        ind[f"a{i}"] = d
    for j in range(n_enf):
        ind[f"e{j}"] = {"date_naissance": {"ETERNITY": f"{2024 - 6 - 2 * j}-01-01"}}
    parents = [k for k in ind if k.startswith("a")]
    enfants = [k for k in ind if k.startswith("e")]
    sit = {"individus": ind,
           "foyers_fiscaux": {"f": {"declarants": parents, "personnes_a_charge": enfants}},
           "familles": {"fa": {"parents": parents, "enfants": enfants}},
           "menages": {"m": {"personne_de_reference": [parents[0]], **({"conjoint": [parents[1]]} if couple else {}), "enfants": enfants,
                             "statut_occupation_logement": {"2024-10": "locataire_vide"}, "loyer": {"2024-10": 550 + 100 * n_enf},
                             "zone_apl": {"2024-10": "zone_2"}}}}
    if couple:
        for p in parents:
            ind[p]["statut_marital"] = {"2024": "marie"}
    sim = SimulationBuilder().build_from_entities(T, sit)
    ir = float(sim.calculate("ip_net", "2024")[0])
    out = {"impot_revenu": ir}
    for v in ("rsa", "ppa", "af", "aide_logement"):
        out[v] = float(sim.calculate(v, "2024-10")[0]) * 12
    rev = sum(a.get("salaire", 0) * 0.98 + a.get("retraite", 0) * 0.93 for a in adultes)
    out["revenu_disponible_approche"] = rev - ir + sum(out[v] for v in ("rsa", "ppa", "af", "aide_logement"))
    return out


def calculer(reforme: dict | None = None) -> dict:
    env = dict(os.environ)
    env.pop("M4_REFORME", None)
    if reforme:
        f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        json.dump(reforme, f)
        f.close()
        env["M4_REFORME"] = f.name
    code = (f"import sys, json; sys.path.insert(0, {str(RACINE)!r}); from simulateur import profils as p; "
            f"print(json.dumps({{k: p._calcul(k) for k in p.PROFILS}}))")
    r = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True, check=True)
    return json.loads(r.stdout.strip().splitlines()[-1])


def comparer(reforme: dict | None) -> list:
    a = calculer(None)
    b = calculer(reforme) if reforme else a
    return [{"profil": k, "libelle": PROFILS[k][0], **{f"{v}_actuel": a[k][v] for v in a[k]},
             "variation_revenu_disponible": b[k]["revenu_disponible_approche"] - a[k]["revenu_disponible_approche"]} for k in PROFILS]


def ajustements_analytiques(mesures: list, actuel: list) -> dict:
    """Variations de revenu disponible des profils (€/an) dues aux mesures non calculées par OpenFisca (version 0.4) :
    CSG (assiette brute approchée : salaire imposable / 0,78 × 98,25 % ; pensions au taux plein seulement au-delà du
    seuil de revenu, non atteint par le profil retraité), TVA et taxe carbone (consommation du profil selon son quintile,
    enquête Budget des familles via Eurostat, répercussion de 80 % pour la TVA), indexation des pensions (première
    année), aides au logement (variation proportionnelle). Les effets sur les prix des autres mesures ne sont pas inclus."""
    sys.path.insert(0, str(RACINE / "src"))
    import m10_couplage as C
    from simulateur import executer as X
    pr = C.profils_consommation()
    out = {k: 0.0 for k in PROFILS}
    rd = {p["profil"]: p["revenu_disponible_approche_actuel"] for p in actuel}
    al = {p["profil"]: p.get("aide_logement_actuel", 0.0) for p in actuel}
    def decile(r):          # décile approché du profil d'après son revenu disponible par unité de consommation
        seuils = [12_000, 15_000, 17_500, 19_500, 21_500, 24_000, 27_000, 31_000, 38_000]
        return sum(r > x for x in seuils)
    for k, (lib, adultes, couple, n_enf) in PROFILS.items():
        uc = 1 + 0.5 * (len(adultes) - 1) + 0.3 * n_enf
        d = decile(rd[k] / uc)
        cons = rd[k] * pr["consommation"][d] / pr["consommation"][4]   # consommation relative à la médiane
        cons = min(cons, rd[k]) * 0.85
        for m in mesures:
            t, p = m["type"], m.get("parametres", {})
            if t == "csg":
                out[k] -= sum(a.get("salaire", 0) / 0.78 * 0.9825 for a in adultes) * float(p.get("activite_points", 0)) / 100
            elif t == "tva":
                out[k] -= cons * pr["tva_normale"][d] * X.REPERCUSSION_TVA * float(p["points"]) / 120
            elif t == "tva_reduite":
                out[k] -= cons * pr["tva_reduite"][d] * X.REPERCUSSION_TVA * float(p["points"]) / 108
            elif t == "taxe_carbone":
                part_moy = sum(pr["energie"]) / 10
                out[k] -= cons * pr["energie"][d] / part_moy * float(p["euros_tonne"]) * X.RENDEMENT_EURO_TONNE * 1e6 / 1_640e9
            elif t == "indexation_pensions":
                out[k] += sum(a.get("retraite", 0) * 0.93 for a in adultes) * float(p["points"]) / 100
            elif t == "aides_logement":
                out[k] += (float(p["facteur"]) - 1) * al[k]
    return out
