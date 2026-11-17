"""Validation de M11 (couplage France-zone euro) et variantes.

1. Règle de taux de la BCE estimée sur 1999-2019 : simulation dynamique 2000-2019 (dans l'échantillon) et 2020-2025
   (hors échantillon) à partir de l'inflation et de l'écart de production observés.
2. Variantes (base 2022, 2023-2035, fermeture d'offre) :
   - consommation publique française +1 point de PIB : sans rétroaction européenne, avec BCE et demande des partenaires,
     avec en plus la prime de risque sur la dette ;
   - même mesure coordonnée dans toute la zone euro (partenaires +1 point de PIB de dépense publique) ;
   - hausse durable des transferts aux ménages de 1 point de PIB (choc de dette).
Sortie : outputs/validation_M11.md
"""
from __future__ import annotations

import copy
import pathlib
import sys
import time
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
import m11_europe as EU  # noqa: E402
import m8_modele as M8  # noqa: E402


def main():
    t0 = time.time()
    e = EU.Europe()
    d = e.d
    L = ["# Validation de M11 — couplage France-zone euro (version 0.1)", "", "Généré par `tests/validation_M11.py`.", "",
         "## 1. Règle de taux de la BCE (Euribor 3 mois, estimée 1999-2019)", "", "| Paramètre | Valeur | t |", "|---|---|---|"]
    for k, (a, b) in e.resume().items():
        L.append(f"| {k} | {a:.2f} | {'' if np.isnan(b) else f'{b:.1f}'} |")
    p = e.taylor.params
    sim = {1999: d.taux_court[1999]}
    for t in range(2000, 2026):
        sim[t] = p["const"] + p["i_1"] * sim[t - 1] + p["pi"] * d.inflation_ze[t] + p["ecart"] * d.ecart_ze[t]
    L += ["", "Simulation dynamique (le taux simulé de l'année précédente alimente l'année suivante), inflation et écart de "
          "production observés :", "", "| Année | Euribor observé | Simulé |", "|---|---|---|"]
    for t in (2003, 2008, 2012, 2016, 2019, 2021, 2022, 2023, 2024, 2025):
        L.append(f"| {t} | {d.taux_court[t]:.2f} | {sim[t]:.2f} |")
    L += ["", "Le plancher effectif des taux (2015-2021, taux négatifs et achats d'actifs) n'est pas représenté ; la remontée "
          "de 2022-2023 est reproduite avec retard.", ""]
    mod = M8.Modele(2022)
    ans = range(2023, 2036)
    base = M8.exogenes_projection(mod, ans)
    g_part = mod.T.Fd.loc[mod.P, ["P3_S13", "P3_S15"]].values.sum() + mod.T.Fm.loc[mod.P, ["P3_S13", "P3_S15"]].values.sum()
    choc_g = pd.Series({t: (1 + 0.01 * mod.macro.pib_cp[2022] / g_part if t >= 2024 else 1.0) for t in base.conso_publique.index})

    def var_g():
        v = M8.exogenes_projection(mod, ans)
        v.conso_publique = v.conso_publique * choc_g
        return v
    central = mod.simuler(ans, base)
    resultats = {}
    resultats["Dépense publique française +1 pt de PIB, sans rétroaction européenne"] = (central, mod.simuler(ans, var_g()), None)
    resultats["… avec BCE et demande des partenaires (sans prime de risque)"] = EU.simuler_couple(mod, ans, base, var_g(), e, theta=0.0)
    resultats["… avec en plus la prime de risque (3 pb par point de dette)"] = EU.simuler_couple(mod, ans, base, var_g(), e)
    # partenaires : même mesure ; leur écart de PIB suit celui de la France dans la variante isolée (même politique,
    # multiplicateur comparable) ; la BCE réagit à l'écart et à l'inflation de toute la zone
    iso = resultats["Dépense publique française +1 pt de PIB, sans rétroaction européenne"][1]
    dev = -M8.OKUN * (iso.chomage - central.chomage)          # écart de production (Okun), comme dans M11
    dinf = (np.log(iso.pc / central.pc).diff().fillna(np.log(iso.pc / central.pc))) * 100
    rho, bp, be = e.taylor.params["i_1"], e.taylor.params["pi"], e.taylor.params["ecart"]
    di, prec = {}, 0.0
    for t in dev.index:
        prec = rho * prec + bp * dinf[t] + be * dev[t]
        di[t] = prec
    coord = var_g()
    coord.demande_mondiale = coord.demande_mondiale * (1 + EU.ELAST_IMPORTS_UE * dev.reindex(coord.demande_mondiale.index).fillna(0) / 100)
    coord.taux_long = coord.taux_long + e.terme.params.iloc[1] * pd.Series(di).reindex(coord.taux_long.index).fillna(0)
    resultats["Relance coordonnée dans toute la zone euro (+1 pt de PIB partout)"] = EU.simuler_couple(mod, ans, base, coord, e)
    tr = M8.exogenes_projection(mod, ans)
    tr.ajust_prestations = pd.Series({t: (0.01 * mod.macro.pib_cp[2022] * 1.03 ** (t - 2022) if t >= 2024 else 0.0) for t in ans})
    resultats["Transferts aux ménages +1 pt de PIB, avec rétroactions et prime de risque"] = EU.simuler_couple(mod, ans, base, tr, e)
    L += ["## 2. Variantes (écarts au compte central, base 2022)", ""]
    for nom, (c, v, E) in resultats.items():
        L += [f"### {nom}", "", "| Année | PIB | Inflation (pt, cumul prix) | Taux BCE (pt) | Taux long FR (pt) | Demande des partenaires | Solde public (pt de PIB) | Dette (pt de PIB) |",
              "|---|---|---|---|---|---|---|---|"]
        for t in (2024, 2026, 2030, 2035):
            L.append(f"| {t} | {(v.pib[t] / c.pib[t] - 1) * 100:+.2f} % | {(v.pc[t] / c.pc[t] - 1) * 100:+.2f} | "
                     f"{(E.taux_bce[t] if E is not None else 0):+.2f} | {(E.taux_long_fr[t] if E is not None else 0):+.2f} | "
                     f"{(E.demande_ue[t] if E is not None else 0):+.2f} % | {v.solde_pib[t] - c.solde_pib[t]:+.2f} | {v.dette_pib[t] - c.dette_pib[t]:+.2f} |")
        L.append("")
    L += [f"Durée : {time.time() - t0:.0f} s.", ""]
    (RACINE / "outputs" / "validation_M11.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
