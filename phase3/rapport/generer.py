"""Tables (LaTeX) et figures du rapport de phase 3, à partir des résultats exécutés (phase3/resultats/*.json).
Aucune valeur n'est saisie à la main : tout est lu dans les fichiers de résultats."""
import json
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

R = pathlib.Path(__file__).resolve().parents[2]
RES = R / "phase3" / "resultats"
V06 = R / "rapport" / "resultats"
TAB = R / "phase3" / "rapport" / "tables"
FIG = R / "phase3" / "rapport" / "figures"
TAB.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
sys.path[:0] = [str(R / "phase3")]
import optimisation as O  # noqa: E402

BLEU, ORANGE, VERT, ROUGE, GRIS = "#1F4E79", "#C55A11", "#2C7C3C", "#A61B1B", "#777777"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
STRAT_NOMS = {"S1_protection": "S1 Protection", "S2_emploi": "S2 Emploi", "S3_productivite": "S3 Productivité",
              "S4_redressement": "S4 Redressement", "S5_global": "S5 Global", "v06_A": "A (v0.6)", "v06_B": "B (v0.6)",
              "v06_C": "C (v0.6)", "v06_D": "D (v0.6)", "v06_R": "R (v0.6)"}
LIB_LEV = {"ir_t1": "IR 1re tranche (pt)", "ir_t4": "IR tranche sup. (pt)", "csg_activite": "CSG activité (pt)", "tva": "TVA normale (pt)",
           "tva_reduite": "TVA réduite (pt)", "isf": "Impôt fortune (%)", "pfu": "PFU (pt)", "taux_is": "IS (pt)",
           "impots_production": "Impôts production (Md€)", "cotisations_employeurs": "Cotis. employeurs (Md€)", "successions": "Successions (%)",
           "taxe_carbone": "Taxe carbone (€/t)", "smic": "SMIC (%)", "point_indice": "Point d'indice (%)", "emploi_public": "Emplois publics (k)",
           "autres_depenses": "Fonctionnement (Md€)", "sante": "Santé (Md€)", "education": "Éducation (Md€)", "defense": "Défense (Md€)",
           "investissement_public": "Invest. public (Md€)", "indexation_pensions": "Indexation pensions (pt/an)",
           "assurance_chomage": "Allocations chômage (%)", "allocations_familiales": "Alloc. familiales (%)", "aides_logement": "Aides logement (%)",
           "rsa": "RSA (%)", "prime_activite": "Prime d'activité (%)", "minimum_vieillesse": "Minimum vieillesse (%)",
           "transferts_menages": "Transferts (pt PIB)", "logements_sociaux": "Logements sociaux (k/an)", "reindustrialisation": "Relocalisation (%)",
           "droits_douane": "Droits de douane (%)", "temps_travail": "Durée du travail (h)", "age_legal": "Âge légal (ans)",
           "recherche": "Aide R\\&D (Md€)", "formation": "Formation (Md€)"}
LIB_LEV = {k: v.replace("%", r"\%") for k, v in LIB_LEV.items()}


def f(x, d=2, signe=True):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "---"
    s = f"{x:+.{d}f}" if signe else f"{x:.{d}f}"
    return "$" + s.replace(".", "{,}").replace("-", "-") + "$"


def ecrire(nom, texte):
    (TAB / nom).write_text(texte)


def ec(tr, k, t, typ):
    s = str(t)
    if k == "rdb_reel":
        a = tr["rdb"]["scenario"][s] / tr["pc"]["scenario"][s]
        b = tr["rdb"]["reference"][s] / tr["pc"]["reference"][s]
        return 100 * (a / b - 1)
    if k not in tr:
        return None
    sc, rf = tr[k]["scenario"].get(s), tr[k]["reference"].get(s)
    if sc is None:
        return None
    return 100 * (sc / rf - 1) if typ == "pct" else sc - rf


def charger_exp(dossier, motif):
    out = {}
    for p in sorted(dossier.glob(motif)):
        if "comportements" in p.name:
            continue
        out.update(json.loads(p.read_text()))
    return out


