"""Figures et tableaux du rapport (reproductibles à partir de rapport/resultats/*.json).
Usage : python3 rapport/figures.py   → rapport/figures/*.pdf et rapport/tableaux/*.tex
"""
from __future__ import annotations

import json
import pathlib
import subprocess

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

R = pathlib.Path(__file__).resolve().parent
RES, FIG, TAB = R / "resultats", R / "figures", R / "tableaux"
FIG.mkdir(exist_ok=True)
TAB.mkdir(exist_ok=True)
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "figure.dpi": 150,
                     "axes.grid": True, "grid.alpha": 0.3, "legend.frameon": False, "font.family": "DejaVu Sans"})
COUL = ["#1f4e79", "#c0504d", "#9bbb59", "#8064a2", "#f79646", "#4bacc6", "#7f7f7f", "#2c7c3c"]
ANS = list(range(2026, 2048))


def charger():
    E = {}
    for f in sorted(RES.glob("experiences_*.json")):
        E.update(json.loads(f.read_text()))
    return E


def serie(e, k, s="ecart", ans=ANS):
    d = e["traj"][k][s]
    return [d.get(str(t), np.nan) for t in ans]


def emploi_k(e, t):
    T = e["traj"]["emploi"]
    return T["scenario"][str(t)] - T["reference"][str(t)]


def pauv(e):
    i = e.get("inegalites")
    return (i["apres_seuil_fixe"]["taux_pauvrete"] - i["avant"]["taux_pauvrete"]) if i else None


def gini(e):
    i = e.get("inegalites")
    return (i["apres"]["gini"] - i["avant"]["gini"]) * 100 if i else None


def save(fig, nom):
    fig.tight_layout()
    fig.savefig(FIG / f"{nom}.pdf")
    plt.close(fig)


def tex(x, d=2, signe=True):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "--"
    if signe and abs(x) < 0.5 * 10 ** (-d):
        x = 0.0
    s = (f"{x:+.{d}f}" if x != 0 else f"{0:.{d}f}") if signe else f"{x:.{d}f}"
    return s.replace(".", "{,}").replace("-", "$-$")


def figure_reference(E):
    e = next(iter(E.values()))
    ans = list(range(2023, 2048))
    fig, ax = plt.subplots(2, 2, figsize=(7.2, 5))
    pib = serie(e, "pib", "reference", ans)
    g = [np.nan] + [(pib[i] / pib[i - 1] - 1) * 100 for i in range(1, len(pib))]
    for a, (y, t) in zip(ax.flat, [(g, "Croissance du PIB en volume (%)"), (serie(e, "chomage", "reference", ans), "Taux de chômage (%)"),
                                   (serie(e, "solde_pib", "reference", ans), "Solde public (% du PIB)"),
                                   (serie(e, "dette_pib", "reference", ans), "Dette publique (% du PIB)")]):
        a.plot(ans, y, color=COUL[0])
        a.axvspan(2023, 2025, color="#dddddd", alpha=0.6, lw=0)
        a.axvspan(2025, 2031, color="#eef3f8", alpha=0.6, lw=0)
        a.set_title(t, fontsize=9)
    ax[0, 0].text(2023.2, ax[0, 0].get_ylim()[1] * 0.9, "observé", fontsize=7)
    ax[0, 0].text(2026, ax[0, 0].get_ylim()[1] * 0.9, "FMI", fontsize=7)
    save(fig, "reference")


def trajectoires(E, noms, k, titre, fichier, ans=ANS, unite="écart à la référence"):
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    for i, n in enumerate(noms):
        if n in E and "traj" in E[n]:
            ax.plot(ans, serie(E[n], k, ans=ans), label=E[n]["libelle"], color=COUL[i % len(COUL)])
    ax.axhline(0, color="black", lw=0.6)
    ax.set_title(f"{titre} ({unite})", fontsize=9)
    ax.legend(fontsize=6.5, loc="best")
    save(fig, fichier)


