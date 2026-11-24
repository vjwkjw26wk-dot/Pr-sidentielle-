"""Phase 4.3, chantier B : test isolé du compte des sociétés (M21) — moteurs observés (EBE, VA, FBCF de S11, PIB nominal,
taux, taux apparent d'IS), comportements simulés (intérêts, dividendes, dette). Sépare les erreurs propres au compte de
celles héritées du reste du modèle (EBE, investissement)."""
import pathlib, sys, warnings
warnings.filterwarnings("ignore")
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src")]
import numpy as np, pandas as pd
import m21_societes as S, m7_series as S7
pd.set_option("display.width", 250)
d = S.donnees()
pibn = S7.macro().pib_cp


def isole(B, fin, variante=None, actifs_obs=False):
    c = S.CompteSocietes(B, variante); c.initialiser()
    rows = {}
    for t in range(B + 1, fin + 1):
        o = c.compte(t, d.ebe[t] / d.ebe[B], pibn[t] / pibn[B], d.va[t] / d.va[B], d.fbcf[t] / d.fbcf[B], d.taux_long[t],
                     d.taux_is_app[t] / d.taux_is_app[B], 1.0, taux_court=d.taux_court[t])
        rows[t] = {"int. versés": (o["interets_verses_s11"] - d.int_verses[t]) / 1e3, "int. reçus": (o["interets_recus_s11"] - d.int_recus[t]) / 1e3,
                   "int. nets": (o["interets_s11"] - d.int_nets[t]) / 1e3, "IS %": 100 * (o["is_s11"] / d.is_[t] - 1),
                   "div. distr. %": 100 * (o["dividendes_distribues"] / d.div_final[t] - 1),
                   "épargne %": 100 * (o["epargne_s11"] / d.b8g[t] - 1), "B9": (o["capacite_s11"] - d.b9[t]) / 1e3,
                   "dette %": 100 * (o["dette_s11"] / d.dette[t] - 1),
                   "div. ménages (Md€)": (c.part_men * o["dividendes_distribues"] - d.men_d42_recus[t]) / 1e3}
    return pd.DataFrame(rows).T


if __name__ == "__main__":
    for B, fin in ((2010, 2019), (2014, 2024), (2019, 2024)):
        print(f"\n=== Compte isolé, origine {B} (Md€ ou %, simulé − observé)")
        print(isole(B, fin).round(1).to_string())
    print("\nVariante μ = 0,35 et lissage des dividendes 0,3 (origine 2019)")
    print(isole(2019, 2024, {"mu_taux": 0.35, "div_lissage": 0.3}).round(1).to_string())
    print("\nActifs liquides / PIB nominal :", (d.actifs_liquides / pibn).loc[[2000, 2005, 2010, 2014, 2019, 2022, 2024]].round(2).to_dict())
