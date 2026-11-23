"""Comparaison détaillée v0.6 / v0.7 : toutes les expériences communes, indicateurs à 5, 10 et 20 ans.
Sorties : phase3/resultats/comparaison_v06_v07.json et phase3/livrables/comparaison_v06_v07.xlsx"""
import json
import pathlib

import pandas as pd

R = pathlib.Path(__file__).resolve().parents[1]
V06, V07 = R / "rapport" / "resultats", R / "phase3" / "resultats"
SORTIE = R / "phase3" / "livrables"
SORTIE.mkdir(exist_ok=True)
ANS = (2032, 2037, 2047)
IND = [  # clé, libellé, type d'écart
    ("pib", "PIB en volume (%)", "pct"), ("c", "Consommation des ménages (%)", "pct"), ("fbcf", "Investissement (%)", "pct"),
    ("x", "Exportations (%)", "pct"), ("m", "Importations (%)", "pct"), ("emploi", "Emploi (milliers)", "niv"),
    ("chomage", "Chômage (points)", "niv"), ("salaire", "Salaire moyen (%)", "pct"), ("pc", "Prix à la consommation (%)", "pct"),
    ("rdb_reel", "Revenu disponible réel (%)", "reel"), ("taux_epargne", "Taux d'épargne (points)", "niv"),
    ("recettes_pib", "Recettes publiques (points de PIB)", "niv"), ("depenses_pib", "Dépenses publiques (points de PIB)", "niv"),
    ("solde_pib", "Solde public (points de PIB)", "niv"), ("dette_pib", "Dette publique (points de PIB)", "niv"),
    ("part_industrie", "Part de l'industrie (points)", "niv"),
]


def ecart(tr, k, typ, t):
    s = str(t)
    if typ == "reel":
        a = tr["rdb"]["scenario"][s] / tr["pc"]["scenario"][s]
        b = tr["rdb"]["reference"][s] / tr["pc"]["reference"][s]
        return 100 * (a / b - 1)
    if k not in tr or s not in tr[k]["scenario"]:
        return None
    if typ == "pct":
        return 100 * (tr[k]["scenario"][s] / tr[k]["reference"][s] - 1)
    return tr[k]["scenario"][s] - tr[k]["reference"][s]


def charger(dossier, motif):
    out = {}
    for f in sorted(dossier.glob(motif)):
        lot = f.stem.split("_")[-1]
        for k, v in json.loads(f.read_text()).items():
            if "traj" in v:
                out[k] = (lot, v)
    return out


def main():
    a = charger(V06, "experiences_*.json")
    b = charger(V07, "experiences_v07_*.json")
    b.pop("comportements", None)
    lignes = []
    for nom, (lot, e7) in b.items():
        e6 = a.get(nom, (None, None))[1]
        for k, lib, typ in IND:
            row = {"lot": lot, "experience": nom, "libelle": e7["libelle"], "indicateur": lib}
            for t in ANS:
                v7 = ecart(e7["traj"], k, typ, t)
                v6 = ecart(e6["traj"], k, typ, t) if e6 else None
                row[f"v0.6 {t}"] = v6
                row[f"v0.7 {t}"] = v7
                row[f"écart {t}"] = (v7 - v6) if (v6 is not None and v7 is not None) else None
            lignes.append(row)
    df = pd.DataFrame(lignes)
    (V07 / "comparaison_v06_v07.json").write_text(df.to_json(orient="records", force_ascii=False))
    # synthèse : PIB, emploi, chômage, dette à 10 ans
    syn = df[df.indicateur.isin(["PIB en volume (%)", "Emploi (milliers)", "Dette publique (points de PIB)", "Prix à la consommation (%)",
                                 "Revenu disponible réel (%)"])].pivot_table(index=["lot", "experience", "libelle"], columns="indicateur",
                                                                              values=["v0.6 2037", "v0.7 2037"], aggfunc="first")
    syn.columns = [f"{i} — {a}" for a, i in syn.columns]
    syn = syn[sorted(syn.columns)]
    with pd.ExcelWriter(SORTIE / "comparaison_v06_v07.xlsx", engine="openpyxl") as w:
        notice = pd.DataFrame({"Notice": [
            "Comparaison des résultats des versions 0.6 et 0.7 du modèle, pour chaque expérience (une mesure ou une combinaison).",
            "Les valeurs sont des écarts à la trajectoire de référence de la version correspondante (scénario − référence).",
            "% : écart relatif ; points : écart absolu ; emploi : milliers. Années : 2032 (5 ans), 2037 (10 ans), 2047 (20 ans).",
            "Expériences propres à la phase 3 (lot « phase3 ») : pas de valeur v0.6.",
            "Résultats de simulation (modèle), non des prévisions ; voir le rapport de phase 3 pour les incertitudes.",
            "Sources : phase3/resultats/experiences_v07_*.json, rapport/resultats/experiences_*.json ; script phase3/comparaison.py."]})
        notice.to_excel(w, sheet_name="Notice", index=False)
        syn.reset_index().to_excel(w, sheet_name="Synthèse 10 ans", index=False)
        df.to_excel(w, sheet_name="Détail", index=False)
        for ws in w.book.worksheets:
            for col in ws.columns:
                ws.column_dimensions[col[0].column_letter].width = min(60, max(10, max(len(str(c.value or "")) for c in col[:50]) + 2))
            for row in ws.iter_rows(min_row=2):
                for c in row:
                    if isinstance(c.value, float):
                        c.number_format = "0.00"
            ws.freeze_panes = "A2"
    print(len(df), "lignes")


if __name__ == "__main__":
    main()