def tableau_mesures(E, noms, fichier, legende):
    L = [r"\begin{tabular}{p{5.2cm}rrrrrrr}", r"\toprule",
         r"Mesure & $\Delta$solde 2030 & PIB 2030 & PIB 2037 & Emploi 2030 & Dette 2037 & Dette 2047 & Pauvreté \\",
         r" & (pt PIB) & (\%) & (\%) & (milliers) & (pt) & (pt) & (pt) \\", r"\midrule"]
    for n in noms:
        if n not in E or "traj" not in E[n]:
            continue
        e = E[n]
        g = lambda k, t: e["traj"][k]["ecart"][str(t)]  # noqa: E731
        L.append(f"{e['libelle'].replace('%', chr(92) + '%')} & {tex(g('solde_pib', 2030))} & {tex(g('pib', 2030))} & {tex(g('pib', 2037))} & {tex(emploi_k(e, 2030), 0)} & "
                 f"{tex(g('dette_pib', 2037), 1)} & {tex(g('dette_pib', 2047), 1)} & {tex(pauv(e))} \\\\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (TAB / f"{fichier}.tex").write_text("\n".join(L) + "\n")


def tableau_detail(E, noms, fichier):
    """Effets de court terme (2030) sur les comptes des agents."""
    L = [r"\begin{tabular}{p{5.0cm}rrrrrrrr}", r"\toprule",
         r"Mesure & Recettes & RDB réel & Conso. & Épargne & Invest. & Prix & Export. & Import. \\",
         r" & (pt PIB) & (\%) & (\%) & (pt) & (\%) & (\%) & (\%) & (\%) \\", r"\midrule"]
    for n in noms:
        if n not in E or "traj" not in E[n]:
            continue
        e = E[n]
        g = lambda k, t=2030: e["traj"][k]["ecart"][str(t)]  # noqa: E731
        L.append(f"{e['libelle'].replace('%', chr(92) + '%')} & {tex(g('recettes_pib'))} & {tex(g('rdb') - g('pc'))} & {tex(g('c'))} & {tex(g('taux_epargne'))} & "
                 f"{tex(g('fbcf'))} & {tex(g('pc'))} & {tex(g('x'))} & {tex(g('m'))} \\\\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (TAB / f"{fichier}.tex").write_text("\n".join(L) + "\n")


RENDEMENTS = {  # Md€ de 2025 : (statique, net des réactions M13) — chiffrages de executer.py / microsimulation
    "ir_bas": (9.06, 9.06), "ir_haut": (1.71, 0.28), "csg": (11.4, 11.4), "tva": (8.2, 8.2), "tva_reduite": (10.0, 10.0),
    "isf": (7.1, 5.04), "pfu": (9.0, 5.32), "production": (10.0, 10.0), "cotisations": (10.0, 10.0),
    "successions": (9.0, 8.1), "carbone": (10.0, 10.0)}
PIB_2025 = 2991.4


def tableau_rendement(E, fichier):
    """Rendement statique et amélioration effective du solde (Md€ de 2025 : points de PIB × PIB 2025)."""
    L = [r"\begin{tabular}{p{5.0cm}rrrrrrr}", r"\toprule",
         r"Mesure & Statique & Net (M13) & $\Delta$solde 2029 & $\Delta$solde 2032 & Conservé 2029 & PIB 2029 & Emploi 2029 \\",
         r" & (Md€) & (Md€) & (Md€) & (Md€) & (\% du net) & (\%) & (milliers) \\", r"\midrule"]
    for n, (st, net) in RENDEMENTS.items():
        e = E.get(n)
        if not e:
            continue
        s29 = e["traj"]["solde_pib"]["ecart"]["2029"] * PIB_2025 / 100
        s32 = e["traj"]["solde_pib"]["ecart"]["2032"] * PIB_2025 / 100
        L.append(f"{e['libelle'].replace('%', chr(92) + '%')} & {tex(st, 1, False)} & {tex(net, 1, False)} & {tex(s29, 1)} & {tex(s32, 1)} & {tex(100 * s29 / net, 0, False)} & "
                 f"{tex(e['traj']['pib']['ecart']['2029'])} & {tex(emploi_k(e, 2029), 0)} \\\\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (TAB / f"{fichier}.tex").write_text("\n".join(L) + "\n")


def efficacite(E, noms, fichier):
    """Coût en activité d'un point de solde : ΔPIB 2030 / Δsolde 2030."""
    rows = []
    for n in noms:
        e = E.get(n)
        if not e or "traj" not in e:
            continue
        s = e["traj"]["solde_pib"]["ecart"]["2030"]
        p = e["traj"]["pib"]["ecart"]["2030"]
        p37 = e["traj"]["pib"]["ecart"]["2037"]
        if abs(s) > 0.02:
            rows.append((e["libelle"], p / s, p37 / s, s))
    rows.sort(key=lambda r: r[1])
    fig, ax = plt.subplots(figsize=(6.8, 0.30 * len(rows) + 1))
    y = np.arange(len(rows))
    ax.barh(y - 0.2, [r[1] for r in rows], 0.4, label="2030", color=COUL[0])
    ax.barh(y + 0.2, [r[2] for r in rows], 0.4, label="2037", color=COUL[5])
    ax.set_yticks(y, [r[0][:60] for r in rows], fontsize=7)
    ax.axvline(0, color="black", lw=0.6)
    ax.set_xlabel("variation du PIB (%) par point de PIB d'amélioration du solde public")
    ax.legend(fontsize=7)
    save(fig, fichier)


def figure_seuils():
    d = json.loads((RES / "seuils_salaires.json").read_text())
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3))
    for i, (k, v) in enumerate(d.items()):
        x = [p["smic"] for p in v["points"]]
        ax[0].plot(x, [p["revenu_disponible"] / 1000 for p in v["points"]], color=COUL[i], label=v["libelle"])
        ax[1].plot(x[1:], [p["taux_marginal_effectif"] for p in v["points"][1:]], color=COUL[i])
    ax[0].plot([0, 2.5], [0, 2.5 * 17.9 * 0.98], ls="--", color="grey", lw=0.8, label="salaire net seul")
    ax[0].set_xlabel("salaire (multiple du SMIC)"); ax[0].set_ylabel("revenu disponible (k€/an)")
    ax[1].set_xlabel("salaire (multiple du SMIC)"); ax[1].set_ylabel("taux marginal effectif (%)")
    ax[1].axhline(0, color="black", lw=0.5)
    ax[0].legend(fontsize=6)
    save(fig, "seuils_salaires")


def figure_distribution(E, noms, fichier, titre):
    fig, ax = plt.subplots(figsize=(6.5, 3))
    w = 0.8 / len(noms)
    for i, n in enumerate(noms):
        e = E.get(n)
        if not e or not e.get("distribution"):
            continue
        dd = sorted(e["distribution"], key=lambda x: x["decile"])
        ax.bar(np.arange(1, 11) + (i - len(noms) / 2) * w + w / 2, [x["variation_pct"] for x in dd], w, label=e["libelle"], color=COUL[i])
    ax.axhline(0, color="black", lw=0.6)
    ax.set_xticks(range(1, 11)); ax.set_xlabel("décile de niveau de vie"); ax.set_ylabel("variation du niveau de vie (%)")
    ax.set_title(titre, fontsize=9)
    ax.legend(fontsize=6.5)
    save(fig, fichier)


def figure_interactions(E):
    paires = [("Cotisations −20 Md€ + TVA +2,4", "tva_sociale", ["cot_moins20", "combi_cot_tva"]),
              ("Investissement public +20 Md€ + âge 65 ans", "combi_invest_age", ["invest20", "age65"]),
              ("RSA et prime d'activité +25 % + CSG +0,5", "combi_rsa_ppa_csg", ["rsa25", "ppa25", "csg05"]),
              ("Réindustrialisation −10 % + droits de douane 10 %", "combi_reindus_douane", ["reindus10", "douanes10"]),
              ("Emplois publics −170 000 + fonctionnement −10 Md€", "combi_emploipub_fonct", ["emploi_public", "fonctionnement"])]
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.2))
    for j, (k, t) in enumerate([("pib", 2032), ("dette_pib", 2037)]):
        lab, comb, som = [], [], []
        for nom, c, parts in paires:
            if c not in E or any(p not in E for p in parts):
                continue
            lab.append(nom)
            comb.append(E[c]["traj"][k]["ecart"][str(t)])
            som.append(sum(E[p]["traj"][k]["ecart"][str(t)] for p in parts))
        y = np.arange(len(lab))
        ax[j].barh(y - 0.2, som, 0.4, label="somme des mesures isolées", color=COUL[6])
        ax[j].barh(y + 0.2, comb, 0.4, label="mesures simulées ensemble", color=COUL[0])
        ax[j].set_yticks(y, lab if j == 0 else [""] * len(lab), fontsize=6.5)
        ax[j].set_title({"pib": "PIB 2032 (%)", "dette_pib": "Dette 2037 (pt de PIB)"}[k], fontsize=9)
        ax[j].axvline(0, color="black", lw=0.5)
    ax[0].legend(fontsize=6.5, loc="lower left")
    save(fig, "interactions")


