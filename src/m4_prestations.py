"""M4 — Prestations sociales (RSA, prime d'activité, allocations familiales, aides au logement) sur la population M4.

Différences avec le calcul de l'impôt (`m4_openfisca.py`) :
- l'entité « famille » est la famille au sens de la CAF : un couple (marié, pacsé ou en concubinage) et ses enfants
  de moins de 25 ans vivant au foyer ; un enfant de 25 ans ou plus et toute personne hors famille forment leur propre
  famille ;
- les ressources sont mensuelles : revenus nets d'activité, allocations chômage, pensions nettes, saisis sur les douze
  mois de l'année de calcul (montants annuels de M4 répartis uniformément) ; les bases de ressources annuelles
  (années N-1 et N-2) reprennent les mêmes montants ;
- logement : statut d'occupation du recensement ; loyer et zone imputés (hypothèses de niveau D, voir `imputer_loyer`).

Limites assumées (version 1) : pas d'allocation aux adultes handicapés (aucune information sur le handicap dans le
recensement), revenus d'indépendants traités comme revenus d'activité nets, revenus du patrimoine ignorés, pas de
non-recours (les montants simulés sont des droits, à comparer aux montants versés corrigés du non-recours publié).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from openfisca_core.simulation_builder import SimulationBuilder

import m4_openfisca as mo

# Zones APL approchées par département (le recensement ne donne la commune que via le département, et seulement
# pour les plus grands) : zone 1 = Paris et petite couronne ; zone 2 = grande couronne et départements de grandes
# agglomérations identifiés dans le fichier ; zone 3 = autres. Hypothèse D.
ZONE1 = {"75", "92", "93", "94"}
ZONE2 = {"77", "78", "91", "95", "06", "13", "31", "33", "34", "35", "38", "44", "59", "67", "69", "74", "83", "974"}
# Loyer mensuel hors charges au m² (hypothèse D, ordres de grandeur publics : parc social ≈ 6,5 €/m² ; parc privé
# ≈ 21 € en zone 1, 13 € en zone 2, 10 € en zone 3) ; meublé : +15 %.
PRIX_M2 = {"hlm": 6.5, ("prive", 1): 21.0, ("prive", 2): 13.0, ("prive", 3): 10.0}
SURFACE = {"1": 25, "2": 35, "3": 50, "4": 70, "5": 90, "6": 110, "7": 140}
STATUT = {"10": "proprietaire", "21": "locataire_vide", "22": "locataire_hlm", "23": "locataire_meuble",
          "30": "loge_gratuitement"}


def familles_caf(ind: pd.DataFrame) -> pd.DataFrame:
    """Ajoute `famille_caf` et `role_fa` (demandeur, conjoint, enfant)."""
    ind = ind.copy()
    fam = ind.NUMF != "Z"
    enfant = fam & (ind.LIENF == "3") & (ind.age < 25)
    adulte = fam & ind.LIENF.isin(["1", "2"])
    ind["famille_caf"] = np.where(enfant | adulte, ind.men + "_F" + ind.NUMF, ind.men + "_I" + ind.index.astype(str))
    ind["role_fa"] = np.where(enfant, "enfant", "demandeur")
    # second adulte d'une famille : conjoint
    ordre = ind[adulte].sort_values(["famille_caf", "age"], ascending=[True, False])
    second = ordre.groupby("famille_caf").cumcount() == 1
    ind.loc[second[second].index, "role_fa"] = "conjoint"
    # famille sans adulte (rare : enfants seuls) : le plus âgé devient demandeur
    sans_dem = ~ind.groupby("famille_caf").role_fa.transform(lambda r: (r == "demandeur").any())
    if sans_dem.any():
        aine = ind[sans_dem].sort_values("age", ascending=False).groupby("famille_caf").head(1).index
        ind.loc[aine, "role_fa"] = "demandeur"
    return ind


def zone(dept: pd.Series) -> np.ndarray:
    return np.where(dept.isin(ZONE1), 1, np.where(dept.isin(ZONE2), 2, 3))


def imputer_loyer(men: pd.DataFrame) -> pd.Series:
    """Loyer mensuel hors charges imputé = surface (milieu de classe) × prix au m² selon parc et zone."""
    s = men.SURF.map(SURFACE).fillna(50).to_numpy()
    z = zone(men.DEPT)
    prix = np.where(men.STOCD == "22", PRIX_M2["hlm"],
                    np.select([z == 1, z == 2], [PRIX_M2[("prive", 1)], PRIX_M2[("prive", 2)]], PRIX_M2[("prive", 3)]))
    prix = np.where(men.STOCD == "23", prix * 1.15, prix)
    loyer = np.where(men.STOCD.isin(["21", "22", "23"]), s * prix, 0.0)
    return pd.Series(loyer, index=men.index)


def simulation(ind: pd.DataFrame, annee: int = 2024):
    """ind : individus M4 (colonnes salaires, pensions annuels, TACT, STAT, STOCD, SURF, DEPT, foyer, role, men…)."""
    T = mo.tbs()
    ind = familles_caf(ind)
    ind = ind.sort_values(["famille_caf", "role_fa"], key=lambda s: s.map({"demandeur": 0, "conjoint": 1, "enfant": 2})
                          if s.name == "role_fa" else s).reset_index(drop=True)
    sb = SimulationBuilder()
    sb.create_entities(T)
    sb.declare_person_entity("individu", [f"i{k}" for k in range(len(ind))])
    fams = ind.famille_caf.unique()
    e = sb.declare_entity("famille", fams)
    sb.join_with_persons(e, ind.famille_caf.to_numpy(), ind.role_fa.to_numpy())
    foyers = ind.foyer.unique()
    roles_f = np.select([ind.role == "dec", ind.role == "conj"], ["declarant_principal", "conjoint"], "personne_a_charge")
    # un foyer fiscal ne peut avoir qu'un déclarant principal : on garde le rôle M4
    e = sb.declare_entity("foyer_fiscal", foyers)
    sb.join_with_persons(e, ind.foyer.to_numpy(), roles_f)
    menages = ind.men.unique()
    rang = ind.groupby("men").cumcount()
    roles_m = np.where(ind.LPRM == "1", "personne_de_reference",
                       np.where(ind.LPRM == "2", "conjoint", np.where(ind.LPRM == "3", "enfant", "autre")))
    # garantit exactement une personne de référence par ménage
    a_pr = ind.assign(pr=roles_m == "personne_de_reference").groupby("men").pr.transform("sum")
    roles_m = np.where((a_pr == 0) & (rang == 0), "personne_de_reference", roles_m)
    roles_m = np.where((a_pr > 1) & (roles_m == "personne_de_reference") & (rang > 0), "autre", roles_m)
    roles_m = np.where((roles_m == "conjoint") & (ind.groupby("men").cumcount() > 0) &
                       (ind.assign(c=roles_m == "conjoint").groupby("men").c.cumsum() > 1), "autre", roles_m)
    e = sb.declare_entity("menage", menages)
    sb.join_with_persons(e, ind.men.to_numpy(), roles_m)
    sim = sb.build(T)
    sim.set_input("date_naissance", "ETERNITY", np.array([f"{annee - int(a)}-07-01" for a in ind.age], dtype="datetime64[D]"))
    occ = (ind.TACT == "11").to_numpy()
    chom = (ind.TACT == "12").to_numpy()
    net_act = np.where(occ, ind.salaires.to_numpy() * 0.97 / 12, 0.0)
    net_cho = np.where(chom, ind.salaires.to_numpy() * 0.95 / 12, 0.0)
    net_ret = ind.pensions.to_numpy() * 0.92 / 12
    # ménage : statut d'occupation, loyer, zone
    men = ind.groupby("men", sort=False).agg(STOCD=("STOCD", "first"), SURF=("SURF", "first"), DEPT=("DEPT", "first")).reindex(menages)
    loyer = imputer_loyer(men).to_numpy()
    sv = T.variables["statut_occupation_logement"].possible_values
    zv = T.variables["zone_apl"].possible_values
    statut = sv.encode(men.STOCD.map(STATUT).fillna("non_renseigne").to_numpy().astype("U"))
    zones = zv.encode(np.array([f"zone_{z}" for z in zone(men.DEPT)]).astype("U"))
    # montants annuels : OpenFisca les répartit sur les mois (variables mensuelles à saisie divisée par période)
    for a in (str(annee - 2), str(annee - 1), str(annee)):
        sim.set_input("salaire_net", a, 12 * net_act)
        sim.set_input("chomage_net", a, 12 * net_cho)
        sim.set_input("retraite_nette", a, 12 * net_ret)
        sim.set_input("salaire_imposable", a, 12 * net_act / 0.97 * 0.99)
        sim.set_input("chomage_imposable", a, 12 * net_cho / 0.95 * 0.97)
        sim.set_input("retraite_imposable", a, 12 * net_ret / 0.92 * 0.96)
    for a in (annee - 1, annee):
        for m in range(1, 13):
            p = f"{a}-{m:02d}"
            sim.set_input("statut_occupation_logement", p, statut)
            sim.set_input("loyer", p, loyer)
            sim.set_input("zone_apl", p, zones)
    return sim, ind, fams, menages


def prestations(ind: pd.DataFrame, mois: str = "2024-10", variables=("rsa", "ppa", "af", "aide_logement")):
    sim, ind2, fams, _ = simulation(ind, int(mois[:4]))
    out = pd.DataFrame({v: sim.calculate(v, mois) for v in variables}, index=fams)
    poids = ind2.groupby("famille_caf", sort=False).poids.first().reindex(fams)
    out["poids"] = poids.to_numpy()
    return out
