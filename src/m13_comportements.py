"""M13 — Réactions des hauts revenus et des patrimoines : optimisation, moindre déclaration, départs (version 0.1).

Le rendement statique d'une mesure (calculé par M4/M10 ou sur une assiette agrégée) est corrigé des réactions
comportementales documentées dans la littérature empirique. Chaque effet est donné en fourchette basse / centrale /
haute ; seule la valeur centrale est transmise au modèle macroéconomique (M8), la fourchette est restituée.

1. Revenus d'activité élevés (tranches supérieures de l'impôt sur le revenu, CSG) : élasticité du revenu imposable au
   taux net de prélèvement e (Saez 2001 ; pour la France : Cabannes, Houdré et Landais 2014, Lehmann, Marical et Rioux
   2013 : 0,1 à 0,3 pour les hauts revenus ; la réponse inclut optimisation, déclaration et mobilité). Pour une hausse
   Δτ du taux marginal sur la part des revenus au-delà d'un seuil, la perte de recette due aux réactions vaut
   e · a · τ/(1 − τ) du rendement statique, a étant le paramètre de Pareto de la queue de distribution (a ≈ 2 en France,
   Garbinti, Goupille-Lebret et Piketty 2018) et τ le taux marginal total (impôt sur le revenu, CSG-CRDS, contribution
   sur les hauts revenus).
2. Revenus du capital (prélèvement forfaitaire unique) : élasticité des revenus distribués e_K (France, réforme de
   2018 : forte hausse des dividendes distribués, Bach, Bozio, Guillouzouic et Malgouyres 2023 ; e_K ≈ 0,5 central,
   0,2 à 1,0).
3. Impôt sur la fortune : réduction de l'assiette déclarée (évasion, optimisation, moindre accumulation) et départs.
   Jakobsen et al. (2020, Danemark), Seim (2017, Suède), Brülhart et al. (2022, Suisse) : l'assiette déclarée baisse
   de 10 à 40 % du rendement statique selon le taux et la durée ; départs : environ 0,2 % des redevables par an avant
   2017 (DGFiP), une partie seulement attribuable à l'impôt. Central : 25 % la première année, 35 % après cinq ans ;
   fourchette 10-50 %.
4. Droits de succession : anticipation et optimisation (donations, assurance vie) : 10 % central (0-25 %).
5. Mobilité des diplômés et cadres (« fuite des cerveaux ») : élasticité de la localisation des hauts revenus nationaux
   au taux net de prélèvement 0,1 à 0,25 (Kleven, Landais et Saez 2013 ; Kleven et al. 2014, nationaux danois). Le
   nombre de départs est restitué à titre indicatif ; son effet budgétaire est déjà compris dans l'élasticité e.
Niveau de preuve : C (élasticités issues d'études publiées, transposées à la France et aux réformes simulées) et D
(transposition à des taux éloignés des réformes observées).
"""
from __future__ import annotations

PARETO = 2.0
TAUX_SOCIAUX = 0.097          # CSG-CRDS sur les revenus d'activité
# taux marginal total au-dessus du seuil de chaque tranche (impôt sur le revenu 2024 + CSG-CRDS ; CEHR au-delà de 250 k€)
TAUX_MARGINAL = {1: 0.11, 2: 0.30, 3: 0.41, 4: 0.45 + 0.03}
ELASTICITE_REVENU = {"basse": 0.1, "centrale": 0.2, "haute": 0.4}
ELASTICITE_CAPITAL = {"basse": 0.2, "centrale": 0.5, "haute": 1.0}
TAUX_PFU = 0.30
ISF = {"basse": 0.10, "centrale": 0.25, "haute": 0.50}
ISF_AN5 = {"basse": 0.15, "centrale": 0.35, "haute": 0.50}
SUCCESSIONS = {"basse": 0.0, "centrale": 0.10, "haute": 0.25}
ELASTICITE_MOBILITE = {"basse": 0.1, "centrale": 0.15, "haute": 0.25}
FOYERS_HAUTS_REVENUS = {3: 1_700_000, 4: 200_000}       # foyers dont le revenu atteint la tranche (ordre de grandeur)


def part_perdue_ir(tranche: int, nouveau_taux: float, niveau="centrale") -> float:
    """Part du rendement statique perdue par les réactions, pour un changement du taux de la tranche (1 à 4).
    Les tranches 1 et 2 concernent l'essentiel des contribuables : réaction négligée (e ≈ 0 hors hauts revenus)."""
    if tranche < 3:
        return 0.0
    tau = max(TAUX_MARGINAL[tranche], nouveau_taux + (0.03 if tranche == 4 else 0.0)) + TAUX_SOCIAUX
    return ELASTICITE_REVENU[niveau] * PARETO * tau / (1 - tau)


def part_perdue_pfu(points: float, niveau="centrale") -> float:
    tau = TAUX_PFU + points / 100
    return min(0.9, ELASTICITE_CAPITAL[niveau] * tau / (1 - tau))


def part_perdue_isf(annees_depuis_debut: int, niveau="centrale") -> float:
    a0, a5 = ISF[niveau], ISF_AN5[niveau]
    return a0 + (a5 - a0) * min(1.0, max(0, annees_depuis_debut) / 5)


def part_perdue_successions(niveau="centrale") -> float:
    return SUCCESSIONS[niveau]


def departs_hauts_revenus(tranche: int, nouveau_taux: float, ancien_taux: float, niveau="centrale") -> float:
    """Variation du nombre de foyers à hauts revenus résidents (positif : départs nets supplémentaires)."""
    if tranche < 3:
        return 0.0
    t0 = ancien_taux + TAUX_SOCIAUX + (0.03 if tranche == 4 else 0.0)
    t1 = nouveau_taux + TAUX_SOCIAUX + (0.03 if tranche == 4 else 0.0)
    import math
    return ELASTICITE_MOBILITE[niveau] * (math.log(1 - t0) - math.log(1 - t1)) * FOYERS_HAUTS_REVENUS[tranche]


def fourchette(f, *args) -> dict:
    return {n: f(*args, niveau=n) for n in ("basse", "centrale", "haute")}
