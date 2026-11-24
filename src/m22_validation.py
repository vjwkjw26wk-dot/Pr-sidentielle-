"""M22 — Validation prédictive (phase 4.3, chantier C).

Quatre niveaux d'évaluation, toujours distingués :
  1. ajustement dans l'échantillon d'estimation (équations, M7/M18/M19/M21) ;
  2. rétrosimulation CONDITIONNELLE hors échantillon : coefficients estimés jusqu'à l'origine, exogènes et politiques
     OBSERVÉES ex post (phase31/backtest.py) — mesure l'erreur du modèle lui-même, pas celle d'une prévision ;
  3. prévision EX ANTE : coefficients estimés jusqu'à l'origine ET exogènes connues à l'origine (millésime d'octobre des
     Perspectives de l'économie mondiale du FMI pour la demande extérieure ; conventions de prévision pour le reste),
     comparée aux prévisions publiées par le FMI dans le même millésime et à une prévision naïve ;
  4. évaluation d'un CHOC DE POLITIQUE identifié (CICE et bascule de 2019 en allègements) : effet du modèle comparé aux
     évaluations ex post publiées.

Conventions ex ante (aucune information postérieure à l'origine B) :
  - demande mondiale : importations en volume de la zone euro (FMI WEO, millésime d'octobre B, agrégat 163) pour
    B+1…B+5, puis dernière croissance prévue ; l'exogène observée est celle de l'UE à 27 (Eurostat) ;
  - prix mondiaux et d'importation, consommation publique, autres investissements, prestations en volume, population
    active : croissance moyenne (log) des cinq années B−4…B, prolongée ;
  - taux longs et courts : constants au niveau de B (marche aléatoire) ;
  - fiscalité : législation de l'année B maintenue (taux d'IS, taux apparents de prélèvements, CICE au taux de B, pas de
    bascule de 2019), autres dépenses publiques en part du PIB constantes ;
  - chômage structurel et PIB potentiel : en temps réel (filtrage jusqu'à B), comme dans les rétrosimulations.
"""
from __future__ import annotations

import json
import pathlib

import numpy as np
import pandas as pd

RACINE = pathlib.Path(__file__).resolve().parents[1]


def _weo(dataset: str, sujet: str) -> dict:
    from telechargement import telecharger
    url = (f"https://api.db.nomics.world/v22/series/IMF/{dataset}?dimensions=%7B%22weo-subject%22:%5B%22{sujet}%22%5D%7D"
           "&observations=1&limit=1000")
    nom = f"dbnomics_imf_{dataset.replace(':', '_').replace('-', '_').lower()}_{sujet.lower()}.json"
    d = json.loads(telecharger(url, nom).read_text())
    out = {}
    for x in d["series"]["docs"]:
        c = x["series_code"].split(".")[0]
        out[c] = pd.Series({int(a): (float(v) if v not in ("NA", None) else np.nan) for a, v in zip(x["period"], x["value"])})
    return out


def millesime(B: int) -> str:
    return f"{B}-10"


def demande_ex_ante(B: int) -> pd.Series:
    """Croissance (%) des importations en volume de la zone euro prévue par le FMI en octobre B."""
    return _weo(f"WEOAGG:{millesime(B)}", "TM_RPCH")["163"]


def previsions_fmi(B: int) -> pd.DataFrame:
    """Prévisions du FMI pour la France, millésime d'octobre B : croissance, inflation, chômage, solde et dette publics."""
    v = f"WEO:{millesime(B)}"
    cols = {"NGDP_RPCH": "pib_g", "PCPIPCH": "inflation", "LUR": "chomage", "GGXCNL_NGDP": "solde_pib", "GGXWDG_NGDP": "dette_pib"}
    return pd.DataFrame({nom: _weo(v, s).get("FRA", pd.Series(dtype=float)) for s, nom in cols.items()})


def _prolonger(serie: pd.Series, B: int, fin: int, base_debut: int | None = None) -> pd.Series:
    s = serie.copy().astype(float)
    a0 = B - 5 if base_debut is None else base_debut
    g = (np.log(float(s[B])) - np.log(float(s[a0]))) / (B - a0)
    for t in range(B + 1, fin + 1):
        s[t] = float(s[B]) * np.exp(g * (t - B))
    return s.sort_index()


