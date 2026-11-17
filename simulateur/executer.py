"""Exécution d'un scénario (version 0.1).

Entrée : un scénario JSON (voir `scenarios/exemple_programme.json`) :
  {"nom", "description", "base": 2022, "horizon": 2030,
   "hypotheses": {"fermeture_offre": 0.15, "europe": true, "incertitude": 0},
   "mesures": [{"type": <clé du catalogue>, "parametres": {...}}, ...]}
Sortie : dictionnaire JSON-sérialisable : trajectoires de référence et du scénario, écarts, effets distributifs
(mesures socio-fiscales), incertitude, et la fiche de transparence (mesures, hypothèses, données, modèles, paramètres
sensibles, incertitudes, limites).
Usage : python3 -m simulateur.executer scenarios/exemple_programme.json [sortie.json]
"""
from __future__ import annotations

import copy
import hashlib
import json
import pathlib
import sys
import time

import numpy as np
import pandas as pd

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
sys.path.insert(0, str(RACINE / "tests"))
import m8_modele as M8  # noqa: E402
from simulateur import catalogue as CAT  # noqa: E402

_MODELES = {}
FIN_REF = 2025           # dernière année observée : les montants en euros des mesures sont exprimés en euros de 2025
COUT_AGENT_PUBLIC = 56.0          # k€ par agent et par an (rémunération et cotisations, ordre de grandeur 2025)
COUT_PUBLIC_POINT_SMIC = 660.0   # M€ par point de SMIC : allègements de cotisations (400) et masse salariale publique (260), Institut Montaigne 2022
PART_SMIC_DIFFUSION = 0.11        # hausse de la masse salariale moyenne pour 1 de hausse du SMIC (diffusion comprise, hypothèse D)
RENDEMENT_POINT_TVA = 8_200.0     # M€ par point de taux normal (80 % de la TVA nette de 206 Md€ au taux de 20 %)
REPERCUSSION_TVA, PART_TAUX_NORMAL = 0.8, 0.55
RENDEMENT_EURO_TONNE = 200.0      # M€ par euro de composante carbone (ordre de grandeur)
RENDEMENT_POINT_PFU = 600.0       # M€ par point (assiette d'environ 60 Md€)
ASSIETTE_ISF, RENDEMENT_IFI = 930_000.0, 2_200.0     # M€ : patrimoine taxable au-delà du seuil (ISF 2017 revalorisé) ; IFI remplacé
RENDEMENT_SUCCESSIONS = 18_000.0  # M€ (droits de mutation à titre gratuit)
DEPENSE_ASSURANCE_CHOMAGE = 40_000.0
EFFET_CHOMAGE_STRUCTUREL = 0.1    # points de chômage structurel pour 10 % de variation des allocations (hypothèse D, 0-0,3)
DEPENSE_ASPA = 4_100.0
REPERCUSSION_IMPOTS_PRODUCTION = 0.5   # part répercutée sur les prix de la valeur ajoutée marchande (hypothèse D)
RENDEMENT_POINT_TVA_REDUITE, PART_TAUX_REDUITS = 5_000.0, 0.35
COMPENSATION_PRODUCTIVITE_HORAIRE = 0.7   # part de la baisse de durée absorbée sans embauche : productivité horaire, intensification, heures supplémentaires (35 heures : environ 350 000 emplois pour −10 % d'heures ; hypothèse D)
PART_HORS_UE, REPERCUSSION_DOUANE, RECETTE_NETTE_DOUANE = 0.45, 0.8, 0.38
PART_EXPORT_HORS_UE, ELAST_EXPORT_DOUANE = 0.40, 0.8
COUT_LOGEMENT_SOCIAL, SUBVENTION_LOGEMENT = 170.0, 0.25    # k€ par logement ; part financée par la dépense publique
ELAST_CAPITAL_PUBLIC, PART_CAPITAL_PUBLIC, DEPRECIATION_PUBLIQUE = 0.08, 0.55, 0.04
DEBUT_DEFAUT = 2028      # premier budget voté après l'élection présidentielle de 2027
HORIZON_DEFAUT = 2032    # fin du mandat
VARIABLES = {"pib": "PIB en volume (M€ 2015)", "c": "Consommation des ménages", "fbcf": "Investissement", "x": "Exportations",
             "m": "Importations", "emploi": "Emploi (milliers)", "chomage": "Taux de chômage (%)", "pc": "Prix à la consommation (indice)",
             "salaire": "Salaire moyen par tête", "rdb": "Revenu disponible brut (M€)", "solde_pib": "Solde public (% du PIB)",
             "dette_pib": "Dette publique (% du PIB)", "recettes": "Recettes publiques (M€)", "depenses": "Dépenses publiques (M€)",
             "tuc_industrie": "Taux d'utilisation des capacités, industrie (%)",
             "croissance": "Croissance du PIB en volume (%)", "inflation": "Inflation (prix à la consommation, %)",
             "recettes_pib": "Recettes publiques (% du PIB)", "depenses_pib": "Dépenses publiques (% du PIB)",
             "interets_pib": "Charge d'intérêts de la dette (% du PIB)", "taux_apparent": "Taux apparent de la dette (%)",
             "pensions_pib": "Pensions de droit direct (% du PIB)", "retraites_pour_100_actifs": "Retraités pour 100 actifs",
             "part_industrie": "Industrie manufacturière (% du PIB, valeur ajoutée)", "emploi_industrie": "Emploi industriel (milliers)",
             "population_active": "Population active (milliers)"}