def figure_validation():
    d = json.loads((R.parent / "outputs" / "validation_hors_echantillon.json").read_text())["retro"]
    fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.6))
    for j, k in enumerate(["pib", "emploi", "pc"]):
        for i, (B, v) in enumerate(d.items()):
            h = len(v[k]["obs"])
            ans = list(range(int(B) + 1, int(B) + h + 1))
            ax[j].plot(ans, v[k]["obs"], color=COUL[i], lw=1.4)
            ax[j].plot(ans, v[k]["sim"], color=COUL[i], ls="--", lw=1)
        ax[j].set_title({"pib": "PIB (croissance, %)", "emploi": "Emploi (croissance, %)", "pc": "Prix conso. (croissance, %)"}[k], fontsize=8)
    ax[0].plot([], [], color="black", label="observé"); ax[0].plot([], [], color="black", ls="--", label="simulé")
    ax[0].legend(fontsize=6)
    save(fig, "validation_retro")


def schemas():
    archi = r'''digraph G { rankdir=LR; node [shape=box, style="rounded,filled", fillcolor="#eef3f8", fontname="Helvetica", fontsize=10];
    edge [fontname="Helvetica", fontsize=8, color="#555555"];
    M [label="Ménages\n(revenus, consommation,\népargne, logement)"]; E [label="Entreprises\n25 branches marchandes\n(production, emploi, prix,\ninvestissement)"];
    A [label="Administrations publiques\n(État, collectivités,\nSécurité sociale)"]; R [label="Reste du monde\n(zone euro, autres pays)"];
    T [label="Tableau entrées-sorties\n64 produits", fillcolor="#fff4e5"]; P [label="Population\n(démographie, activité,\nretraites)", fillcolor="#f0f7ec"];
    M -> E [label="consommation"]; E -> M [label="salaires, dividendes"]; M -> A [label="impôts, cotisations"]; A -> M [label="prestations, pensions"];
    E -> A [label="IS, impôts de production,\ncotisations employeurs"]; A -> E [label="achats publics"]; E -> R [label="exportations"]; R -> E [label="importations,\nprix de l'énergie"];
    E -> T [dir=both, label="consommations\nintermédiaires"]; P -> M [label="actifs, retraités"]; P -> A [label="pensions,\nsanté"];
    R -> A [label="taux d'intérêt\n(BCE, marchés)"]; E -> R [label="dividendes aux\nnon-résidents", style=dashed]; }'''
    chaine = r'''digraph G { rankdir=TB; node [shape=box, style="rounded,filled", fillcolor="#eef3f8", fontname="Helvetica", fontsize=9]; edge [color="#555555"];
    a [label="Hausse de la TVA (+1 point)", fillcolor="#fde9d9"]; b [label="Prix à la consommation +0,4 %"]; c [label="Revenu réel des ménages −"];
    d [label="Consommation −"]; e [label="Production nationale −\n(contenu importé : une partie de la baisse\nporte sur les importations)"]; f [label="Emploi −  →  chômage +"];
    g [label="Salaires indexés sur les prix (+)\n/ courbe de Phillips (−)"]; h [label="Recettes : TVA + ; IR, cotisations −"];
    i [label="Solde public + (effet net)"]; j [label="Dette − ; intérêts −"]; k [label="Fermeture d'offre : la politique monétaire\net le crédit ramènent le chômage\nvers son niveau structurel"];
    a -> b -> c -> d -> e -> f; b -> g -> c; f -> g; e -> h; a -> h; h -> i -> j; f -> k -> e; }'''
    for nom, src in (("architecture", archi), ("chaine_causale", chaine)):
        (FIG / f"{nom}.dot").write_text(src)
        subprocess.run(["dot", "-Tpdf", str(FIG / f"{nom}.dot"), "-o", str(FIG / f"{nom}.pdf")], check=True)


