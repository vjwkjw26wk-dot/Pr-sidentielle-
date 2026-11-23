"""M15 — Offre de travail des ménages (phase 3, version 0.7).

Réaction de la participation au marché du travail (marge extensive) et des heures (marge intensive) aux mesures
socio-fiscales, différenciée par configuration familiale et niveau de salaire.

Méthode (Saez 2002 ; Immervoll et al. 2007) :
1. Cas types OpenFisca-France (législation 2024) : revenu disponible d'une personne selon qu'elle travaille (0,5 ou
   1 SMIC) ou non, pour cinq configurations familiales ; avant et après une variation unitaire de chaque levier.
   Gain à l'emploi G = RD(travail) − RD(sans emploi) ; taux marginal effectif à 1,5 SMIC.
2. Population concernée : personnes de 20 à 64 ans en emploi, par configuration et tranche de salaire, comptées sur
   l'échantillon du recensement 2022 (M4, pondéré).
3. Participation : ΔP_g = η_ext × P_g × Δln G_g ; heures : Δh/h = η_int × Δln(1 − TME) pour les salariés de 1 à 2 SMIC.

Élasticités (phase3/PARAMETRES) : η_ext = 0,2 (0,1 à 0,4), η_int = 0,1 (0,05 à 0,2) [L : revues de la littérature
française et européenne, OFCE 2023, DARES ; Bargain, Orsini et Peichl 2014].

Les effets sont linéarisés : chaque levier est caractérisé par son effet pour une variation unitaire (table mise en cache
dans outputs/m15_offre_travail.json), puis mis à l'échelle. Les seuils et non-linéarités du barème ne sont donc
représentés qu'au voisinage de la législation actuelle.
"""
from __future__ import annotations

import json
import pathlib

import numpy as np

RACINE = pathlib.Path(__file__).resolve().parents[1]
CACHE = RACINE / "outputs" / "m15_offre_travail.json"
SMIC = 17_900.0            # salaire imposable annuel au SMIC (2024), comme rapport/seuils_salaires.py
ETA_EXT = {"basse": 0.1, "centrale": 0.2, "haute": 0.4}
ETA_INT = {"basse": 0.05, "centrale": 0.1, "haute": 0.2}
# configurations : (couple, enfants, conjoint en emploi au SMIC)
TYPES = {"seul": (False, 0, False), "parent_isole": (False, 1, False), "couple_sans_enfant_conjoint_emploi": (True, 0, True),
         "couple_enfants_conjoint_emploi": (True, 2, True), "couple_enfants_conjoint_sans_emploi": (True, 2, False)}
NIVEAUX = (0.5, 1.0)
# leviers : variation unitaire et traduction
LEVIERS = {"rsa": "RSA, montant de base +10 %", "prime_activite": "Prime d'activité, montant de base +10 %",
           "allocations_familiales": "Base mensuelle des allocations familiales +10 %", "aides_logement": "Aides au logement −10 %",
           "ir_t1": "Taux de la première tranche de l'IR +1 point", "csg_activite": "CSG sur les revenus d'activité +1 point"}


