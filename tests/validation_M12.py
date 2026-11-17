"""Phase 7 — Incertitude des variantes (Monte-Carlo) et comparaison des multiplicateurs à la littérature.

Variantes (base 2022, fermeture d'offre tirée entre 0,2 et 0,5) :
  - consommation publique +1 point de PIB ;
  - taux d'IS de 25,8 % à 20 % ;
  - prix de l'énergie importée +20 % ;
  - impôt sur le revenu : première tranche de 11 % à 14 % (+13,6 Md€ statiques, M10) ;
  - âge d'ouverture des droits porté à 65 ans (M9 ; population active et pensions de la règle, calculées une fois).
Sortie : outputs/validation_M12.md (+ outputs/monte_carlo_M12.csv)
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
import m12_incertitude as MC  # noqa: E402
import m8_modele as M8  # noqa: E402
import m9_retraites as R  # noqa: E402

N = int(sys.argv[1]) if len(sys.argv) > 1 else 40


def variantes(mod, ans):
    g_part = mod.T.Fd.loc[mod.P, ["P3_S13", "P3_S15"]].values.sum() + mod.T.Fm.loc[mod.P, ["P3_S13", "P3_S15"]].values.sum()
    act = R.ActiviteSeniors()
    P = R.Pensions(act)
    k = act.estimer_part_emploi()
    central = mod.simuler(ans, M8.exogenes_projection(mod, ans))
    base9 = R.liens_m8(mod, ans, "actuelle", "actuelle", act, P, k)
    l65 = R.liens_m8(mod, ans, "65", "actuelle", act, P, k, central=central)

    def g(mod, ans, rho):
        v = M8.exogenes_projection(mod, ans, fermeture_offre=rho)
        v.conso_publique = v.conso_publique * pd.Series({t: (1 + 0.01 * mod.macro.pib_cp[2022] / g_part if t >= 2024 else 1.0) for t in v.conso_publique.index})
        return v

    def is_(mod, ans, rho):
        return M8.exogenes_projection(mod, ans, fermeture_offre=rho,
                                      taux_is=pd.Series({t: (M8.S.taux_is().get(t, 25.83) if t < 2024 else 20.0) for t in range(2019, max(ans) + 1)}))

    def ene(mod, ans, rho):
        v = M8.exogenes_projection(mod, ans, fermeture_offre=rho)
        for p in ("CPA_B", "CPA_C19", "CPA_D"):
            v.prix_import[p] = [x * (1.2 if t >= 2024 else 1.0) for t, x in zip(v.prix_import.index, v.prix_import[p])]
        return v

    def ir(mod, ans, rho):
        return M8.exogenes_projection(mod, ans, fermeture_offre=rho, mesure_menages={"impots": 13550.0, "prestations": 0.0, "annee": 2024})

    def ret(mod, ans, rho):
        return M8.exogenes_projection(mod, ans, fermeture_offre=rho, population_active=l65["population_active"],
                                      ajust_prestations=l65["ajust_prestations"])
    # pour la retraite, le compte central doit utiliser la population active de M9 : variante relative à base9
    def ret_central(mod, ans, rho):
        return M8.exogenes_projection(mod, ans, fermeture_offre=rho, population_active=base9["population_active"])
    return {"Consommation publique +1 pt de PIB": g, "IS de 25,8 % à 20 %": is_, "Énergie importée +20 %": ene,
            "IR : première tranche 11 % → 14 %": ir, "Âge légal 65 ans": (ret, ret_central)}, ret_central


def main():
    t0 = time.time()
    mod = M8.Modele(2022)
    ans = range(2023, 2031)
    V, ret_central = variantes(mod, ans)
    df = MC.monte_carlo(mod, ans, V, n=N)
    df.to_csv(RACINE / "outputs" / "monte_carlo_M12.csv", index=False)
    c, q = MC.resume(df)
    L = ["# Phase 7 — Incertitude des variantes et comparaison aux modèles de référence", "",
         f"Généré par `tests/validation_M12.py` : {N} tirages Monte-Carlo (paramètres estimés tirés dans leur loi "
         "estimée ; paramètres calibrés tirés dans leur plage), base 2022. Valeur centrale [intervalle à 90 %].", "",
         "Pour l'âge légal, le compte de référence de chaque tirage utilise la population active de M9 en législation actuelle.", ""]
    for var in V:
        L += [f"## {var}", "", "| Horizon | PIB (%) | Emploi (milliers) | Prix (%) | Solde public (pt de PIB) | Dette (pt de PIB) |", "|---|---|---|---|---|---|"]
        for t in sorted(df.annee.unique()):
            cel = []
            for col, f in (("pib", "{:+.2f}"), ("emploi", "{:+.0f}"), ("prix", "{:+.2f}"), ("solde", "{:+.2f}"), ("dette", "{:+.2f}")):
                cel.append(f"{f.format(c.loc[(var, t), col])} [{f.format(q.loc[(var, t), (col, 0.05)])} ; {f.format(q.loc[(var, t), (col, 0.95)])}]")
            L.append(f"| {t} | " + " | ".join(cel) + " |")
        L.append("")
    L += [f"Durée : {time.time() - t0:.0f} s.", ""]
    (RACINE / "outputs" / "validation_M12.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
