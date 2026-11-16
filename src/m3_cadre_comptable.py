"""M3 — Cadre comptable T0 : matrice des transactions non financières par secteur institutionnel.

Source : Eurostat nasa_10_nf_tr (comptes annuels des secteurs, France, base 2020, M€ courants).
Convention : pour chaque secteur, PAID = emplois, RECV = ressources (le reste du monde S2 est vu de son
propre point de vue : ses ressources sont les importations françaises P7, ses emplois les exportations P6).

Construction :
1. On retient des opérations « feuilles » qui ne se recouvrent pas (aucune grandeur comptée deux fois).
2. Ligne par opération : Σ emplois = Σ ressources sur l'ensemble des secteurs (dont S2 et S1N, pseudo-secteur
   portant les impôts nets des subventions sur les produits). Les biens et services forment une seule ligne
   (P1 + P7 = P2 + P3 + P5 + NP + P6 n'est pas exact : NP est une acquisition d'actifs non produits, ligne propre).
3. Colonne par secteur : capacité de financement B9 = Σ ressources − Σ emplois, comparée au B9 publié.
4. Écarts des données publiées (arrondis, opérations non ventilées) : reportés dans une colonne explicite
   « ECART » pour chaque ligne ; le cadre réconcilié vérifie alors toutes les identités exactement.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pandas as pd

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
from telechargement import jsonstat_dict, telecharger  # noqa: E402

SECTEURS = ["S11", "S12", "S13", "S14", "S15", "S1N", "S2"]
NOMS_SECTEURS = {"S11": "Sociétés non financières", "S12": "Sociétés financières", "S13": "Administrations publiques",
                 "S14": "Ménages", "S15": "ISBLSM", "S1N": "Impôts nets sur produits (non sectorisé)", "S2": "Reste du monde"}

# Opérations feuilles : (code, ligne de la matrice, signe)  — le signe sert pour D61SC (soustrait de D61)
FEUILLES = [
    ("P1", "BS", 1), ("D21X31", "BS", 1), ("P7", "BS", 1),
    ("P2", "BS", 1), ("P3", "BS", 1), ("P51G", "BS", 1), ("P52", "BS", 1), ("P53", "BS", 1), ("P6", "BS", 1),
    ("D11", "D11", 1), ("D12", "D12", 1),
    ("D21", "D21", 1), ("D29", "D29", 1), ("D31", "D31", 1), ("D39", "D39", 1),
    ("D41", "D41", 1), ("D421", "D421", 1), ("D422", "D422", 1), ("D43", "D43", 1),
    ("D441", "D441", 1), ("D442", "D442", 1), ("D443", "D443", 1), ("D45", "D45", 1),
    ("D51", "D51", 1), ("D59", "D59", 1),
    ("D611", "D611", 1), ("D612", "D612", 1), ("D613", "D613", 1), ("D614", "D614", 1), ("D61SC", "D61SC", -1),
    ("D62", "D62", 1),
    ("D71", "D71", 1), ("D72", "D72", 1), ("D74", "D74", 1), ("D75", "D75", 1), ("D76", "D76", 1),
    ("D8", "D8", 1),
    ("D91", "D91", 1), ("D92", "D92", 1), ("D99", "D99", 1),
    ("NP", "NP", 1),
]
LIGNES = list(dict.fromkeys(l for _, l, _ in FEUILLES))
LIBELLES = {"BS": "Biens et services (P1, impôts nets sur produits, P7 | P2, P3, P5, P6)"}


def charger_eurostat(force: bool = False) -> pd.DataFrame:
    u = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nasa_10_nf_tr"
         "?format=JSON&geo=FR&unit=CP_MEUR&sinceTimePeriod=2019")
    d = json.loads(telecharger(u, "eurostat_nasa_10_nf_tr_FR.json", force=force).read_text(encoding="utf-8"))
    s = pd.Series(jsonstat_dict(d))
    s.index.names = ["direct", "na", "sect", "t"]
    df = s.unstack("t")
    df.columns = df.columns.astype(int)
    return df


def valeur(df, direct, na, sect, t) -> float:
    try:
        v = df.loc[(direct, na, sect), t]
        return 0.0 if pd.isna(v) else float(v)
    except KeyError:
        return 0.0


def matrice(df: pd.DataFrame, t: int) -> pd.DataFrame:
    """Matrice brute : lignes = opérations, colonnes = (secteur, E|R) ; M€."""
    cols = pd.MultiIndex.from_product([SECTEURS, ["E", "R"]])
    M = pd.DataFrame(0.0, index=LIGNES, columns=cols)
    for code, ligne, signe in FEUILLES:
        for s in SECTEURS:
            if code == "D21X31":
                if s == "S1N":  # ressource du pseudo-secteur : impôts nets sur produits (= sa valeur ajoutée)
                    M.loc[ligne, (s, "R")] += valeur(df, "RECV", "D21X31", s, t)
                continue
            M.loc[ligne, (s, "E")] += signe * valeur(df, "PAID", code, s, t)
            M.loc[ligne, (s, "R")] += signe * valeur(df, "RECV", code, s, t)
    return M


def b9_publie(df, t) -> pd.Series:
    return pd.Series({s: valeur(df, "RECV", "B9", s, t) for s in SECTEURS})


def reconcilier(M: pd.DataFrame, b9_cible: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Ajoute les écarts explicites :
    - écart de ligne (Σ emplois − Σ ressources) imputé en ressource d'un compte ECART ;
    - écart de colonne (B9 calculé − B9 publié) imputé dans une ligne « ECART_SECTEUR » de chaque secteur,
      contrepartie dans le compte ECART, de sorte que le cadre réconcilié reproduise exactement les B9 publiés.
    Renvoie (matrice réconciliée, table des écarts)."""
    R = M.copy()
    R[("ECART", "E")] = 0.0
    R[("ECART", "R")] = 0.0
    R.loc["ECART_SECTEUR"] = 0.0
    secteurs_E = [(s, "E") for s in SECTEURS]
    secteurs_R = [(s, "R") for s in SECTEURS]
    ecart_ligne = M[secteurs_E].sum(axis=1) - M[secteurs_R].sum(axis=1)
    R.loc[M.index, ("ECART", "R")] = ecart_ligne.clip(lower=0)
    R.loc[M.index, ("ECART", "E")] = (-ecart_ligne).clip(lower=0)
    b9_calc = M[secteurs_R].sum().droplevel(1) - M[secteurs_E].sum().droplevel(1)
    ecart_col = b9_calc - b9_cible
    for s in SECTEURS:
        e = ecart_col[s]
        if e > 0:
            R.loc["ECART_SECTEUR", (s, "E")] = e
        else:
            R.loc["ECART_SECTEUR", (s, "R")] = -e
    tot = R.loc["ECART_SECTEUR", secteurs_E].sum() - R.loc["ECART_SECTEUR", secteurs_R].sum()
    R.loc["ECART_SECTEUR", ("ECART", "R" if tot > 0 else "E")] = abs(tot)
    table = pd.DataFrame({"ecart_ligne": ecart_ligne}).reindex(list(M.index))
    return R, table, ecart_col