EN_POINTS = {"chomage", "solde_pib", "dette_pib", "tuc_industrie", "croissance", "inflation", "recettes_pib", "depenses_pib",
             "interets_pib", "taux_apparent", "pensions_pib", "retraites_pour_100_actifs", "part_industrie"}


def derivees(mod, r, ex, pensions_M, retraites_k):
    """Indicateurs dérivés d'une trajectoire simulée (DataFrame M8) : taux de croissance, ratios au PIB, retraites."""
    r = r.copy()
    m = mod.macro
    pib1 = pd.concat([pd.Series({mod.B: float(m.pib[mod.B])}), r.pib])
    pc1 = pd.concat([pd.Series({mod.B: float(m.p_c[mod.B])}), r.pc])
    r["croissance"] = (pib1 / pib1.shift(1) - 1).reindex(r.index) * 100
    r["inflation"] = (pc1 / pc1.shift(1) - 1).reindex(r.index) * 100
    for k in ("recettes", "depenses", "interets"):
        r[k + "_pib"] = r[k] / r.pib_nominal * 100
    r["pensions_pib"] = pd.Series(pensions_M).reindex(r.index) / r.pib_nominal * 100
    r["population_active"] = ex.population_active.reindex(r.index)
    r["retraites_pour_100_actifs"] = pd.Series(retraites_k).reindex(r.index) / r.population_active * 100
    return r


def modele(base: int) -> M8.Modele:
    if base not in _MODELES:
        _MODELES[base] = M8.Modele(base)
    return _MODELES[base]


def _serie_g(mod, ex, points, debut, montee=1):
    """Consommation publique modifiée de `points` de PIB à partir de `debut`, atteints linéairement en `montee` ans."""
    g_part = mod.T.Fd.loc[mod.P, ["P3_S13", "P3_S15"]].values.sum() + mod.T.Fm.loc[mod.P, ["P3_S13", "P3_S15"]].values.sum()
    frac = lambda t: min(1.0, (t - debut + 1) / max(1, montee)) if t >= debut else 0.0  # noqa: E731
    return ex.conso_publique * pd.Series({t: 1 + frac(t) * points / 100 * mod.macro.pib_cp[mod.B] / g_part
                                          for t in ex.conso_publique.index})


def regle_age(p: dict) -> str:
    """Règle M9 : {"age": 60, "debut": 2028, "mode": "progressif"|"immediat"} ou ancienne forme {"regle": ...}."""
    if "age" in p:
        return f"{float(p['age']):g}@{int(p.get('debut', DEBUT_DEFAUT))}:{p.get('mode', 'progressif')}"
    return str(p["regle"])


def debut_socio_fiscal(mesures) -> int:
    """Année d'entrée en vigueur commune des mesures de ménages (M10) et des transferts ; la première si plusieurs."""
    d = [int(m.get("parametres", {}).get("debut", DEBUT_DEFAUT)) for m in mesures
         if m["type"] in ("bareme_ir", "rsa", "prime_activite", "allocations_familiales", "transferts_menages", "csg", "pfu", "isf",
                          "aides_logement")]
    return min(d) if d else DEBUT_DEFAUT


