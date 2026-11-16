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
    global _TBS
    if _TBS is None:
        _TBS = FranceTaxBenefitSystem()
    return _TBS


STATUT = {"1": "marie", "2": "pacse", "3": "celibataire", "4": "veuf", "5": "divorce", "6": "celibataire"}


def simulation(ind: pd.DataFrame, annee: int, autres: pd.Series | None = None, option_bareme: bool = False):
    """autres : revenus de capitaux mobiliers (case 2TR) par foyer ; option_bareme : case 2OP (imposition au barème)."""
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
    return sim, foyers


def impot(ind: pd.DataFrame, annee: int = 2024, variables=("ip_net", "rfr", "nbptr", "prelevement_forfaitaire_unique_ir"),
          autres: pd.Series | None = None, option_bareme: bool = False) -> pd.DataFrame:
    sim, foyers = simulation(ind, annee, autres, option_bareme)
    return pd.DataFrame({v + "_of": sim.calculate(v, str(annee)) for v in variables}, index=foyers)
