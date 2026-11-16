"""Projection de référence M1 (scénario central Insee 2026), départ au 1er janvier 2026.

Produit outputs/M1_reference.csv (population par grands groupes, naissances, décès, actifs à taux constants).
"""
from __future__ import annotations

import pathlib
import sys

import pandas as pd

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
import insee_projections as ip  # noqa: E402
import m1_demographie as m1  # noqa: E402
from telechargement import eurostat  # noqa: E402

T0, T1 = 2026, 2070


def taux_activite_2024() -> tuple[pd.Series, pd.Series]:
    ages = [f"Y{a}-{a + 4}" for a in range(15, 75, 5)]
    d = eurostat("lfsa_argan", {"geo": "FR", "time": "2024", "sex": ["F", "M"], "age": ages, "citizen": "TOTAL"},
                 nom="eurostat_lfsa_argan_FR_2024.json")
    out = {}
    for s in ("F", "M"):
        v = {}
        for g in ages:
            a0 = int(g[1:3])
            for a in range(a0, a0 + 5):
                v[a] = d[(s, g)] / 100
        out[s] = pd.Series(v)
    return out["F"], out["M"]


def hypotheses_centrales():
    d = ip.charger("00_central")
    h = m1.Hypotheses(d["qF"], d["qH"], d["fec"], d["smF"], d["smH"], d["ajF"], d["ajH"])
    pF = m1.etendre_population(d["popF"][T0].to_numpy(), h.qF[T0].reindex(m1.AGES).to_numpy())
    pH = m1.etendre_population(d["popH"][T0].to_numpy(), h.qH[T0].reindex(m1.AGES).to_numpy())
    return d, h, pF, pH


def main():
    d, h, pF, pH = hypotheses_centrales()
    res = m1.projeter(pF, pH, T0, T1, h)
    tF, tH = taux_activite_2024()
    actifs = m1.population_active(res, tF, tH)
    tab = pd.DataFrame({
        "population": res.total(),
        "0-19": res.groupe(0, 19), "20-64": res.groupe(20, 64), "65+": res.groupe(65), "80+": res.groupe(80),
        "naissances": res.naissances, "deces": (res.decesF + res.decesH).sum(),
        "actifs_15_74_taux_2024": actifs,
    })
    tab["rapport_dependance_65_20_64"] = tab["65+"] / tab["20-64"]
    tab.index.name = "annee"
    (RACINE / "outputs").mkdir(exist_ok=True)
    tab.round(4).to_csv(RACINE / "outputs" / "M1_reference.csv")
    print(tab.loc[[2026, 2030, 2037, 2040, 2050, 2070]].round(3).to_string())


if __name__ == "__main__":
    main()
