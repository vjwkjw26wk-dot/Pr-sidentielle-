"""M25 — Programmes de politique économique pour le moteur de la phase 5 (lot 5.3).

Pont entre le catalogue de mesures du simulateur (simulateur/catalogue.py : curseurs → mesures ; executer.construire :
mesures → exogènes) et le moteur à régimes (M23). Les mesures sont traduites UNE FOIS, sur l'environnement de même
configuration à convention de dépense historique (celle du simulateur), puis transférées sous forme d'écarts
(rapports pour les volumes et les prix, différences pour les autres grandeurs) à n'importe quel environnement : les
programmes deviennent comparables sous tous les régimes et toutes les variantes d'environnement.

Microsimulation des ménages (OpenFisca, M10) : les montants statiques (impôts, prestations, ajustement de consommation
par décile) ne dépendent que de la législation et des microdonnées ; ils sont repris des calculs déjà faits pour le
même programme (phase31/resultats/strategies_v08_<programme>.json, configuration centrale) au lieu de relancer la
microsimulation (≈ 4 Go, plusieurs minutes). Un programme nouveau devra passer une fois par la microsimulation.
"""
from __future__ import annotations

import copy
import json
import pathlib
import sys
import types

import numpy as np
import pandas as pd

RACINE = pathlib.Path(__file__).resolve().parents[1]
MULTIPLICATIFS = {"conso_publique", "autres_investissements", "population_active", "demande_mondiale", "prix_mondial",
                  "taux_cotisations", "prestations_volume"}
BASE_CURSEURS = {"ir_t1": 11, "ir_t4": 45, "taux_is": 25.8, "temps_travail": 35, "age_legal": 64}


def strategies() -> dict:
    """Leviers des stratégies S1-S5 (phase 3, définitions inchangées), en valeurs de curseurs."""
    o = json.loads((RACINE / "phase3" / "resultats" / "optimisation_v07.json").read_text())["strategies"]
    out = {}
    for k, s in o.items():
        cur = {}
        for lev, v in s["leviers"].items():
            val = BASE_CURSEURS.get(lev, 0.0) + v
            cur[lev] = round(val) if lev == "age_legal" else round(val, 2)
        out[k] = {"curseurs": cur, "libelle": s.get("libelle", k)}
    return out


def _statique(nom):
    f = RACINE / "phase31" / "resultats" / f"strategies_v08_{nom}.json"
    if not f.exists():
        return None
    return (json.loads(f.read_text()).get("central") or {}).get("statique")


def _module_microsimulation_fige():
    """Remplace M10 pendant la traduction : aucune microsimulation (les montants sont réinjectés ensuite)."""
    m = types.ModuleType("m10_couplage")
    m.PRESTATIONS = []
    m.evaluer = lambda *a, **k: {"ir_net": 0.0}
    m.mesure_pour_m8 = lambda base, r: {"impots": 0.0, "prestations": 0.0}
    m.csg_foyers = lambda *a, **k: (None, 0.0)
    m.reforme_analytique = lambda r, d, tot: r
    m.total_prestation = lambda *a, **k: 0.0
    m.extra_prestation = lambda *a, **k: (lambda *x, **y: 0.0)
    m.extra_profil = lambda *a, **k: (lambda *x, **y: 0.0)

    def distribution(base, r, extra=None):
        d = pd.DataFrame({"decile": [1]})
        d.attrs = {}
        return d
    m.distribution = distribution
    return m


# Mesures du catalogue sans curseur d'interface, utilisables par la traduction des programmes (corpus, phase 6)
MESURES_HORS_CURSEURS = {
    "investissement_hors_apu": lambda v: {"type": "investissement_hors_apu", "parametres": {"md": v}},
}


