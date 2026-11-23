"""Livrables complémentaires du rapport : synthèse des mesures et de leurs impacts, paramètres des scénarios, résultats
détaillés, tableau du programme recommandé (chiffrage mesure par mesure par le méta-modèle de rapport/strategie.py).
Usage : python3 rapport/livrables.py  → rapport/livrables/*, rapport/tableaux/programme_R.tex
"""
from __future__ import annotations

import csv
import json
import pathlib
import sys

R = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(R))
import strategie as S  # noqa: E402
from figures import tex, emploi_k, pauv  # noqa: E402

RES, OUT, TAB = R / "resultats", R / "livrables", R / "tableaux"
OUT.mkdir(exist_ok=True)
PIB_2025 = 2991.4
INDIC = ["pib", "emploi", "chomage", "inflation", "rdb", "pc", "c", "fbcf", "x", "m", "taux_epargne", "solde_pib", "dette_pib",
         "recettes_pib", "depenses_pib", "interets_pib", "solde_exterieur_pib", "rnb", "part_industrie", "pensions_pib", "salaire"]


def experiences():
    E = {}
    for f in sorted(RES.glob("experiences_*.json")):
        lot = f.stem.replace("experiences_", "")
        for k, v in json.loads(f.read_text()).items():
            v["lot"] = lot
            E[k] = v
    return E


def scenarios():
    V = {}
    for k in "ABCDR":
        f = RES / f"verification_{k}.json"
        if f.exists():
            V[k] = json.loads(f.read_text())[k]
    return V


def ligne_synthese(nom, lot, libelle, curseurs, T, ineg):
    g = lambda k, t: T[k]["ecart"][str(t)]  # noqa: E731
    emp = lambda t: T["emploi"]["scenario"][str(t)] - T["emploi"]["reference"][str(t)]  # noqa: E731
    d = {"code": nom, "lot": lot, "mesure": libelle, "curseurs": json.dumps(curseurs, ensure_ascii=False)}
    for t in (2029, 2032, 2037, 2047):
        d[f"solde_pt_pib_{t}"] = round(g("solde_pib", t), 3)
        d[f"solde_Md€2025_{t}"] = round(g("solde_pib", t) * PIB_2025 / 100, 2)
        d[f"pib_pct_{t}"] = round(g("pib", t), 3)
        d[f"emploi_milliers_{t}"] = round(emp(t), 1)
        d[f"dette_pt_pib_{t}"] = round(g("dette_pib", t), 2)
        d[f"pouvoir_achat_pct_{t}"] = round(g("rdb", t) - g("pc", t), 3)
    d["prix_pct_2030"] = round(g("pc", 2030), 3)
    d["chomage_pt_2030"] = round(g("chomage", 2030), 3)
    d["investissement_pct_2030"] = round(g("fbcf", 2030), 3)
    d["solde_exterieur_pt_2030"] = round(g("solde_exterieur_pib", 2030), 3)
    if ineg:
        d["pauvrete_pt_statique"] = round(ineg["apres_seuil_fixe"]["taux_pauvrete"] - ineg["avant"]["taux_pauvrete"], 3)
        d["gini_x100_statique"] = round((ineg["apres"]["gini"] - ineg["avant"]["gini"]) * 100, 3)
        d["mediane_pct_statique"] = round((ineg["apres"]["mediane"] / ineg["avant"]["mediane"] - 1) * 100, 3)
    return d