NOMS_SC = {"A": "A — budgétaire", "B": "B — croissance", "C": "C — équilibré", "D": "D — effort maximal", "R": "R — recommandé"}
LIB_CURSEURS = {"tva": "TVA taux normal (points)", "tva_reduite": "TVA taux réduits (points)", "csg_activite": "CSG activité (points)",
                "ir_t1": "IR, taux de la 1re tranche (%)", "isf": "Impôt sur la fortune (taux moyen, %)", "pfu": "PFU (points)",
                "successions": "Droits de succession (%)", "taxe_carbone": "Taxe carbone (€/t)", "cotisations_employeurs": "Cotisations employeurs (Md€)",
                "autres_depenses": "Fonctionnement (Md€)", "investissement_public": "Investissement public (Md€)", "emploi_public": "Emplois publics (milliers)",
                "indexation_pensions": "Indexation des pensions (points/an)", "assurance_chomage": "Allocations chômage (%)", "rsa": "RSA (%)",
                "prime_activite": "Prime d'activité (%)", "allocations_familiales": "Allocations familiales (%)", "minimum_vieillesse": "Minimum vieillesse (%)",
                "temps_travail": "Durée du travail (heures)", "droits_douane": "Droits de douane hors UE (%)", "age_legal": "Âge légal (ans)"}


