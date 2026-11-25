"""Tableaux et figures des chapitres de résultats (9, 10, 12) et des annexes A, C, E, F, H, K.
Écrit des fichiers d'inclusion dans etude/gen/ ; les gabarits des chapitres y font référence par {{inc:nom}}."""
import json, pathlib, pickle, re, subprocess, sys, warnings
warnings.filterwarnings("ignore")
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src"), str(R), str(R / "etude")]
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from generer import fr, tab, NOMS, COUL, H, FIG, CH, GA, E, RES
import m27_corpus as C

GEN = E / "gen"; GEN.mkdir(exist_ok=True)
VARS = ["PIB (%)", "emploi (milliers)", "chômage (pt)", "salaire réel (%)", "prix (%)", "pouvoir d'achat (%)",
        "consommation (%)", "taux d'épargne (pt)", "investissement (%)", "taux de marge (pt)", "exportations (%)",
        "importations (%)", "solde (pt PIB)", "dette (pt PIB)", "intérêts (pt PIB)", "recettes (pt PIB)", "dépenses (pt PIB)"]
CLES = ["PIB (%)", "emploi (milliers)", "chômage (pt)", "pouvoir d'achat (%)", "solde (pt PIB)", "dette (pt PIB)"]
DEC = {"emploi (milliers)": 0}
SOURCE = "Source : modèle du projet (configuration P4, convention « part constante »), campagne phase7/campagne.py."


def ecrire(nom, texte):
    (GEN / f"{nom}.md").write_text(texte)


def figure(nom, legende):
    return (f"```{{=latex}}\n\\begin{{figure}}[htbp]\\centering\\includegraphics[width=0.95\\textwidth]{{figures/{nom}.pdf}}"
            f"\\caption{{{legende}}}\\end{{figure}}\n```\n")


def t_horizons(res, sim, variables=VARS):
    df = res[sim]
    out = pd.DataFrame({f"{h} ans": df.loc[y, variables] for h, y in H.items()})
    out.index.name = "indicateur (écart à la référence)"
    return out


def comparatif(D, sim, variables=CLES, titre=""):
    blocs = []
    for c, d in D.items():
        if sim not in d["resultats"]:
            continue
        df = d["resultats"][sim]
        for v in variables:
            blocs.append({"candidat": NOMS[c], "indicateur": v, **{f"{h} ans": df.loc[y, v] for h, y in H.items()}})
    t = pd.DataFrame(blocs).set_index(["candidat", "indicateur"])
    t.index = [f"{a} — {b}" for a, b in t.index]; t.index.name = "candidat — indicateur"
    return t


def fig_trajectoires(D, sims, var, nom, ylabel, titre, niveau=False):
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    styles = {"A": "-", "B": "--", "A:oat_382": ":", "B:oat_382": "-."}
    for c, d in D.items():
        for s in sims:
            if s not in d["resultats"]:
                continue
            x = d["resultats"][s][var].loc[2026:2046]
            ax.plot(x.index, x.values, styles.get(s, "-"), color=COUL[c], lw=1.4, label=f"{NOMS[c]} — {s}")
    if niveau and "le_pen" in D:
        # trajectoire de référence (niveau) : A − écart
        d = D["le_pen"]["resultats"]["A"]
        ref = (d["niveau " + ("dette" if "dette" in var else "solde") + " (% PIB)"] - d[("dette" if "dette" in var else "solde") + " (pt PIB)"]).loc[2026:2046]
        ax.plot(ref.index, ref.values, color="grey", lw=1.2, label="référence (sans programme)")
    from matplotlib.ticker import MaxNLocator
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.axhline(0, color="k", lw=0.4); ax.set_ylabel(ylabel); ax.set_title(titre, fontsize=9)
    ax.legend(fontsize=6.5, frameon=False, ncol=2)
    fig.text(0.01, 0.005, SOURCE, fontsize=5.5)
    fig.tight_layout(); fig.savefig(FIG / f"{nom}.pdf"); plt.close(fig)