def traduire(curseurs: dict, env_hist, nom: str = "programme", statique: dict | None = None,
             microsimulation: str = "reprise", debuts: dict | None = None) -> dict:
    """Exogènes de référence et du programme sur l'environnement `env_hist` (convention historique), via le simulateur.
    Renvoie le dictionnaire des écarts transférables.

    microsimulation : "reprise" (montants statiques enregistrés des stratégies S1-S5, M10 figé) ou "calcul" (M10 et
    OpenFisca exécutés pour ce programme : programmes des candidats).
    debuts : {curseur: première année d'application} (défaut : convention du simulateur)."""
    sys.path[:0] = [str(RACINE), str(RACINE / "rapport")]
    from simulateur import executer as X, catalogue as CAT
    import m14_heterogeneite as H14
    CUR = {c["cle"]: c for c in CAT.CURSEURS}
    CUR.update({k: {"mesure": f} for k, f in MESURES_HORS_CURSEURS.items()})
    mesures = []
    # curseurs : {curseur: valeur} ou liste de (curseur, valeur, début ou None) — la liste permet plusieurs mesures de
    # même type avec des calendriers différents (programmes des candidats, variantes institutionnelles de M26)
    items = curseurs.items() if isinstance(curseurs, dict) else [(a, v) for a, v, *_ in curseurs]
    debs = [None] * len(items) if isinstance(curseurs, dict) else [(x[2] if len(x) > 2 else None) for x in curseurs]
    for (a, v), d0 in zip(items, debs):
        m_ = CUR[a]["mesure"](v)
        d0 = d0 if d0 is not None else (debuts or {}).get(a)
        if d0 is not None:
            m_["parametres"]["debut"] = int(d0)
        mesures.append(m_)
    if microsimulation == "calcul":
        env_hist.activer()
        ref, var, ans, info = X.construire(sc_ := {"nom": nom, "horizon": env_hist.fin, "hypotheses": {
            "europe": False, "incertitude": 0, "profils": False, "distribution_dynamique": False}, "mesures": mesures},
            env_hist.mod, central=env_hist.reference)
        mm = copy.deepcopy(var.mesure_menages) if var.mesure_menages else None
        if mm:
            mm.setdefault("variante_pmc", "central"); mm.setdefault("variante_distribution", "central")
        return {"ecarts": _ecarts(ref, var), "mesure_menages": mm, "curseurs": curseurs if isinstance(curseurs, dict)
                else [list(x) for x in curseurs], "nom": nom, "comportements": info.get("comportements"),
                "microsimulation_reprise": False, "debuts": debuts or {}}
    sc = {"nom": nom, "horizon": env_hist.fin, "hypotheses": {"europe": False, "incertitude": 0, "profils": False,
                                                               "distribution_dynamique": False}, "mesures": mesures}
    statique = statique if statique is not None else _statique(nom)
    env_hist.activer()
    sauv_m10, sauv_aj = sys.modules.get("m10_couplage"), H14.ajustement_conso
    sys.modules["m10_couplage"] = _module_microsimulation_fige()
    H14.ajustement_conso = lambda *a, **k: 0.0
    try:
        ref, var, ans, info = X.construire(sc,
                                           env_hist.mod, central=env_hist.reference)
    finally:
        if sauv_m10 is not None:
            sys.modules["m10_couplage"] = sauv_m10
        else:
            sys.modules.pop("m10_couplage", None)
        H14.ajustement_conso = sauv_aj
    mm = copy.deepcopy(var.mesure_menages) if var.mesure_menages else None
    micro = any(m["type"] in ("bareme_ir", "csg", "rsa", "prime_activite", "allocations_familiales", "aides_logement",
                              "minimum_vieillesse", "tva", "tva_reduite", "taxe_carbone", "pfu", "isf", "indexation_pensions")
                for m in mesures)
    if micro:
        if statique is None:
            raise ValueError(f"{nom} : mesures des ménages sans résultats de microsimulation enregistrés")
        mm = mm or {"impots": 0.0, "prestations": 0.0, "annee": 2024, "debut": X.debut_socio_fiscal(mesures)}
        mm["impots"] = float(statique["impot_revenu_M€"])
        mm["prestations"] = float(statique["prestations_versees_M€"])
        mm["conso"] = float(statique["ajustement_conso_M€"])
        mm.setdefault("variante_pmc", "central"); mm.setdefault("variante_distribution", "central")
    return {"ecarts": _ecarts(ref, var), "mesure_menages": mm, "curseurs": curseurs, "nom": nom,
            "comportements": info.get("comportements"), "microsimulation_reprise": micro}


def _ecarts(ref, var) -> dict:
    out = {}
    for k, v in vars(var).items():
        r = getattr(ref, k, None)
        if k in ("mesure_menages", "regime_hook", "lpgf", "lpot_ref", "lk_ref", "ly_ref", "gel", "phi_impose"):
            continue
        if isinstance(v, pd.DataFrame):
            if r is not None and not v.equals(r):
                out[k] = ("ratio", (v / r).fillna(1.0))
        elif isinstance(v, pd.Series):
            if r is None:
                out[k] = ("valeur", v.copy())
            elif not v.equals(r):
                if k in MULTIPLICATIFS:
                    out[k] = ("ratio", (v / r.reindex(v.index)).fillna(1.0))
                else:
                    out[k] = ("difference", v.sub(r.reindex(v.index), fill_value=0.0))
        elif isinstance(v, dict) and k in ("niveaux", "calage"):
            d = {}
            for kk, s in v.items():
                s0 = (r or {}).get(kk)
                if isinstance(s, pd.Series):
                    diff = s.sub(s0, fill_value=0.0) if isinstance(s0, pd.Series) else s.copy()
                    if diff.abs().max() > 0:
                        d[kk] = diff
            if d:
                out[k] = ("dictionnaire", d)
        elif v is not None and r is None and k in ("reindustrialisation", "comportements"):
            out[k] = ("valeur", copy.deepcopy(v))
    return out


def appliquer_ecarts(trad: dict, ex):
    for k, (mode, val) in trad["ecarts"].items():
        cur = getattr(ex, k, None)
        if mode == "ratio":
            setattr(ex, k, cur * val.reindex(cur.index).fillna(1.0) if isinstance(cur, pd.Series)
                    else cur * val.reindex(index=cur.index, columns=cur.columns).fillna(1.0))
        elif mode == "difference":
            setattr(ex, k, cur.add(val, fill_value=0.0) if cur is not None else val.copy())
        elif mode == "valeur":
            setattr(ex, k, copy.deepcopy(val))
        elif mode == "dictionnaire":
            dd = dict(cur or {})
            for kk, s in val.items():
                base = dd.get(kk)
                dd[kk] = base.add(s, fill_value=0.0) if isinstance(base, pd.Series) else s.copy()
            setattr(ex, k, dd)
    if trad["mesure_menages"]:
        ex.mesure_menages = copy.deepcopy(trad["mesure_menages"])


def programme(trad: dict):
    import m23_regimes as G
    return G.Programme(trad["nom"], lambda mod, ex: appliquer_ecarts(trad, ex), json.dumps(trad["curseurs"]))