def soldes(R: pd.DataFrame) -> pd.Series:
    cols = sorted(set(R.columns.get_level_values(0)), key=lambda x: (SECTEURS + ["ECART"]).index(x))
    return pd.Series({s: R[(s, "R")].sum() - R[(s, "E")].sum() for s in cols})


def agregats(df: pd.DataFrame, t: int) -> dict:
    v = lambda d, n, s: valeur(df, d, n, s, t)  # noqa: E731
    pib = valeur(df, "RECV", "B1GQ", "S1", t)
    va = sum(v("RECV", "B1G", s) for s in ("S11", "S12", "S13", "S14", "S15")) + v("RECV", "D21X31", "S1N")
    demande = sum(v("PAID", n, s) for n in ("P3", "P51G", "P52", "P53") for s in ("S11", "S12", "S13", "S14", "S15")) \
        + v("PAID", "P6", "S2") - v("RECV", "P7", "S2")
    rdb_men = v("RECV", "B6G", "S14")
    epargne_men = v("RECV", "B8G", "S14")
    conso_men = v("PAID", "P3", "S14")
    return {
        "PIB publié (B1GQ)": pib,
        "PIB optique production (Σ VA + impôts nets sur produits)": va,
        "PIB optique demande (P3 + P5 + P6 − P7)": demande,
        "Capacité de financement APU (B9, M€)": v("RECV", "B9", "S13"),
        "Solde APU en % du PIB": 100 * v("RECV", "B9", "S13") / pib,
        "Taux d'épargne des ménages S14 (B8G / (B6G + D8 net)), définition Insee": 100 * epargne_men / (rdb_men + v("RECV", "D8", "S14") - v("PAID", "D8", "S14")),
        "Dépenses publiques (OTE) en % du PIB": 100 * v("PAID", "OTE", "S13") / pib,
        "Recettes publiques (OTR) en % du PIB": 100 * v("RECV", "OTR", "S13") / pib,
        "Dépense de consommation finale des ménages S14 (M€)": conso_men,
    }


