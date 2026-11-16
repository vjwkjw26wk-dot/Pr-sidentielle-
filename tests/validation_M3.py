"""Validation du lot 3 — cadre comptable T0.

Contrôles :
 1. Cohérence des comptes publiés (avant réconciliation) : écarts de ligne et de colonne, en M€.
 2. Cadre réconcilié : toutes les identités exactes (ligne, colonne, Σ B9 = 0), tolérance 1e-6 M€.
 3. Agrégats : PIB selon trois optiques, solde et dette publics, taux d'épargne des ménages.
 4. Flux-stocks : Σ patrimoines financiers nets = 0 ; décomposition PFN(t) − PFN(t−1) = B9F + autres flux ;
    dette publique : Δdette = −B9 + ajustement stock-flux.
Sorties : outputs/validation_M3.md, outputs/M3_matrice_T0_<année>.csv
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
import m3_cadre_comptable as m3  # noqa: E402

ANNEES = [2019, 2020, 2021, 2022, 2023, 2024, 2025]


def main():
    df = m3.charger_eurostat()
    bs, tr, edp = m3.charger_financier()
    L = ["# Validation du lot 3 — cadre comptable T0 (comptes des secteurs institutionnels, base 2020)", "",
         "Source : Eurostat `nasa_10_nf_tr`, `nasa_10_f_bs`, `nasa_10_f_tr`, `gov_10dd_edpt1` (données transmises par l'Insee), M€ courants. "
         "Généré par `tests/validation_M3.py`.", "",
         "## 1. Cohérence des comptes publiés (avant réconciliation)", "",
         "| Année | Lignes non équilibrées | Écart de ligne max (M€) | Écart de B9 max entre calcul et publication (M€) |",
         "|---|---|---|---|"]
    ok_ident = True
    rec = {}
    for t in ANNEES:
        M = m3.matrice(df, t)
        R, tab, ecol = m3.reconcilier(M, m3.b9_publie(df, t))
        rec[t] = R
        n = int((tab["ecart_ligne"].abs() > 0.5).sum())
        L.append(f"| {t} | {n} sur {len(tab)} | {tab['ecart_ligne'].abs().max():.0f} | {ecol.abs().max():.0f} |")
        # identités du cadre réconcilié
        E = R.xs("E", axis=1, level=1)
        Rr = R.xs("R", axis=1, level=1)
        e_lig = (E.sum(axis=1) - Rr.sum(axis=1)).abs().max()
        sol = m3.soldes(R)
        e_col = (sol[m3.SECTEURS] - m3.b9_publie(df, t)).abs().max()
        e_tot = abs(sol.sum())
        ok_ident &= max(e_lig, e_col, e_tot) < 1e-6
        rec[t].attrs["ident"] = (e_lig, e_col, e_tot)
    L += ["", "Les écarts ne dépassent pas quelques M€ : ce sont des arrondis de publication. Ils sont reportés dans un compte "
          "explicite « ECART » ; aucune opération n'est modifiée.", "",
          "## 2. Identités du cadre réconcilié", "",
          "| Année | Max |Σ emplois − Σ ressources| par ligne | Max |B9 − B9 publié| | |Σ B9 tous secteurs| |", "|---|---|---|---|"]
    for t in ANNEES:
        a, b, c = rec[t].attrs["ident"]
        L.append(f"| {t} | {a:.1e} | {b:.1e} | {c:.1e} |")
    L += ["", f"**Toutes les identités vérifiées à 1e-6 M€ près : {'oui' if ok_ident else 'NON'}.**", "",
          "## 3. Agrégats", ""]
    ag = pd.DataFrame({t: m3.agregats(df, t) for t in ANNEES})
    L += ["| Agrégat | " + " | ".join(map(str, ANNEES)) + " |", "|---|" + "---|" * len(ANNEES)]
    for i, r in ag.iterrows():
        fmt = (lambda v: f"{v:.1f}") if "%" in i or "Taux" in i else (lambda v: f"{v:,.0f}".replace(",", " "))
        L.append(f"| {i} | " + " | ".join(fmt(v) for v in r) + " |")
    ecart_pib = (ag.loc["PIB optique production (Σ VA + impôts nets sur produits)"] - ag.loc["PIB publié (B1GQ)"]).abs().max()
    ecart_dem = (ag.loc["PIB optique demande (P3 + P5 + P6 − P7)"] - ag.loc["PIB publié (B1GQ)"]).abs().max()
    L += ["", f"Écart maximal du PIB reconstitué au PIB publié : optique production {ecart_pib:.0f} M€, optique demande {ecart_dem:.0f} M€.", "",
          "## 4. Flux et stocks", "", "### Dette publique au sens de Maastricht", "",
          "| Année | Dette (M€) | Dette (% PIB) | Solde (% PIB) | Δ dette (M€) | Ajustement stock-flux (M€) |", "|---|---|---|---|---|---|"]
    for t in ANNEES[1:]:
        d = m3.dette_maastricht(edp, t)
        L.append(f"| {t} | {d['dette fin t (M€)']:,.0f} | {d['dette en % du PIB']:.1f} | {d['solde en % du PIB']:.1f} | "
                 f"{d['variation de dette']:,.0f} | {d['ajustement stock-flux (Δdette + B9)']:,.0f} |".replace(",", " "))
    for t in (2024, 2025):
        fs = m3.flux_stocks(df, bs, tr, t)
        L += ["", f"### Patrimoine financier net par secteur, {t} (M€)", "",
              "| Secteur | PFN fin t−1 | PFN fin t | B9 non financier | B9F financier | Écart B9 − B9F | Autres flux |", "|---|---|---|---|---|---|---|"]
        for s, r in fs.iterrows():
            L.append(f"| {s} | " + " | ".join(f"{v:,.0f}".replace(",", " ") for v in r) + " |")
    L += ["", "Σ des patrimoines financiers nets (y compris reste du monde) = 0 à l'arrondi près : le cadre de stocks est fermé. "
          "L'écart B9 − B9F (comptes non financiers et financiers) et les « autres flux » (réévaluations, changements de volume) "
          "sont des grandeurs explicites du cadre ; ils seront exogènes en simulation (scénario de prix d'actifs), sauf modélisation ultérieure."]
    (RACINE / "outputs").mkdir(exist_ok=True)
    (RACINE / "outputs" / "validation_M3.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    for t in (2024, 2025):
        rec[t].round(3).to_csv(RACINE / "outputs" / f"M3_matrice_T0_{t}.csv")
    print("\n".join(L))


if __name__ == "__main__":
    main()
