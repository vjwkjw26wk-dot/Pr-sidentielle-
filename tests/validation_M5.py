"""Validation du bloc productif M5 (tableaux entrées-sorties, modèle de prix et de quantités).

1. Identités comptables de chaque tableau 2010-2022 (équilibres ressources-emplois et coûts de production).
2. Test rétrospectif du modèle de prix, année par année (2012-2022) : avec les coefficients techniques de N−1,
   on calcule les prix de production de N par produit à partir
   (a) des seuls prix d'importation observés en N, valeur ajoutée unitaire inchangée (transmission pure des coûts
       importés) ;
   (b) des prix d'importation et des prix de la valeur ajoutée observés en N (cohérence du modèle et stabilité des
       coefficients techniques ; la valeur ajoutée unitaire sera rendue endogène par les équations du lot 7).
   Comparaison aux prix de production observés (tableaux aux prix courants et aux prix de l'année précédente).
3. Test rétrospectif du modèle de quantités : production de N par produit prévue par la demande finale intérieure
   observée de N et les coefficients de N−1, comparée à la production observée (volumes aux prix de N−1).
4. Illustrations : contenu en importations, multiplicateurs, transmission d'une hausse de 50 % des prix de l'énergie
   importée (2021).
Sortie : outputs/validation_M5.md
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pandas as pd

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
import m5_productif as m5  # noqa: E402

ANNEES = list(range(2012, 2023))
NOMS = {"CPA_B": "Industries extractives (dont pétrole brut, gaz)", "CPA_C19": "Cokéfaction et raffinage",
        "CPA_D": "Électricité, gaz, vapeur", "CPA_C24": "Métallurgie", "CPA_C20": "Chimie", "CPA_C23": "Minéraux non métalliques",
        "CPA_A01": "Agriculture", "CPA_C10-12": "Industries agroalimentaires", "CPA_H49": "Transports terrestres",
        "CPA_C29": "Automobile", "CPA_F": "Construction", "CPA_C17": "Papier-carton", "CPA_C30": "Autres matériels de transport (aéronautique, naval, ferroviaire)",
        "CPA_C27": "Équipements électriques", "CPA_C22": "Caoutchouc et plastiques", "CPA_H51": "Transport aérien", "CPA_C28": "Machines et équipements",
        "CPA_C26": "Produits informatiques, électroniques et optiques", "CPA_C21": "Pharmacie", "CPA_H50": "Transport par eau"}


def deflateur(t_cour: m5.TableES, t_pyp: m5.TableES, champ) -> pd.Series:
    return champ(t_cour) / champ(t_pyp).replace(0, np.nan) - 1


def main():
    T = m5.charger_tables()
    L = ["# Validation du bloc productif M5", "",
         "Source : Eurostat, tableaux entrées-sorties symétriques de la France (64 produits, aux prix de base), 2010-2022 ; "
         "prix courants et prix de l'année précédente. Généré par `tests/validation_M5.py`.", "",
         "## 1. Identités comptables", "", "| Année | Produits | Production (Md€) | Valeur ajoutée (Md€) | Importations (Md€) | Écart max. ressources-emplois (M€) | Écart max. coûts-production (M€) |",
         "|---|---|---|---|---|---|---|"]
    for a in range(2010, 2023):
        t = m5.TableES(T, a)
        I = t.identites()
        L.append(f"| {a} | {len(t.actifs)} | {t.x.sum() / 1e3:,.0f} | {t.va.B1G.sum() / 1e3:,.0f} | {t.m.sum() / 1e3:,.0f} | "
                 f"{I.iloc[:, 0].abs().max():.1f} | {I.iloc[:, 1].abs().max():.1f} |".replace(",", " "))
    L += ["", "Les écarts sont des arrondis de publication (≤ 2 M€ sur des productions de plusieurs milliards).", "",
          "## 2. Test rétrospectif du modèle de prix (coefficients de N−1, chocs observés en N)", "",
          "Erreur absolue moyenne sur les 64 produits, pondérée par la production, en points de pourcentage de variation annuelle de prix ; "
          "corrélation entre variations prévues et observées.", "",
          "| Année | Prix de production observés, moyenne pondérée | (a) Imports seuls : prévision moyenne | (a) erreur abs. moyenne | (a) corrélation | (b) Imports + VA : erreur abs. moyenne | (b) corrélation | Prix à la consommation des ménages : observé | (b) prévu |",
          "|---|---|---|---|---|---|---|---|---|"]
    lignes_2022 = None
    for a in ANNEES:
        prec = m5.TableES(T, a - 1)
        cour, pyp = m5.TableES(T, a), m5.TableES(T, a, "pyp")
        P = prec.actifs
        ip = m5.indices_prix(T, a).reindex(P)
        obs = ip.prix_production
        pm = ip.prix_import.fillna(0)
        dva = (cour.va.B1G / pyp.va.B1G.replace(0, np.nan) - 1).reindex(P).fillna(0)
        # (b) : prix de la VA appliqué à la VA ; les impôts sur produits suivent le prix de production (approximation)
        pa = prec.prix(choc_import=pm) - 1
        pb = prec.prix(choc_import=pm, choc_va=dva) - 1
        w = cour.x[P] / cour.x[P].sum()
        ok = obs.notna()
        mae = lambda p: float((w[ok] * (p[ok] - obs[ok]).abs()).sum() / w[ok].sum() * 100)  # noqa: E731
        cor = lambda p: float(np.corrcoef(p[ok], obs[ok])[0, 1])  # noqa: E731
        c_cour = (cour.Fd.loc[P, "P3_S14"] + cour.Fm.loc[P, "P3_S14"]).sum()
        c_pyp = pyp.F.loc[P, "P3_S14"].sum()
        cpi_obs = c_cour / c_pyp - 1
        cpi_b = prec.prix_consommation(pb + 1, pm) - 1
        L.append(f"| {a} | {(w * obs).sum() * 100:+.1f} % | {(w * pa).sum() * 100:+.1f} % | {mae(pa):.1f} | {cor(pa):.2f} | {mae(pb):.1f} | {cor(pb):.2f} | {cpi_obs * 100:+.1f} % | {cpi_b * 100:+.1f} % |")
        if a == 2022:
            lignes_2022 = pd.DataFrame({"obs": obs, "a": pa, "b": pb, "imp": pm})
    L += ["", "Détail 2022 (choc énergétique), produits les plus touchés : variation des prix de production, %.", "",
          "| Produit | Prix d'importation | Observé | (a) Imports seuls | (b) Imports + VA |", "|---|---|---|---|---|"]
    for p in ["CPA_C19", "CPA_D", "CPA_B", "CPA_C24", "CPA_C20", "CPA_C23", "CPA_C17", "CPA_A01", "CPA_C10-12", "CPA_H49", "CPA_C29", "CPA_F"]:
        r = lignes_2022.loc[p]
        L.append(f"| {NOMS[p]} | {r.imp * 100:+.1f} | {r.obs * 100:+.1f} | {r.a * 100:+.1f} | {r.b * 100:+.1f} |")
    L += ["", "## 3. Test rétrospectif du modèle de quantités", "",
          "Production en volume de N (aux prix de N−1) prévue par x = (I − Ad,N−1)⁻¹ · fd,N, la demande finale intérieure de N étant "
          "déflatée par les prix de production observés. Erreur absolue moyenne pondérée sur les 64 produits, en % de la production.", "",
          "| Année | Croissance observée du volume de production | Prévue | Erreur abs. moyenne par produit |", "|---|---|---|---|"]
    for a in ANNEES:
        prec = m5.TableES(T, a - 1)
        cour, pyp = m5.TableES(T, a), m5.TableES(T, a, "pyp")
        P = prec.actifs
        defl = (cour.x / pyp.x.replace(0, np.nan)).reindex(P)
        fd = (cour.Fd.loc[P].sum(axis=1) / defl).fillna(0)
        xprev = prec.quantites(fd)
        xobs = pyp.x[P]
        w = xobs / xobs.sum()
        err = float((w * ((xprev - xobs) / xobs).abs()).sum() * 100)
        L.append(f"| {a} | {(xobs.sum() / prec.x[P].sum() - 1) * 100:+.1f} % | {(xprev.sum() / prec.x[P].sum() - 1) * 100:+.1f} % | {err:.1f} % |")
    t21 = m5.TableES(T, 2021)
    ci = t21.contenu_importe().sort_values(ascending=False)
    Lm = t21.leontief().sum(axis=0).sort_values(ascending=False)
    choc = pd.Series({p: 0.5 for p in m5.ENERGIE})
    p50 = t21.prix(choc_import=choc) - 1
    w = t21.x[t21.actifs] / t21.x[t21.actifs].sum()
    L += ["", "## 4. Illustrations (tableau 2021)", "",
          "Contenu en importations par euro de demande finale (direct et indirect), produits les plus dépendants :", "",
          "| Produit | Importations induites par € |", "|---|---|"]
    for p, v in ci.head(8).items():
        L.append(f"| {NOMS.get(p, p)} | {v:.2f} |")
    L += ["", f"Contenu moyen en importations de la demande finale intérieure : "
          f"{(ci * (t21.Fd.loc[ci.index].sum(axis=1))).sum() / t21.Fd.loc[ci.index].sum(axis=1).sum():.2f} € par €.", "",
          "Hausse de 50 % des prix de l'énergie importée (produits B, C19, D), coefficients et valeur ajoutée unitaire fixes :", "",
          f"- prix de production, moyenne pondérée : {(w * p50).sum() * 100:+.1f} % ;",
          f"- prix à la consommation des ménages : {(t21.prix_consommation(p50 + 1, choc) - 1) * 100:+.1f} % ;",
          "- produits les plus touchés : " + " ; ".join(f"{NOMS.get(p, p)} {v * 100:+.1f} %" for p, v in p50.sort_values(ascending=False).head(5).items()) + ".", ""]
    (RACINE / "outputs" / "validation_M5.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
