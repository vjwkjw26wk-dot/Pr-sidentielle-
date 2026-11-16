"""Lecture des fichiers « Résultats détaillés des projections de population 2026 » de l'Insee.

Chaque onglet est converti en DataFrame : lignes = âges (entiers ; le libellé « 105+ » devient 105),
colonnes = années. Les blocs d'agrégats situés sous la table par âge sont ignorés.
"""
from __future__ import annotations

import io
import pathlib
import zipfile

import openpyxl
import pandas as pd

RAW = pathlib.Path(__file__).resolve().parents[1] / "data" / "raw"

SCENARIOS_ZIP = {
    "insee_proj2026_variantes1.zip": ["11_fec_haute", "12_fec_basse", "13_ev_haute", "14_ev_basse", "15_smi_haut", "16_smi_bas"],
    "insee_proj2026_extremes.zip": ["21_population_haute", "22_population_basse", "23_population_agee", "24_population_jeune"],
    "insee_proj2026_travail.zip": ["52_ev_constante", "53_smi_nul"],
    "insee_proj2026_combines.zip": [
        "31_fec_centrale_ev_haute_smi_haut", "32_fec_centrale_ev_haute_smi_bas", "33_fec_centrale_ev_basse_smi_haut",
        "34_fec_centrale_ev_basse_smi_bas", "35_fec_haute_ev_centrale_smi_haut", "36_fec_haute_ev_centrale_smi_bas",
        "37_fec_haute_ev_haute_smi_central", "38_fec_haute_ev_haute_smi_bas", "39_fec_haute_ev_basse_smi_central",
        "40_fec_haute_ev_basse_smi_bas", "41_fec_basse_ev_centrale_smi_haut", "42_fec_basse_ev_centrale_smi_bas",
        "43_fec_basse_ev_haute_smi_central", "44_fec_basse_ev_haute_smi_haut", "45_fec_basse_ev_basse_smi_central",
        "46_fec_basse_ev_basse_smi_haut"],
}


def _age(x):
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        return int(x)
    if isinstance(x, str) and x.strip().rstrip("+").isdigit():
        return int(x.strip().rstrip("+"))
    return None


def _table(rows, debut: int) -> pd.DataFrame:
    """Table par âge à partir de la ligne d'en-tête `debut` (années en colonnes)."""
    hdr = rows[debut]
    cols = [(j, int(v)) for j, v in enumerate(hdr) if isinstance(v, (int, float)) and j > 0]
    data, ages = [], []
    commence = False
    for r in rows[debut + 1:]:
        a = _age(r[0])
        if a is None:
            if commence:
                break
            continue
        commence = True
        ages.append(a)
        data.append([r[j] for j, _ in cols])
    return pd.DataFrame(data, index=ages, columns=[y for _, y in cols], dtype="float64")


def lire_onglet(wb, nom: str, bloc: int = 0) -> pd.DataFrame:
    rows = list(wb[nom].iter_rows(values_only=True))
    entetes = [i for i, r in enumerate(rows) if sum(isinstance(v, (int, float)) and 1900 < v < 2200 for v in r[1:]) > 20]
    return _table(rows, entetes[bloc])


def ouvrir(scenario: str = "00_central"):
    if scenario == "00_central":
        return openpyxl.load_workbook(RAW / "insee_proj2026_00_central.xlsx", read_only=True, data_only=True)
    for z, noms in SCENARIOS_ZIP.items():
        if scenario in noms:
            with zipfile.ZipFile(RAW / z) as zf:
                nom = [n for n in zf.namelist() if n.endswith(scenario + ".xlsx")][0]
                return openpyxl.load_workbook(io.BytesIO(zf.read(nom)), read_only=True, data_only=True)
    raise KeyError(scenario)


def charger(scenario: str = "00_central") -> dict:
    wb = ouvrir(scenario)
    d = {}
    for s in ("F", "H"):
        d[f"pop{s}"] = lire_onglet(wb, f"population{s}")
        d[f"deces{s}"] = lire_onglet(wb, f"deces{s}")
        d[f"q{s}"] = lire_onglet(wb, f"hyp_mortalite{s}") / 1e5
        d[f"sm{s}"] = lire_onglet(wb, f"hyp_soldemig{s}")
        d[f"aj{s}"] = lire_onglet(wb, f"ajustement{s}")
    d["fec"] = lire_onglet(wb, "hyp_fecondite") / 1e4
    d["naiss_age"] = lire_onglet(wb, "naissance")
    d["pop"] = lire_onglet(wb, "population")
    return d