def construire(scenario: dict, mod, central=None, journal=None):
    """Exogènes de référence et du scénario, et informations complémentaires (distribution, M9)."""
    H = scenario.get("hypotheses", {})
    ans = range(mod.B + 1, scenario.get("horizon", HORIZON_DEFAUT) + 1)
    rho = H.get("fermeture_offre", M8.RHO_DEFAUT)
    mesures = scenario.get("mesures", [])
    info = {"distribution": None, "statique": {}}
    kw = {"fermeture_offre": rho}
    ages = [m for m in mesures if m["type"] == "age_legal"]
    import m8_reference as RF
    R = RF.compte_reference(mod, range(mod.B + 1, max(2035, max(ans)) + 1), journal=(journal.append if journal is not None else (lambda *a: None)))
    nom_ref = scenario.get("hypotheses", {}).get("reference", "inchangee")
    ref = RF.exogenes_variante(mod, range(mod.B + 1, max(2035, max(ans)) + 1), nom_ref,
                               journal=(journal.append if journal is not None else (lambda *a: None)))
    info["reference"] = RF.VARIANTES_REFERENCE[nom_ref]
    ref.fermeture_offre = rho
    var = copy.deepcopy(ref)
    if central is None:
        central = R["trajectoire"] if nom_ref == "inchangee" else mod.simuler(range(mod.B + 1, max(2035, max(ans)) + 1), ref)
    info["pensions_reference"] = R["pensions"]
    if ages:
        import m9_retraites as R9
        act = R9.ActiviteSeniors()
        pens = R9.Pensions(act)
        k = act.estimer_part_emploi()
        regle = regle_age(ages[-1]["parametres"])
        l9 = R9.liens_m8(mod, ans, regle, "actuelle", act, pens, k, central=central)
        base9 = R9.liens_m8(mod, ans, "actuelle", "actuelle", act, pens, k)
        fact = (l9["population_active"] / base9["population_active"]).reindex(var.population_active.index).fillna(1.0)
        var.population_active = var.population_active * fact
        var.ajust_prestations = var.ajust_prestations.add(l9["ajust_prestations"], fill_value=0.0)
        var.emploi_additionnel = l9["emploi_additionnel"]
        info["statique"]["pensions_M€"] = {int(t): float(v) for t, v in l9["ajust_prestations"].items()}
        info["regle_age"] = regle
        info["retraites_variante"] = {t: P9 * pens.masse(t, regle)[0] / pens.masse(t, "actuelle")[0]
                                      for t, (_, P9) in R["pensions"].items()}
    mm = {"impots": 0.0, "prestations": 0.0, "annee": 2024, "debut": debut_socio_fiscal(mesures)}
    m_, apu = mod.macro, mod.apu
    A0 = FIN_REF                                           # année de référence des montants (euros de 2025)
    pib0 = float(m_.pib_cp[A0])
    idx_nom = (central.pib_nominal / pib0).to_dict()       # indexation des montants sur le PIB nominal de référence
    ab = apu.loc[mod.B]
    ratio0 = float((ab.te - ab.p3 - ab.d62pay - ab.d41pay) / m_.pib_cp[mod.B])
    niveaux = {}
    extras, comport = [], {}
    analytique = {"impots": 0.0, "prestations": 0.0}
    def ajouter_niveau(k, debut, v):
        niveaux.setdefault(k, pd.Series({a: 0.0 for a in var.population_active.index}))
        for a in niveaux[k].index:
            if a >= debut:
                niveaux[k][a] += v
    def ajouter_transfert(debut, montant_M):                # M€ de 2025, indexés sur le PIB nominal
        aj = var.ajust_prestations.copy()
        for a in idx_nom:
            if a >= debut:
                aj[a] = aj.get(a, 0.0) + montant_M * idx_nom[a]
        var.ajust_prestations = aj
    def ajouter_recette_apu(debut, montant_M):              # recette publique hors revenu des ménages (points de PIB)
        cal = var.calage
        for a in idx_nom:
            if a >= debut:
                cal["recettes"][a] = cal["recettes"].get(a, 0.0) + montant_M / pib0 * 100
    choc_w = {}
    for m in mesures:
        t, p = m["type"], m.get("parametres", {})
        debut = int(p.get("debut", DEBUT_DEFAUT))
        if t == "depense_publique":
            var.conso_publique = _serie_g(mod, var, float(p["points_pib"]), debut)
        elif t in ("depense_fonction", "emploi_public"):
            md = float(p["md"]) if t == "depense_fonction" else float(p["milliers"]) * COUT_AGENT_PUBLIC / 1e3
            var.conso_publique = _serie_g(mod, var, md * 1e3 / pib0 * 100, debut, int(p.get("montee", 1)))
        elif t == "investissement_public":
            md = float(p["md"])
            f = 1 + md * 1e3 / float(m_.p_fbcf[A0]) / float(var.autres_investissements[A0])
            var.autres_investissements = pd.Series({a: v * (f if a >= debut else 1.0) for a, v in var.autres_investissements.items()})
            # effet d'offre du capital public : élasticité de la production au capital public 0,08 (Bom et Ligthart
            # 2014, méta-analyse ; 0,12 pour les infrastructures), capital public net ≈ 55 % du PIB, dépréciation 4 %/an,
            # capital productif l'année suivant l'investissement ; transmis comme gain de productivité par tête
            kg, niv_prev, prod = 0.0, 0.0, {}
            for a in sorted(idx_nom):
                niv_a = ELAST_CAPITAL_PUBLIC / PART_CAPITAL_PUBLIC * kg / (pib0 / 1e3) if a > debut else 0.0
                prod[a] = niv_a - niv_prev
                niv_prev = niv_a
                kg = kg * (1 - DEPRECIATION_PUBLIQUE) + (md if a >= debut else 0.0)
            base_p = var.productivite if var.productivite is not None else pd.Series(dtype=float)
            var.productivite = pd.Series({a: float(base_p.get(a, 0.0)) + prod.get(a, 0.0) for a in var.population_active.index})
            info["statique"]["capital_public_productivite_%"] = {int(a): float(sum(v for b2, v in prod.items() if b2 <= a) * 100) for a in prod}
            base_r = var.autres_depenses_pib
            var.autres_depenses_pib = pd.Series({a: float(base_r.get(a, ratio0)) + (md * 1e3 / pib0 if a >= debut else 0.0)
                                                 for a in var.population_active.index})
        elif t == "point_indice":
            ajouter_niveau("salaire_public", debut, float(p["hausse"]))
        elif t == "taux_is":
            var.taux_is = pd.Series({a: (M8.S.taux_is().get(a, 25.83) if a < debut else float(p["taux"])) for a in range(2019, max(ans) + 1)})
        elif t == "transferts_menages":
            mm["prestations"] += float(p["points_pib"]) / 100 * mod.macro.pib_cp[mod.B]
            mm["annee"] = mod.B
        elif t == "energie_import":
            for prod in ("CPA_B", "CPA_C19", "CPA_D"):
                var.prix_import[prod] = [x * (1 + float(p["hausse"]) if a >= debut else 1.0) for a, x in zip(var.prix_import.index, var.prix_import[prod])]
        elif t == "salaires":
            choc_w[debut] = choc_w.get(debut, 0.0) + float(np.log1p(float(p["hausse"])))
        elif t == "smic":
            choc_w[debut] = choc_w.get(debut, 0.0) + float(np.log1p(PART_SMIC_DIFFUSION * float(p["hausse"])))
            # coût public direct : allègements généraux indexés sur le SMIC et bas salaires publics
            ajouter_recette_apu(debut, -float(p["hausse"]) * 100 * COUT_PUBLIC_POINT_SMIC)
            comport["smic_cout_public_M€"] = float(p["hausse"]) * 100 * COUT_PUBLIC_POINT_SMIC
        elif t == "cotisations_employeurs":
            md = float(p["md"])
            d1, d61 = float(mod.men.d1[A0]), float(mod.men.d61[A0])
            choc_w[debut] = choc_w.get(debut, 0.0) + float(np.log1p(md * 1e3 / d1))
            base_tc = var.taux_cotisations if var.taux_cotisations is not None else pd.Series(dtype=float)
            var.taux_cotisations = pd.Series({a: float(base_tc.get(a, 1.0)) * ((1 + md * 1e3 / d61) if a >= debut else 1.0)
                                              for a in var.population_active.index})
        elif t == "tva":
            rec = float(p["points"]) * RENDEMENT_POINT_TVA
            ajouter_niveau("impots_produits", debut, rec / float(apu.d2rec[A0]))
            ajouter_niveau("prix_conso", debut, float(np.log1p(REPERCUSSION_TVA * PART_TAUX_NORMAL * float(p["points"]) / 120)))
            extras.append(("tva_normale", -rec))
            comport["tva_M€"] = rec
        elif t == "tva_reduite":
            rec = float(p["points"]) * RENDEMENT_POINT_TVA_REDUITE
            ajouter_niveau("impots_produits", debut, rec / float(apu.d2rec[A0]))
            ajouter_niveau("prix_conso", debut, float(np.log1p(REPERCUSSION_TVA * PART_TAUX_REDUITS * float(p["points"]) / 108)))
            extras.append(("tva_reduite", -rec))
        elif t == "temps_travail":
            dh = float(p["heures"]) / 35.0 - 1.0
            n = int(p.get("montee", 2))
            perte = (1 - COMPENSATION_PRODUCTIVITE_HORAIRE) * dh          # productivité par tête (log approx.)
            base_p = var.productivite if var.productivite is not None else pd.Series(dtype=float)
            var.productivite = pd.Series({a: float(base_p.get(a, 0.0)) + (perte / n if debut <= a < debut + n else 0.0)
                                          for a in var.population_active.index})
            # fonction publique : embauches compensatrices (coût en points de PIB)
            cout = -perte * float(apu.d1pay[A0]) / pib0 * 100
            var.conso_publique = _serie_g(mod, var, cout, debut)
            comport["temps_travail_productivite_%"] = perte * 100
        elif t == "droits_douane":
            tau = float(p["taux"])
            f = 1 + tau * PART_HORS_UE * REPERCUSSION_DOUANE
            for prod in var.prix_import.columns:
                var.prix_import[prod] = [x * (f if a >= debut else 1.0) for a, x in zip(var.prix_import.index, var.prix_import[prod])]
            ajouter_recette_apu(debut, tau * PART_HORS_UE * float(m_.m_cp[A0]) * RECETTE_NETTE_DOUANE)
            if p.get("riposte", True):
                g = 1 - ELAST_EXPORT_DOUANE * tau * PART_EXPORT_HORS_UE
                var.demande_mondiale = pd.Series({a: v * (g if a >= debut else 1.0) for a, v in var.demande_mondiale.items()})
        elif t == "logements_sociaux":
            md = float(p["milliers"]) * COUT_LOGEMENT_SOCIAL / 1e3
            f = 1 + md * 1e3 / float(m_.p_fbcf[A0]) / float(var.autres_investissements[A0])
            var.autres_investissements = pd.Series({a: v * (f if a >= debut else 1.0) for a, v in var.autres_investissements.items()})
            base_r = var.autres_depenses_pib
            var.autres_depenses_pib = pd.Series({a: float(base_r.get(a, ratio0)) + (SUBVENTION_LOGEMENT * md * 1e3 / pib0 if a >= debut else 0.0)
                                                 for a in var.population_active.index})
        elif t == "impots_production":
            md = float(p["md"])
            ajouter_recette_apu(debut, md * 1e3)
            va_m = float(m_.pib_cp[A0]) * 0.8
            cal = var.calage
            cal["prix"][debut] = cal["prix"].get(debut, 0.0) + float(np.log1p(REPERCUSSION_IMPOTS_PRODUCTION * md * 1e3 / va_m))
        elif t == "recettes_neutres":
            ajouter_recette_apu(debut, float(p["md"]) * 1e3)
        elif t == "taxe_carbone":
            rec = float(p["euros_tonne"]) * RENDEMENT_EURO_TONNE
            ajouter_niveau("impots_produits", debut, rec / float(apu.d2rec[A0]))
            ajouter_niveau("prix_conso", debut, float(np.log1p(rec / float(m_.c_cp[A0]))))
            extras.append(("energie", -rec))
            comport["taxe_carbone_M€"] = rec
        elif t == "pfu":
            import m13_comportements as B13
            st = float(p["points"]) * RENDEMENT_POINT_PFU
            fr = B13.fourchette(B13.part_perdue_pfu, float(p["points"]))
            net = st * (1 - fr["centrale"])
            analytique["impots"] += net
            extras.append(("haut_decile", -net))
            comport["pfu"] = {"statique_M€": st, **{f"net_{k}_M€": st * (1 - v) for k, v in fr.items()}}
        elif t == "isf":
            import m13_comportements as B13
            st = float(p["taux_moyen"]) / 100 * ASSIETTE_ISF - RENDEMENT_IFI
            fr = {k: sum(B13.part_perdue_isf(a, niveau=k) for a in range(5)) / 5 for k in ("basse", "centrale", "haute")}
            net = st * (1 - fr["centrale"])
            analytique["impots"] += net
            extras.append(("top1", -net))
            comport["isf"] = {"statique_M€": st, **{f"net_{k}_M€": st * (1 - v) for k, v in fr.items()}}
        elif t == "successions":
            import m13_comportements as B13
            st = float(p["variation"]) * RENDEMENT_SUCCESSIONS
            fr = B13.fourchette(B13.part_perdue_successions)
            ajouter_recette_apu(debut, st * (1 - fr["centrale"]))
            comport["successions"] = {"statique_M€": st, **{f"net_{k}_M€": st * (1 - v) for k, v in fr.items()}}
        elif t == "assurance_chomage":
            v = float(p["variation"])
            ajouter_transfert(debut, v * DEPENSE_ASSURANCE_CHOMAGE)
            var.chomage_structurel = pd.Series({a: u + (EFFET_CHOMAGE_STRUCTUREL * v * 10 if a >= debut else 0.0)
                                                for a, u in var.chomage_structurel.items()})
        elif t == "minimum_vieillesse":
            mt = float(p["hausse"]) * DEPENSE_ASPA
            ajouter_transfert(debut, mt)
            extras.append(("bas_retraites", mt))
        elif t == "indexation_pensions":
            import m9_retraites as R9
            pens9 = R9.Pensions(R9.ActiviteSeniors())
            prix, sal = R9.trajectoires_m8(pens9, central, mod.macro.p_c[mod.B], mod.B)
            n = int(p.get("duree", 5))
            rev = {a: (float(p["points"]) if debut <= a < debut + n else 0.0) for a in range(1940, max(ans) + 1)}
            dp = {}
            for a in ans:
                if a >= debut:
                    dp[a] = (pens9.masse(a, "actuelle", salaires=sal, prix=prix, revalo=rev)[1]
                             - pens9.masse(a, "actuelle", salaires=sal, prix=prix)[1]) / 1e6
            var.ajust_prestations = var.ajust_prestations.add(pd.Series(dp), fill_value=0.0)
            info["statique"]["pensions_M€"] = {**info["statique"].get("pensions_M€", {}), **{int(a): float(v) for a, v in dp.items()}}
            extras.append(("pensions", float(p["points"]) / 100))
        elif t == "reindustrialisation":
            prods = p.get("produits", CAT.INDUSTRIE_DEFAUT)
            var.reindustrialisation = {"produits": {x: 1 - float(p["baisse_parts_importees"]) for x in prods}, "debut": debut,
                                       "duree": int(p.get("duree", 5)), "surcout": float(p.get("surcout", 0.10))}
            var.phi_impose = central.phi
    if choc_w:
        var.choc_salaire = pd.Series(choc_w)
    if niveaux:
        var.niveaux = {**(var.niveaux or {}), **niveaux}
    # --- mesures des ménages : microsimulation (OpenFisca) et mesures analytiques sur les mêmes microdonnées
    reforme, calc = CAT.reforme_openfisca(mesures)
    csg = [m for m in mesures if m["type"] == "csg"]
    logt = [m for m in mesures if m["type"] == "aides_logement"]
    if reforme or csg or logt or extras:
        import m10_couplage as C
        if journal is not None:
            journal.append("microsimulation des ménages (OpenFisca) : quelques minutes")
        base = C.evaluer("base", None)
        if reforme:
            nom = "scn_" + hashlib.sha1(json.dumps(reforme, sort_keys=True).encode()).hexdigest()[:10]
            r = C.evaluer(nom, reforme, calculer=calc)
        else:
            r = base
        d_ir = (r["ir_net"] - base["ir_net"]) / 1e6
        # réactions des hauts revenus (M13) aux taux des tranches supérieures
        import m13_comportements as B13
        perte = 0.0
        for m in mesures:
            if m["type"] == "bareme_ir":
                for tr, v in (m["parametres"].get("taux") or {}).items():
                    tr = int(tr)
                    if tr >= 3:
                        anc = {3: 0.41, 4: 0.45}[tr]
                        fr = B13.fourchette(B13.part_perdue_ir, tr, float(v))
                        perte += d_ir * fr["centrale"]
                        comport[f"ir_tranche_{tr}"] = {"statique_M€": d_ir, **{f"net_{k}_M€": d_ir * (1 - x) for k, x in fr.items()},
                                                      "departs_foyers": B13.fourchette(B13.departs_hauts_revenus, tr, float(v), anc)}
        for m in csg:
            d, tot = C.csg_foyers(float(m["parametres"].get("activite_points", 0)), float(m["parametres"].get("retraite_points", 0)))
            r = C.reforme_analytique(r, d, tot)
            comport["csg_M€"] = tot
        x = C.mesure_pour_m8(base, r)
        mm["impots"] += x["impots"] - perte + analytique["impots"]
        mm["prestations"] += x["prestations"]
        fonctions = []
        for m in logt:
            f = float(m["parametres"]["facteur"])
            mm["prestations"] += C.total_prestation(base, "aide_logement", f)
            fonctions.append(C.extra_prestation("aide_logement", f))
        for prof, montant in extras:
            if prof == "pensions":
                taux = montant
                def fp(k, men, ind, foyers, taux=taux):
                    fo = C._prep()
                    pf = fo.pensions.reindex(foyers.index).fillna(0).groupby(foyers).sum()
                    return taux * pf.reindex(men.index).fillna(0) * 1.06
                fonctions.append(fp)
            else:
                fonctions.append(C.extra_profil(montant, prof))
        extra = (lambda k, men, ind, foyers: sum(f(k, men, ind, foyers) for f in fonctions)) if fonctions else None
        D = C.distribution(base, r, extra=extra)
        info["distribution"] = D.reset_index().to_dict(orient="records")
        info["statique"].update({"impot_revenu_M€": x["impots"] - perte + analytique["impots"], "prestations_versees_M€": mm["prestations"],
                                 "droits_M€": {v: (r[v] - base[v]) / 1e6 for v in C.PRESTATIONS}})
    info["comportements"] = comport
    if mm["impots"] or mm["prestations"]:
        var.mesure_menages = mm
    return ref, var, ans, info


