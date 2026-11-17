"""M11 — Couplage France-zone euro (version 0.1).

La France représente environ 20 % du PIB de la zone euro. Une mesure française modifie l'activité et l'inflation de la
zone, donc la politique monétaire commune et la demande adressée à la France ; une dette française plus élevée peut
modifier la prime de risque sur les taux français. Ce module ajoute ces rétroactions autour du modèle bouclé M8.

Équations (annuelles) :
1. Règle de taux de la BCE (estimée 1999-2019, Euribor 3 mois) :
     i_t = a + ρ i_{t−1} + b π_t + c écart_t
   π : inflation de l'indice des prix harmonisé de la zone euro ; écart : écart du PIB de la zone à sa tendance (filtre
   de Hodrick-Prescott, λ = 100).
   La réaction porte sur l'écart de production (mesuré pour la France par l'écart de chômage, loi d'Okun), pas sur
   le niveau du PIB.
2. Transmission au taux long français (estimée 1999-2024) : Δ taux_long = α + β Δ i.
3. Prime de risque : +θ point de taux long par point de dette publique française (en % du PIB) au-dessus du compte
   central. θ = 0,03 (3 points de base par point de dette) : ordre de grandeur des estimations empiriques sur les
   écarts de taux souverains en zone euro ; hypothèse de niveau C, sensibilité 0 à 0,05.
4. Reste de la zone euro : PIB des partenaires = multiplicateur κ × exportations supplémentaires vers la France (part de
   la zone dans les importations françaises : 55 %, poids du reste de la zone dans le PIB de la zone : 80 %) ; κ = 1
   (hypothèse C). Inflation de la zone = 0,2 × inflation française + 0,8 × pente de Phillips (0,2) × écart des
   partenaires.
5. Demande adressée à la France (importations de l'UE) : + élasticité 1,5 × écart de PIB des partenaires.

Résolution : M8 est simulé avec des trajectoires de taux longs et de demande mondiale ; on en déduit les écarts de la
zone euro, la réaction de la BCE et des marchés, puis on resimule M8 (point fixe en quelques itérations).
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pandas as pd
import statsmodels.api as sm

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
import m7_series as S  # noqa: E402
from telechargement import jsonstat_dict  # noqa: E402

POIDS_FR = 0.20
PART_IMPORTS_ZE = 0.55
KAPPA = 1.0
PENTE_PHILLIPS_ZE = 0.2
ELAST_IMPORTS_UE = 1.5
THETA_PRIME = 0.03


def _js(nom):
    return pd.Series(jsonstat_dict(json.loads((RACINE / "data" / "raw" / nom).read_text())))


def series() -> pd.DataFrame:
    m = S.macro()
    h = _js("eurostat_prc_hicp_aind_EA.json")
    i = _js("eurostat_irt_st_a_EA.json")
    d = pd.DataFrame(index=range(1995, 2026))
    d["pib_ze"] = m.ze_pib.reindex(d.index)
    d["inflation_ze"] = [float(h.get(("EA", str(t)), np.nan)) for t in d.index]
    d["inflation_fr"] = [float(h.get(("FR", str(t)), np.nan)) for t in d.index]
    d["taux_court"] = [float(i.get(str(t), np.nan)) for t in d.index]
    d["taux_long_fr"] = m.taux_long.reindex(d.index)
    from statsmodels.tsa.filters.hp_filter import hpfilter
    c, _ = hpfilter(np.log(d.pib_ze.dropna()), lamb=100)
    d["ecart_ze"] = (c * 100).reindex(d.index)
    return d


class Europe:
    def __init__(self, debut=1999, fin=2019):
        d = series()
        self.d = d
        ok = (d.index >= debut) & (d.index <= fin)
        X = pd.DataFrame({"i_1": d.taux_court.shift(1), "pi": d.inflation_ze, "ecart": d.ecart_ze})
        self.taylor = sm.OLS(d.taux_court[ok], sm.add_constant(X[ok])).fit(cov_type="HAC", cov_kwds={"maxlags": 1})
        ok2 = (d.index >= 1999) & (d.index <= 2024)
        y = d.taux_long_fr.diff()
        self.terme = sm.OLS(y[ok2], sm.add_constant(d.taux_court.diff()[ok2])).fit(cov_type="HAC", cov_kwds={"maxlags": 1})
        p = self.taylor.params
        rho = p["i_1"]
        self.reponse_inflation = p["pi"] / (1 - rho)
        self.reponse_ecart = p["ecart"] / (1 - rho)

    def resume(self) -> dict:
        p, t = self.taylor.params, self.taylor.tvalues
        return {"lissage ρ": (p["i_1"], t["i_1"]), "réponse de court terme à l'inflation": (p["pi"], t["pi"]),
                "réponse de court terme à l'écart de production": (p["ecart"], t["ecart"]),
                "réponse de long terme à l'inflation": (self.reponse_inflation, np.nan),
                "transmission au taux long français β": (self.terme.params.iloc[1], self.terme.tvalues.iloc[1])}

    def ecarts(self, central: pd.DataFrame, variante: pd.DataFrame, imports_m: pd.Series, theta=THETA_PRIME):
        """Écarts de la zone euro et réactions (en points) induits par l'écart variante − central de M8."""
        p = self.taylor.params
        rho = p["i_1"]
        beta = self.terme.params.iloc[1]
        di_prec = 0.0
        out = {}
        for t in variante.index:
            # écart de production français : mesuré par l'écart de chômage (loi d'Okun), et non par l'écart de PIB, qui
            # inclut les effets d'offre durables (emplois publics, population active)
            import m8_modele as M8
            dpib_fr = -M8.OKUN * (variante.chomage[t] - central.chomage[t])
            dinf_fr = (np.log(variante.pc[t] / variante.pc.get(t - 1, central.pc[t])) - np.log(central.pc[t] / central.pc.get(t - 1, central.pc[t]))) * 100 \
                if (t - 1) in variante.index else (variante.pc[t] / central.pc[t] - 1) * 100
            # importations françaises supplémentaires provenant de la zone, en % du PIB des partenaires
            dm = (variante.m[t] - central.m[t]) / central.m[t] * imports_m[t]
            pib_part = (1 - POIDS_FR) * self.d.pib_ze.iloc[-1] * central.pib[t] / central.pib.iloc[0]
            decart_part = KAPPA * PART_IMPORTS_ZE * dm / pib_part * 100
            decart_ze = POIDS_FR * dpib_fr + (1 - POIDS_FR) * decart_part
            dinf_ze = POIDS_FR * dinf_fr + (1 - POIDS_FR) * PENTE_PHILLIPS_ZE * decart_part
            di = rho * di_prec + p["pi"] * dinf_ze + p["ecart"] * decart_ze
            ddette = variante.dette_pib[t] - central.dette_pib[t]
            out[t] = dict(ecart_pib_partenaires=decart_part, ecart_pib_ze=decart_ze, inflation_ze=dinf_ze, taux_bce=di,
                          taux_long_fr=beta * di + theta * ddette, demande_ue=ELAST_IMPORTS_UE * decart_part)
            di_prec = di
        return pd.DataFrame(out).T


def simuler_couple(mod, ans, ex_central, ex_variante, europe: Europe | None = None, iterations=4, theta=THETA_PRIME):
    """Simule central et variante avec rétroactions zone euro ; renvoie (central, variante, écarts zone euro)."""
    import copy
    europe = europe or Europe()
    central = mod.simuler(ans, ex_central)
    imports_m = central.m * mod.macro.m_cp[mod.B] / mod.macro.m[mod.B]          # importations en valeur (M€)
    ex = copy.copy(ex_variante)
    tl0, dm0 = ex_variante.taux_long.copy(), ex_variante.demande_mondiale.copy()
    E = None
    for _ in range(iterations):
        v = mod.simuler(ans, ex)
        E = europe.ecarts(central, v, imports_m, theta)
        ex = copy.copy(ex_variante)
        ex.taux_long = tl0.add(E.taux_long_fr, fill_value=0.0)
        ex.demande_mondiale = dm0 * (1 + E.demande_ue.reindex(dm0.index).fillna(0.0) / 100)
    v = mod.simuler(ans, ex)
    return central, v, E
