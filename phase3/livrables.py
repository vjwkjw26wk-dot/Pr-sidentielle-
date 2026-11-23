"""Fichier Excel des résultats de l'optimisation et de la vérification des stratégies (phase 3).
Sortie : phase3/livrables/strategies_v07.xlsx"""
import json
import pathlib
import sys

import pandas as pd

R = pathlib.Path(__file__).resolve().parents[1]
RES = R / "phase3" / "resultats"
OUT = R / "phase3" / "livrables"
OUT.mkdir(exist_ok=True)
sys.path[:0] = [str(R / "phase3")]
import optimisation as O  # noqa: E402

ANS = (2029, 2030, 2032, 2037, 2042, 2047)


def ec(tr, k, t, pct):
    s = str(t)
    if k not in tr or s not in tr[k]["scenario"]:
        return None
    a, b = tr[k]["scenario"][s], tr[k]["reference"][s]
    return 100 * (a / b - 1) if pct else a - b


def main():
    o = json.loads((RES / "optimisation_v07.json").read_text())
    feuilles = {}
    feuilles["Notice"] = pd.DataFrame({"Notice": [
        "Phase 3 — première optimisation multicritère des politiques publiques (modèle v0.7). Résultats de simulation, non des recommandations.",
        "Leviers : effet de chaque levier poussé à sa borne, simulé seul avec le modèle complet (écart à la référence en 2037).",
        "Stratégies : composition (écart à la valeur actuelle de chaque levier) et prévision du métamodèle additif.",
        "Vérification : modèle complet (comportements centraux, bas, hauts ; mise en œuvre à moitié), horizons 2029 à 2047.",
        "Environnements : effet du programme sous chaque choc (le choc est appliqué à la référence et au programme).",
        "Acceptabilité : microsimulation statique (année de base), par décile et par groupe ; règle de classement dans phase3/acceptabilite.py.",
        "Préférences : 300 optimums à poids aléatoires ; fréquence d'emploi de chaque levier.",
        "Niveaux de preuve : A instruments fiscaux et budgétaires ; B réformes structurelles (comportement documenté) ; C exploratoires ou supposés.",
        "Scripts : phase3/optimisation.py, phase3/verifier_strategies.py, phase3/acceptabilite.py, phase3/livrables.py."]})
    E = o["perimetres"]["avec_exploratoires"]["efficacite"]
    feuilles["Leviers"] = pd.DataFrame([{"levier": k.split("|")[0], "sens": k.split("|")[1], "niveau": O.NIVEAU.get(k.split("|")[0], "A"),
                                         "difficulté": O.LEVIERS[k.split("|")[0]][6], **{c: v for c, v in E[k].items()}} for k in E])
    rows = []
    for per, P in o["perimetres"].items():
        for s, v in P["strategies"].items():
            if "leviers" not in v:
                continue
            for lev, x in v["leviers"].items():
                rows.append({"périmètre": per, "stratégie": s, "libellé": v["libelle"], "levier": lev, "écart à l'actuel": x})
    feuilles["Stratégies"] = pd.DataFrame(rows)
    rows = []
    for per, P in o["perimetres"].items():
        for s, v in P["strategies"].items():
            if "metamodele" in v:
                for t in ("2032", "2037", "2042", "2047"):
                    rows.append({"périmètre": per, "stratégie": s, "année": int(t), **v["metamodele"][t]})
    feuilles["Métamodèle"] = pd.DataFrame(rows)
    rows, env = [], []
    for f in sorted(RES.glob("verification_v07_*.json")):
        p = f.stem.replace("verification_v07_", "")
        V = json.loads(f.read_text())
        for alt in ("complet", "basse", "haute", "mi_chemin"):
            if alt not in V:
                continue
            tr = V[alt]["traj"]
            for t in ANS:
                rows.append({"programme": p, "variante": alt, "année": t, "PIB (%)": ec(tr, "pib", t, True), "emploi (milliers)": ec(tr, "emploi", t, False),
                             "chômage (pt)": ec(tr, "chomage", t, False), "prix (%)": ec(tr, "pc", t, True), "salaire (%)": ec(tr, "salaire", t, True),
                             "investissement (%)": ec(tr, "fbcf", t, True), "consommation (%)": ec(tr, "c", t, True), "RDB (%)": ec(tr, "rdb", t, True),
                             "solde (pt)": ec(tr, "solde_pib", t, False), "dette (pt)": ec(tr, "dette_pib", t, False),
                             "intérêts (pt)": ec(tr, "interets_pib", t, False), "industrie (pt)": ec(tr, "part_industrie", t, False)})
        for c, x in V["resistance"].items():
            if "erreur" in x:
                continue
            for t in (2030, 2032, 2037, 2047):
                env.append({"programme": p, "environnement": c, "année": t, **{f"{k} (écart du programme)": x[k][str(t)]["ecart"] for k in x if str(t) in x[k]}})
    feuilles["Vérification"] = pd.DataFrame(rows)
    feuilles["Environnements"] = pd.DataFrame(env)
    fa = RES / "anticipation_v07.json"
    if fa.exists():
        rows = []
        for k, v in json.loads(fa.read_text()).items():
            p, niv = k.split("|")
            for t in (2032, 2037, 2047):
                rows.append({"programme": p, "anticipation": niv, "année": t, "PIB (%)": ec(v["traj"], "pib", t, True),
                             "chômage (pt)": ec(v["traj"], "chomage", t, False), "dette (pt)": ec(v["traj"], "dette_pib", t, False)})
        feuilles["Anticipation"] = pd.DataFrame(rows)
    A = json.loads((RES / "acceptabilite_v07.json").read_text())
    rows, grp = [], []
    for p, a in A.items():
        for d, x in a["deciles"].items():
            rows.append({"programme": p, "acceptabilité": a["niveau"], "décile": int(d), **x})
        for dim, gs in (a["groupes"] or {}).items():
            for g, x in gs.items():
                grp.append({"programme": p, "dimension": dim, "groupe": g, **x})
    feuilles["Déciles"] = pd.DataFrame(rows)
    feuilles["Groupes"] = pd.DataFrame(grp)
    feuilles["Acceptabilité"] = pd.DataFrame([{"programme": p, "niveau": a["niveau"], "perte max. décile (%)": a["perte_max_decile_pct"],
                                               "perte max. groupe (%)": a["perte_max_groupe_pct"], "droits réduits": ", ".join(a["droits_reduits"]),
                                               "leviers de difficulté 3": ", ".join(a["leviers_difficulte_3"]),
                                               "coût de compensation D1-D3 (M€/an)": a["cout_compensation_D1_D3_M€"]} for p, a in A.items()])
    rp = o["perimetres"]["principal"]["robustesse_preferences"]
    feuilles["Préférences"] = pd.DataFrame([{"levier|sens": k, "fréquence": v} for k, v in rp["frequence"].items()])
    with pd.ExcelWriter(OUT / "strategies_v07.xlsx", engine="openpyxl") as w:
        for n, df in feuilles.items():
            df.to_excel(w, sheet_name=n, index=False)
        for ws in w.book.worksheets:
            for col in ws.columns:
                ws.column_dimensions[col[0].column_letter].width = min(55, max(9, max(len(str(c.value or "")) for c in col[:60]) + 2))
            for row in ws.iter_rows(min_row=2):
                for c in row:
                    if isinstance(c.value, float):
                        c.number_format = "0.00"
            ws.freeze_panes = "A2"
    print("ok", list(feuilles))


if __name__ == "__main__":
    main()