VERSION_MODELE = "0.4"


def empreintes() -> dict:
    """Version du modèle et empreintes du code et des données (reproductibilité, version 0.4) : SHA-256 tronqué de
    chaque module de src/ et simulateur/, et du registre des téléchargements (chaque fichier de données y figure
    avec son URL, sa date et son SHA-256)."""
    import hashlib
    import pathlib as _p
    rac = _p.Path(__file__).resolve().parents[1]
    code = {f"{d}/{f.name}": hashlib.sha256(f.read_bytes()).hexdigest()[:12]
            for d in ("src", "simulateur") for f in sorted((rac / d).glob("*.py"))}
    reg = rac / "data" / "raw" / "_registre.json"
    tout = hashlib.sha256("".join(code.values()).encode()).hexdigest()[:12]
    return {"version": VERSION_MODELE, "code": tout, "modules": code,
            "donnees": hashlib.sha256(reg.read_bytes()).hexdigest()[:12] if reg.exists() else None}


def depuis_curseurs(scenario: dict) -> dict:
    """Traduit un scénario de l'interface ({"curseurs": [{"cle", "valeur"}]}) en mesures du catalogue."""
    if "curseurs" not in scenario:
        return scenario
    cur = {c["cle"]: c for c in CAT.CURSEURS}
    sc = dict(scenario)
    sc["mesures"] = list(scenario.get("mesures", [])) + [cur[x["cle"]]["mesure"](float(x["valeur"])) for x in scenario["curseurs"]]
    return sc