def _situation(salaire, couple, n_enf, conj_emploi, csg_pts=0.0):
    net = salaire * 0.98 * (1 - 0.0125 * csg_pts)
    ind = {"a0": {"date_naissance": {"ETERNITY": "1989-01-01"}}}
    if salaire > 0:
        ind["a0"]["salaire_imposable"] = {"2024": salaire}
        ind["a0"]["salaire_net"] = {f"2024-{m:02d}": net / 12 for m in range(1, 13)}
        ind["a0"]["salaire_net"].update({"2023": net, "2022": net})
    if couple:
        ind["a1"] = {"date_naissance": {"ETERNITY": "1990-01-01"}, "statut_marital": {"2024": "marie"}}
        ind["a0"]["statut_marital"] = {"2024": "marie"}
        if conj_emploi:
            n1 = SMIC * 0.98 * (1 - 0.0125 * csg_pts)
            ind["a1"]["salaire_imposable"] = {"2024": SMIC}
            ind["a1"]["salaire_net"] = {f"2024-{m:02d}": n1 / 12 for m in range(1, 13)}
            ind["a1"]["salaire_net"].update({"2023": n1, "2022": n1})
    for j in range(n_enf):
        ind[f"e{j}"] = {"date_naissance": {"ETERNITY": f"{2018 - 2 * j}-01-01"}}
    par = [k for k in ind if k.startswith("a")]
    enf = [k for k in ind if k.startswith("e")]
    return {"individus": ind, "foyers_fiscaux": {"f": {"declarants": par, "personnes_a_charge": enf}},
            "familles": {"fa": {"parents": par, "enfants": enf}},
            "menages": {"m": {"personne_de_reference": [par[0]], **({"conjoint": [par[1]]} if couple else {}), "enfants": enf,
                              "statut_occupation_logement": {"2024-10": "locataire_vide"}, "loyer": {"2024-10": 550 + 100 * n_enf},
                              "zone_apl": {"2024-10": "zone_2"}}}}, net + (SMIC * 0.98 * (1 - 0.0125 * csg_pts) if couple and conj_emploi else 0.0)


def _revenu(T, salaire, typ, csg_pts=0.0, facteur_al=1.0):
    from openfisca_core.simulation_builder import SimulationBuilder
    couple, n, ce = TYPES[typ]
    sit, net = _situation(salaire, couple, n, ce, csg_pts)
    sim = SimulationBuilder().build_from_entities(T, sit)
    ir = float(sim.calculate("ip_net", "2024")[0])
    pr = {v: float(sim.calculate(v, "2024-10")[0]) * 12 for v in ("rsa", "ppa", "af", "aide_logement")}
    pr["aide_logement"] *= facteur_al
    return net - ir + sum(pr.values())


def _tbs(reforme: dict | None):
    from openfisca_france import FranceTaxBenefitSystem
    import m4_openfisca as mo
    T = FranceTaxBenefitSystem()
    if reforme:
        mo.appliquer_reforme(T, reforme, "2024-01-01")
    return T


def _indicateurs(T, csg=0.0, fal=1.0):
    out = {}
    for typ in TYPES:
        r0 = _revenu(T, 0.0, typ, csg, fal)
        g = {f"gain_{lv}": _revenu(T, SMIC * lv, typ, csg, fal) - r0 for lv in NIVEAUX}
        a, b = _revenu(T, SMIC * 1.5, typ, csg, fal), _revenu(T, SMIC * 1.53, typ, csg, fal)
        g["tme_15"] = 1 - (b - a) / (SMIC * 0.03 * 0.98)
        out[typ] = g
    return out


def construire_table():
    """Effets unitaires des leviers sur les gains à l'emploi et les taux marginaux (OpenFisca). Quelques minutes."""
    refs = {"rsa": ({"prestations_sociales.solidarite_insertion.minima_sociaux.rsa.rsa_m.montant_de_base_du_rsa": {"facteur": 1.1, "debut": "2024-01-01"}}, 0, 1),
            "prime_activite": ({"prestations_sociales.solidarite_insertion.minima_sociaux.ppa.pa_m.montant_de_base": {"facteur": 1.1}}, 0, 1),
            "allocations_familiales": ({"prestations_sociales.prestations_familiales.bmaf.bmaf": {"facteur": 1.1, "debut": "2024-01-01"}}, 0, 1),
            "aides_logement": (None, 0, 0.9),
            "ir_t1": ({"impot_revenu.bareme_ir_depuis_1945.bareme.brackets[1].rate": 0.12}, 0, 1),
            "csg_activite": (None, 1.0, 1)}
    base = _indicateurs(_tbs(None))
    table = {"base": base, "leviers": {}}
    for k, (ref, csg, fal) in refs.items():
        ind = _indicateurs(_tbs(ref), csg, fal)
        table["leviers"][k] = {typ: {"dlog_gain_" + str(lv): float(np.log(max(ind[typ][f"gain_{lv}"], 1.0) / max(base[typ][f"gain_{lv}"], 1.0)))
                                     for lv in NIVEAUX} | {"dlog_1_tme": float(np.log(max(1 - ind[typ]["tme_15"], 0.01) / max(1 - base[typ]["tme_15"], 0.01)))}
                               for typ in TYPES}
        print(k, "ok", flush=True)
    table["populations"] = populations()
    table["unites"] = {"rsa": 0.10, "prime_activite": 0.10, "allocations_familiales": 0.10, "aides_logement": -0.10, "ir_t1": 1.0, "csg_activite": 1.0}
    CACHE.write_text(json.dumps(table, ensure_ascii=False, indent=1))
    return table


