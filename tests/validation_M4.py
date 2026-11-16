"""Validation du lot 4 (population M4) et des masses d'impôt sur le revenu du lot 5.

Construit la population (échantillon de 2 % des ménages du recensement 2022), puis calcule l'IR 2024 avec
OpenFisca-France en trois passes :
 V0. salaires et pensions seuls (« autres revenus » non imposables) → RFR et impôt ;
 V1. ajout des « autres revenus » = RFR DGFiP de rang − RFR de V0, déclarés en revenus de capitaux (2TR)
     soumis au prélèvement forfaitaire unique ;
 V2. mêmes revenus imposés au barème (option 2OP).
Marges utilisées pour construire : distribution des foyers par tranche de RFR, salaires et pensions moyens par tranche.
Grandeurs de TEST (non utilisées) : impôt net et part de foyers imposés par tranche, impôt total.
Sortie : outputs/validation_M4.md
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
import m4_openfisca as mo  # noqa: E402
import m4_population as m4  # noqa: E402

F = 0.02


def main():
    t0 = time.time()
    ind, fo, ir = m4.construire(f=F)
    p1 = mo.impot(ind, 2024, variables=("rfr", "nbptr", "impot_revenu_restant_a_payer"))
    fo["ir_salpen"] = -p1.impot_revenu_restant_a_payer_of  # variante 0 : autres revenus non imposables
    fo["rfr_salpen"] = p1.rfr_of
    fo["nbptr"] = p1.nbptr_of
    fo["autres"] = (fo.rfr - fo.rfr_salpen).clip(lower=0)
    # impôt au sens de l'IRCOM : barème + contribution exceptionnelle sur les hauts revenus + PFU, après seuils de
    # mise en recouvrement (variable OpenFisca impot_revenu_restant_a_payer, signe inversé) ; sans réductions ni crédits
    v = ("impot_revenu_restant_a_payer", "prelevement_forfaitaire_unique_ir", "contribution_exceptionnelle_hauts_revenus", "rfr")
    pa = mo.impot(ind, 2024, variables=v, autres=fo.autres)
    pb = mo.impot(ind, 2024, variables=v, autres=fo.autres, option_bareme=True)
    fo["ir_pfu"] = -pa.impot_revenu_restant_a_payer_of
    fo["ir_bareme"] = -pb.impot_revenu_restant_a_payer_of
    fo["pfu"] = pa.prelevement_forfaitaire_unique_ir_of
    fo["cehr"] = pa.contribution_exceptionnelle_hauts_revenus_of
    fo["rfr_final"] = pa.rfr_of
    w = fo.poids
    t = ir.set_index("tranche")
    g = lambda col: (fo[col] * w).groupby(fo.tranche).sum()  # noqa: E731
    n = w.groupby(fo.tranche).sum()
    tab = pd.DataFrame({
        "foyers_sim": n, "foyers_dgfip": t.foyers,
        "rfr_moy_cible": g("rfr") / n, "rfr_moy_openfisca": g("rfr_final") / n, "rfr_moy_dgfip": t.rfr / t.foyers,
        "part_autres": g("autres") / g("rfr"),
        "imposes_sim": (w * (fo.ir_pfu > 0)).groupby(fo.tranche).sum() / n, "imposes_dgfip": t.foyers_imposes / t.foyers,
        "ir_moy_pfu": g("ir_pfu") / n, "ir_moy_bareme": g("ir_bareme") / n, "ir_moy_dgfip": t.impot / t.foyers,
    }).reindex(ir.tranche)
    # regroupement lisible
    groupes = {"0 à 15 000": ["0 à 10 000", "10 001 à 12 000", "12 001 à 15 000"], "15 001 à 20 000": ["15 001 à 20 000"],
               "20 001 à 30 000": ["20 001 à 30 000"], "30 001 à 50 000": ["30 001 à 50 000"],
               "50 001 à 100 000": ["50 001 à 100 000"], "100 001 à 200 000": ["100 001 à 200 000"],
               "200 001 à 1 000 000": [x for x in ir.tranche if x.split(" à ")[0].replace(" ", "").isdigit()
                                         and 200_000 <= float(x.split(" à ")[0].replace(" ", "")) < 1_000_000],
               "Plus de 1 000 000": [x for x in ir.tranche if x.startswith("Plus de 9") or
                                     (x.split(" à ")[0].replace(" ", "").isdigit() and float(x.split(" à ")[0].replace(" ", "")) >= 1_000_000)]}
    lignes_g = []
    for nom, membres in groupes.items():
        m = fo.tranche.isin(membres)
        ns = w[m].sum()
        nd = t.loc[membres, "foyers"].sum()
        lignes_g.append({"tranche": nom, "foyers_sim_M": ns / 1e6, "foyers_dgfip_M": nd / 1e6,
                         "imposes_sim": (w[m] * (fo.ir_pfu[m] > 0)).sum() / ns,
                         "imposes_v0": (w[m] * (fo.ir_salpen[m] > 0)).sum() / ns,
                         "imposes_dgfip": t.loc[membres, "foyers_imposes"].sum() / t.loc[membres, "foyers"][t.loc[membres, "foyers_imposes"].notna()].sum(),
                         "ir_salpen_Md": (w[m] * fo.ir_salpen[m]).sum() / 1e9 * nd / ns,
                         "ir_pfu_Md": (w[m] * fo.ir_pfu[m]).sum() / 1e9 * nd / ns,
                         "ir_bareme_Md": (w[m] * fo.ir_bareme[m]).sum() / 1e9 * nd / ns,
                         "ir_dgfip_Md": t.loc[membres, "impot"].sum() / 1e9})
    G = pd.DataFrame(lignes_g)
    tot = G[["ir_salpen_Md", "ir_pfu_Md", "ir_bareme_Md", "ir_dgfip_Md"]].sum()
    L = ["# Validation du lot 4 — population de foyers et impôt sur le revenu 2024", "",
         f"Généré par `tests/validation_M4.py` (échantillon de {F:.0%} des ménages du recensement 2022 : "
         f"{fo.index.size:,} foyers, {len(ind):,} personnes ; durée {time.time() - t0:.0f} s).".replace(",", " "), "",
         "## Couverture", "",
         "| Grandeur | Modèle | Référence |", "|---|---|---|",
         f"| Personnes des ménages ordinaires | {ind.poids.sum() / 1e6:.2f} M | 66,3 M (Insee, RP 2022) |",
         f"| Ménages | {ind.groupby('men').poids.first().sum() / 1e6:.2f} M | 30,9 M (Insee, RP 2022) |",
         f"| Foyers fiscaux | {w.sum() / 1e6:.2f} M | {ir.foyers.sum() / 1e6:.2f} M (DGFiP, dont 0,30 M de non-résidents) |",
         f"| Salaires déclarés | {(fo.salaires * w).sum() / 1e9:.0f} Md€ | {ir.salaires.sum() / 1e9:.0f} Md€ |",
         f"| Pensions déclarées | {(fo.pensions * w).sum() / 1e9:.0f} Md€ | {ir.pensions.sum() / 1e9:.0f} Md€ |", "",
         "Les montants par tranche sont calés en moyenne par foyer ; l'écart de masse reflète l'écart du nombre de foyers.", "",
         "## Test : impôt sur le revenu par tranche de RFR (grandeur non utilisée pour construire la population)", "",
         "Masses du modèle ramenées au nombre de foyers DGFiP de chaque tranche. Les « autres revenus » (RFR DGFiP moins RFR issu "
         "des salaires et pensions) sont de composition inconnue ; trois variantes les encadrent : V0 non imposables, "
         "V1 revenus de capitaux au prélèvement forfaitaire unique, V2 imposés au barème. Impôt au sens de l'IRCOM "
         "(barème, contribution sur les hauts revenus, prélèvement forfaitaire, seuils de recouvrement), avant réductions et crédits.", "",
         "| Tranche de RFR | Foyers modèle (M) | Foyers DGFiP (M) | Part imposée, V0 | Part imposée, V1 | Part imposée, DGFiP | IR V0 (Md€) | IR V1 (Md€) | IR V2 (Md€) | IR net DGFiP (Md€) |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in G.iterrows():
        L.append(f"| {r.tranche} | {r.foyers_sim_M:.2f} | {r.foyers_dgfip_M:.2f} | {r.imposes_v0:.0%} | {r.imposes_sim:.0%} | {r.imposes_dgfip:.0%} | "
                 f"{r.ir_salpen_Md:.1f} | {r.ir_pfu_Md:.1f} | {r.ir_bareme_Md:.1f} | {r.ir_dgfip_Md:.1f} |")
    L.append(f"| **Total** | {G.foyers_sim_M.sum():.2f} | {G.foyers_dgfip_M.sum():.2f} | | | | **{tot.ir_salpen_Md:.1f}** | **{tot.ir_pfu_Md:.1f}** | **{tot.ir_bareme_Md:.1f}** | **{tot.ir_dgfip_Md:.1f}** |")
    pfu_tot = (fo.pfu * w).sum() / 1e9 * ir.foyers.sum() / w.sum()
    cehr_tot = (fo.cehr * w).sum() / 1e9 * ir.foyers.sum() / w.sum()
    L += ["", f"Dont, en V1 : prélèvement forfaitaire unique {pfu_tot:.1f} Md€, contribution exceptionnelle sur les hauts revenus {cehr_tot:.1f} Md€.", "",
          "**Lecture.** L'impôt DGFiP est net des réductions et crédits d'impôt, que le modèle ne calcule pas encore (faute de données "
          "sur les dépenses ouvrant droit). Les crédits d'impôt représentent à eux seuls environ 9,7 Md€ (8,6 millions de foyers, "
          "1 132 € en moyenne, DGFiP, novembre 2025) ; les réductions s'y ajoutent. L'impôt du modèle avant réductions et crédits devrait donc dépasser "
          "l'impôt net DGFiP d'au moins 10 Md€.", ""]
    L += ["", "## Détail par tranche fine", "",
          "| Tranche | RFR moyen visé | RFR moyen OpenFisca | Part des autres revenus | IR moyen V1 | IR moyen V2 | IR net moyen DGFiP |",
          "|---|---|---|---|---|---|---|"]
    for k, r in tab.iterrows():
        if pd.isna(r.foyers_sim):
            continue
        L.append(f"| {k} | {r.rfr_moy_cible:,.0f} | {r.rfr_moy_openfisca:,.0f} | {r.part_autres:.0%} | {r.ir_moy_pfu:,.0f} | {r.ir_moy_bareme:,.0f} | {r.ir_moy_dgfip:,.0f} |".replace(",", " "))
    (RACINE / "outputs" / "validation_M4.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    fo.to_pickle("/tmp/fo_valid.pkl")


if __name__ == "__main__":
    main()