# ============================================================================================== chapitre 9
def chapitre9(D):
    ecrire("t9_A", "**Tableau : lecture A (mesures documentées), principaux indicateurs.** Écarts à la référence du même "
           "environnement et du même régime (R2 figé, taux exogènes) ; horizons 2031, 2036, 2046. " + SOURCE + "\n\n"
           + tab(comparatif(D, "A"), 1))
    ecrire("t9_B", "**Tableau : lecture B (objectifs budgétaires).** Mesures documentées + effort supplémentaire pour suivre "
           "la trajectoire de solde annoncée, réparti selon les compositions du tableau du chapitre \\ref{sec:prog-regimes}. "
           + SOURCE + "\n\n" + tab(comparatif(D, "B", CLES + ["effort objectif (pt PIB)", "niveau solde (% PIB)", "niveau dette (% PIB)"]), 1))
    # niveaux A et B, deux hypothèses de taux
    rows = []
    for c, d in D.items():
        for s in ("A", "B", "A:oat_382", "B:oat_382"):
            if s in d["resultats"]:
                x = d["resultats"][s]
                rows.append({"candidat — lecture": f"{NOMS[c]} — {s.replace(':oat_382', ', OAT 3,82 %')}",
                             **{f"solde {h} ans (% PIB)": x.loc[y, "niveau solde (% PIB)"] for h, y in H.items() if h in (5, 10)},
                             **{f"dette {h} ans (% PIB)": x.loc[y, "niveau dette (% PIB)"] for h, y in H.items()},
                             "effort B 10 ans (pt)": x.loc[2036, "effort objectif (pt PIB)"]})
    t = pd.DataFrame(rows).set_index("candidat — lecture")
    ecrire("t9_niveaux", "**Tableau : niveaux de solde et de dette publics (% du PIB), lectures A et B, sous deux hypothèses de taux "
           "longs** (OAT à 4,89 %, dernier point observé, ou à 3,82 %, moyenne des douze derniers mois). " + SOURCE + "\n\n" + tab(t, 1, signe=False))
    # écart à la cible (lecture B)
    lignes = ["| candidat | cible annoncée | écart moyen à la cible 2028-2032 (pt) | écart maximal (pt) |", "|---|---|---|---|"]
    for c, d in D.items():
        ec = {int(k): v for k, v in d["meta"].get("B_ecart_cible", {}).items()}
        if not ec:
            continue
        sel = [ec[t] for t in range(2028, 2033) if t in ec]
        lignes.append(f"| {NOMS[c]} | {C.OBJECTIFS[c]['texte']} | {fr(np.mean(sel), 2)} | {fr(max(sel, key=abs), 2)} |")
    ecrire("t9_cible", "**Tableau : atteinte des cibles de la lecture B** (solde simulé − cible annoncée).\n\n" + "\n".join(lignes))
    # décomposition par mesure
    blocs = []
    for c, d in D.items():
        res = d["resultats"]
        mes = {k.split(":")[1]: v for k, v in res.items() if k.startswith("mesure:")}
        if not mes:
            continue
        lib = {m.id: m.intitule for m in C.M}
        t = pd.DataFrame({mid: {"PIB 5 ans (%)": v.loc[2031, "PIB (%)"], "PIB 10 ans (%)": v.loc[2036, "PIB (%)"],
                                "emploi 5 ans (k)": v.loc[2031, "emploi (milliers)"], "solde 5 ans (pt)": v.loc[2031, "solde (pt PIB)"],
                                "dette 10 ans (pt)": v.loc[2036, "dette (pt PIB)"]} for mid, v in mes.items()}).T
        somme = t.sum(); paquet = res["A"]
        t.loc["Σ mesures isolées"] = somme
        t.loc["paquet complet (A)"] = [paquet.loc[2031, "PIB (%)"], paquet.loc[2036, "PIB (%)"], paquet.loc[2031, "emploi (milliers)"],
                                       paquet.loc[2031, "solde (pt PIB)"], paquet.loc[2036, "dette (pt PIB)"]]
        t.loc["interactions (A − Σ)"] = t.loc["paquet complet (A)"] - somme
        t.index = [f"{i} {lib.get(i, '')[:55]}" if i in lib else i for i in t.index]
        t.index.name = "mesure"
        blocs.append(f"\n**Tableau : effets des mesures isolées — {NOMS[c]}** (régime principal ; chaque mesure simulée seule). "
                     + SOURCE + "\n\n" + tab(t, 2))
    ecrire("t9_mesures", "\n".join(blocs))
    # régimes : fourchettes
    rows = []
    for c, d in D.items():
        reg = {k.split(":", 1)[1]: v for k, v in d["resultats"].items() if k.startswith("regime:")}
        for v in ("PIB (%)", "chômage (pt)", "dette (pt PIB)"):
            for h, y in ((5, 2031), (10, 2036), (20, 2046)):
                vals = pd.Series({n: x.loc[y, v] for n, x in reg.items()})
                rows.append({"candidat — indicateur — horizon": f"{NOMS[c]} — {v} — {h} ans",
                             "principal": d["resultats"]["A"].loc[y, v], "minimum": vals.min(), "maximum": vals.max(),
                             "régime du minimum": vals.idxmin(), "régime du maximum": vals.idxmax(),
                             "signe robuste": "oui" if (np.sign(vals) == np.sign(d["resultats"]["A"].loc[y, v])).all() or vals.abs().max() < 0.05 else "non"})
    t = pd.DataFrame(rows).set_index("candidat — indicateur — horizon")
    ecrire("t9_regimes", "**Tableau : lecture A sous les dix régimes de robustesse** (fourchette des effets, régimes extrêmes, "
           "stabilité du signe). " + SOURCE + "\n\n" + tab(t, 2))
    # europe et mise en œuvre
    rows = []
    for c, d in D.items():
        r = d["resultats"]
        for s in ("europe:conforme", "europe:contentieux", "europe:tension", "mise_en_oeuvre:partielle_50", "mise_en_oeuvre:retard_2ans",
                  "additionnalite:50", "additionnalite:25", "additionnalite:0"):
            if s in r:
                x = r[s]
                lab = s.split(':')[1].replace('_', ' ')
                if s.startswith("additionnalite"):
                    lab = f"investissement hors APU additionnel à {lab} %"
                rows.append({"candidat — variante": f"{NOMS[c]} — {lab}",
                             "PIB 5 ans (%)": x.loc[2031, "PIB (%)"], "PIB 10 ans (%)": x.loc[2036, "PIB (%)"],
                             "chômage 5 ans (pt)": x.loc[2031, "chômage (pt)"], "solde 5 ans (pt)": x.loc[2031, "solde (pt PIB)"],
                             "dette 10 ans (pt)": x.loc[2036, "dette (pt PIB)"], "dette 20 ans (pt)": x.loc[2046, "dette (pt PIB)"]})
    t = pd.DataFrame(rows).set_index("candidat — variante")
    ecrire("t9_variantes", "**Tableau : variantes européennes (régime BCE + prime pour les trois) et mise en œuvre partielle (50 %) "
           "ou retardée (2 ans) ; pour LFI, additionnalité de l'investissement hors budget (100 % dans la lecture A ; régime principal)** (écarts à la référence du régime correspondant). " + SOURCE + "\n\n" + tab(t, 2))
    # environnements
    rows = []
    for c, d in D.items():
        r = d["resultats"]
        for s in ("A", "environnement:p4_sigma03", "environnement:p4_sigma06", "environnement:p4_prix_v09"):
            if s in r:
                x = r[s]
                rows.append({"candidat — environnement": f"{NOMS[c]} — {'P4 (référence)' if s == 'A' else s.split(':')[1]}",
                             "PIB 10 ans (%)": x.loc[2036, "PIB (%)"], "emploi 10 ans (k)": x.loc[2036, "emploi (milliers)"],
                             "chômage 10 ans (pt)": x.loc[2036, "chômage (pt)"], "dette 10 ans (pt)": x.loc[2036, "dette (pt PIB)"],
                             "dette 20 ans (pt)": x.loc[2046, "dette (pt PIB)"]})
    t = pd.DataFrame(rows).set_index("candidat — environnement")
    ecrire("t9_environnements", "**Tableau : lecture A dans les environnements alternatifs** (σ = 0,3 et 0,6 ; équation de prix "
           "v0.9). " + SOURCE + "\n\n" + tab(t, 2))
    # figures
    fig_trajectoires(D, ["A", "B"], "PIB (%)", "f9_pib", "écart de PIB (%)", "PIB : écart à la référence, lectures A (trait plein) et B (tirets)")
    fig_trajectoires(D, ["A", "B"], "niveau dette (% PIB)", "f9_dette", "dette publique (% du PIB)",
                     "Dette publique (niveau), lectures A et B — OAT 4,89 %", niveau=True)
    fig_trajectoires(D, ["A:oat_382", "B:oat_382"], "niveau dette (% PIB)", "f9_dette_oat", "dette publique (% du PIB)",
                     "Dette publique (niveau), lectures A et B — OAT 3,82 %")
    fig_trajectoires(D, ["A", "B"], "chômage (pt)", "f9_chomage", "écart de taux de chômage (pt)", "Chômage : écart à la référence")
    fig_trajectoires(D, ["A", "B"], "niveau solde (% PIB)", "f9_solde", "solde public (% du PIB)", "Solde public (niveau), lectures A et B", niveau=True)
    ecrire("f9", figure("f9_pib", "PIB : écart à la référence (lectures A et B).") + figure("f9_chomage", "Chômage : écart à la référence (points).")
           + figure("f9_solde", "Solde public en niveau (lectures A et B ; référence en gris).")
           + figure("f9_dette", "Dette publique en niveau, OAT à 4,89 \\% (référence en gris).")
           + figure("f9_dette_oat", "Dette publique en niveau, OAT à 3,82 \\%."))
    # tableaux complets par candidat (annexe E)
    blocs = []
    for c, d in D.items():
        for s in ("A", "B"):
            blocs.append(f"\n### {NOMS[c]} — lecture {s}\n\n" + tab(t_horizons(d["resultats"], s), 2))
    ecrire("annexe_E_principal", "\n".join(blocs))