def charger_scenarios():
    V = {}
    for k in "ABCDR":
        f = RES / f"verification_{k}.json"
        if f.exists():
            V[k] = json.loads(f.read_text())[k]
    return V


def scenarios_figures(V):
    ans = list(range(2025, 2048))
    fig, ax = plt.subplots(2, 3, figsize=(7.4, 5))
    spec = [("pib", "ecart", "PIB (écart, %)"), ("emploi", "k", "Emploi (écart, milliers)"), ("chomage", "niv", "Chômage (%)"),
            ("solde_pib", "niv", "Solde public (% du PIB)"), ("dette_pib", "niv", "Dette publique (% du PIB)"), ("rdb_reel", "ecart", "Pouvoir d'achat du RDB (écart, %)")]
    ref_trace = False
    for a, (k, mode, titre) in zip(ax.flat, spec):
        for i, (n, v) in enumerate(V.items()):
            T = v["complet"]["traj"]
            if k == "rdb_reel":
                y = [T["rdb"]["ecart"][str(t)] - T["pc"]["ecart"][str(t)] for t in ans]
            elif mode == "k":
                y = [T["emploi"]["scenario"][str(t)] - T["emploi"]["reference"][str(t)] for t in ans]
            elif mode == "niv":
                y = [T[k]["scenario"][str(t)] for t in ans]
            else:
                y = [T[k]["ecart"][str(t)] for t in ans]
            a.plot(ans, y, color=COUL[i], label=NOMS_SC[n], lw=1.6 if n == "R" else 1.1)
        if mode == "niv":
            T = next(iter(V.values()))["complet"]["traj"]
            a.plot(ans, [T[k]["reference"][str(t)] for t in ans], color="black", ls="--", lw=1, label="référence")
        else:
            a.axhline(0, color="black", lw=0.6)
        a.axvline(2028, color="grey", lw=0.5, ls=":")
        a.set_title(titre, fontsize=8)
    ax[0, 0].legend(fontsize=6)
    save(fig, "scenarios")
    fig, ax = plt.subplots(figsize=(6.8, 3))
    w = 0.8 / len(V)
    for i, (n, v) in enumerate(V.items()):
        dd = sorted(v["complet"]["distribution"], key=lambda x: x["decile"])
        ax.bar(np.arange(1, 11) + (i - len(V) / 2) * w + w / 2, [x["variation_pct"] for x in dd], w, label=NOMS_SC[n], color=COUL[i])
    ax.axhline(0, color="black", lw=0.6)
    ax.set_xticks(range(1, 11)); ax.set_xlabel("décile de niveau de vie"); ax.set_ylabel("variation du niveau de vie (%)")
    ax.legend(fontsize=6.5)
    save(fig, "scenarios_distribution")


