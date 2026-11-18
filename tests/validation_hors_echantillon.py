"""Validation historique hors échantillon et stabilité des coefficients (contre-expertise, version 0.6).

1. Rétrosimulations à origines multiples : coefficients estimés jusqu'à l'année d'origine (2019 au plus, la crise
   sanitaire étant exclue des estimations), exogènes observées, simulation sur 2 à 4 ans. Les variables endogènes
   sont comparées aux observations et à deux modèles de référence simples (prolongement de la croissance moyenne des
   cinq années précédentes ; AR(1) de la croissance estimé jusqu'à l'origine).
2. Stabilité des coefficients : réestimation des équations principales sur plusieurs fenêtres.
Variables injectées (exogènes observées, donc non validées) : demande et prix mondiaux, prix d'importation par produit,
consommation publique, FBCF hors branches et hors ménages, population active, chômage structurel, taux long, taux d'IS,
prestations en volume. Variables prédites : PIB, consommation, investissement, exportations, importations, emploi,
chômage, prix à la consommation, salaires, solde et dette publics.
Sortie : outputs/validation_hors_echantillon.md et .json.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pandas as pd

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
import m7_equations as E  # noqa: E402
import m7_series as S  # noqa: E402
import m8_modele as M  # noqa: E402

ORIGINES = [(2012, 4, "crise des dettes souveraines et reprise"), (2014, 4, "période calme (estimation jusqu'en 2014)"),
            (2016, 3, "période calme"), (2019, 3, "crise sanitaire (rupture de régime)"), (2021, 3, "choc d'inflation 2022-2023")]
VARS = [("pib", "pib"), ("c", "c"), ("fbcf", "fbcf"), ("x", "x"), ("m", "m"), ("emploi", None), ("pc", "p_c")]


def obs_series(mod, k):
    m = mod.macro
    if k == "emploi":
        return mod.emp.emploi
    if k == "pc":
        return m.p_c
    return m[k]


def croissances(s, t0, h):
    return np.array([(s[t] / s[t - 1] - 1) * 100 for t in range(t0 + 1, t0 + h + 1)])


def main():
    out, L = {}, ["# Validation historique hors échantillon (version 0.6)", "",
                  "Erreur quadratique moyenne (RMSE, points de pourcentage) des taux de croissance annuels simulés, comparée à deux "
                  "modèles simples : « naïf » (croissance moyenne des cinq années précédant l'origine) et AR(1) (croissance "
                  "annuelle régressée sur sa valeur passée, estimée jusqu'à l'origine). Un ratio modèle / naïf inférieur à 1 "
                  "indique un gain de prévision conditionnelle. Le modèle bénéficie des exogènes observées (avantage "
                  "informationnel que n'ont pas les modèles simples) : la comparaison mesure la valeur ajoutée des mécanismes "
                  "conditionnellement à ces exogènes, non une capacité de prévision inconditionnelle.", ""]
    for B, h, lib in ORIGINES:
        fin_est = min(B, 2019)
        try:
            mod = M.Modele(B, fin_est)
        except Exception as e:  # noqa: BLE001
            L += [f"## Origine {B} : non disponible ({e})", ""]
            continue
        h = min(h, 2024 - B)
        ans = range(B + 1, B + h + 1)
        r = mod.simuler(ans, M.exogenes_observes(mod, ans))
        res = {}
        for k, _ in VARS:
            o = obs_series(mod, k)
            sim = pd.concat([pd.Series({B: float(o[B])}), r[k] if k != "pc" else r.pc]).astype(float)
            gs, go = croissances(sim, B, h), croissances(o, B, h)
            moy5 = np.mean([(o[t] / o[t - 1] - 1) * 100 for t in range(B - 4, B + 1)])
            g_hist = pd.Series({t: (o[t] / o[t - 1] - 1) * 100 for t in range(1997, fin_est + 1) if t not in (2020, 2021)})
            x, y = g_hist.shift(1).dropna(), g_hist.loc[g_hist.shift(1).dropna().index]
            a, b = np.polyfit(x.values, y.values, 1)
            ar, g = [], (o[B] / o[B - 1] - 1) * 100
            for _ in range(h):
                g = b + a * g
                ar.append(g)
            rm = lambda e: float(np.sqrt(np.mean(np.square(e))))  # noqa: E731
            res[k] = {"rmse_modele": rm(gs - go), "rmse_naif": rm(moy5 - go), "rmse_ar1": rm(np.array(ar) - go),
                      "erreur_niveau_fin": float((sim[B + h] / o[B + h] - 1) * 100), "obs": go.tolist(), "sim": gs.tolist()}
        res["chomage"] = {"erreur_fin_points": float(r.chomage[B + h] - mod.macro.chomage[B + h])}
        out[B] = res
        L += [f"## Origine {B} ({lib}) : estimation jusqu'en {fin_est}, simulation {B + 1}-{B + h}", "",
              "| Variable | RMSE modèle | RMSE naïf | RMSE AR(1) | Modèle / naïf | Erreur de niveau en fin de période |", "|---|---|---|---|---|---|"]
        for k, _ in VARS:
            d = res[k]
            L.append(f"| {k} | {d['rmse_modele']:.2f} | {d['rmse_naif']:.2f} | {d['rmse_ar1']:.2f} | {d['rmse_modele'] / max(d['rmse_naif'], 1e-9):.2f} | {d['erreur_niveau_fin']:+.1f} % |")
        L += [f"| chômage (points, fin) | | | | | {res['chomage']['erreur_fin_points']:+.1f} |", ""]
        print(B, "ok", flush=True)
    # stabilité des coefficients
    m = S.macro()
    fen = [(1997, 2007), (1997, 2012), (1997, 2019), (2003, 2019), (1997, 2024)]
    suivis = {"consommation": ["dlrdb", "ecart_1"], "importations": ["dld", "dlprel", "lm_1"], "exportations": ["dldm", "dlprel"],
              "salaires": ["dlpc", "ecm_1"], "investissement_snf": ["dlq", "lcu_1"]}
    stab = {}
    L += ["## Stabilité des coefficients (estimation sur différentes fenêtres)", "",
          "Coefficient (erreur-type). La fenêtre 1997-2024 inclut 2020-2022 sans traitement particulier : elle illustre la sensibilité "
          "aux chocs exceptionnels, elle n'est pas utilisée par le modèle.", "",
          "| Équation | Coefficient | " + " | ".join(f"{a}-{b}" for a, b in fen) + " |", "|---|---|" + "---|" * len(fen)]
    fonctions = {"consommation": E.consommation, "importations": E.importations, "exportations": E.exportations, "salaires": E.salaires,
                 "investissement_snf": E.investissement_snf}
    for eq, coefs in suivis.items():
        for c in coefs:
            cells = []
            for a, b in fen:
                try:
                    r = (fonctions[eq](S.panel_branches(), m, a, b) if eq == "salaires" else fonctions[eq](m, a, b)).res
                    cells.append(f"{r.params[c]:+.2f} ({r.bse[c]:.2f})")
                    stab.setdefault(eq, {}).setdefault(c, {})[f"{a}-{b}"] = [float(r.params[c]), float(r.bse[c])]
                except Exception as e:  # noqa: BLE001
                    cells.append("n.d.")
            L.append(f"| {eq} | {c} | " + " | ".join(cells) + " |")
    (RACINE / "outputs" / "validation_hors_echantillon.json").write_text(json.dumps({"retro": out, "stabilite": stab}, default=float, indent=1))
    (RACINE / "outputs" / "validation_hors_echantillon.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
