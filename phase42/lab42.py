"""Banc d'essai de la phase 4.2 : configurations v0.8, v0.9 et nouvelles spécifications (cumulables, isolables)."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "phase34"))
from lab import *  # noqa: F401,F403
from lab import V09, run, table
CONFIGS = {
    "v0.8": {},
    "v0.9": V09,
    "v0.9 + prix VA (CI)": {**V09, "prix_va": "ci_hausse"},
    "v0.9 + salaires cible conso": {**V09, "salaires": "cible_conso"},
    "v0.9 + salaires cible conso + SMIC": {**V09, "salaires": "cible_conso_smic"},
    "A complet (prix VA + salaires + SMIC)": {**V09, "prix_va": "ci_hausse", "salaires": "cible_conso_smic"},
    "A complet, indexation 0,5": {**V09, "prix_va": "ci_hausse", "salaires": "cible_conso_smic", "indexation_salaires": 0.5},
    "A complet, indexation 0,8": {**V09, "prix_va": "ci_hausse", "salaires": "cible_conso_smic", "indexation_salaires": 0.8},
    "v0.9 + prix VA, indexation 0,5": {**V09, "prix_va": "ci_hausse", "indexation_salaires": 0.5},
    "v0.9 + prix VA, indexation 0,8": {**V09, "prix_va": "ci_hausse", "indexation_salaires": 0.8},
    "v0.9 + prix VA + salaires bruts": {**V09, "prix_va": "ci_hausse", "salaires": "brut"},
    "v0.9 + prix VA + salaires bruts, indexation 0,5": {**V09, "prix_va": "ci_hausse", "salaires": "brut", "indexation_salaires": 0.5},
}
CONFIGS["v0.9 + rattrapage salarial (0,17)"] = {**V09, "indexation_retard": 0.17}
CONFIGS["v0.9 + prix VA + rattrapage salarial (0,17)"] = {**V09, "prix_va": "ci_hausse", "indexation_retard": 0.17}
SELECTION_C = ["v0.9", "v0.9 + prix VA (CI)", "v0.9 + rattrapage salarial (0,17)", "v0.9 + prix VA + rattrapage salarial (0,17)"]
SELECTION_B = ["v0.9", "v0.9 + prix VA + salaires bruts", "v0.9 + prix VA + salaires bruts, indexation 0,5"]
SELECTION = ["v0.8", "v0.9", "v0.9 + prix VA (CI)", "v0.9 + prix VA, indexation 0,5", "v0.9 + prix VA, indexation 0,8",
             "v0.9 + prix VA + salaires bruts", "v0.9 + prix VA + salaires bruts, indexation 0,5"]

# ---- A.2
CONFIGS["C1 frontière des prix de facteurs"] = {**V09, "prix_va": "frontiere"}
CONFIGS["C2 frontière + rattrapage salarial"] = {**V09, "prix_va": "frontiere", "indexation_retard": 0.17}
SELECTION_A2 = ["v0.8", "v0.9", "v0.9 + rattrapage salarial (0,17)", "C1 frontière des prix de facteurs", "C2 frontière + rattrapage salarial"]
CONFIGS["T0 v0.9 sans tension"] = {**V09, "tension_prix": "aucune"}
CONFIGS["T1 frontière sans tension"] = {**V09, "prix_va": "frontiere", "tension_prix": "aucune"}
CONFIGS["T2 frontière sans tension + rattrapage"] = {**V09, "prix_va": "frontiere", "tension_prix": "aucune", "indexation_retard": 0.17}
SELECTION_T = ["v0.9", "T0 v0.9 sans tension", "T1 frontière sans tension", "T2 frontière sans tension + rattrapage"]