def populations():
    """Personnes de 20 à 64 ans en emploi par configuration familiale et tranche de salaire (milliers, recensement 2022,
    salaires imputés M4)."""
    import pandas as pd
    import sys
    sys.path.insert(0, str(RACINE / "src"))
    import m10_couplage as C
    lignes = []
    for k in range(C.K_PREST):
        ind = pd.read_pickle(C.TMP / f"prest_ind_{k}.pkl")
        ind = ind.assign(adulte=ind.age >= 18, enfant=ind.age < 18, occupe=ind.TACT.astype(str) == "11")
        g = ind.groupby("men")
        men = pd.DataFrame({"n_adultes": g.adulte.sum(), "n_enfants": g.enfant.sum(), "n_occupes": g.occupe.sum()})
        ind = ind.join(men, on="men")
        ind["poids"] = ind.poids / C.K_PREST
        lignes.append(ind)
    d = pd.concat(lignes)
    d = d[(d.age >= 20) & (d.age <= 64) & d.occupe]
    s = d.salaires / SMIC
    d["tranche"] = np.select([s <= 0.75, s <= 1.25, s <= 2.0], ["0.5", "1.0", "1.5"], "haut")
    couple = d.n_adultes >= 2
    conj_emp = d.n_occupes >= 2
    d["type"] = np.select([~couple & (d.n_enfants == 0), ~couple, couple & (d.n_enfants == 0), couple & conj_emp],
                          ["seul", "parent_isole", "couple_sans_enfant_conjoint_emploi", "couple_enfants_conjoint_emploi"],
                          "couple_enfants_conjoint_sans_emploi")
    t = d.groupby(["type", "tranche"]).poids.sum() / 1e3
    return {f"{a}|{b}": float(v) for (a, b), v in t.items()}


def table():
    if not CACHE.exists():
        return construire_table()
    return json.loads(CACHE.read_text())


def effets(leviers: dict, niveau: str = "centrale") -> dict:
    """leviers : {"rsa": facteur−1, "prime_activite": facteur−1, "allocations_familiales": facteur−1,
    "aides_logement": facteur−1, "ir_t1": points, "csg_activite": points}.
    Renvoie la variation de la population active (milliers) et des heures (en % de l'emploi total), par type."""
    T = table()
    pop = T["populations"]
    d_pa, d_h, detail = 0.0, 0.0, {}
    emploi_tot = sum(pop.values())
    for lev, v in leviers.items():
        if not v or lev not in T["leviers"]:
            continue
        k = v / T["unites"][lev]
        for typ, e in T["leviers"][lev].items():
            dp = sum(ETA_EXT[niveau] * pop.get(f"{typ}|{lv}", 0.0) * k * e[f"dlog_gain_{lv}"] for lv in NIVEAUX)
            dh = ETA_INT[niveau] * pop.get(f"{typ}|1.5", 0.0) * k * e["dlog_1_tme"]
            d_pa += dp
            d_h += dh
            detail[f"{lev}|{typ}"] = {"participation_milliers": dp, "heures_equivalent_milliers": dh}
    return {"population_active_milliers": d_pa, "heures_pct_emploi": 100 * d_h / emploi_tot, "detail": detail,
            "emploi_couvert_milliers": emploi_tot}


if __name__ == "__main__":
    t = construire_table()
    print(json.dumps({k: v for k, v in t.items() if k != "base"}, indent=1)[:3000])