def scenarios_tableaux(V):
    leviers = [k for k in LIB_CURSEURS if any(k in v["curseurs"] for v in V.values())]
    L = [r"\begin{tabular}{l" + "r" * len(V) + "}", r"\toprule", "Levier & " + " & ".join(V) + r" \\", r"\midrule"]
    for k in leviers:
        L.append(LIB_CURSEURS[k].replace("%", "\\%") + " & " + " & ".join(tex(v["curseurs"][k], 2, False).replace("{,}00", "") if k in v["curseurs"] else
                                                      ("64" if k == "age_legal" else "--") for v in V.values()) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (TAB / "scenarios_mesures.tex").write_text("\n".join(L) + "\n")
    lignes = [("PIB (\\%)", lambda T, t: T["pib"]["ecart"][t], 2), ("Emploi (milliers)", lambda T, t: T["emploi"]["scenario"][t] - T["emploi"]["reference"][t], 0),
              ("Chômage (pt)", lambda T, t: T["chomage"]["ecart"][t], 2), ("Solde public (pt de PIB)", lambda T, t: T["solde_pib"]["ecart"][t], 2),
              ("Dette publique (pt de PIB)", lambda T, t: T["dette_pib"]["ecart"][t], 1), ("Pouvoir d'achat du RDB (\\%)", lambda T, t: T["rdb"]["ecart"][t] - T["pc"]["ecart"][t], 2),
              ("Prix à la consommation (\\%)", lambda T, t: T["pc"]["ecart"][t], 2), ("Investissement (\\%)", lambda T, t: T["fbcf"]["ecart"][t], 2),
              ("Solde extérieur (pt de PIB)", lambda T, t: T["solde_exterieur_pib"]["ecart"][t], 2), ("Industrie (pt de PIB)", lambda T, t: T["part_industrie"]["ecart"][t], 2),
              ("Revenu national brut (\\%)", lambda T, t: T["rnb"]["ecart"][t], 2), ("Pensions (pt de PIB)", lambda T, t: T["pensions_pib"]["ecart"][t], 2)]
    for n, v in V.items():
        T = v["complet"]["traj"]
        L = [r"\begin{tabular}{lrrrrr}", r"\toprule", r"Indicateur (écart à la référence) & 2029 & 2030 & 2032 & 2037 & 2047 \\", r"\midrule"]
        for lib, f, d in lignes:
            L.append(lib + " & " + " & ".join(tex(f(T, str(t)), d) for t in (2029, 2030, 2032, 2037, 2047)) + r" \\")
        L.append(r"\midrule")
        for lib, k, d in (("Chômage (niveau, \\%)", "chomage", 2), ("Solde public (niveau, \\% du PIB)", "solde_pib", 1), ("Dette publique (niveau, \\% du PIB)", "dette_pib", 0)):
            L.append(lib + " & " + " & ".join(tex(T[k]["scenario"][str(t)], d, False) for t in (2029, 2030, 2032, 2037, 2047)) + r" \\")
            L.append("\\quad référence & " + " & ".join(tex(T[k]["reference"][str(t)], d, False) for t in (2029, 2030, 2032, 2037, 2047)) + r" \\")
        i = v["complet"].get("inegalites")
        if i:
            L.append(r"\midrule")
            L.append("Pauvreté, seuil fixe (pt, statique) & \\multicolumn{5}{c}{" + tex(i["apres_seuil_fixe"]["taux_pauvrete"] - i["avant"]["taux_pauvrete"]) + "}" + r" \\")
            L.append("Indice de Gini ($\\times$100, statique) & \\multicolumn{5}{c}{" + tex((i["apres"]["gini"] - i["avant"]["gini"]) * 100) + "}" + r" \\")
            L.append("Niveau de vie médian (\\%, statique) & \\multicolumn{5}{c}{" + tex((i["apres"]["mediane"] / i["avant"]["mediane"] - 1) * 100) + "}" + r" \\")
        L += [r"\bottomrule", r"\end{tabular}"]
        (TAB / f"scenario_{n}.tex").write_text("\n".join(L) + "\n")
    # robustesse
    L = [r"\begin{tabular}{p{4.6cm}" + "rr" * len(V) + "}", r"\toprule",
         "Hypothèse & " + " & ".join(f"\\multicolumn{{2}}{{c}}{{{n}}}" for n in V) + r" \\",
         " & " + " & ".join("PIB 2037 & Dette 2037" for _ in V) + r" \\", r"\midrule"]
    noms = list(next(iter(V.values()))["resistance"].keys())
    for h in noms:
        L.append(h.replace("%", "\\%") + " & " + " & ".join(f"{tex(v['resistance'][h]['pib']['2037']['ecart'])} & {tex(v['resistance'][h]['dette_pib']['2037']['ecart'], 1)}" for v in V.values()) + r" \\")
    mc = " & ".join(f"{tex(v['mi_chemin']['traj']['pib']['ecart']['2037'])} & {tex(v['mi_chemin']['traj']['dette_pib']['ecart']['2037'], 1)}" for v in V.values())
    L.append(r"\midrule")
    L.append("mise en œuvre à moitié (tous les curseurs divisés par 2) & " + mc + r" \\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (TAB / "scenarios_robustesse.tex").write_text("\n".join(L) + "\n")
    L = [r"\begin{tabular}{p{4.6cm}" + "r" * (len(V) + 1) + "}", r"\toprule", "Dette publique en 2037 (\\% du PIB) & " + " & ".join(V) + r" & Référence \\", r"\midrule"]
    for h in noms:
        r0 = next(iter(V.values()))["resistance"][h]["dette_pib"]["2037"]["ref"]
        L.append(h.replace("%", "\\%") + " & " + " & ".join(tex(v["resistance"][h]["dette_pib"]["2037"]["prog"], 0, False) for v in V.values()) + f" & {tex(r0, 0, False)}" + r" \\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (TAB / "scenarios_dette_niveaux.tex").write_text("\n".join(L) + "\n")


def registre():
    import csv
    L = []
    esc = lambda x: str(x).replace("%", "\\%").replace("_", "\\_").replace("&", "\\&").replace("±", "$\\pm$")  # noqa: E731
    with open(R.parent / "outputs" / "registre_parametres.csv", newline="") as f:
        for r in csv.DictReader(f):
            try:
                v = f"{float(r['valeur']):.3g}".replace(".", "{,}").replace("-", "$-$")
            except ValueError:
                v = esc(r["valeur"])
            t = r["t"] if r["t"] not in ("", "nan") else "--"
            L.append(f"{esc(r['parametre'])} & {v} & {esc(r['categorie'])} & {esc(t).replace('-', '$-$')} & {esc(r['confiance'])} & {esc(r['plage']).replace(' à ', ' à ')} \\\\")
    (TAB / "registre.tex").write_text("\n".join(L) + "\n")


def main():
    registre()
    E = charger()
    V = charger_scenarios()
    if V:
        scenarios_figures(V)
        scenarios_tableaux(V)
    schemas()
    figure_reference(E)
    figure_validation()
    figure_seuils()
    figure_interactions(E)
    groupes = {
        "impots": ["ir_bas", "ir_haut", "csg", "tva", "isf", "pfu", "is", "production", "cotisations", "successions", "carbone"],
        "salaires": ["sal2", "sal5", "smic5", "smic10", "point3"],
        "depenses": ["emploi_public", "fonctionnement", "sante", "education", "defense", "invest_public_moins", "indexation", "chomage", "prestations_moins", "transferts_moins"],
        "cotisations": ["cot_moins10", "cot_moins20", "tva_sociale"],
        "investissement": ["invest_public10", "invest_public30", "is_baisse", "logements_sociaux"],
        "industrie": ["reindus10", "reindus20", "reindus10_energie", "douanes10"],
        "prestations": ["rsa25", "ppa25", "af25", "apl_moins10", "aspa25"],
        "travail": ["temps37", "temps32", "age65", "age66", "age62"],
        "complementaires": ["energie50", "energie_moins20", "tva_reduite", "transferts_plus"],
        "interactions": ["cot_moins20", "combi_cot_tva", "tva_sociale", "invest20", "age65", "combi_invest_age", "rsa25", "ppa25", "csg05",
                         "combi_rsa_ppa_csg", "reindus10", "douanes10", "combi_reindus_douane", "emploi_public", "fonctionnement", "combi_emploipub_fonct"],
    }
    choix = {"impots": ["ir_bas", "csg", "tva", "is", "cotisations", "carbone", "production", "successions"],
             "depenses": ["emploi_public", "fonctionnement", "invest_public_moins", "indexation", "chomage", "transferts_moins"],
             "travail": ["temps37", "temps32", "age65", "age66", "age62"]}
    for g, noms in groupes.items():
        tableau_mesures(E, noms, f"tab_{g}", g)
        tableau_detail(E, noms, f"tabd_{g}")
        sel = choix.get(g, noms[:6])
        trajectoires(E, sel, "pib", "PIB en volume", f"pib_{g}")
        trajectoires(E, sel, "dette_pib", "Dette publique", f"dette_{g}", unite="écart en points de PIB")
        trajectoires(E, sel, "chomage", "Taux de chômage", f"chomage_{g}", unite="écart en points")
        trajectoires(E, sel, "solde_pib", "Solde public", f"solde_{g}", unite="écart en points de PIB")
    tableau_rendement(E, "tab_rendement")
    efficacite(E, groupes["impots"] + groupes["depenses"] + ["tva_reduite"], "efficacite_consolidation")
    figure_distribution(E, ["ir_bas", "csg", "tva", "isf", "carbone"], "distribution_impots", "Effet statique sur le niveau de vie par décile : impôts")
    figure_distribution(E, ["rsa25", "ppa25", "af25", "apl_moins10", "aspa25"], "distribution_prestations", "Effet statique sur le niveau de vie par décile : prestations")
    figure_distribution(E, ["indexation", "prestations_moins", "tva_sociale"], "distribution_economies", "Effet statique sur le niveau de vie par décile : économies et TVA sociale")
    trajectoires(E, ["sal2", "sal5", "smic10", "point3"], "inflation", "Inflation", "inflation_salaires", unite="écart en points")
    trajectoires(E, ["sal2", "sal5", "smic10", "point3"], "emploi", "Emploi", "emploi_salaires", unite="écart en %")
    trajectoires(E, ["invest_public10", "invest_public30", "is_baisse"], "fbcf", "Investissement total", "fbcf_invest")
    trajectoires(E, ["reindus10", "reindus20", "reindus10_energie", "douanes10"], "part_industrie", "Part de l'industrie dans le PIB", "industrie_part", unite="écart en points")
    trajectoires(E, ["energie50", "energie_moins20"], "solde_exterieur_pib", "Solde extérieur", "energie_ext", unite="écart en points de PIB")
    trajectoires(E, ["age62", "age65", "age66", "temps37", "temps32"], "pensions_pib", "Pensions", "pensions_travail", unite="écart en points de PIB")
    print("figures :", len(list(FIG.glob('*.pdf'))), "tableaux :", len(list(TAB.glob('*.tex'))))


if __name__ == "__main__":
    main()
