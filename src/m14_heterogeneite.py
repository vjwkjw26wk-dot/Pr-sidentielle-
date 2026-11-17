"""M14 — Hétérogénéité des comportements des ménages et des entreprises (audit de novembre 2026).

1. Propension marginale à consommer par décile de niveau de vie
   L'équation agrégée de consommation (lot 7) est estimée sur des variations du revenu disponible dont la répartition
   entre ménages suit, en moyenne, celle du revenu. Une mesure qui concentre ses gains ou ses pertes sur certains
   déciles a un effet différent sur la consommation. Le revenu pris en compte par l'équation est corrigé :
       revenu « effectif » = revenu disponible + Σ_d ΔR_d (π_d / π̄ − 1),
   ΔR_d : variation du revenu disponible du décile d due à la mesure (microsimulation M10),
   π_d : propension marginale à consommer du décile, π̄ : sa moyenne pondérée par le revenu disponible.
   Seul le profil relatif π_d / π̄ intervient : le niveau moyen reste celui de l'équation estimée.
   Niveau de preuve C (calibré) : profil décroissant cohérent avec
   - Insee Focus n° 338 (2024) : taux d'épargne de −29 % (quintile 1) à 27 % (quintile 5) en 2022 ;
   - Garbinti et Lamarche (Économie et Statistique n° 472-473, 2014) : taux d'épargne croissant avec le revenu
     permanent ;
   - Jappelli et Pistaferri (AEJ Macroeconomics, 2014), Fagereng, Holm et Natvik (AEJ Macro, 2021) : propension
     de première année proche de 0,5 en moyenne, nettement plus forte pour les ménages peu liquides ;
   - Arrondel, Lamarche et Savignac (Banque de France, 2015) ; Garbinti et al. (Banque de France, document de travail
     n° 751) : propension à consommer la richesse décroissante le long de la distribution.
   Le profil n'est pas estimé sur données françaises de panel (non disponibles en données ouvertes) : variantes de
   sensibilité « plat » (pas d'hétérogénéité) et « accentué ».

2. Distribution des profits des sociétés et revenus versés au reste du monde
   Une hausse des profits après impôt (baisse de l'IS ou des impôts de production) n'est ni intégralement investie ni
   intégralement distribuée. Part distribuée en dividendes à moyen terme : DISTRIBUTION_PROFITS ; part des dividendes
   versés aux non-résidents : PART_NON_RESIDENTS ; part reçue directement par les ménages résidents (le reste transite
   par les sociétés financières résidentes et les assureurs, sans effet de court terme sur la consommation) :
   PART_MENAGES_DIVIDENDES ; ces dividendes reviennent pour l'essentiel au dernier décile (π du dernier centile).
"""
from __future__ import annotations

import numpy as np

# Propension marginale à consommer de première année par décile de niveau de vie (profil calibré, voir ci-dessus)
PMC_DECILES = {
    "central": [0.90, 0.85, 0.80, 0.75, 0.72, 0.68, 0.64, 0.60, 0.53, 0.40],
    "plat": [0.65] * 10,
    "accentue": [1.00, 0.95, 0.88, 0.80, 0.74, 0.68, 0.61, 0.54, 0.44, 0.28],
}
PMC_TOP1 = 0.25

# Comptes nationaux 2022 (Eurostat nasa_10_nf_tr) : SNF, excédent brut 420 Md€, dividendes versés 273 Md€, reçus 220 Md€ ;
# ménages, dividendes reçus 64 Md€. Banque de France (Bulletin 261/3, 2025) : 50 % du capital des sociétés françaises
# du CAC 40 détenu par des non-résidents en 2024 ; environ 40 % pour l'ensemble des actions cotées.
DISTRIBUTION_PROFITS = {"bas": 0.3, "central": 0.5, "haut": 0.7}   # part d'un supplément de profit distribuée (2-3 ans)
PART_NON_RESIDENTS = 0.40
PART_MENAGES_DIVIDENDES = 0.35   # des dividendes versés aux résidents, part reçue directement par les ménages


def profil(variante: str = "central") -> np.ndarray:
    return np.asarray(PMC_DECILES[variante], dtype=float)


def ajustement_conso(distribution, variante: str = "central") -> float:
    """Supplément de revenu « effectif » pour la consommation (M€ par an, aux revenus de l'année de la microsimulation).
    `distribution` : liste de dictionnaires par décile (M10) avec "masse_M€" et "revenu_M€"."""
    if not distribution or "masse_M€" not in distribution[0]:
        return 0.0
    d = sorted(distribution, key=lambda x: x["decile"])
    pi = profil(variante)
    rev = np.array([x["revenu_M€"] for x in d])
    dm = np.array([x["masse_M€"] for x in d])
    moy = float((pi * rev).sum() / rev.sum())
    return float((dm * (pi / moy - 1)).sum())


# Parts des déciles dans le revenu disponible (ordre de grandeur, Insee, comptes par catégorie de ménages 2022) : pondération
# de la propension moyenne quand la distribution de la microsimulation n'est pas disponible.
PARTS_REVENU = [0.03, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.12, 0.15, 0.25]


def pmc_moyenne(variante: str = "central") -> float:
    return float((profil(variante) * np.array(PARTS_REVENU)).sum() / sum(PARTS_REVENU))


def facteur_top1(variante: str = "central") -> float:
    """π du dernier centile rapporté à la moyenne (revenus concentrés au sommet : dividendes, ISF, PFU)."""
    return 1.0 if variante == "plat" else PMC_TOP1 / pmc_moyenne(variante)


def dividendes_menages(supplement_profit_M: float, part_distribuee: float) -> dict:
    """Répartition d'un supplément de profits après impôt (M€) : dividendes aux non-résidents, aux ménages résidents,
    et part conservée par les entreprises (autofinancement, trésorerie, désendettement)."""
    div = supplement_profit_M * part_distribuee
    return {"non_residents": div * PART_NON_RESIDENTS, "menages": div * (1 - PART_NON_RESIDENTS) * PART_MENAGES_DIVIDENDES,
            "autres_residents": div * (1 - PART_NON_RESIDENTS) * (1 - PART_MENAGES_DIVIDENDES),
            "conserve": supplement_profit_M * (1 - part_distribuee)}


def revenus_primaires_nets(annee: int) -> float:
    """Solde des revenus primaires reçus du reste du monde rapporté au PIB (RNB / PIB − 1), Eurostat nasa_10_nf_tr
    (B5G du total de l'économie) et nama_10_gdp via m7_series."""
    import json
    import m7_series as S
    from telechargement import jsonstat_dict
    u = S.B + "nasa_10_nf_tr?format=JSON&geo=FR&unit=CP_MEUR&sinceTimePeriod=1995&sector=S1&direct=RECV&direct=PAID&na_item=B5G"
    d = jsonstat_dict(json.loads(S.telecharger(u, "eurostat_nasa_B5G_S1_FR.json").read_text()))
    b5 = None
    for cle, v in d.items():
        if (cle if isinstance(cle, str) else cle[-1]) == str(annee):
            b5 = v
    return float(b5) / float(S.macro().pib_cp[annee]) - 1.0
