"""Livrables Excel de la phase 3.1 :
- phase31/livrables/distribution_effets_v08.xlsx : gagnants et perdants par stratégie, configuration, horizon et groupe ;
- phase31/livrables/comparaison_v07_v08.xlsx : écarts de résultats v0.7 / v0.8 et leurs causes, registre des
  paramètres, backtest."""
import json
import pathlib
import re

import pandas as pd

R = pathlib.Path(__file__).resolve().parents[1]
RES = R / "phase31" / "resultats"
OUT = R / "phase31" / "livrables"
OUT.mkdir(exist_ok=True)
STRAT = ["S1_protection", "S2_emploi", "S3_productivite", "S4_redressement", "S5_global", "v06_A", "v06_B", "v06_C", "v06_D", "v06_R"]


def mise_en_forme(w):
    for ws in w.book.worksheets:
        for col in ws.columns:
            ws.column_dimensions[col[0].column_letter].width = min(55, max(9, max(len(str(c.value or "")) for c in col[:80]) + 2))
        for row in ws.iter_rows(min_row=2):
            for c in row:
                if isinstance(c.value, float):
                    c.number_format = "0.00"
        ws.freeze_panes = "A2"


def distribution():
    lignes, glob = [], []
    for k in STRAT:
        p = RES / f"strategies_v08_{k}.json"
        if not p.exists():
            continue
        v = json.loads(p.read_text())
        for cfg in ("central", "faible", "fort"):
            dd = (v.get(cfg) or {}).get("distribution_dynamique")
            if not dd:
                continue
            for t, d in dd.items():
                g = d["global"]
                glob.append({"programme": k, "configuration": cfg, "année": int(t), "revenu réel moyen (€/UC)": g["euros_par_uc_moyen"],
                             "revenu réel moyen (%)": g["pct_moyen"], "niveau de vie médian (%)": g["variation_niveau_de_vie_median_pct"],
                             "part gagnants": g["part_gagnants"], "part perdants": g["part_perdants"],
                             "pauvreté avant (%)": g["pauvrete_avant"], "pauvreté après (%)": g["pauvrete_apres"],
                             "Gini avant": g["gini_avant"], "Gini après": g["gini_apres"],
                             **{f"canal {c} (%)": x for c, x in g["canaux_pct"].items()},
                             "RDB macro nominal (%)": g["coherence"]["rdb_macro_nominal_pct"], "somme micro nominal (%)": g["coherence"]["somme_micro_nominal_pct"],
                             "RDB macro réel (%)": g["coherence"].get("rdb_macro_reel_pct"), "somme micro réelle hors successions (%)": g["coherence"].get("somme_micro_reel_hors_successions_pct"),
                             "résiduel réel (%)": g["coherence"]["residuel_pct"]})
                for dim in ("decile", "age", "statut", "csp", "famille", "occupation"):
                    for gr, x in d[dim].items():
                        lignes.append({"programme": k, "configuration": cfg, "année": int(t), "dimension": dim, "groupe": gr,
                                       "€ par UC (réel)": x["euros_par_uc"], "% du revenu (réel)": x["pct"], "part gagnants": x["part_gagnants"],
                                       "part perdants": x["part_perdants"], "poids": x["poids"],
                                       **{f"canal {c} (€/UC)": y for c, y in x["canaux_euros_par_uc"].items()}})
    notice = pd.DataFrame({"Notice": [
        "Distribution des effets des stratégies après propagation macroéconomique (modèle v0.8, module M16). Résultats de simulation.",
        "Écarts au scénario de référence, en revenu disponible réel (déflaté par un indice de prix propre au décile, hors composante fiscale).",
        "€ par UC : euros de l'année de la microsimulation par unité de consommation et par an ; % : en pourcentage du revenu disponible initial.",
        "Gagnant / perdant : variation réelle de plus de +0,5 % / de moins de −0,5 % du revenu ; effets d'emploi en espérance (pas de tirage individuel).",
        "Canaux : direct (prélèvements et prestations, taxes sur la consommation), salaires, emploi, patrimoine (revenus de la propriété et des indépendants),",
        "successions, indexation (retard des pensions et prestations sur les prix), prix (déflateur). Résiduel : écart entre la variation macroéconomique du revenu réel et la somme des canaux hors successions.",
        "Le canal direct inclut les mesures absentes de la microsimulation, réparties par clé : allocations chômage (chômeurs), transferts (prestations), point d'indice (salaires), pensions non versées en cas de report de l'âge légal (retraités de 58 à 67 ans).",
        "Configurations : central ; faible (réactions faibles, transmission lente) ; fort (réactions fortes, transmission rapide). Voir le rapport v0.8.",
        "2027 : avant la mise en œuvre (écarts nuls). Sources : phase31/resultats/strategies_v08_*.json ; script phase31/livrables31.py."]})
    with pd.ExcelWriter(OUT / "distribution_effets_v08.xlsx", engine="openpyxl") as w:
        notice.to_excel(w, sheet_name="Notice", index=False)
        pd.DataFrame(glob).to_excel(w, sheet_name="Synthèse", index=False)
        df = pd.DataFrame(lignes)
        for dim, nom in (("decile", "Déciles"), ("statut", "Statut"), ("csp", "Catégorie sociale"), ("famille", "Famille"), ("age", "Âge"),
                         ("occupation", "Logement")):
            df[df.dimension == dim].drop(columns=["dimension"]).to_excel(w, sheet_name=nom, index=False)
        mise_en_forme(w)