def main():
    E, V = experiences(), scenarios()
    lignes = [ligne_synthese(k, e["lot"], e["libelle"], e["curseurs"], e["traj"], e.get("inegalites")) for k, e in E.items()]
    lib = {"A": "Scénario A — redressement budgétaire prioritaire", "B": "Scénario B — croissance et réindustrialisation",
           "C": "Scénario C — redressement équilibré", "D": "Scénario D — effort maximal sur la dette", "R": "Scénario R — programme recommandé"}
    lignes += [ligne_synthese(f"scenario_{k}", "scenarios", lib[k], v["curseurs"], v["complet"]["traj"], v["complet"].get("inegalites")) for k, v in V.items()]
    champs = list(dict.fromkeys(c for l_ in lignes for c in l_))
    with open(OUT / "mesures_impacts.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=champs)
        w.writeheader()
        w.writerows(lignes)
    # résultats détaillés (format long)
    with open(OUT / "resultats_detailles.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["simulation", "indicateur", "annee", "reference", "scenario", "ecart", "unite_ecart"])
        src = [(k, e["traj"]) for k, e in E.items()] + [(f"scenario_{k}", v["complet"]["traj"]) for k, v in V.items()]
        for k, T in src:
            for ind in INDIC:
                if ind not in T:
                    continue
                for a in sorted(T[ind]["ecart"], key=int):
                    w.writerow([k, ind, a, T[ind]["reference"][a], T[ind]["scenario"][a], T[ind]["ecart"][a],
                                "points" if ind in ("chomage", "inflation", "taux_epargne", "solde_pib", "dette_pib", "recettes_pib", "depenses_pib",
                                                    "interets_pib", "solde_exterieur_pib", "part_industrie", "pensions_pib") else "%"])
    # paramètres des scénarios
    strat = json.loads((RES / "strategie.json").read_text())
    params = {"version_modele": "0.6", "debut_mesures": 2028, "objectifs_et_contraintes": {k: {kk: str(vv) for kk, vv in d.items()} for k, d in S.OBJECTIFS.items()},
              "plafonds": {"prelevements_pt_pib_2030": S.PLAFOND_IMPOTS, "economies_pt_pib_2030": S.PLAFOND_ECONOMIES},
              "leviers_exclus": ["hausse de l'IS et des impôts de production", "réindustrialisation (objectif, non instrument)", "SMIC"],
              "scenarios": {k: {"libelle": lib[k], "curseurs": v["curseurs"]} for k, v in V.items()},
              "essais_par_age": {k: d.get("essais") for k, d in strat["scenarios"].items()}}
    (OUT / "scenarios_parametres.json").write_text(json.dumps(params, ensure_ascii=False, indent=1))
    # programme R : chiffrage mesure par mesure (méta-modèle) et total (modèle complet)
    cur = dict(V["R"]["curseurs"])
    age = int(cur.pop("age_legal", 64))
    rows = []
    for lev, val in cur.items():
        act, lo, hi, plus, moins = S.LEVIERS[lev]
        d = val - act
        src = (plus if d > 0 else moins) or (plus or moins)
        nom, v = src[-1]
        f = d / (v - act)
        e = E[nom]
        ef = S.effets(e)
        rows.append((lev, val, f, ef, e))
    if age != 64:
        e = E[S.AGES[age]]
        rows.append(("age_legal", age, 1.0, S.effets(e), e))
    L = [r"\begin{tabular}{p{4.6cm}rrrrrrr}", r"\toprule",
         r"Mesure & Solde 2030 & Solde 2030 & PIB 2030 & PIB 2037 & Emploi 2037 & Dette 2037 & Pauvreté \\",
         r" & (pt PIB) & (Md€ 2025) & (\%) & (\%) & (milliers) & (pt) & (pt) \\", r"\midrule"]
    from figures import LIB_CURSEURS
    tot = {}
    for lev, val, f, ef, e in rows:
        g = lambda k, t: f * ef[(k, t)]  # noqa: E731
        for k in [("solde", 2030), ("pib", 2030), ("pib", 2037), ("emploi_k", 2037), ("dette", 2037), ("pauvrete", 2037)]:
            tot[k] = tot.get(k, 0.0) + f * ef[k]
        lbl = LIB_CURSEURS.get(lev, lev).replace("%", r"\%")
        L.append(f"{lbl} : {tex(val, 2, False).replace('{,}00', '')} & {tex(g('solde', 2030))} & {tex(g('solde', 2030) * PIB_2025 / 100, 1)} & {tex(g('pib', 2030))} & "
                 f"{tex(g('pib', 2037))} & {tex(g('emploi_k', 2037), 0)} & {tex(g('dette', 2037), 1)} & {tex(g('pauvrete', 2037))} \\\\")
    T = V["R"]["complet"]["traj"]
    i = V["R"]["complet"]["inegalites"]
    L.append(r"\midrule")
    L.append(f"Somme des mesures (méta-modèle) & {tex(tot[('solde', 2030)])} & {tex(tot[('solde', 2030)] * PIB_2025 / 100, 1)} & {tex(tot[('pib', 2030)])} & "
             f"{tex(tot[('pib', 2037)])} & {tex(tot[('emploi_k', 2037)], 0)} & {tex(tot[('dette', 2037)], 1)} & {tex(tot[('pauvrete', 2037)])} \\\\")
    emp37 = T["emploi"]["scenario"]["2037"] - T["emploi"]["reference"]["2037"]
    L.append(f"\\textbf{{Programme simulé ensemble (modèle complet)}} & {tex(T['solde_pib']['ecart']['2030'])} & {tex(T['solde_pib']['ecart']['2030'] * PIB_2025 / 100, 1)} & "
             f"{tex(T['pib']['ecart']['2030'])} & {tex(T['pib']['ecart']['2037'])} & {tex(emp37, 0)} & {tex(T['dette_pib']['ecart']['2037'], 1)} & "
             f"{tex(i['apres_seuil_fixe']['taux_pauvrete'] - i['avant']['taux_pauvrete'])} \\\\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (TAB / "programme_R.tex").write_text("\n".join(L) + "\n")
    try:
        import openpyxl  # noqa: F401
        import pandas as pd
        with pd.ExcelWriter(OUT / "mesures_impacts.xlsx") as xw:
            pd.read_csv(OUT / "mesures_impacts.csv").to_excel(xw, sheet_name="Mesures et scénarios", index=False)
            pd.DataFrame([{"scenario": k, **v["curseurs"]} for k, v in V.items()]).to_excel(xw, sheet_name="Paramètres des scénarios", index=False)
    except ImportError:
        pass
    print("livrables :", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