# ============================================================================================== chapitre 10
def chapitre10(D):
    blocs = []
    for c, d in D.items():
        tr = d["traductions"].get("A", {})
        dist = tr.get("distribution")
        if not dist:
            blocs.append(f"\n*{NOMS[c]} : aucune mesure du paquet n'a d'incidence ménage par ménage représentée.*\n")
            continue
        t = pd.DataFrame(dist).set_index("decile")
        t = t[["niveau_de_vie_moyen", "variation_euros_par_uc", "variation_pct", "part_gagnants", "part_perdants"]]
        t["part_gagnants"] *= 100; t["part_perdants"] *= 100
        t.columns = ["niveau de vie moyen (€/UC)", "variation (€/UC/an)", "variation (%)", "gagnants (%)", "perdants (%)"]
        t.index.name = "décile"
        ineg = tr.get("inegalites") or {}
        txt = ""
        if ineg:
            a, b = ineg.get("avant", {}), ineg.get("apres", {})
            txt = (f"\n\nIndicateurs (avant → après, effet statique) : indice de Gini {fr(a.get('gini'), 4, False)} → {fr(b.get('gini'), 4, False)} ; "
                   f"rapport interdécile D9/D1 {fr(a.get('d9_d1'), 3, False)} → {fr(b.get('d9_d1'), 3, False)} ; "
                   f"taux de pauvreté (seuil à 60 % de la médiane) {fr(a.get('taux_pauvrete'), 2, False)} % → {fr(b.get('taux_pauvrete'), 2, False)} %.")
        mm = tr.get("mesure_menages") or {}
        cov = (f" Montants agrégés pris en compte par la microsimulation : impôts {fr(mm.get('impots', 0) / 1e3, 1)} Md€, prestations "
               f"{fr(mm.get('prestations', 0) / 1e3, 1)} Md€ (euros de 2024).")
        blocs.append(f"\n**Tableau : effets statiques par décile de niveau de vie — {NOMS[c]}** (mesures dont l'incidence ménage par "
                     "ménage est représentée ; revenus de 2024, comportements inchangés)." + cov + "\n\n" + tab(t, 1, signe=False) + txt)
        grp = tr.get("groupes") or {}
        if grp.get("age"):
            g = pd.DataFrame(grp["age"]).T[["variation_euros_par_uc", "variation_pct", "part_gagnants", "poids"]]
            g["part_gagnants"] *= 100; g["poids"] *= 100
            g.columns = ["variation (€/UC/an)", "variation (%)", "gagnants (%)", "poids (%)"]
            g.index.name = "âge de la personne de référence"
            blocs.append("\n" + tab(g, 1, signe=False))
    ecrire("t10_deciles", "\n".join(blocs))
    # effets générationnels des réformes des retraites
    import m9_retraites as M9
    act = M9.ActiviteSeniors()
    rows = []
    import simulateur.executer as X
    for c in NOMS:
        for m in C.M:
            if m.candidat == c and m.canal and m.canal[0][0] == "retraites" and m.id != "L36":
                p = dict(m.canal[0][1]); p["debut"] = m.debut
                regle = X.regle_age(p)
                e = M9.effets_generationnels(regle, act, generations=(1960, 1965, 1970, 1975, 1980, 1990))
                for _, r in e.iterrows():
                    rows.append({"candidat — génération — sexe": f"{NOMS[c]} — {int(r.generation)} — {r.sexe}",
                                 "AOD actuelle": r.aod_actuelle, "AOD réforme": r.aod_regle,
                                 "durée actuelle (trim.)": r.duree_actuelle_trim, "durée réforme (trim.)": r.duree_regle_trim,
                                 "écart d'âge pivot (ans)": r.ecart_pivot_ans, "facteur de pension": r.facteur_pension})
    t = pd.DataFrame(rows).set_index("candidat — génération — sexe")
    ecrire("t10_generations", "**Tableau : effets générationnels moyens des réformes des retraites (module M9).** Âge d'ouverture des "
           "droits (AOD), durée requise, écart d'âge pivot du profil d'activité (≈ report moyen de la cessation d'activité ; "
           "l'écart de durée de retraite attendue en est l'opposé, à espérance de vie inchangée) et facteur de niveau de pension dû "
           "à la durée requise. Effets moyens, non individuels.\n\n" + tab(t, 2, signe=False))