# ------------------------------------------------------------------------------------------------------------------
def diagnostic():
    d6 = json.loads((RES / "diagnostic_v06.json").read_text())
    d7 = json.loads((RES / "diagnostic_v07.json").read_text())
    lignes = []
    for cle in [k for k in d6 if "rho=central" in k]:
        lib = cle.split(" | ")[0].replace("%", r"\%")
        for v, d in (("v0.6", d6), ("v0.7", d7)):
            x = d[cle]
            lignes.append(f"{lib if v == 'v0.6' else ''} & {v} & " + " & ".join(
                f(x[k]["2037"]) for k in ("pib", "emploi", "chomage", "pc", "dette_pib", "solde_pib")) + r"\\")
        lignes.append(r"\addlinespace")
    ecrire("diagnostic.tex", r"\begin{tabular}{llrrrrrr}\toprule Choc & Version & PIB (\%) & Emploi (\%) & Chômage (pt) & Prix (\%) & Dette (pt) & Solde (pt)\\ \midrule" + "\n" +
           "\n".join(lignes[:-1]) + r"\bottomrule\end{tabular}")
    # figure : trajectoires du choc de productivité
    cle = [k for k in d6 if "productivit" in k and "rho=central" in k][0]
    fig, ax = plt.subplots(1, 3, figsize=(10, 2.9))
    for i, (k, lib) in enumerate((("pib", "PIB en volume (%)"), ("chomage", "Chômage (points)"), ("dette_pib", "Dette publique (points de PIB)"))):
        for v, d, c in (("v0.6", d6, GRIS), ("v0.7", d7, BLEU)):
            ans = sorted(int(a) for a in d[cle][k])
            ax[i].plot(ans, [d[cle][k][str(a)] for a in ans], "o-", color=c, label=v, lw=1.6, ms=4)
        ax[i].axhline(0, color="#999", lw=0.6)
        ax[i].set_title(lib, fontsize=9)
    ax[0].legend(frameon=False)
    fig.suptitle("Productivité −0,3 point par an à partir de 2028 : écarts à la référence", fontsize=9.5)
    fig.tight_layout()
    fig.savefig(FIG / "diagnostic_productivite.pdf")
    plt.close(fig)


def comparaison():
    e6, e7 = charger_exp(V06, "experiences_*.json"), charger_exp(RES, "experiences_v07_*.json")
    sel = ["tva", "tva_moins1", "csg", "ir_bas", "is", "is_baisse", "cot_moins20", "tva_sociale", "invest20", "fonctionnement",
           "emploi_public", "indexation", "chomage", "rsa25", "ppa25", "apl_moins10", "age65", "age62", "temps37", "reindus10",
           "energie50", "recherche3", "formation2"]
    lignes = []
    for n in sel:
        if n not in e7:
            continue
        lib = e7[n]["libelle"].replace("%", r"\%").replace("&", r"\&")
        r = []
        for e in (e6.get(n), e7[n]):
            if e is None or "traj" not in e:
                r += ["---"] * 4
                continue
            tr = e["traj"]
            r += [f(ec(tr, "pib", 2037, "pct")), f(ec(tr, "emploi", 2037, "niv"), 0), f(ec(tr, "chomage", 2037, "niv")), f(ec(tr, "dette_pib", 2037, "niv"), 1)]
        lignes.append(lib + " & " + " & ".join(r) + r"\\")
    ecrire("comparaison.tex", r"\begin{tabular}{p{6.2cm}rrrr|rrrr}\toprule & \multicolumn{4}{c|}{v0.6} & \multicolumn{4}{c}{v0.7}\\ Mesure & PIB & Emploi & Chôm. & Dette & PIB & Emploi & Chôm. & Dette\\ \midrule" +
           "\n" + "\n".join(lignes) + r"\bottomrule\end{tabular}")
    # figure : PIB et dette 2037, v0.6 contre v0.7
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
    for i, (k, typ, lib) in enumerate((("pib", "pct", "PIB 2037 (%)"), ("dette_pib", "niv", "Dette 2037 (points de PIB)"))):
        xs, ys, noms = [], [], []
        for n in e7:
            if n in e6 and "traj" in e6[n] and "traj" in e7[n]:
                xs.append(ec(e6[n]["traj"], k, 2037, typ))
                ys.append(ec(e7[n]["traj"], k, 2037, typ))
                noms.append(n)
        ax[i].scatter(xs, ys, s=14, color=BLEU)
        lim = [min(xs + ys), max(xs + ys)]
        ax[i].plot(lim, lim, color=GRIS, lw=0.7, ls="--")
        for x, y, n in zip(xs, ys, noms):
            if abs(y - x) > (0.6 if k == "pib" else 2.5):
                ax[i].annotate(n, (x, y), fontsize=6.5, color=ORANGE, xytext=(3, 2), textcoords="offset points")
        ax[i].set_xlabel("v0.6")
        ax[i].set_ylabel("v0.7")
        ax[i].set_title(lib, fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG / "comparaison_v06_v07.pdf")
    plt.close(fig)


