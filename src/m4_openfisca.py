"""Couplage de la population M4 avec OpenFisca-France (calcul vectorisé de l'impôt sur le revenu).

Entités : individu ; foyer fiscal = foyer M4 ; famille = foyer M4 (approximation : ignore les familles de
concubins, sans effet sur l'IR) ; ménage = ménage du recensement.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from openfisca_core.simulation_builder import SimulationBuilder
from openfisca_france import FranceTaxBenefitSystem

_TBS = None


def tbs():
    """Système socio-fiscal. Si la variable d'environnement M4_REFORME désigne un fichier JSON
    {"debut": "AAAA-MM-JJ", "parametres": {chemin: valeur}}, les paramètres sont modifiés à partir de cette date
    (réforme paramétrique ; voir `appliquer_reforme`)."""
    global _TBS
    if _TBS is None:
        import json
        import os
        _TBS = FranceTaxBenefitSystem()
        chemin = os.environ.get("M4_REFORME")
        if chemin:
            r = json.loads(open(chemin, encoding="utf-8").read())
            appliquer_reforme(_TBS, r["parametres"], r.get("debut", "2024-01-01"))
    return _TBS


def noeud(parametres, chemin: str):
    """Paramètre OpenFisca désigné par un chemin pointé ; « brackets[i] » sélectionne une tranche de barème."""
    import re
    n = parametres
    for morceau in chemin.split("."):
        m = re.fullmatch(r"(\w+)\[(\d+)\]", morceau)
        if m:
            n = getattr(n, m.group(1))[int(m.group(2))]
        else:
            n = getattr(n, morceau)
    return n


def appliquer_reforme(T, parametres: dict, debut: str = "2024-01-01"):
    """Modifie en place les paramètres de T : {chemin: valeur} (valeur absolue) ou {chemin: {"facteur": x}} (valeur
    de la législation en vigueur multipliée par x)."""
    from openfisca_core import periods
    for chemin, v in parametres.items():
        p = noeud(T.parameters, chemin)
        d = debut
        if isinstance(v, dict):
            d = v.get("debut", debut)
            v = p(d) * v["facteur"] if "facteur" in v else v["valeur"]
        p.update(start=periods.instant(d), value=v)
    return T


STATUT = {"1": "marie", "2": "pacse", "3": "celibataire", "4": "veuf", "5": "divorce", "6": "celibataire"}


def simulation(ind: pd.DataFrame, annee: int, autres: pd.Series | None = None, option_bareme: bool = False,
               entrees_foyer: dict | None = None, entrees_individu: dict | None = None):
    """autres : revenus de capitaux mobiliers (case 2TR) par foyer ; option_bareme : case 2OP (imposition au barème) ;
    entrees_foyer : {variable OpenFisca annuelle du foyer: Series indexée par foyer} ;
    entrees_individu : {variable OpenFisca de l'individu: nom de colonne de ind} (montant annuel)."""
    ind = ind.sort_values(["foyer", "role"], key=lambda s: s.map({"dec": 0, "conj": 1, "pac": 2}) if s.name == "role" else s)
    ind = ind.reset_index(drop=True)
    T = tbs()
    sb = SimulationBuilder()
    sb.create_entities(T)
    ids = [f"i{k}" for k in range(len(ind))]
    sb.declare_person_entity("individu", ids)
    foyers = ind.foyer.unique()
    # sous-rôles exigés par OpenFisca-France : déclarant principal / conjoint ; demandeur / conjoint
    roles_f = np.select([ind.role == "dec", ind.role == "conj"], ["declarant_principal", "conjoint"], "personne_a_charge")
    roles_fa = np.select([ind.role == "dec", ind.role == "conj"], ["demandeur", "conjoint"], "enfant")
    for ent, roles in (("foyer_fiscal", roles_f), ("famille", roles_fa)):
        e = sb.declare_entity(ent, foyers)
        sb.join_with_persons(e, ind.foyer.to_numpy(), roles)
    menages = ind.men.unique()
    rm = ind.groupby("men").cumcount()
    roles_m = np.where(rm == 0, "personne_de_reference", np.where(ind.role == "pac", "enfant", "autre"))
    e = sb.declare_entity("menage", menages)
    sb.join_with_persons(e, ind.men.to_numpy(), roles_m)
    sim = sb.build(T)
    a = str(annee)
    naissance = np.array([f"{annee - int(x)}-07-01" for x in ind.age], dtype="datetime64[D]")
    sim.set_input("date_naissance", "ETERNITY", naissance)
    statut = ind.STAT_CONJ.map(STATUT).to_numpy()
    # marié ou pacsé déclarant seul (conjoint absent du ménage) : traité comme célibataire
    couple_foyer = ind.groupby("foyer").role.transform(lambda r: (r == "conj").any()).to_numpy()
    statut = np.where(~couple_foyer & np.isin(statut, ["marie", "pacse"]), "celibataire", statut)
    # dans un foyer de couple, les deux déclarants partagent le statut du déclarant principal
    statut = np.where(couple_foyer & (ind.role != "pac").to_numpy(),
                      ind.groupby("foyer").STAT_CONJ.transform("first").map(STATUT).to_numpy(), statut)
    sv = T.variables["statut_marital"].possible_values
    for m in range(1, 13):
        sim.set_input("statut_marital", f"{annee}-{m:02d}", sv.encode(np.asarray(statut).astype("U")))
    sim.set_input("salaire_imposable", a, ind.salaires.to_numpy())
    sim.set_input("retraite_imposable", a, ind.pensions.to_numpy())
    # case T : parent isolé ayant des personnes à charge
    fo = ind.groupby("foyer", sort=False).agg(couple=("role", lambda r: (r == "conj").any()), pac=("role", lambda r: (r == "pac").sum()))
    fo = fo.reindex(foyers)
    sim.set_input("caseT", a, (~fo.couple & (fo.pac > 0)).to_numpy())
    if autres is not None:
        sim.set_input("f2tr", a, autres.reindex(foyers).fillna(0).to_numpy())
    sim.set_input("f2op", a, np.full(len(foyers), option_bareme))
    for var, serie in (entrees_foyer or {}).items():
        sim.set_input(var, a, serie.reindex(foyers).fillna(0).to_numpy())
    for var, col in (entrees_individu or {}).items():
        sim.set_input(var, a, ind[col].to_numpy())
    return sim, foyers


def impot(ind: pd.DataFrame, annee: int = 2024, variables=("ip_net", "rfr", "nbptr", "prelevement_forfaitaire_unique_ir"),
          autres: pd.Series | None = None, option_bareme: bool = False,
          entrees_foyer: dict | None = None, entrees_individu: dict | None = None) -> pd.DataFrame:
    sim, foyers = simulation(ind, annee, autres, option_bareme, entrees_foyer, entrees_individu)
    return pd.DataFrame({v + "_of": sim.calculate(v, str(annee)) for v in variables}, index=foyers)