# ============================================================================================== chapitre 12
def chapitre12(D):
    p5 = R / "phase5" / "resultats"
    syn = pd.read_csv(p5 / "lot53_synthese_S1_S5.csv")
    x = syn[syn.horizon.isin([10, 20]) & syn.variable.isin(["PIB (%)", "chômage (pt)", "dette (pt PIB)", "emploi (milliers)"])]
    x = x.set_index(["stratégie", "horizon", "variable"])[["principal", "min", "max", "signe robuste"]]
    x["signe robuste"] = x["signe robuste"].map({True: "oui", False: "non"})
    x.index = [f"{a} — {b} ans — {c}" for a, b, c in x.index]; x.index.name = "stratégie — horizon — indicateur"
    ecrire("t12_S", "**Tableau : stratégies de test S1-S5 sous les dix régimes** (principal, minimum, maximum, stabilité du signe). "
           "Source : phase5/resultats/lot53_synthese_S1_S5.csv.\n\n" + tab(x, 2))
    cl = pd.read_csv(p5 / "lot53_classements_S1_S5.csv", header=[0, 1], index_col=0)
    ecrire("t12_classements", "**Tableau : classements des stratégies S1-S5 par régime** (du plus favorable au moins favorable). Source : "
           "phase5/resultats/lot53_classements_S1_S5.csv.\n\n" + cl.to_markdown())
    # robustesse des candidats : part des signes robustes
    rows = []
    for c, d in D.items():
        reg = {k: v for k, v in d["resultats"].items() if k.startswith("regime:") or k.startswith("environnement:")}
        for v in ("PIB (%)", "emploi (milliers)", "chômage (pt)", "pouvoir d'achat (%)", "solde (pt PIB)", "dette (pt PIB)"):
            for h, y in H.items():
                vals = pd.Series({n: s.loc[y, v] for n, s in reg.items()})
                ref = d["resultats"]["A"].loc[y, v]
                rows.append({"candidat": NOMS[c], "indicateur": v, "horizon": h, "robuste": bool((np.sign(vals) == np.sign(ref)).all() or vals.abs().max() < 0.05),
                             "étendue": vals.max() - vals.min(), "principal": ref})
    r = pd.DataFrame(rows)
    p = r.pivot_table(index=["candidat", "indicateur"], columns="horizon", values="robuste", aggfunc="first").replace({True: "oui", False: "non"})
    p.columns = [f"signe robuste à {h} ans" for h in p.columns]
    e = r.pivot_table(index=["candidat", "indicateur"], columns="horizon", values="étendue")
    e.columns = [f"étendue à {h} ans" for h in e.columns]
    t = pd.concat([p, e], axis=1); t.index = [f"{a} — {b}" for a, b in t.index]; t.index.name = "candidat — indicateur"
    ecrire("t12_candidats", "**Tableau : robustesse de la lecture A des programmes aux dix régimes et aux trois environnements "
           "alternatifs** (signe identique dans les 13 variantes ; étendue max − min). " + SOURCE + "\n\n" + tab(t, 2))
    share = r.groupby("indicateur").robuste.mean() * 100
    ecrire("t12_part", " ; ".join(f"{k} : {fr(v, 0, False)} %" for k, v in share.items()))
    for nom, fich in (("structurels", "lot53_structurels_S1_S5.csv"), ("monetaires", "lot53_structurels_monetaires_S1_S5.csv")):
        f = p5 / fich
        if f.exists():
            s = pd.read_csv(f)
            s = s[s.horizon == 20]
            cen = s[s["paramètre"].str.startswith("central")].groupby("stratégie")[["PIB (%)", "dette (pt PIB)"]].first()
            out = []
            for pnom, g in s[~s["paramètre"].str.startswith("central")].groupby("paramètre"):
                dv = {v: (g.set_index("stratégie")[v] - cen[v].reindex(g["stratégie"]).values).abs().max() for v in ("PIB (%)", "dette (pt PIB)")}
                out.append({"paramètre": pnom, "amplitude PIB 20 ans (pt de %)": dv["PIB (%)"], "amplitude dette 20 ans (pt)": dv["dette (pt PIB)"]})
            ecrire(f"t12_{nom}", tab(pd.DataFrame(out).set_index("paramètre"), 2, signe=False))