def comportements():
    c = json.loads((RES / "experiences_v07_comportements.json").read_text())
    e7 = charger_exp(RES, "experiences_v07_*.json")
    noms = sorted({k.split("|")[0] for k in c}, key=lambda n: list(e7).index(n) if n in e7 else 99)
    lignes = []
    for n in noms:
        lib = e7[n]["libelle"].replace("%", r"\%").replace("&", r"\&")
        r = []
        for k, typ, d in (("pib", "pct", 2), ("chomage", "niv", 2), ("dette_pib", "niv", 1)):
            for niv in ("basse", "centrale", "haute"):
                e = e7[n] if niv == "centrale" else c.get(f"{n}|{niv}")
                r.append(f(ec(e["traj"], k, 2037, typ), d) if e and "traj" in e else "---")
        lignes.append(lib + " & " + " & ".join(r) + r"\\")
    ecrire("comportements.tex", r"\begin{tabular}{p{4.6cm}rrr|rrr|rrr}\toprule & \multicolumn{3}{c|}{PIB (\%)} & \multicolumn{3}{c|}{Chômage (pt)} & \multicolumn{3}{c}{Dette (pt)}\\ Mesure (2037) & bas & central & haut & bas & central & haut & bas & central & haut\\ \midrule" +
           "\n" + "\n".join(lignes) + r"\bottomrule\end{tabular}")