def comparaison():
    rows = []
    R7 = R / "phase3" / "resultats"
    for k in STRAT:
        p7, p8 = R7 / f"verification_v07_{k}.json", RES / f"strategies_v08_{k}.json"
        if not (p7.exists() and p8.exists()):
            continue
        t7 = json.loads(p7.read_text())["complet"]["traj"]
        t8 = json.loads(p8.read_text())["central"]["trajectoires"]
        for var, pct in (("pib", True), ("emploi", False), ("chomage", False), ("pc", True), ("solde_pib", False), ("dette_pib", False)):
            for t in (2032, 2037, 2042, 2047):
                s7, r7 = t7[var]["scenario"][str(t)], t7[var]["reference"][str(t)]
                v7 = 100 * (s7 / r7 - 1) if pct else s7 - r7
                v8 = t8[var]["ecart"][str(t)]
                rows.append({"programme": k, "indicateur": var, "année": t, "v0.7": v7, "v0.8": v8, "écart": v8 - v7})
    strat = pd.DataFrame(rows)
    dec = []
    f = RES / "decomposition_v07_v08.json"
    if f.exists():
        D = json.loads(f.read_text())
        e7 = {}
        for p in sorted((R7).glob("experiences_v07_*.json")):
            if "comport" not in p.name:
                e7.update(json.loads(p.read_text()))
        e8 = {}
        for p in sorted(RES.glob("experiences_v08_*.json")):
            if "comport" not in p.name:
                e8.update(json.loads(p.read_text()))
        for k, d in D.items():
            if k.startswith("S"):
                t7 = json.loads((R7 / f"verification_v07_{k}.json").read_text())["complet"]["traj"]
                t8 = json.loads((RES / f"strategies_v08_{k}.json").read_text())["central"]["trajectoires"]
            else:
                t7 = e7[k]["traj"] if k in e7 else None
                t8 = e8[k]["traj"] if k in e8 else None
            if t7 is None or t8 is None:
                continue
            for var in ("pib", "chomage", "dette_pib"):
                for t in (2030, 2037, 2047):
                    s7, r7 = t7[var]["scenario"][str(t)], t7[var]["reference"][str(t)]
                    v7 = 100 * (s7 / r7 - 1) if var == "pib" else s7 - r7
                    tr8 = t8[var]
                    v8 = tr8["ecart"][str(t)] if "ecart" in tr8 else (100 * (tr8["scenario"][str(t)] / tr8["reference"][str(t)] - 1) if var == "pib" else tr8["scenario"][str(t)] - tr8["reference"][str(t)])
                    a = d["A_fermeture_et_incidence_v07"][var][str(t)]
                    b = d["B_incidence_v07"][var][str(t)]
                    dec.append({"programme": k, "indicateur": var, "année": t, "v0.7": v7, "v0.8": v8, "écart total": v8 - v7,
                                "dont défaut de code, référence, offre de travail (A − v0.7)": a - v7, "dont fermeture estimée (B − A)": b - a,
                                "dont incidence fiscale (v0.8 − B)": v8 - b})
    # registre des paramètres (depuis le document 20)
    reg = []
    txt = (R / "doc" / "20_registre_parametres_v08.md").read_text()
    section = ""
    for ligne in txt.splitlines():
        if ligne.startswith("## "):
            section = ligne[3:]
        if ligne.startswith("|") and not ligne.startswith("|---") and "Paramètre" not in ligne and "Donnée manquante" not in ligne:
            cells = [c.strip() for c in ligne.strip("|").split("|")]
            reg.append({"section": section, **{f"col{i}": c for i, c in enumerate(cells)}})
    regdf = pd.DataFrame(reg).rename(columns={"col0": "paramètre", "col1": "définition", "col2": "valeur", "col3": "intervalle", "col4": "source et méthode",
                                              "col5": "confiance", "col6": "date"})
    bt = json.loads((RES / "analyse_backtest.json").read_text())["tableau"]
    btr = [{"période": per, "variante": var, "variable": x, **d} for per, vv in bt.items() for var, xx in vv.items() for x, d in xx.items()]
    notice = pd.DataFrame({"Notice": [
        "Comparaison des résultats v0.7 et v0.8 et causes des écarts (modèle économique et social de la France, phase 3.1).",
        "Stratégies : écarts à la référence (PIB, prix en % ; autres en points ou milliers), configuration centrale.",
        "Causes : trois simulations intermédiaires (phase31/decomposition_v07_v08.py) : A = v0.8 avec fermeture et incidence de la v0.7 ;",
        "B = v0.8 avec incidence de la v0.7 ; v0.8. A − v0.7 : défaut de code corrigé, référence recalée, offre de travail à 18 cas types ;",
        "B − A : fermeture estimée (θ, ρ, termes en différence) ; v0.8 − B : incidence fiscale. Les trois termes somment à l'écart total.",
        "Registre : paramètres de la v0.8 (document 20). Backtest : erreurs quadratiques moyennes et erreurs de fin de période (phase31/analyse_backtest.py)."]})
    with pd.ExcelWriter(OUT / "comparaison_v07_v08.xlsx", engine="openpyxl") as w:
        notice.to_excel(w, sheet_name="Notice", index=False)
        strat.to_excel(w, sheet_name="Stratégies", index=False)
        pd.DataFrame(dec).to_excel(w, sheet_name="Causes des écarts", index=False)
        regdf.to_excel(w, sheet_name="Registre des paramètres", index=False)
        pd.DataFrame(btr).to_excel(w, sheet_name="Backtest", index=False)
        mise_en_forme(w)


if __name__ == "__main__":
    distribution()
    comparaison()
    print("ok")