# ============================================================================================== annexes
def annexes(D):
    # A : registre des paramètres
    import m23_regimes as G
    import m24_monetaire as M24
    lignes = ["| paramètre | catégorie | valeur centrale | basse | haute | statut | source, justification |", "|---|---|---|---|---|---|---|"]
    for k, (cat, c0, b, h, st, src) in G.STRUCTURELS.items():
        lignes.append(f"| `{k}` | {cat} | {c0 if c0 is not None else 'estimé (M24)'} | {b} | {h} | {st} | {src} |")
    pm = M24.parametres()
    l2 = ["| paramètre (M24) | valeur | statut |", "|---|---|---|"]
    for k, v in pm.items():
        l2.append(f"| `{k}` | {fr(v, 4, False) if isinstance(v, float) else v} | [E] |")
    import m9_retraites as M9
    l3 = ["| paramètre (M9) | valeur | statut | source |", "|---|---|---|---|",
          f"| report par année de durée requise, hommes | {M9.ELASTICITE_DUREE['M']} an | [E, littérature] | Bozio (2011) |",
          f"| report par année de durée requise, femmes | {fr(M9.ELASTICITE_DUREE['F'], 3, False)} an | [E, littérature] | Bozio (2011) |",
          f"| part de la pension soumise à proratisation et décote | {M9.PART_PENSION_BASE} | [H] | ordre de grandeur |",
          f"| décote par année manquante | {M9.DECOTE_PAR_AN} | [D] | code de la sécurité sociale |",
          f"| part des carrières longues | {M9.PART_CARRIERES_LONGUES} | [D] | CNAV, données 2024 |",
          f"| coefficient sur l'écart de masse des pensions | {M9.COEF_PENSION_MARGINALE} | [C] | étude d'impact 2023, Institut Montaigne |"]
    reg = ["| paramètre de régime | valeur | statut |", "|---|---|---|"]
    rb = G.RegleBudgetaire()
    for k in ("debut", "alpha", "beta", "dette_cible", "plafond", "ecart_suspension", "epsilon"):
        reg.append(f"| `{k}` | {getattr(rb, k)} | [H] |")
    reg.append(f"| répartition de l'effort | {rb.parts} | [H] |")
    v08 = (R / "doc" / "20_registre_parametres_v08.md").read_text()
    v08 = v08[v08.index("## Bouclage"):]
    v08 = re.sub(r"^## ", "### ", v08, flags=re.M)
    ecrire("annexe_A", "### Paramètres structurels modifiables sans recalibration (M23)\n\n" + "\n".join(lignes) +
           "\n\n### Politique monétaire et conditions financières (M24, estimés)\n\n" + "\n".join(l2) +
           "\n\n### Retraites (M9, finalisation)\n\n" + "\n".join(l3) + "\n\n### Règle budgétaire R2 (M23)\n\n" + "\n".join(reg) +
           "\n\n### Registre détaillé de la version 0.8 (toujours en vigueur pour ces paramètres)\n\n" + v08)
    # C : registre des mesures (règles de conversion)
    ecrire("annexe_C", "\n".join(f"- **{m.id}** ({NOMS[m.candidat]}) — {m.intitule}. *Sources* : {', '.join(m.sources)}. "
                                 f"*Règle* : {m.regle or '—'}" for m in C.M) + "\n\n**Sources du corpus.**\n\n"
           + "\n".join(f"- `{k}` : {v}" for k, v in C.SOURCES.items()))
    # E : toutes les simulations, indicateurs clés
    blocs = []
    for c, d in D.items():
        rows = {k: {f"{v} {h}a": x.loc[y, v] for v in ("PIB (%)", "chômage (pt)", "dette (pt PIB)") for h, y in H.items() if h in (5, 10, 20)}
                for k, x in d["resultats"].items()}
        t = pd.DataFrame(rows).T; t.index.name = "simulation"
        blocs.append(f"\n### {NOMS[c]} — toutes les simulations\n\n" + tab(t, 2))
    ecrire("annexe_E_toutes", "\n".join(blocs))
    # F : tests
    try:
        out = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q", "tests/test_finalisation.py", "tests/test_phase6.py",
                              "tests/test_lot53.py", "tests/test_lot52.py", "tests/test_phase5.py", "tests/test_phase43.py"],
                             cwd=R, capture_output=True, text=True, timeout=600).stdout
        tests = [l for l in out.splitlines() if "::" in l]
    except Exception as ex_:
        tests = [f"(collecte impossible : {ex_})"]
    ecrire("annexe_F_tests", "\n".join(f"- `{t}`" for t in tests))