def exogenes_ex_ante(mod, ex, B: int, fin: int):
    """Remplace, au-delà de B, les exogènes observées par celles connues à l'origine (voir l'en-tête). Modifie `ex`."""
    ans = range(B + 1, fin + 1)
    # demande mondiale
    g = demande_ex_ante(B)
    dm = ex.demande_mondiale.copy().astype(float)
    # dernière croissance prévue disponible (le millésime 2010-10 ne couvre que B et B+1 dans DBnomics)
    prev = g.loc[B + 1:B + 5].dropna()
    derniere = float(prev.iloc[-1])
    for t in ans:
        gt = float(g.get(t, np.nan)) if t <= B + 5 else derniere
        gt = derniere if np.isnan(gt) else gt
        dm[t] = float(dm[t - 1]) * (1 + gt / 100)
    ex.demande_mondiale = dm.sort_index()
    # prolongements tendanciels
    ex.prix_mondial = _prolonger(ex.prix_mondial, B, fin)
    pi = ex.prix_import.copy()
    for p in pi.columns:
        col = pi[p]
        # indices de prix d'importation (base B = 1) : croissance agrégée observée avant B (prix d'importation agrégés)
        gm = (np.log(float(mod.macro.p_m[B])) - np.log(float(mod.macro.p_m[B - 5]))) / 5
        for t in ans:
            col[t] = float(col[B]) * np.exp(gm * (t - B))
        pi[p] = col
    ex.prix_import = pi
    for nom in ("conso_publique", "autres_investissements", "prestations_volume", "population_active"):
        setattr(ex, nom, _prolonger(getattr(ex, nom), B, fin))
    for nom in ("taux_long", "taux_court", "taux_is", "autres_depenses_pib", "taux_is_apparent"):
        s = getattr(ex, nom, None)
        if s is None:
            continue
        s = s.copy().astype(float)
        for t in ans:
            s[t] = float(s[B])
        setattr(ex, nom, s.sort_index())
    # politiques : législation de B maintenue
    if ex.niveaux:
        ex.niveaux = {k: (v * 0.0 if isinstance(v, pd.Series) else v) for k, v in ex.niveaux.items() if k != "ancre_salaire"}
    if ex.taux_cotisations is not None:
        ex.taux_cotisations = pd.Series({t: 1.0 for t in ex.taux_cotisations.index})
    ex.choc_salaire = None
    if getattr(ex, "subvention_salaires", None) is not None:
        sv = ex.subvention_salaires.copy()
        for t in sv.index:
            if t > B:
                sv[t] = float(sv[B])
        ex.subvention_salaires = sv
    return ex


# ---------------------------------------------------------------------------------------------------------------------
# Classement des variables des rétrosimulations (niveau 2) : imposées (exogènes ou politiques injectées), partiellement
# imposées (une composante observée entre dans leur calcul), prédites (jamais injectées).
CLASSEMENT = {
    "imposées": ["demande mondiale", "prix mondiaux et d'importation (dont énergie)", "consommation publique en volume",
                 "investissement des APU et autres FBCF hors ménages et branches", "population active", "taux longs et courts",
                 "taux d'IS légal", "taux apparents des impôts sur les produits, des impôts des ménages et des cotisations",
                 "prestations en volume (hors chômage)", "autres dépenses publiques en part du PIB", "CICE et bascule de 2019",
                 "taux apparent de l'IS des sociétés (compte des sociétés)"],
    "partiellement imposées": ["recettes publiques (taux apparents imposés, assiettes simulées)",
                               "dépenses publiques (volumes imposés, prix, chômage et charge d'intérêts simulés)",
                               "IS (taux apparent imposé, résultat simulé)", "intérêts des sociétés (taux de marché imposés)"],
    "prédites": ["PIB et composantes de la demande", "importations", "emploi marchand et non marchand", "chômage",
                 "productivité", "prix de VA, de consommation, d'exportation", "salaires", "marges et EBE", "dividendes",
                 "épargne et capacité de financement des sociétés", "revenu disponible et épargne des ménages",
                 "solde public", "dette publique", "dette des sociétés"],
}