def optimisation():
    o = json.loads((RES / "optimisation_v07.json").read_text())
    P = o["perimetres"]
    # composition des stratégies (trois périmètres)
    for per in P:
        S = P[per]["strategies"]
        levs = sorted({l for s in S.values() for l in s.get("leviers", {})}, key=lambda l: list(O.LEVIERS).index(l))
        lignes = []
        for l in levs:
            r = [f(S[s]["leviers"][l], 1) if l in S[s].get("leviers", {}) else "" for s in S]
            lignes.append(f"{LIB_LEV.get(l, l)} & {O.NIVEAU.get(l, 'A')} & " + " & ".join(r) + r"\\")
        lignes.append(r"\midrule")
        for c, (lib, sens) in list(O.CRITERES.items()) + [("solde", ("Solde public (pt)", 1)), ("emploi", ("Emploi (milliers)", 1))]:
            r = [f(S[s]["metamodele"]["2037"][c], 0 if c == "emploi" else 2) if "metamodele" in S[s] else "" for s in S]
            lignes.append(f"{lib.replace('%', chr(92) + '%')} & & " + " & ".join(r) + r"\\")
        ecrire(f"strategies_{per}.tex", r"\begin{tabular}{p{4.8cm}c" + "r" * len(S) + r"}\toprule Levier (écart à l'actuel) & Niv. & " +
               " & ".join(STRAT_NOMS.get(s, s).replace(" ", r"\\ ", 1).join([r"\makecell{", "}"]) for s in S) + r"\\ \midrule" + "\n" + "\n".join(lignes) + r"\bottomrule\end{tabular}")
    # efficacité des leviers (périmètre complet), à la borne
    E = P["avec_exploratoires"]["efficacite"]
    lignes = []
    for k, v in sorted(E.items(), key=lambda kv: list(O.LEVIERS).index(kv[0].split("|")[0])):
        lev, sens = k.split("|")
        b = v["borne"] * (1 if sens == "hausse" else -1)
        lignes.append(f"{LIB_LEV.get(lev, lev)} & {f(b, 1)} & {O.NIVEAU.get(lev, 'A')} & {f(v['pib'])} & {f(v['chomage'])} & {f(v['dette'], 1)} & {f(v['modestes'])} & {f(v['gini'])}\\\\")
    ecrire("efficacite.tex", r"{\scriptsize\setlength{\tabcolsep}{3pt}\begin{longtable}{p{4.2cm}rcrrrrr}\caption{Effet de chaque levier poussé à sa borne, seul (modèle complet, comportements centraux, écart à la référence en 2037 ; niveau de vie des 30 \% les plus modestes et Gini : microsimulation statique).}\label{tab:efficacite}\\ \toprule Levier & Valeur & Niv. & PIB (\%) & Chômage (pt) & Dette (pt) & Modestes (\%) & Gini (×100)\\ \midrule\endfirsthead \toprule Levier & Valeur & Niv. & PIB & Chômage & Dette & Modestes & Gini\\ \midrule\endhead" +
           "\n" + "\n".join(lignes) + r"\bottomrule\end{longtable}}")
    # robustesse aux préférences
    rp = P["principal"]["robustesse_preferences"]
    lignes = [f"{LIB_LEV.get(k.split('|')[0], k)} & {k.split('|')[1]} & {f(100 * v, 0, False)}\\\\" for k, v in list(rp["frequence"].items())[:18]]
    ecrire("preferences.tex", r"\begin{tabular}{lll}\toprule Levier & Sens & Fréquence (\%)\\ \midrule" + "\n" + "\n".join(lignes) + r"\bottomrule\end{tabular}")
    # figures : fronts de Pareto
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.9))
    for i, (a, b, la, lb) in enumerate((("chomage", "dette", "Chômage 2037 (points)", "Dette 2037 (points de PIB)"),
                                        ("modestes", "dette", "Niveau de vie des 30 % les plus modestes (%)", "Dette 2037 (points de PIB)"))):
        for per, c, lab in (("principal", BLEU, "périmètre principal (A+B)"), ("avec_exploratoires", ORANGE, "avec leviers exploratoires (C)")):
            nu = np.array(P[per]["pareto"][f"nuage|{a}|{b}"])
            if per == "principal":
                ax[i].scatter(nu[:, 0], nu[:, 1], s=2, color="#c9d6e3", label="portefeuilles aléatoires (A+B)")
            fr = np.array([[x[0], x[1]] for x in P[per]["pareto"][f"exact|{a}|{b}"]])
            fr = fr[np.argsort(fr[:, 0])]
            ax[i].plot(fr[:, 0], fr[:, 1], "o-", ms=2.5, color=c, lw=1.6, label=f"front de Pareto, {lab}")
        for s, v in P["principal"]["strategies"].items():
            if "metamodele" in v:
                m = v["metamodele"]["2037"]
                ax[i].scatter([m[a]], [m[b]], color=ROUGE, s=22, zorder=5)
                ax[i].annotate(STRAT_NOMS[s].split()[0], (m[a], m[b]), fontsize=7.5, color=ROUGE, xytext=(3, 3), textcoords="offset points")
        ax[i].set_xlabel(la)
        ax[i].set_ylabel(lb)
        ax[i].axhline(0, color="#999", lw=0.5)
        ax[i].axvline(0, color="#999", lw=0.5)
    ax[0].legend(frameon=False, fontsize=6.5, loc="upper right")
    fig.tight_layout()
    fig.savefig(FIG / "pareto.pdf")
    plt.close(fig)
    return o


