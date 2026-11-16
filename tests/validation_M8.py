"""Validation du modèle bouclé M8 (version 0.1).

1. Simulations rétrospectives du modèle complet (toutes les équations bouclées, seules les variables exogènes sont
   observées : demande et prix mondiaux, prix d'importation par produit, consommation publique en volume, autres
   investissements, population active, taux long, taux d'IS, prestations en volume, autres dépenses publiques) :
     - base 2014, simulation 2015-2019 (coefficients estimés sur 1997-2014) ;
     - base 2022, simulation 2023-2024 (coefficients estimés sur 1997-2019).
2. Variantes autour d'un compte central conventionnel (base 2022, 2023-2028) : écarts au compte central.
Sortie : outputs/validation_M8.md
"""
from __future__ import annotations

import pathlib
import sys
import time
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
import m8_modele as M  # noqa: E402

VARS = [("pib", "PIB en volume"), ("c", "Consommation des ménages"), ("fbcf", "Investissement total"), ("x", "Exportations"),
        ("m", "Importations"), ("emploi", "Emploi total"), ("pc", "Prix à la consommation"), ("salaire", "Salaire moyen par tête (marchand)"),
        ("rdb", "Revenu disponible brut (valeur)")]


def observe(mod):
    m, men, em = mod.macro, mod.men, mod.emp
    g = mod.panel.groupby("annee")[["wb", "ns"]].sum()
    return pd.DataFrame({"pib": m.pib, "c": m.c, "fbcf": m.fbcf, "x": m.x, "m": m.m, "emploi": em.emploi, "pc": m.p_c,
                         "salaire": g.wb / g.ns, "rdb": men.rdb, "chomage": m.chomage,
                         "solde_pib": mod.apu.b9 / m.pib_cp * 100, "dette_pib": mod.apu.dette / m.pib_cp * 100})


def retro(base, fin, fin_estimation):
    mod = M.Modele(base, fin_estimation)
    ans = range(base + 1, fin + 1)
    r = mod.simuler(ans, M.exogenes_observes(mod, ans))
    o = observe(mod)
    L = [f"### Base {base}, simulation {base + 1}-{fin} (coefficients estimés sur 1997-{fin_estimation})", "",
         "| Variable | Croissance annuelle moyenne observée | Simulée | Erreur sur le niveau en " + str(fin) + " |", "|---|---|---|---|"]
    n = fin - base
    for v, lib in VARS:
        go = (o[v][fin] / o[v][base]) ** (1 / n) - 1
        gs = (r[v][fin] / o[v][base]) ** (1 / n) - 1
        L.append(f"| {lib} | {go * 100:+.1f} % | {gs * 100:+.1f} % | {(r[v][fin] / o[v][fin] - 1) * 100:+.1f} % |")
    L += [f"| Taux de chômage en {fin} | {o.chomage[fin]:.1f} % | {r.chomage[fin]:.1f} % | {r.chomage[fin] - o.chomage[fin]:+.1f} point |",
          f"| Solde public en {fin} (% du PIB) | {o.solde_pib[fin]:.1f} | {r.solde_pib[fin]:.1f} | {r.solde_pib[fin] - o.solde_pib[fin]:+.1f} point |",
          f"| Dette publique en {fin} (% du PIB) | {o.dette_pib[fin]:.1f} | {r.dette_pib[fin]:.1f} | {r.dette_pib[fin] - o.dette_pib[fin]:+.1f} points |", ""]
    return L


def variantes():
    mod = M.Modele(2022)
    ans = range(2023, 2029)
    central = mod.simuler(ans, M.exogenes_projection(mod, ans))
    ene = M.exogenes_projection(mod, ans)
    for p in ("CPA_B", "CPA_C19", "CPA_D"):
        ene.prix_import[p] = [v * (1.5 if t >= 2024 else 1.0) for t, v in zip(ene.prix_import.index, ene.prix_import[p])]
    indus = ["CPA_C20", "CPA_C21", "CPA_C24", "CPA_C25", "CPA_C26", "CPA_C27", "CPA_C28", "CPA_C29"]
    vs = {
        "Énergie importée +50 % (dès 2024)": ene,
        "Salaires +2 % (choc ponctuel en 2024)": M.exogenes_projection(mod, ans, choc_salaire=pd.Series({2024: 0.02})),
        "Taux d'IS de 25,8 % à 20 % (dès 2024)": M.exogenes_projection(mod, ans, taux_is=pd.Series({t: (25.83 if t < 2024 else 20.0) for t in range(2019, 2029)})),
        "Réindustrialisation : parts importées −20 % (chimie, pharmacie, métallurgie, électronique, équipements, automobile)":
            M.exogenes_projection(mod, ans, parts_importees={p: 0.8 for p in indus}, phi_impose=central.phi),
        "Consommation publique +1 % du PIB en volume (dès 2024)":
            M.exogenes_projection(mod, ans),
    }
    g = vs["Consommation publique +1 % du PIB en volume (dès 2024)"]
    pibb = mod.macro.pib_cp[2022]
    g_part = mod.T.Fd.loc[mod.P, ["P3_S13", "P3_S15"]].values.sum() + mod.T.Fm.loc[mod.P, ["P3_S13", "P3_S15"]].values.sum()
    g.conso_publique = g.conso_publique * pd.Series({t: (1 + 0.01 * pibb / g_part if t >= 2024 else 1.0) for t in g.conso_publique.index})
    L = ["## 2. Variantes (écarts au compte central, base 2022)", "",
         "Compte central conventionnel, et non une prévision (`exogenes_projection`). Écarts en % (volumes, prix) ou en points.", ""]
    for nom, ex in vs.items():
        t0 = time.time()
        r = mod.simuler(ans, ex)
        L += [f"### {nom}", "", "| Année | PIB | Consommation | Investissement | Exportations | Importations | Emploi (milliers) | Chômage (pt) | Prix conso. | Salaire | Solde public (pt de PIB) | Dette (pt de PIB) |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for t in (2024, 2026, 2028):
            e = lambda v: (r[v][t] / central[v][t] - 1) * 100  # noqa: E731
            L.append(f"| {t} | {e('pib'):+.2f} % | {e('c'):+.2f} % | {e('fbcf'):+.2f} % | {e('x'):+.2f} % | {e('m'):+.2f} % | "
                     f"{r.emploi[t] - central.emploi[t]:+.0f} | {r.chomage[t] - central.chomage[t]:+.2f} | {e('pc'):+.2f} % | {e('salaire'):+.2f} % | "
                     f"{r.solde_pib[t] - central.solde_pib[t]:+.2f} | {r.dette_pib[t] - central.dette_pib[t]:+.2f} |")
        L.append("")
    return L, central


def main():
    t0 = time.time()
    L = ["# Validation du modèle bouclé M8 (version 0.1)", "", "Généré par `tests/validation_M8.py`.", "",
         "## 1. Simulations rétrospectives du modèle complet", "",
         "Toutes les équations sont bouclées ; seules les variables exogènes sont observées. Les mesures de politique publique "
         "ne sont pas introduites une à une : les recettes suivent les assiettes à taux apparents constants, sauf l'impôt sur "
         "les sociétés (taux normal) ; les dépenses publiques hors consommation, prestations et intérêts sont prises observées en part du PIB. "
         "La dette évolue avec le solde seulement (ajustements stock-flux nuls).", ""]
    L += retro(2014, 2019, 2014)
    L += retro(2022, 2024, 2019)
    Lv, central = variantes()
    L += Lv
    L += [f"Durée : {time.time() - t0:.0f} s.", ""]
    (RACINE / "outputs" / "validation_M8.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
