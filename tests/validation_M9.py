"""Validation de M9 (activité des seniors et retraites) et variantes de règles de retraite dans le modèle bouclé M8.

1. Taux d'activité par tranche d'âge et sexe : estimation 2003-2019, comparaison 2003-2025 (2020-2025 hors échantillon,
   période du relèvement de l'AOD de 62 ans à 62 ans et 9 mois).
2. Retraités de droit direct et masse des pensions : calage en 2015, comparaison 2006-2024.
3. Variantes de règle (base 2022, 2023-2035) : retour à 62 ans ; législation de 2023 sans suspension ; 65 ans.
Sortie : outputs/validation_M9.md
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
import m8_modele as M8  # noqa: E402
import m9_retraites as R  # noqa: E402


def main():
    t0 = time.time()
    act = R.ActiviteSeniors(2019)
    k = act.estimer_part_emploi()
    P = R.Pensions(act, 2015)
    L = ["# Validation de M9 — activité des seniors et retraites (version 0.1)", "", "Généré par `tests/validation_M9.py`.", "",
         "## 1. Taux d'activité par âge (enquête Emploi) : observé / simulé, en %", "",
         "Paramètres estimés sur 2003-2019 ; 2020-2025 hors échantillon. " + " ; ".join(
             f"{'femmes' if sx == 'F' else 'hommes'} : sorties précoces e0 = {th[0]:.2f}, tendance {th[1] * 100:+.1f} pt/an, activité relative à l'AOD s = {th[2]:.2f}, décroissance k = {th[3]:.2f} ; erreur quadratique moyenne {act.diag[sx]['rmse'] * 100:.1f} pt"
             for sx, th in act.theta.items()) + ".", "",
         "| Sexe | Âge | 2005 | 2010 | 2015 | 2019 | 2021 | 2023 | 2024 | 2025 |", "|---|---|---|---|---|---|---|---|---|---|"]
    o = act.obs
    for sx in ("F", "M"):
        for a0, a1 in R.TRANCHES:
            cel = []
            for t in (2005, 2010, 2015, 2019, 2021, 2023, 2024, 2025):
                v = o[(o.sexe == sx) & (o.a0 == a0) & (o.annee == t)].activite
                cel.append(f"{v.iloc[0] * 100:.0f} / {act.tranche(sx, t, a0, a1) * 100:.0f}" if len(v) else "—")
            L.append(f"| {'Femmes' if sx == 'F' else 'Hommes'} | {a0}-{a1} | " + " | ".join(cel) + " |")
    L += ["", f"Part des actifs supplémentaires de 60-64 ans en emploi (Δ taux d'emploi / Δ taux d'activité, 2010-2019) : {k:.2f}.", "",
          "## 2. Retraités de droit direct et masse des pensions (calage en 2015)", "",
          "| Année | Retraités observés (M) | Simulés | Masse observée (Md€) | Simulée | Écart |", "|---|---|---|---|---|---|"]
    for t in range(2008, 2025, 2):
        nb, m = P.masse(t)
        L.append(f"| {t} | {P.obs.retraites.get(t, np.nan) / 1e6:.2f} | {nb / 1e6:.2f} | {P.obs.masse_droit_direct[t] / 1e3:.0f} | {m / 1e9:.0f} | {(m / 1e9 / (P.obs.masse_droit_direct[t] / 1e3) - 1) * 100:+.1f} % |")
    L += ["", "Sources : Eurostat `spr_pns_ben` (OLD_TOT, y compris les retraités résidant à l'étranger), `spr_exp_pens` (OLD) ; 2024 provisoire.", ""]
    # 3. variantes
    mod = M8.Modele(2022)
    ans = range(2023, 2036)
    base = R.liens_m8(mod, ans, "actuelle", "actuelle", act, P, k)
    central = mod.simuler(ans, M8.exogenes_projection(mod, ans, population_active=base["population_active"]))
    L += ["## 3. Variantes de règle de retraite dans le modèle bouclé (écarts à la législation actuelle)", "",
          "Compte central : législation actuelle (LFSS 2026), population active issue de M9. Les pensions des variantes sont "
          "calculées avec les prix et salaires simulés par M8 dans le compte central.", "",
          "PIB, modèle de demande : M8 tel quel ; les seniors maintenus en emploi perçoivent un salaire (revenu, cotisations) mais "
          "la production reste déterminée par la demande. PIB, borne offre : à long terme, la production suit l'emploi "
          "(capital ajusté, productivité moyenne) : + Δemploi / emploi ; le solde public gagne alors le taux de prélèvements "
          "apparent sur ce surcroît de PIB. La réalité se situe entre les deux, plus près de la borne offre à long terme.", ""]
    for nom, regle in (("Retour à 62 ans", "2010"), ("Loi de 2023 sans suspension", "2023"), ("65 ans (+3 mois par génération dès 1964)", "65")):
        l = R.liens_m8(mod, ans, regle, "actuelle", act, P, k, central=central)
        r = mod.simuler(ans, M8.exogenes_projection(mod, ans, **l))
        L += [f"### {nom}", "", "| Année | AOD (génération ayant 63 ans) | Actifs (milliers) | Emplois seniors directs | Emploi total | Chômage (pt) | PIB, modèle de demande | PIB, borne offre | Pensions (Md€) | Solde public, modèle (pt de PIB) | Solde, borne offre | Dette, modèle (pt de PIB) |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for t in (2027, 2030, 2035):
            g = int(t - 63)
            dpib = (r.pib[t] / central.pib[t] - 1) * 100
            doffre = dpib + l["emploi_additionnel"][t] / central.emploi[t] * 100
            taux_prelev = central.recettes[t] / (mod.macro.pib_cp[2022] * 1.0) / (central.pib[t] / mod.macro.pib[2022] * central.pc[t] / mod.macro.p_c[2022])
            dsolde_offre = r.solde_pib[t] - central.solde_pib[t] + (doffre - dpib) * taux_prelev
            L.append(f"| {t} | {R.aod(g, regle):.2f} ({g}) | {l['population_active'][t] - base['population_active'][t]:+.0f} | "
                     f"{l['emploi_additionnel'][t]:+.0f} | {r.emploi[t] - central.emploi[t]:+.0f} | {r.chomage[t] - central.chomage[t]:+.2f} | "
                     f"{dpib:+.2f} % | {doffre:+.2f} % | {l['ajust_prestations'][t] / 1e3:+.1f} | {r.solde_pib[t] - central.solde_pib[t]:+.2f} | {dsolde_offre:+.2f} | {r.dette_pib[t] - central.dette_pib[t]:+.2f} |")
        L.append("")
    L += [f"Durée : {time.time() - t0:.0f} s.", ""]
    (RACINE / "outputs" / "validation_M9.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