def executer(scenario: dict) -> dict:
    scenario = depuis_curseurs(scenario)
    t0 = time.time()
    journal = []
    mod = modele(scenario.get("base", 2022))
    H = scenario.get("hypotheses", {})
    ref, var, ans, info = construire(scenario, mod, journal=journal)
    if H.get("europe", True):
        import m11_europe as EU
        c, v, E = EU.simuler_couple(mod, ans, ref, var, theta=H.get("prime_risque", EU.THETA_PRIME))
        europe = E.reset_index().rename(columns={"index": "annee"}).to_dict(orient="records")
    else:
        c, v = mod.simuler(ans, ref), mod.simuler(ans, var)
        europe = None
    P = info["pensions_reference"]
    pm_ref = {t: P[t][0] for t in P}
    nb_ref = {t: P[t][1] for t in P}
    dpm = info["statique"].get("pensions_M€", {})
    pm_var = {t: pm_ref[t] + dpm.get(t, 0.0) for t in pm_ref}
    nb_var = info.get("retraites_variante", nb_ref)
    c, v = derivees(mod, c, ref, pm_ref, nb_ref), derivees(mod, v, var, pm_var, nb_var)
    traj = {}
    for k in VARIABLES:
        traj[k] = {"reference": {int(t): float(c[k][t]) for t in ans}, "scenario": {int(t): float(v[k][t]) for t in ans},
                   "ecart": {int(t): float(v[k][t] - c[k][t] if k in EN_POINTS else (v[k][t] / c[k][t] - 1) * 100) for t in ans},
                   "unite_ecart": "points" if k in EN_POINTS else "%"}
    incert = None
    n = int(H.get("incertitude", 0))
    if n:
        import m12_incertitude as MC
        sc = copy.deepcopy(scenario)

        def f_var(mod_, ans_, rho):
            sc["hypotheses"]["fermeture_offre"] = rho
            return construire(sc, mod_)[1]

        def f_ref(mod_, ans_, rho):
            sc["hypotheses"]["fermeture_offre"] = rho
            return construire(sc, mod_)[0]
        df = MC.monte_carlo(mod, ans, {"scenario": (f_var, f_ref)}, n=n, horizons=tuple(sorted({a for a in (DEBUT_DEFAUT, DEBUT_DEFAUT + 2, ans[-1]) if a in ans})))
        tir = df[df.tirage > 0]
        incert = {int(a): {col: [float(g[col].quantile(0.05)), float(g[col].quantile(0.95))] for col in ("pib", "emploi", "prix", "solde", "dette")}
                  for a, g in tir.groupby("annee")}
    profils_res = None
    reforme, _ = CAT.reforme_openfisca(scenario.get("mesures", []))
    ANALYTIQUES = ("csg", "tva", "tva_reduite", "taxe_carbone", "indexation_pensions", "aides_logement")
    mes_ = scenario.get("mesures", [])
    if H.get("profils", True) and (reforme or any(m["type"] in ANALYTIQUES for m in mes_)):
        from simulateur import profils
        profils_res = profils.comparer(reforme)
        aj = profils.ajustements_analytiques(mes_, profils_res)
        for pr_ in profils_res:
            pr_["variation_revenu_disponible"] += aj[pr_["profil"]]
    return {"scenario": scenario, "trajectoires": traj, "distribution": info["distribution"], "statique": info["statique"],
            "comportements": info.get("comportements"), "version": empreintes(), "reference": info.get("reference"),
            "profils": profils_res,
            "europe": europe, "incertitude": incert, "transparence": transparence(scenario), "duree_s": round(time.time() - t0),
            "journal": journal}