# ============================================================================================== chapitre 14 et annexe K
def chapitre14(D):
    """Tableau de synthèse : lectures A et B, fourchette des 13 variantes (10 régimes + 3 environnements) pour A."""
    rows = []
    for c, d in D.items():
        r = d["resultats"]
        var = {k: v for k, v in r.items() if k.startswith(("regime:", "environnement:"))}
        for v in ("PIB (%)", "chômage (pt)", "pouvoir d'achat (%)", "dette (pt PIB)"):
            for h in (5, 10):
                y = H[h]
                vals = [x.loc[y, v] for x in var.values()]
                rows.append({"candidat — indicateur — horizon": f"{NOMS[c]} — {v} — {h} ans",
                             "lecture A": r["A"].loc[y, v], "min. variantes A": min(vals) if vals else np.nan,
                             "max. variantes A": max(vals) if vals else np.nan,
                             "lecture B": r["B"].loc[y, v] if "B" in r else np.nan})
    t = pd.DataFrame(rows).set_index("candidat — indicateur — horizon")
    ecrire("t14_synthese", "**Tableau : synthèse des résultats, horizons de 5 et 10 ans.** Lecture A (mesures documentées) avec la "
           "fourchette de ses treize variantes (dix régimes, trois environnements) ; lecture B (objectifs budgétaires). Écarts à la "
           "référence. " + SOURCE + "\n\n" + tab(t, 2))