# ---------------------------------------------------------------------------------------------
# Stocks financiers et lien flux-stocks
# ---------------------------------------------------------------------------------------------
SECTEURS_FIN = ["S11", "S12", "S13", "S14_S15", "S2"]


def _charge(nom: str) -> pd.Series:
    d = json.loads((RACINE / "data" / "raw" / nom).read_text(encoding="utf-8"))
    return pd.Series(jsonstat_dict(d))


def charger_financier(force: bool = False):
    B = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
    telecharger(B + "nasa_10_f_bs?format=JSON&geo=FR&unit=MIO_EUR&co_nco=NCO&na_item=BF90&na_item=F&sinceTimePeriod=2018",
                "eurostat_nasa_10_f_bs_FR.json", force=force)
    telecharger(B + "nasa_10_f_tr?format=JSON&geo=FR&unit=MIO_EUR&co_nco=NCO&na_item=B9F&na_item=F&sinceTimePeriod=2019",
                "eurostat_nasa_10_f_tr_FR.json", force=force)
    telecharger(B + "gov_10dd_edpt1?format=JSON&geo=FR&sector=S13&na_item=B9&na_item=GD&unit=MIO_EUR&unit=PC_GDP&sinceTimePeriod=2019",
                "eurostat_gov_10dd_edpt1_FR.json", force=force)
    bs = _charge("eurostat_nasa_10_f_bs_FR.json")   # clés (sector, finpos, na_item, time)
    tr = _charge("eurostat_nasa_10_f_tr_FR.json")   # clés (sector, finpos, time) ; seul B9F est renseigné
    edp = _charge("eurostat_gov_10dd_edpt1_FR.json")  # clés (unit, na_item, time)
    return bs, tr, edp


def flux_stocks(df_nf: pd.DataFrame, bs: pd.Series, tr: pd.Series, t: int) -> pd.DataFrame:
    """Par secteur : patrimoine financier net (fin t−1, fin t), B9 non financier, B9F financier,
    écart B9 − B9F, autres changements de volume et réévaluations (résidu explicite)."""
    lignes = {}
    for s in SECTEURS_FIN:
        nfw0 = bs.get((s, "ASS", "F", str(t - 1)), np.nan) - bs.get((s, "LIAB", "F", str(t - 1)), np.nan)
        nfw1 = bs.get((s, "ASS", "F", str(t)), np.nan) - bs.get((s, "LIAB", "F", str(t)), np.nan)
        b9f = tr.get((s, "LIAB", str(t)), np.nan)  # Eurostat publie B9F sous finpos = LIAB
        b9 = valeur(df_nf, "RECV", "B9", s, t)
        lignes[s] = {"PFN fin t-1": nfw0, "PFN fin t": nfw1, "B9 non financier": b9, "B9F financier": b9f,
                     "écart B9 − B9F": b9 - b9f, "autres flux (réévaluations, volume)": nfw1 - nfw0 - b9f}
    out = pd.DataFrame(lignes).T
    out.loc["Somme, reste du monde compris (doit être nulle)"] = out.sum()
    return out


def dette_maastricht(edp: pd.Series, t: int) -> dict:
    d1, d0 = edp[("MIO_EUR", "GD", str(t))], edp[("MIO_EUR", "GD", str(t - 1))]
    b9 = edp[("MIO_EUR", "B9", str(t))]
    return {"dette fin t (M€)": d1, "dette en % du PIB": edp[("PC_GDP", "GD", str(t))],
            "solde B9 (M€)": b9, "solde en % du PIB": edp[("PC_GDP", "B9", str(t))],
            "variation de dette": d1 - d0, "ajustement stock-flux (Δdette + B9)": d1 - d0 + b9}