def verification():
    progs = [p.stem.replace("verification_v07_", "") for p in sorted(RES.glob("verification_v07_*.json"))]
    ordre = [s for s in STRAT_NOMS if s in progs]
    V = {p: json.loads((RES / f"verification_v07_{p}.json").read_text()) for p in ordre}
    o = json.loads((RES / "optimisation_v07.json").read_text())
    S = o["perimetres"]["principal"]["strategies"]
    # trajectoires 5/10/15/20 ans (modèle complet)
    IND = (("pib", "pct", "PIB (\\%)"), ("emploi", "niv", "Emploi (milliers)"), ("chomage", "niv", "Chômage (pt)"), ("rdb_reel", "pct", "RDB réel (\\%)"),
           ("solde_pib", "niv", "Solde (pt)"), ("dette_pib", "niv", "Dette (pt)"))
    lignes = []
    for p in ordre:
        tr = V[p]["complet"]["traj"]
        for j, (k, typ, lib) in enumerate(IND):
            r = [f(ec(tr, k, t, typ), 0 if k == "emploi" else (1 if k == "dette_pib" else 2)) for t in (2032, 2037, 2042, 2047)]
            meta = ""
            if p in S and "metamodele" in S[p]:
                mk = {"pib": "pib", "emploi": "emploi", "chomage": "chomage", "rdb_reel": "rdb_reel", "solde_pib": "solde", "dette_pib": "dette"}[k]
                meta = f(S[p]["metamodele"]["2037"][mk], 0 if k == "emploi" else (1 if k == "dette_pib" else 2))
            lignes.append((STRAT_NOMS[p] if j == 0 else "") + f" & {lib} & " + " & ".join(r) + f" & {meta}" + r"\\")
        lignes.append(r"\addlinespace")
    ecrire("horizons.tex", r"\begin{longtable}{llrrrrr}\caption{Effets des programmes à 5, 10, 15 et 20 ans (modèle complet v0.7, comportements centraux, écarts à la référence). Dernière colonne : prévision du métamodèle à 10 ans.}\label{tab:horizons}\\ \toprule Programme & Indicateur & 2032 & 2037 & 2042 & 2047 & Métam. 2037\\ \midrule\endfirsthead\toprule Programme & Indicateur & 2032 & 2037 & 2042 & 2047 & Métam.\\ \midrule\endhead" +
           "\n" + "\n".join(lignes[:-1]) + r"\bottomrule\end{longtable}")
    # robustesse : dette et chômage 2037 sous chocs, comportements, mi-chemin
    chocs = []
    for p in ordre:
        for c in V[p]["resistance"]:
            if c not in chocs:
                chocs.append(c)
    lignes = []
    for p in ordre:
        v = V[p]
        tr = v["complet"]["traj"]
        cells = [f"{f(ec(tr, 'dette_pib', 2037, 'niv'), 1)} / {f(ec(tr, 'chomage', 2037, 'niv'))}"]
        for alt in ("basse", "haute", "mi_chemin"):
            if alt in v:
                t2 = v[alt]["traj"]
                cells.append(f"{f(ec(t2, 'dette_pib', 2037, 'niv'), 1)} / {f(ec(t2, 'chomage', 2037, 'niv'))}")
            else:
                cells.append("---")
        lignes.append(STRAT_NOMS[p] + " & " + " & ".join(cells) + r"\\")
    ecrire("robustesse_comportements.tex", r"\begin{tabular}{lllll}\toprule Programme & Central & Comportements bas & Comportements hauts & Mise en œuvre à moitié\\ \midrule" +
           "\n" + "\n".join(lignes) + r"\bottomrule\end{tabular}")
    lignes = []
    for c in chocs:
        cells = []
        for p in ordre:
            x = V[p]["resistance"].get(c)
            cells.append(f(x["dette_pib"]["2037"]["ecart"], 1) if x and "dette_pib" in x else "")
        lib = c.replace("%", r"\%")
        lignes.append(lib + " & " + " & ".join(cells) + r"\\")
    lignes.append(r"\midrule")
    for c in chocs:
        cells = []
        for p in ordre:
            x = V[p]["resistance"].get(c)
            cells.append(f(x["chomage"]["2037"]["ecart"]) if x and "chomage" in x else "")
        lignes.append(c.replace("%", r"\%") + " & " + " & ".join(cells) + r"\\")
    ecrire("robustesse_chocs.tex", r"\begin{tabular}{p{4.8cm}" + "r" * len(ordre) + r"}\toprule Environnement (haut : dette, bas : chômage) & " +
           " & ".join(r"\makecell{" + STRAT_NOMS[p].replace(" ", r"\\", 1) + "}" for p in ordre) + r"\\ \midrule" + "\n" + "\n".join(lignes) + r"\bottomrule\end{tabular}")
    # figure : trajectoires de dette et de chômage des stratégies
    fig, ax = plt.subplots(1, 3, figsize=(10.5, 3.2))
    cols = {"S1_protection": "#1F77B4", "S2_emploi": "#2CA02C", "S3_productivite": "#9467BD", "S4_redressement": "#D62728", "S5_global": "#FF7F0E"}
    for p in ordre:
        tr = V[p]["complet"]["traj"]
        ans = list(range(2028, 2048))
        st = dict(color=cols.get(p, GRIS), lw=1.6 if p in cols else 0.9, ls="-" if p in cols else ":")
        for i, (k, typ) in enumerate((("pib", "pct"), ("chomage", "niv"), ("dette_pib", "niv"))):
            ax[i].plot(ans, [ec(tr, k, t, typ) for t in ans], label=STRAT_NOMS[p], **st)
    for i, lib in enumerate(("PIB en volume (%)", "Chômage (points)", "Dette publique (points de PIB)")):
        ax[i].set_title(lib, fontsize=9)
        ax[i].axhline(0, color="#999", lw=0.5)
    ax[2].legend(frameon=False, fontsize=6.3, ncol=1, loc="lower left")
    fig.tight_layout()
    fig.savefig(FIG / "strategies_trajectoires.pdf")
    plt.close(fig)