TRACE = [
    # (conclusion, simulations, tableaux / sections, sources)
    ("R1. Les mesures d'offre de travail sont les plus structurantes pour l'activité à moyen terme : retraites pour LFI et le "
     "RN (effet négatif), fin des 35 heures puis retraites pour Horizons (effet positif).", "mesure:L34, mesure:P08, mesure:H05, mesure:H06 ; A", "t9_mesures ; t10_generations ; ch. 9, 10",
     "LFI_BUDGET ; RN_RETRAITES_PS ; EP_COMPTES ; Bozio (2011) ; CNAV 2024"),
    ("R2. Les signes des effets importants (PIB à cinq ans, dette de LFI et d'Horizons à dix ans, chômage) sont stables dans les "
     "dix régimes et les trois environnements ; les effets proches de zéro ne le sont pas.",
     "regime:* ; environnement:*", "t12_candidats ; t12_part ; ch. 12", "phase7/resultats/*_synthese.csv"),
    ("R3. L'ampleur des effets sur le chômage est peu fiable ; pour les stratégies S1-S5, leur signe est aussi moins robuste "
     "que celui des effets sur le PIB et la dette.",
     "regime:* ; environnement:* ; S1-S5", "t12_S ; t12_candidats ; ch. 12", "phase5/resultats/lot53_synthese_S1_S5.csv"),
    ("R4. Les mesures documentées du RN et d'Horizons ne représentent qu'une faible part de l'effort nécessaire à leurs "
     "objectifs de déficit ; celles de LFI dépassent à court terme l'effort requis par son objectif.", "A ; B ; B:oat_382",
     "t9_B ; t9_cible ; t9_niveaux ; ch. 9", "RN_MONEYVOX ; EP_COMPTES ; LFI_BUDGET"),
    ("R5. Atteindre les objectifs de déficit du RN et d'Horizons dans ce modèle demande un effort de plusieurs points de PIB, "
     "aux effets récessifs importants ; l'ampleur dépend de l'hypothèse de taux longs.", "B ; B:oat_382 ; B_variante_2pc",
     "t9_B ; t9_niveaux ; ch. 9, 12", "doc 22 (référence) ; M24"),
    ("R6. Les résultats de LFI dépendent fortement de la traduction des recettes sans canal propre et de l'additionnalité de "
     "l'investissement hors budget.", "A ; additionnalite:* ; mesure:L03, L08-L16, L33", "t9_mesures ; t9_variantes ; ch. 9",
     "LFI_BUDGET"),
    ("R7. Les variantes européennes modifient peu les effets à cinq ans ; la variante « tension » pèse surtout sur la dette à "
     "long terme.", "europe:conforme, contentieux, tension", "t9_variantes ; ch. 8, 9", "règlement (UE) 2024/1264 ; directive 2022/542"),
    ("R8. Les effets distributifs statiques diffèrent par leur concentration : prélèvements sur le haut de la distribution "
     "(LFI), gains diffus (RN), pertes concentrées sur les allocataires du RSA (Horizons).", "traductions A (microsimulation)",
     "t10_deciles ; ch. 10", "OpenFisca-France ; M4"),
    ("R9. Une mise en œuvre à 50 % divise les effets à peu près par deux ; un retard de deux ans décale les effets de court "
     "terme.", "mise_en_oeuvre:*", "t9_variantes ; ch. 9", "—"),
    ("R10. Les multiplicateurs simulés diminuent avec l'horizon ; ils sont plus élevés pour la consommation publique que "
     "pour les transferts et les baisses de prélèvements sur les entreprises.", "multiplicateurs", "ch. 7",
     "phase7/resultats/multiplicateurs.csv ; Blanchard et Leigh (2013) ; Ramey (2019)"),
]


def annexe_k(D):
    l = ["| conclusion | simulations (clés de `phase7/resultats/<candidat>.pkl`) | tableaux et sections | sources |",
         "|---|---|---|---|"]
    for a, b, c, d in TRACE:
        l.append(f"| {a} | {b} | {c} | {d} |")
    ecrire("annexe_K", "\n".join(l))


def generer(D):
    chapitre9(D); chapitre10(D); chapitre12(D); annexes(D); chapitre14(D); annexe_k(D)
    for g in sorted(GA.glob("*.md")):
        if g.name in ("06_programmes.md", "07_transmission.md"):
            continue
        txt = g.read_text()
        for m in re.findall(r"\{\{inc:([a-zA-Z0-9_]+)\}\}", txt):
            f = GEN / f"{m}.md"
            txt = txt.replace("{{inc:" + m + "}}", f.read_text() if f.exists() else f"*(élément « {m} » non généré)*")
        (CH / g.name).write_text(txt)
