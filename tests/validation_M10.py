"""Validation de M10 : réformes socio-fiscales simulées ménage par ménage (M4, OpenFisca) puis transmises au modèle
bouclé (M8).

Réformes de test :
  R1 — taux de la première tranche du barème de l'impôt sur le revenu porté de 11 % à 14 %. Repère externe : la baisse
       de 14 % à 11 % de 2020 a été chiffrée à environ 5 Md€ par le gouvernement (avec des ajustements de seuils et de
       décote non reproduits ici).
  R3 — barème non revalorisé : seuils, décote et plafond du quotient familial −2 %. Repères externes : une
       revalorisation de 2,1 % est chiffrée à près de 4 Md€ (projet de loi de finances pour 2027) ; le gel du barème
       de 2026 (face à une inflation de 0,9 %) à 1,9 Md€ (Bercy, jugé vraisemblable par le Haut Conseil des finances
       publiques).
  R2 — montant forfaitaire du RSA augmenté de 10 %.
Sortie : outputs/validation_M10.md
"""
from __future__ import annotations

import pathlib
import sys
import time
import warnings

import pandas as pd

warnings.filterwarnings("ignore")
RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
import m10_couplage as C  # noqa: E402
import m8_modele as M8  # noqa: E402

REFORMES = {
    "R1": ("Impôt sur le revenu : première tranche de 11 % à 14 %",
           {"debut": "2024-01-01", "parametres": {"impot_revenu.bareme_ir_depuis_1945.bareme.brackets[1].rate": 0.14}}, ("ir",)),
    "R3": ("Impôt sur le revenu : barème non revalorisé (seuils des tranches, décote et plafond du quotient familial −2 %, "
           "soit l'équivalent d'un gel face à une indexation de 2 %)",
           {"debut": "2024-01-01", "parametres": {
               **{f"impot_revenu.bareme_ir_depuis_1945.bareme.brackets[{i}].threshold": {"facteur": 1 / 1.02} for i in (1, 2, 3, 4)},
               "impot_revenu.calcul_impot_revenu.plaf_qf.decote.seuil_celib": {"facteur": 1 / 1.02},
               "impot_revenu.calcul_impot_revenu.plaf_qf.decote.seuil_couple": {"facteur": 1 / 1.02},
               "impot_revenu.calcul_impot_revenu.plaf_qf.plafond_avantages_procures_par_demi_part.general": {"facteur": 1 / 1.02}}}, ("ir",)),
    "R2": ("RSA : montant forfaitaire +10 %",
           {"debut": "2024-10-01", "parametres": {"prestations_sociales.solidarite_insertion.minima_sociaux.rsa.rsa_m.montant_de_base_du_rsa": {"facteur": 1.1}}},
           ("prest",)),
}


def main():
    t0 = time.time()
    base = C.evaluer("base", None)
    L = ["# Validation de M10 — réformes socio-fiscales de la microsimulation au modèle bouclé (version 0.1)", "",
         "Généré par `tests/validation_M10.py`. Effets statiques sur les revenus 2024 (impôt : 2 % des ménages ; prestations : "
         "deux sous-échantillons de 0,5 %), puis effets macroéconomiques dans M8 (base 2022, compte central avec fermeture d'offre).", "",
         f"Législation actuelle : impôt net {base['ir_net'] / 1e9:.1f} Md€ ; droits simulés RSA {base['rsa'] / 1e9:.1f}, prime d'activité "
         f"{base['ppa'] / 1e9:.1f}, allocations familiales {base['af'] / 1e9:.1f}, aides au logement {base['aide_logement'] / 1e9:.1f} Md€.", ""]
    mod = M8.Modele(2022)
    ans = range(2023, 2031)
    central = mod.simuler(ans, M8.exogenes_projection(mod, ans))
    for code, (titre, ref, calc) in REFORMES.items():
        r = C.evaluer(code, ref, calculer=calc)
        mm = C.mesure_pour_m8(base, r)
        D = C.distribution(base, r)
        v = mod.simuler(ans, M8.exogenes_projection(mod, ans, mesure_menages=mm))
        L += [f"## {code} — {titre}", "", "### Effet statique (revenus 2024)", "",
              f"- Impôt sur le revenu net : {mm['impots'] / 1e3:+.2f} Md€ ;",
              f"- prestations versées (droits × recours apparent) : {mm['prestations'] / 1e3:+.2f} Md€ "
              f"(droits : " + ", ".join(f"{k} {(r[k] - base[k]) / 1e9:+.2f}" for k in C.PRESTATIONS) + " Md€).", "",
              "| Décile de niveau de vie | Niveau de vie moyen (€/UC/an, approché) | Variation (€/UC/an) | Variation (%) | Part de gagnants | Part de perdants |",
              "|---|---|---|---|---|---|"]
        for d_, x in D.iterrows():
            L.append(f"| {d_} | {x.niveau_de_vie_moyen:,.0f} | {x.variation_euros_par_uc:+.0f} | {x.variation_pct:+.2f} % | {x.part_gagnants:.0%} | {x.part_perdants:.0%} |".replace(",", " "))
        L += ["", "### Effets macroéconomiques (écarts au compte central)", "",
              "| Année | PIB | Consommation | Emploi (milliers) | Prix conso. | Revenu disponible | Solde public (pt de PIB) | Dette (pt de PIB) |",
              "|---|---|---|---|---|---|---|---|"]
        for t in (2024, 2026, 2030):
            e = lambda c: (v[c][t] / central[c][t] - 1) * 100  # noqa: E731
            L.append(f"| {t} | {e('pib'):+.2f} % | {e('c'):+.2f} % | {v.emploi[t] - central.emploi[t]:+.0f} | {e('pc'):+.2f} % | {e('rdb'):+.2f} % | "
                     f"{v.solde_pib[t] - central.solde_pib[t]:+.2f} | {v.dette_pib[t] - central.dette_pib[t]:+.2f} |")
        L.append("")
    L += ["## Limites", "", "- Effets statiques : pas de réaction de l'offre de travail ni du recours aux prestations à la réforme.",
          "- Niveau de vie approché à partir du revenu fiscal de référence (avant CSG, hors revenus exonérés), et non du revenu disponible de l'Insee.",
          "- Prestations : erreur d'échantillonnage de l'ordre de 2 % (deux sous-échantillons) ; les petites réformes de prestations sont donc imprécises.",
          "- Le sens macro → micro (revalorisation des revenus de M4 par M8) n'est pas encore fait : le montant statique est indexé sur le PIB nominal.", "",
          f"Durée : {time.time() - t0:.0f} s.", ""]
    (RACINE / "outputs" / "validation_M10.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