def transparence(scenario: dict) -> dict:
    """Fiche de transparence exigée par le cahier des charges (§ 17.1)."""
    mes = []
    modules = {"M8", "M1"}
    for m in scenario.get("mesures", []):
        c = CAT.MESURES[m["type"]]
        modules.update(c["modules"])
        mes.append({"type": m["type"], "libelle": c["libelle"], "parametres": m.get("parametres", {}), "niveau_de_preuve": c["preuve"], "limites": c["limites"]})
    H = scenario.get("hypotheses", {})
    if H.get("europe", True):
        modules.add("M11")
    return {
        "mesures": mes,
        "hypotheses": {
            "compte_de_reference": "Trajectoire à politique inchangée (aucune mesure nouvelle après la loi de finances 2026), qui n'est pas une prévision : "
                                   "recalée sur les comptes observés 2023-2025 ; croissance, chômage et inflation du FMI (octobre 2026) jusqu'en 2031, puis "
                                   "productivité +0,7 %/an et chômage 7 % (hypothèses du COR) ; population active et pensions selon la démographie de l'Insee "
                                   "et la législation actuelle (M9) ; OAT à 10 ans au dernier niveau observé ; dépenses publiques et prestations hors "
                                   "pensions à leur rythme 2011-2019 ; finances publiques calculées par le modèle.",
            "fermeture_offre": H.get("fermeture_offre", M8.RHO_DEFAUT),
            "europe": H.get("europe", True),
            "productivite": "productivité apparente issue du calage (FMI jusqu'en 2031), puis 0,7 %/an (COR)"},
        "donnees": "Insee, Eurostat, DGFiP, DREES, FMI, OpenFisca-France 177 ; registre complet avec empreintes : resultats/registre_telechargements.json",
        "modeles": sorted(modules),
        "parametres_sensibles": ["fermeture d'offre ρ (0,1-0,25)", "élasticité de l'emploi au coût du travail (calibrée, 0,2-0,6)",
                                 "effet du chômage sur les salaires (calibré)", "élasticité de l'investissement au coût du capital (fragile)",
                                 "prime de risque sur la dette (3 pb par point)", "délai de transmission des prix d'importation"],
        "incertitudes": "Intervalle à 90 % si demandé (tirages des paramètres estimés et calibrés) ; n'inclut ni l'incertitude sur les données, "
                        "ni celle sur la spécification des équations, ni celle sur l'environnement international.",
        "limites": ["Effets statiques des mesures socio-fiscales (pas de réaction de l'offre de travail ni du recours).",
                    "Modèle annuel, volumes non chaînés : horizon recommandé inférieur à 10 ans.",
                    "Pas de flux physiques d'énergie ni de matières.",
                    "Les taux d'intérêt n'agissent que sur l'investissement et la charge de la dette.",
                    "Aucune note globale n'est attribuée : les résultats sont des écarts conditionnels à un compte de référence."],
    }


def main():
    sc = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    res = executer(sc)
    out = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else RACINE / "outputs" / (pathlib.Path(sys.argv[1]).stem + "_resultats.json")
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    from simulateur import restitution
    restitution.ecrire_html(res, out.with_suffix(".html"))
    print(out, out.with_suffix(".html"), res["duree_s"], "s")


if __name__ == "__main__":
    main()