def acceptabilite():
    A = json.loads((RES / "acceptabilite_v07.json").read_text())
    ordre = [s for s in STRAT_NOMS if s in A]
    lignes = []
    for p in ordre:
        a = A[p]
        d = a["deciles"]
        dd = lambda i: f(d[str(i)]["euros_par_uc"], 0) if str(i) in d else "---"  # noqa: E731
        lignes.append(f"{STRAT_NOMS[p]} & {a['niveau']} & {dd(1)} & {dd(3)} & {dd(5)} & {dd(8)} & {dd(10)} & {f(-a['perte_max_groupe_pct'], 2)} & "
                      f"{len(a['droits_reduits'])} & {len(a['leviers_difficulte_3'])}\\\\")
    ecrire("acceptabilite.tex", r"\begin{tabular}{llrrrrrrcc}\toprule Programme & Acceptabilité & D1 & D3 & D5 & D8 & D10 & Groupe le plus perdant (\%) & Droits réduits & Diff. 3\\ \midrule" +
           "\n" + "\n".join(lignes) + r"\bottomrule\end{tabular}")
    # gagnants / perdants par dimension pour les cinq stratégies
    for dim, lib in (("age", "Âge de la personne de référence"), ("csp", "Catégorie sociale"), ("famille", "Configuration familiale"), ("region", "Région")):
        groupes = sorted({g for p in ordre for g in (A[p]["groupes"].get(dim) or {})})
        strat = [p for p in ordre if p.startswith("S")]
        lignes = []
        for g in groupes:
            cells = []
            for p in strat:
                x = (A[p]["groupes"].get(dim) or {}).get(g)
                cells.append(f(x["variation_euros_par_uc"], 0) if x else "")
            poids = (A[strat[0]]["groupes"].get(dim) or {}).get(g, {}).get("poids", 0)
            lignes.append(f"{g} & {f(100 * poids, 1, False)} & " + " & ".join(cells) + r"\\")
        ecrire(f"groupes_{dim}.tex", r"\begin{tabular}{p{5cm}r" + "r" * len(strat) + r"}\toprule " + lib + r" & Poids (\%) & " +
               " & ".join(r"\makecell{" + STRAT_NOMS[p].replace(" ", r"\\", 1) + "}" for p in strat) + r"\\ \midrule" + "\n" + "\n".join(lignes) + r"\bottomrule\end{tabular}")
    # figure : variation par décile
    fig, ax = plt.subplots(figsize=(10, 3.4))
    strat = [p for p in ordre if p.startswith("S")]
    w = 0.8 / len(strat)
    cols = ["#1F77B4", "#2CA02C", "#9467BD", "#D62728", "#FF7F0E"]
    for i, p in enumerate(strat):
        d = A[p]["deciles"]
        ax.bar(np.arange(1, 11) + (i - len(strat) / 2 + 0.5) * w, [d[str(k)]["pct"] for k in range(1, 11)], width=w, color=cols[i % 5], label=STRAT_NOMS[p])
    ax.axhline(0, color="#555", lw=0.6)
    ax.set_xticks(range(1, 11))
    ax.set_xlabel("Décile de niveau de vie")
    ax.set_ylabel("Variation du niveau de vie (%)")
    ax.legend(frameon=False, fontsize=7, ncol=5)
    fig.tight_layout()
    fig.savefig(FIG / "deciles.pdf")
    plt.close(fig)


if __name__ == "__main__":
    for fn in sys.argv[1:] or ["diagnostic", "comparaison", "comportements", "optimisation", "verification", "acceptabilite"]:
        globals()[fn]()
        print(fn, "ok")
