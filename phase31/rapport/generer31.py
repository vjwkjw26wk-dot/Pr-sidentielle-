"""Tables LaTeX et figures du rapport v0.8 à partir des résultats exécutés (phase31/resultats)."""
import json
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

R = pathlib.Path(__file__).resolve().parents[2]
RES = R / "phase31" / "resultats"
TAB = R / "phase31" / "rapport" / "tables"
FIG = R / "phase31" / "rapport" / "figures"
TAB.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)
BLEU, ORANGE, VERT, ROUGE, GRIS = "#1F4E79", "#C55A11", "#2C7C3C", "#A61B1B", "#777777"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
STRAT = {"S1_protection": "S1 Protection", "S2_emploi": "S2 Emploi", "S3_productivite": "S3 Productivité", "S4_redressement": "S4 Redressement",
         "S5_global": "S5 Global", "v06_A": "A (v0.6)", "v06_B": "B (v0.6)", "v06_C": "C (v0.6)", "v06_D": "D (v0.6)", "v06_R": "R (v0.6)"}


def f(x, d=2, signe=True):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "---"
    s = f"{x:+.{d}f}" if signe else f"{x:.{d}f}"
    return "$" + s.replace(".", "{,}") + "$"


def ecrire(n, t):
    (TAB / n).write_text(t)


def backtest():
    a = json.loads((RES / "analyse_backtest.json").read_text())
    T = a["tableau"]
    vars_ = [("pib", "PIB"), ("c", "Conso."), ("fbcf", "Invest."), ("x", "Export."), ("m", "Import."), ("emploi", "Emploi"), ("pc", "Prix"),
             ("salaire_reel", "Sal. réel"), ("chomage", "Chômage"), ("recettes_pib", "Recettes"), ("depenses_pib", "Dépenses"), ("dette_pib", "Dette")]
    lignes = []
    for per in ("2010-2019", "2014-2019", "2021-2025"):
        for var, lib in (("demande", "demande seule"), ("v06", "v0.6"), ("v07", "v0.7"), ("v08", "v0.8")):
            d = T[per].get(var)
            if not d:
                continue
            lignes.append((per if var == "demande" else "") + f" & {lib} & " + " & ".join(f(d[k]["rmse"], 2, False) for k, _ in vars_) + r"\\")
        d = T[per]["v08"]
        lignes.append(" & naïf & " + " & ".join(f(d[k]["rmse_naif"], 2, False) if d[k].get("rmse_naif") else "" for k, _ in vars_) + r"\\ \addlinespace")
    ecrire("backtest_rmse.tex", r"\begin{tabular}{ll" + "r" * len(vars_) + r"}\toprule Période & Modèle & " + " & ".join(l for _, l in vars_) + r"\\ \midrule" + "\n" +
           "\n".join(lignes) + r"\bottomrule\end{tabular}")
    H = a["horizons_2010"]
    lignes = []
    for k, lib, typ in (("pib", "PIB (\\%)", ""), ("emploi", "Emploi (\\%)", ""), ("productivite", "Productivité (\\%)", ""), ("pc", "Prix (\\%)", ""),
                        ("c", "Consommation (\\%)", ""), ("fbcf", "Investissement (\\%)", ""), ("x", "Exportations (\\%)", ""),
                        ("salaire_reel", "Salaire réel (\\%)", ""), ("chomage", "Chômage (points)", ""), ("recettes_pib", "Recettes (pt PIB)", ""),
                        ("depenses_pib", "Dépenses (pt PIB)", ""), ("solde_pib", "Solde (pt PIB)", ""), ("dette_pib", "Dette (pt PIB)", "")):
        lignes.append(lib + " & " + " & ".join(f(H[k].get(h) if isinstance(H[k], dict) else None, 1) for h in ("1", "3", "5", "9")) + r"\\")
    ecrire("backtest_horizons.tex", r"\begin{tabular}{lrrrr}\toprule Erreur (simulé − observé) & 1 an & 3 ans & 5 ans & 9 ans\\ \midrule" + "\n" + "\n".join(lignes) + r"\bottomrule\end{tabular}")
    B = a["bloc_finances_publiques"]
    lignes = []
    for t, d in B.items():
        lignes.append(f"{t} & {f(d['erreur_pib_nominal_pct'], 1)} & {f(d['recettes_sim'], 1, False)} / {f(d['recettes_obs'], 1, False)} & "
                      f"{f(d['depenses_sim'], 1, False)} / {f(d['depenses_obs'], 1, False)} & {f(d['prestations_sim'], 1, False)} / {f(d['prestations_obs'], 1, False)} & "
                      f"{f(d['interets_sim'], 2, False)} / {f(d['interets_obs'], 2, False)} & {f(d['taux_apparent_sim'], 2, False)} / {f(d['taux_apparent_obs'], 2, False)}\\\\")
    ecrire("backtest_bloc.tex", r"\begin{tabular}{lrrrrrr}\toprule Année & PIB nominal (\% d'erreur) & Recettes & Dépenses & Prestations & Intérêts & Taux apparent\\ \midrule" + "\n" +
           "\n".join(lignes) + r"\bottomrule\end{tabular}")


# ------------------------------------------------------------------------------------------------------------------
def charger_strategies():
    S = {}
    for k in STRAT:
        p = RES / f"strategies_v08_{k}.json"
        if p.exists():
            S[k] = json.loads(p.read_text())
    return S


def ec(tr, k, t):
    return tr[k]["ecart"][str(t)] if str(t) in tr[k]["ecart"] else tr[k]["ecart"].get(t)


def strategies():
    S = charger_strategies()
    ANS = (2027, 2030, 2035, 2040, 2047)
    IND = (("pib", "PIB (\\%)", 2), ("pib_potentiel", "PIB potentiel (\\%)", 2), ("emploi", "Emploi (milliers)", 0), ("chomage", "Chômage (pt)", 2),
           ("salaire", "Coût salarial (\\%)", 2), ("rdb", "RDB nominal (\\%)", 2), ("recettes_pib", "Recettes (pt)", 2), ("depenses_pib", "Dépenses (pt)", 2),
           ("solde_pib", "Solde (pt)", 2), ("dette_pib", "Dette (pt)", 1))
    lignes = []
    for k, v in S.items():
        if not k.startswith("S") or "central" not in v:
            continue
        tr = v["central"]["trajectoires"]
        for j, (var, lib, d) in enumerate(IND):
            if var not in tr:
                continue
            if var == "emploi":
                vals = [tr[var]["scenario"][str(t)] - tr[var]["reference"][str(t)] for t in ANS]
            else:
                vals = [ec(tr, var, t) for t in ANS]
            lignes.append((STRAT[k] if j == 0 else "") + f" & {lib} & " + " & ".join(f(x, d) for x in vals) + r"\\")
        sr = [100 * ((tr["salaire"]["scenario"][str(t)] / tr["pc"]["scenario"][str(t)]) / (tr["salaire"]["reference"][str(t)] / tr["pc"]["reference"][str(t)]) - 1) for t in ANS]
        lignes.append(" & Coût salarial réel (\\%) & " + " & ".join(f(x, 2) for x in sr) + r"\\")
        if "part_industrie" in tr:
            lignes.append(" & Part de l'industrie (pt) & " + " & ".join(f(ec(tr, "part_industrie", t), 2) for t in ANS) + r"\\")
        dd = v["central"].get("distribution_dynamique") or {}
        G = lambda t, c: dd.get(str(t), {}).get("global", {}).get(c)  # noqa: E731
        lignes.append(" & RDB réel des ménages (\\%, M16) & " + " & ".join(f(G(t, "pct_moyen"), 2) for t in ANS) + r"\\")
        lignes.append(" & Niveau de vie médian réel (\\%) & " + " & ".join(f(G(t, "variation_niveau_de_vie_median_pct"), 2) for t in ANS) + r"\\")
        lignes.append(" & Pauvreté, seuil fixe (pt) & " + " & ".join(f((G(t, "pauvrete_apres") - G(t, "pauvrete_avant")) if G(t, "pauvrete_apres") is not None else None, 2) for t in ANS) + r"\\")
        lignes.append(" & Gini (×100) & " + " & ".join(f((100 * (G(t, "gini_apres") - G(t, "gini_avant"))) if G(t, "gini_apres") is not None else None, 2) for t in ANS) + r"\\")
        lignes.append(r"\addlinespace")
    ecrire("strategies_horizons.tex", r"\begin{longtable}{llrrrrr}\caption{Stratégies S1 à S5 (définitions de la v0.7) avec le modèle v0.8 : écarts à la référence, configuration centrale.}\label{tab:strat_horizons}\\ \toprule Stratégie & Indicateur & 2027 & 2030 & 2035 & 2040 & 2047\\ \midrule\endfirsthead \toprule Stratégie & Indicateur & 2027 & 2030 & 2035 & 2040 & 2047\\ \midrule\endhead" +
           "\n" + "\n".join(lignes[:-1]) + r"\bottomrule\end{longtable}")
    # central / faible / fort, et comparaison v0.7
    lignes = []
    for k, v in S.items():
        if not k.startswith("S"):
            continue
        row = [STRAT[k]]
        for var, d in (("pib", 2), ("chomage", 2), ("dette_pib", 1)):
            for t in (2035, 2047):
                cells = []
                for c in ("faible", "central", "fort"):
                    if c in v:
                        cells.append(ec(v[c]["trajectoires"], var, t))
                cells = [x for x in cells if x is not None]
                row.append(f"{f(v['central']['trajectoires'][var]['ecart'][str(t)], d)} [{f(min(cells), d)} ; {f(max(cells), d)}]" if cells else "---")
        lignes.append(" & ".join(row) + r"\\")
    ecrire("strategies_configs.tex", r"\begin{tabular}{lllllll}\toprule & \multicolumn{2}{c}{PIB (\%)} & \multicolumn{2}{c}{Chômage (pt)} & \multicolumn{2}{c}{Dette (pt)}\\ Stratégie & 2035 & 2047 & 2035 & 2047 & 2035 & 2047\\ \midrule" +
           "\n" + "\n".join(lignes) + r"\bottomrule\end{tabular}")
    R7 = R / "phase3" / "resultats"
    lignes = []
    for k, v in S.items():
        p7 = R7 / f"verification_v07_{k}.json"
        if not p7.exists() or "central" not in v:
            continue
        t7 = json.loads(p7.read_text())["complet"]["traj"]
        t8 = v["central"]["trajectoires"]
        def g7(var, t):
            tr = t7[var]
            s, r_ = tr["scenario"][str(t)], tr["reference"][str(t)]
            return 100 * (s / r_ - 1) if var in ("pib", "emploi_pct") else s - r_
        cells = []
        for var, d in (("pib", 2), ("chomage", 2), ("dette_pib", 1)):
            for t in (2037, 2047):
                cells.append(f"{f(g7(var, t), d)} / {f(ec(t8, var, t), d)}")
        lignes.append(STRAT[k] + " & " + " & ".join(cells) + r"\\")
    ecrire("strategies_v07_v08.tex", r"\begin{tabular}{lllllll}\toprule & \multicolumn{2}{c}{PIB (\%)} & \multicolumn{2}{c}{Chômage (pt)} & \multicolumn{2}{c}{Dette (pt)}\\ Programme (v0.7 / v0.8) & 2037 & 2047 & 2037 & 2047 & 2037 & 2047\\ \midrule" +
           "\n" + "\n".join(lignes) + r"\bottomrule\end{tabular}")
    # figure : dette et PIB, central avec bande faible-fort
    fig, ax = plt.subplots(1, 3, figsize=(10.5, 3.2))
    cols = {"S1_protection": "#1F77B4", "S2_emploi": "#2CA02C", "S3_productivite": "#9467BD", "S4_redressement": "#D62728", "S5_global": "#FF7F0E"}
    ans = list(range(2028, 2048))
    for k, c in cols.items():
        if k not in S:
            continue
        for i, var in enumerate(("pib", "chomage", "dette_pib")):
            y = [ec(S[k]["central"]["trajectoires"], var, t) for t in ans]
            ax[i].plot(ans, y, color=c, lw=1.6, label=STRAT[k])
            if "faible" in S[k] and "fort" in S[k]:
                lo = [ec(S[k]["faible"]["trajectoires"], var, t) for t in ans]
                hi = [ec(S[k]["fort"]["trajectoires"], var, t) for t in ans]
                ax[i].fill_between(ans, np.minimum(lo, hi), np.maximum(lo, hi), color=c, alpha=0.12)
    for i, lib in enumerate(("PIB en volume (%)", "Chômage (points)", "Dette publique (points de PIB)")):
        ax[i].set_title(lib, fontsize=9)
        ax[i].axhline(0, color="#999", lw=0.5)
    ax[2].legend(frameon=False, fontsize=6.5)
    fig.tight_layout()
    fig.savefig(FIG / "strategies_v08.pdf")
    plt.close(fig)


def distribution():
    S = charger_strategies()
    ANS = ("2030", "2035", "2047")
    lignes = []
    for k, v in S.items():
        if "central" not in v or not v["central"].get("distribution_dynamique"):
            continue
        dd = v["central"]["distribution_dynamique"]
        st = v["central"].get("distribution") or []
        stat = {d_["decile"]: d_["variation_pct"] for d_ in st}
        for j, t in enumerate(ANS):
            d = dd[t]
            g = d["global"]
            lignes.append((STRAT[k] if j == 0 else "") + f" & {t} & " + " & ".join(f(d["decile"][str(i)]["pct"], 1) for i in (1, 2, 3, 5, 8, 10)) +
                          f" & {f(g['variation_niveau_de_vie_median_pct'], 1)} & {f(100 * g['part_gagnants'], 0, False)} / {f(100 * g['part_perdants'], 0, False)} & "
                          f"{f(g['pauvrete_apres'] - g['pauvrete_avant'], 1)} & {f(100 * (g['gini_apres'] - g['gini_avant']), 2)}\\\\")
        if stat:
            lignes.append(" & statique & " + " & ".join(f(stat.get(i), 1) for i in (1, 2, 3, 5, 8, 10)) + r" & & & & \\")
        lignes.append(r"\addlinespace")
    ecrire("distribution_deciles.tex", r"\begin{longtable}{llrrrrrrrrrr}\caption{Revenu disponible réel après propagation (M16), par décile de niveau de vie initial (\% du revenu), niveau de vie médian (\%), part des ménages gagnants / perdants (variation de plus de 0,5 \%), pauvreté (seuil fixe, points), Gini (×100). Ligne « statique » : incidence directe seule (v0.7).}\label{tab:distrib}\\ \toprule Stratégie & Année & D1 & D2 & D3 & D5 & D8 & D10 & Médiane & G / P & Pauvreté & Gini\\ \midrule\endfirsthead\toprule Stratégie & Année & D1 & D2 & D3 & D5 & D8 & D10 & Médiane & G / P & Pauvreté & Gini\\ \midrule\endhead" +
           "\n" + "\n".join(lignes[:-1]) + r"\bottomrule\end{longtable}")
    # canaux (2035), moyenne nationale
    lignes = []
    canaux = ("direct", "salaires", "emploi", "patrimoine", "successions", "indexation", "prix")
    for k, v in S.items():
        if "central" not in v or not v["central"].get("distribution_dynamique"):
            continue
        g = v["central"]["distribution_dynamique"]["2035"]["global"]
        lignes.append(STRAT[k] + " & " + " & ".join(f(g["canaux_pct"][c], 2) for c in canaux) + f" & {f(g['pct_moyen'], 2)} & {f(g['coherence']['residuel_pct'], 2)}\\\\")
    ecrire("distribution_canaux.tex", r"\begin{tabular}{lrrrrrrrrr}\toprule Programme (2035) & Direct & Salaires & Emploi & Patrimoine & Successions & Indexation & Prix & Total & Résiduel\\ \midrule" +
           "\n" + "\n".join(lignes) + r"\bottomrule\end{tabular}")
    # groupes 2035 pour S1-S5
    for dim, lib in (("statut", "Statut de la personne de référence"), ("occupation", "Statut d'occupation"), ("famille", "Configuration familiale"),
                     ("age", "Âge de la personne de référence"), ("csp", "Catégorie sociale")):
        strat = [k for k in S if k.startswith("S") and S[k].get("central", {}).get("distribution_dynamique")]
        groupes = sorted({gr for k in strat for gr in S[k]["central"]["distribution_dynamique"]["2035"][dim]})
        lignes = []
        for gr in groupes:
            cells = []
            for k in strat:
                x = S[k]["central"]["distribution_dynamique"]["2035"][dim].get(gr)
                cells.append(f"{f(x['euros_par_uc'], 0)} ({f(x['pct'], 1)})" if x else "")
            poids = S[strat[0]]["central"]["distribution_dynamique"]["2035"][dim].get(gr, {}).get("poids", 0)
            lignes.append(f"{gr} & {f(100 * poids, 1, False)} & " + " & ".join(cells) + r"\\")
        ecrire(f"distribution_{dim}.tex", r"\begin{tabular}{p{4.2cm}r" + "r" * len(strat) + r"}\toprule " + lib + r" & Poids (\%) & " +
               " & ".join(r"\makecell{" + STRAT[k].replace(" ", r"\\", 1) + "}" for k in strat) + r"\\ \midrule" + "\n" + "\n".join(lignes) + r"\bottomrule\end{tabular}")
    # figure : déciles, statique vs dynamique 2035
    strat = [k for k in S if k.startswith("S") and S[k].get("central", {}).get("distribution_dynamique")]
    fig, axs = plt.subplots(1, len(strat), figsize=(11, 2.8), sharey=True)
    for a, k in zip(np.atleast_1d(axs), strat):
        v = S[k]["central"]
        st = {d_["decile"]: d_["variation_pct"] for d_ in (v.get("distribution") or [])}
        dy = v["distribution_dynamique"]
        a.bar(np.arange(1, 11) - 0.2, [st.get(i, 0) for i in range(1, 11)], 0.4, color=GRIS, label="statique")
        a.bar(np.arange(1, 11) + 0.2, [dy["2035"]["decile"][str(i)]["pct"] for i in range(1, 11)], 0.4, color=BLEU, label="après propagation (2035)")
        a.axhline(0, color="#555", lw=0.5)
        a.set_title(STRAT[k], fontsize=8.5)
        a.set_xticks(range(1, 11))
        a.tick_params(labelsize=7)
    np.atleast_1d(axs)[0].legend(frameon=False, fontsize=6.5)
    np.atleast_1d(axs)[0].set_ylabel("% du revenu disponible")
    fig.tight_layout()
    fig.savefig(FIG / "deciles_dynamique.pdf")
    plt.close(fig)


def politiques():
    """Effets de politiques publiques simulés (v0.8) confrontés aux évaluations empiriques."""
    E = {}
    for fch in RES.glob("experiences_v08_*.json"):
        E.update(json.loads(fch.read_text()))

    def niv(nom, v, t):
        tr = E[nom]["traj"][v]
        return tr["scenario"][str(t)] - tr["reference"][str(t)]

    def pct(nom, v, t):
        return E[nom]["traj"][v]["ecart"][str(t)]
    L = []

    def ligne(mesure, effet, simule, evaluation, nature):
        L.append(f"{mesure} & {effet} & {simule} & {evaluation} & {nature} \\\\")
    if "cot_moins20" in E:
        e = [niv("cot_moins20", "emploi", t) for t in (2030, 2032, 2037)]
        ligne("Cotisations employeurs $-20$\\md{} (CICE)", "Emploi (milliers) 2030 / 2032 / 2037",
              " / ".join(f"{x:+.0f}" for x in e), "100 (France Stratégie 2020) ; 160 (modèles macro.)", "Causal (écart de ciblage) ; modèle")
    if "tva" in E and "tva_moins1" in E:
        ligne("TVA taux normal $\\pm 1$ point", "Prix à la consommation après 1 an (\\%)",
              f"{pct('tva', 'pc', 2028):+.2f} / {pct('tva_moins1', 'pc', 2028):+.2f}".replace(".", ","),
              "Répercussion complète des hausses, moitié des baisses (Benzarti et al. 2020) ; 57-77 \\% (Carbonnier 2007)", "Causal")
    if "is_baisse" in E:
        ligne("IS à 20 \\%", "Investissement des entreprises 2032 (\\%)", f"{pct('is_baisse', 'fbcf', 2032):+.2f}".replace(".", ","),
              "Élasticité au coût d'usage $-0{,}5$ à $-1{,}6$ (Chirinko et al. 1999 ; Zwick et Mahon 2017) ; la hausse de la taxation des dividendes de 2013 n'a pas réduit l'investissement (Boissel et Matray 2022)", "Causal (international) ; causal (France)")
    if "invest_public10" in E:
        m1, m3 = (niv("invest_public10", "pib", t) / 10000 for t in (2028, 2030))
        ligne("Investissement public $+10$\\md", "Multiplicateur du PIB, 1 an / 3 ans", f"{m1:.2f} / {m3:.2f}".replace(".", ","),
              "0,4 à 1 la 1re année, plus élevé à moyen terme (FMI 2014 ; Ramey 2019)", "Causal (pays avancés)")
    if "chomage" in E:
        c30, c47 = niv("chomage", "chomage", 2030), niv("chomage", "chomage", 2047)
        es = niv("chomage", "emploi_structurel", 2035)
        ligne("Allocations chômage $-25$ \\%", "Chômage 2030 / 2047 (points) ; emploi structurel (milliers)",
              f"{c30:+.2f} / {c47:+.2f} ; {es:+.0f}".replace(".", ","),
              "Durée d'indemnisation : élasticité 0,3-1 (Schmieder et von Wachter 2016) ; effet macroéconomique plus faible que l'effet micro (Landais, Michaillat, Saez 2018)", "Causal (micro) ; macro incertain")
    if "ppa25" in E:
        ligne("Prime d'activité $+25$ \\%", "Population active 2030 (milliers)", f"{niv('ppa25', 'population_active', 2030):+.0f}",
              "Effets de participation faibles (évaluations du RSA activité, Bargain et Vicard 2014)", "Causal (discontinuité)")
    if "rsa25" in E:
        ligne("RSA $+25$ \\%", "Population active 2030 (milliers)", f"{niv('rsa25', 'population_active', 2030):+.0f}",
              "Effet faible sur l'emploi au seuil de 25 ans (Bargain et Vicard 2014)", "Causal (discontinuité)")
    t = ("\\begin{tabular}{p{3.2cm}p{3.2cm}p{2.2cm}p{5cm}p{2.4cm}}\\toprule\nMesure & Effet & v0.8 & Évaluations & Nature \\\\ \\midrule\n"
         + "\n".join(L) + "\n\\bottomrule\\end{tabular}\n")
    ecrire("politiques.tex", t)
    return L


def sensibilite():
    """Sensibilité un à un : intervalle [basse ; haute] de la dette et du PIB en 2047 par paramètre et stratégie."""
    D = {}
    for k in STRAT:
        fch = RES / f"sensibilite_{k}.json"
        if fch.exists():
            D[k] = json.loads(fch.read_text())
    if not D:
        return
    params = [p for p in next(iter(D.values())) if p != "central"]
    lib = {p: next(iter(D.values()))[p]["libelle"] for p in params}
    for var, nom, d in (("dette_pib", "sensibilite_dette.tex", 0), ("pib", "sensibilite_pib.tex", 2), ("chomage", "sensibilite_chomage.tex", 2)):
        cols = list(D)
        amp = {p: max(abs(D[k][p]["haute"][var]["2047"] - D[k][p]["basse"][var]["2047"]) for k in cols if p in D[k]) for p in params}
        ordre = sorted(params, key=lambda p: -amp[p])
        L = ["Valeur centrale & " + " & ".join(f(D[k]["central"][var]["2047"], d) for k in cols) + " \\\\ \\midrule"]
        for p in ordre:
            cel = []
            for k in cols:
                if p in D[k]:
                    b, h = D[k][p]["basse"][var]["2047"], D[k][p]["haute"][var]["2047"]
                    cel.append(f"{f(b, d)} ; {f(h, d)}")
                else:
                    cel.append("---")
            L.append(lib[p].replace("θ", "$\\theta$").replace("ρ", "$\\rho$").replace("κ", "$\\kappa$") + " & " + " & ".join(cel) + " \\\\")
        t = ("\\begin{tabular}{l" + "c" * len(cols) + "}\\toprule\nParamètre (basse / haute) & " + " & ".join(STRAT[k] for k in cols)
             + " \\\\ \\midrule\n" + "\n".join(L) + "\n\\bottomrule\\end{tabular}\n")
        ecrire(nom, t)
    # figure : amplitude par paramètre (dette 2047)
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    cols = list(D)
    amp = {p: [abs(D[k][p]["haute"]["dette_pib"]["2047"] - D[k][p]["basse"]["dette_pib"]["2047"]) if p in D[k] else 0 for k in cols] for p in params}
    ordre = sorted(params, key=lambda p: max(amp[p]))
    y = np.arange(len(ordre))
    w = 0.8 / len(cols)
    coul = [BLEU, ORANGE, VERT, ROUGE, GRIS]
    for i, k in enumerate(cols):
        ax.barh(y + i * w, [amp[p][i] for p in ordre], height=w, color=coul[i % 5], label=STRAT[k])
    ax.set_yticks(y + 0.4 - w / 2)
    ax.set_yticklabels([lib[p].split(" (")[0] for p in ordre], fontsize=7.5)
    ax.set_xlabel("Écart de dette en 2047 entre valeur haute et valeur basse (points de PIB)")
    ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "sensibilite.pdf")
    plt.close(fig)


def tests():
    """Table des tests automatisés à partir du rapport JUnit de pytest."""
    import ast
    import xml.etree.ElementTree as ET
    src = (R / "tests" / "test_phase31.py").read_text()
    doc = {n.name: " ".join((ast.get_docstring(n) or "").split()) for n in ast.parse(src).body if isinstance(n, ast.FunctionDef)}
    xml = RES / "tests_phase31.xml"
    L = []
    nb = {"ok": 0, "échec": 0}
    for tc in ET.parse(xml).getroot().iter("testcase"):
        n = tc.get("name")
        etat = "échec" if (tc.find("failure") is not None or tc.find("error") is not None) else "ok"
        nb[etat] += 1
        lib = doc.get(n) or n.replace("test_", "").replace("_", " ")
        L.append(f"\\code{{{n.replace('_', chr(92) + '_' + chr(92) + 'allowbreak{}')}}} & {lib.replace('%', chr(92) + '%').replace('_', chr(92) + '_')} & {etat} & {float(tc.get('time')):.0f} \\\\")
    t = ("{\\small\\begin{longtable}{@{}p{5.2cm}p{8.2cm}cr@{}}\\toprule\nTest & Propriété vérifiée & Résultat & s \\\\ \\midrule\\endhead\n"
         + "\n".join(L) + f"\n\\bottomrule\\end{{longtable}}}}\n\n\\noindent Bilan : {nb['ok']} tests réussis, {nb['échec']} en échec.\n")
    ecrire("tests.tex", t)


LIB_LEV = {"ir_t1": "IR 1re tranche (pt)", "ir_t4": "IR tranche sup. (pt)", "csg_activite": "CSG activité (pt)", "tva": "TVA normale (pt)",
           "tva_reduite": "TVA réduite (pt)", "isf": "Impôt fortune (%)", "pfu": "PFU (pt)", "taux_is": "IS (pt)",
           "impots_production": "Impôts production (Md€)", "cotisations_employeurs": "Cotis. employeurs (Md€)", "successions": "Successions (%)",
           "taxe_carbone": "Taxe carbone (€/t)", "smic": "SMIC (%)", "point_indice": "Point d'indice (%)", "emploi_public": "Emplois publics (k)",
           "autres_depenses": "Fonctionnement (Md€)", "sante": "Santé (Md€)", "education": "Éducation (Md€)", "defense": "Défense (Md€)",
           "investissement_public": "Invest. public (Md€)", "indexation_pensions": "Indexation pensions (pt/an)",
           "assurance_chomage": "Alloc. chômage (%)", "allocations_familiales": "Alloc. familiales (%)", "aides_logement": "Aides logement (%)",
           "rsa": "RSA (%)", "prime_activite": "Prime d'activité (%)", "minimum_vieillesse": "Minimum vieillesse (%)",
           "transferts_menages": "Transferts (pt PIB)", "logements_sociaux": "Logements sociaux (k/an)", "age_legal": "Âge légal (ans)"}
LIB_LEV = {k: v.replace("%", r"\%") for k, v in LIB_LEV.items()}


def optimisation():
    """Réoptimisation exploratoire : compositions v0.7 / v0.8 (statique, dynamique), contraintes, préférences."""
    O7 = json.loads((R / "phase3" / "resultats" / "optimisation_v07.json").read_text())
    O8 = {c: json.loads((RES / f"optim_{c}" / "optimisation_v07.json").read_text()) for c in ("statique", "dyn")}
    C = {c: json.loads((RES / f"comparaison_optimisation_{c[0]}.json").read_text()) for c in ("statique", "dyn")}
    strat = list(O7["strategies"])
    sources = [("v0.7", O7), ("v0.8 stat.", O8["statique"]), ("v0.8 dyn.", O8["dyn"])]
    # composition : une ligne par levier, colonnes stratégie × version
    levs = sorted({l for _, o in sources for s in strat for l in o["strategies"][s]["leviers"]}, key=lambda l: list(LIB_LEV).index(l) if l in LIB_LEV else 99)
    L = []
    for l in levs:
        cel = []
        for s in strat:
            for _, o in sources:
                v = o["strategies"][s]["leviers"].get(l)
                cel.append("" if v is None else f"{v:+.1f}".replace(".", ",").replace("-", "$-$"))
        L.append(LIB_LEV.get(l, l.replace("_", " ")) + " & " + " & ".join(cel) + " \\\\")
    entete1 = " & " + " & ".join(f"\\multicolumn{{3}}{{c}}{{{STRAT[s].split()[0]}}}" for s in strat) + " \\\\"
    entete2 = "Levier & " + " & ".join(["07", "08s", "08d"] * len(strat)) + " \\\\ \\midrule"
    ecrire("optim_composition.tex", "\\begin{tabular}{l" + "rrr" * len(strat) + "}\\toprule\n" + entete1 + "\n" + entete2 + "\n" + "\n".join(L) + "\n\\bottomrule\\end{tabular}\n")
    # pertinence de la composition v0.7 évaluée avec la v0.8
    L = []
    for s in strat:
        for c, lab in (("statique", "statique"), ("dyn", "dynamique")):
            d = C[c][s]
            viol = [f"{x['critere']} {x['horizon'] or ''} ({x['valeur']:+.1f})".replace(".", ",").replace("_", " ") for x in d["contraintes_v07_eval_v08"] if not x["respectee"]]
            L.append(f"{STRAT[s]} & {lab} & {f(d['objectif_v07_eval_v08'])} & {f(d['objectif_v08'])} & {f(d['v07_eval_v08']['2047']['dette'], 1)} & {f(d['v08']['2047']['dette'], 1)} & "
                     + ("; ".join(viol) if viol else "aucune") + " & " + str(len(d["communs"])) + " \\\\")
    ecrire("optim_pertinence.tex", "\\begin{tabular}{llrrrrp{4.2cm}c}\\toprule\nStratégie & Distribution & \\makecell{Objectif\\\\ compo. v0.7} & \\makecell{Objectif\\\\ optimum v0.8} & "
           "\\makecell{Dette 2047\\\\ compo. v0.7} & \\makecell{Dette 2047\\\\ optimum v0.8} & Contraintes violées par la composition v0.7 & \\makecell{Leviers\\\\ communs} \\\\ \\midrule\n"
           + "\n".join(L) + "\n\\bottomrule\\end{tabular}\n")
    # robustesse aux préférences
    fr = {"v0.7": O7["perimetres"]["principal"]["robustesse_preferences"]["frequence"]}
    for c, lab in (("statique", "v0.8 stat."), ("dyn", "v0.8 dyn.")):
        fr[lab] = O8[c]["perimetres"]["principal"]["robustesse_preferences"]["frequence"]
    cles = sorted(set().union(*fr.values()), key=lambda k: -min(fr[v].get(k, 0) for v in fr))[:20]
    L = [f"{LIB_LEV.get(k.split('|')[0], k.split('|')[0])} & {k.split('|')[1]} & " + " & ".join(f"{100 * fr[v].get(k, 0):.0f}" for v in fr) + " \\\\" for k in cles]
    ecrire("optim_preferences.tex", "\\begin{tabular}{llrrr}\\toprule\nLevier & Sens & v0.7 & v0.8 stat. & v0.8 dyn. \\\\ \\midrule\n" + "\n".join(L) + "\n\\bottomrule\\end{tabular}\n")
    # front de Pareto chômage-dette et modestes-dette, v0.7 et v0.8 dynamique
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.9))
    for i, (a, b, la, lb) in enumerate((("chomage", "dette", "Chômage 2037 (points)", "Dette 2037 (points de PIB)"),
                                        ("modestes", "dette", "Niveau de vie des 30 % les plus modestes (%)", "Dette 2037 (points de PIB)"))):
        for o, c, lab in ((O7, GRIS, "v0.7"), (O8["statique"], BLEU, "v0.8, distribution statique"), (O8["dyn"], ORANGE, "v0.8, distribution après propagation")):
            k = f"exact|{a}|{b}"
            if k not in o["perimetres"]["principal"]["pareto"]:
                continue
            fr_ = np.array([[x[0], x[1]] for x in o["perimetres"]["principal"]["pareto"][k]])
            fr_ = fr_[np.argsort(fr_[:, 0])]
            ax[i].plot(fr_[:, 0], fr_[:, 1], "o-", ms=2.5, color=c, lw=1.5, label=lab)
        ax[i].set_xlabel(la)
        ax[i].set_ylabel(lb)
        ax[i].axhline(0, color="#999", lw=0.5)
        ax[i].axvline(0, color="#999", lw=0.5)
    ax[0].legend(frameon=False, fontsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "pareto_v08.pdf")
    plt.close(fig)


def decomposition():
    """Causes des écarts v0.7 → v0.8 (dette et PIB 2047) : table et texte."""
    D = json.loads((RES / "decomposition_v07_v08.json").read_text())
    R7 = R / "phase3" / "resultats"
    e7, e8 = {}, {}
    for p_ in sorted(R7.glob("experiences_v07_*.json")):
        if "comport" not in p_.name:
            e7.update(json.loads(p_.read_text()))
    for p_ in sorted(RES.glob("experiences_v08_*.json")):
        if "comport" not in p_.name:
            e8.update(json.loads(p_.read_text()))
    LIBX = {"cot_moins20": "Cotisations $-20$\\md", "is_baisse": "IS à 20 \\%", "is": "IS à 30,5 \\%", "production": "Impôts de production $+10$\\md",
            "tva": "TVA $+1$ pt", "csg": "CSG $+1$ pt", "rsa25": "RSA $+25$ \\%", "ppa25": "Prime d'activité $+25$ \\%", "invest20": "Investissement public $+20$\\md",
            "age65": "Âge légal 65 ans", "temps37": "Durée du travail 37 h", "recherche3": "R\\&D $+3$\\md"}
    L = []
    rows = {}
    for k, d in D.items():
        if k.startswith("S"):
            t7 = json.loads((R7 / f"verification_v07_{k}.json").read_text())["complet"]["traj"]
            t8 = json.loads((RES / f"strategies_v08_{k}.json").read_text())["central"]["trajectoires"]
        else:
            t7 = e7.get(k, {}).get("traj")
            t8 = e8.get(k, {}).get("traj")
        if not t7 or not t8:
            continue
        cel = []
        for var in ("dette_pib", "pib"):
            s7, r7 = t7[var]["scenario"]["2047"], t7[var]["reference"]["2047"]
            v7 = 100 * (s7 / r7 - 1) if var == "pib" else s7 - r7
            v8 = t8[var]["ecart"]["2047"]
            a, b = d["A_fermeture_et_incidence_v07"][var]["2047"], d["B_incidence_v07"][var]["2047"]
            dd = 1 if var == "dette_pib" else 2
            cel += [f(v7, dd), f(a - v7, dd), f(b - a, dd), f(v8 - b, dd), f(v8, dd)]
            rows.setdefault(k, {})[var] = (v7, a - v7, b - a, v8 - b, v8)
        L.append((STRAT.get(k) or LIBX.get(k, k)) + " & " + " & ".join(cel) + " \\\\")
        if k == "S5_global":
            L.append("\\midrule")
    t = ("\\begin{tabular}{l rrrrr rrrrr}\\toprule\n & \\multicolumn{5}{c}{Dette publique 2047 (points de PIB)} & \\multicolumn{5}{c}{PIB 2047 (\\%)} \\\\ "
         "\\cmidrule(lr){2-6}\\cmidrule(lr){7-11}\nProgramme & v0.7 & (a) & (b) & (c) & v0.8 & v0.7 & (a) & (b) & (c) & v0.8 \\\\ \\midrule\n" + "\n".join(L) + "\n\\bottomrule\\end{tabular}\n")
    ecrire("decomposition.tex", t)
    S = {k: v for k, v in rows.items() if k.startswith("S")}
    txt = ["\\begin{table}[htbp]\\centering\\scriptsize\n\\caption{Décomposition de l'écart v0.7 → v0.8 en 2047, configuration centrale : (a) correction du "
           "défaut de code, recalage de la référence, offre de travail en 18 cas types ; (b) fermeture estimée (θ, ρ, sans termes en différence) ; "
           "(c) incidence des prélèvements sur les entreprises.}\\label{tab:decomp}\n\\tabfit{../tables/decomposition.tex}\n\\end{table}\n"]
    principal = {k: max(range(1, 4), key=lambda i: abs(v["dette_pib"][i])) for k, v in S.items()}
    noms = {1: "la correction du code et du recalage (a)", 2: "la fermeture estimée (b)", 3: "l'incidence fiscale (c)"}
    phr = "; ".join(f"{STRAT[k].split()[0]} : {noms[i]} ({v['dette_pib'][i]:+.0f} points)".replace(".", ",") for (k, i), v in zip(principal.items(), S.values()))
    print(phr)
    ecrire("decomposition_texte.tex", "".join(txt) + "\n")


def europe():
    """Contribution du module zone euro et de la prime de risque à la dette de 2047."""
    D = json.loads((RES / "diagnostic_europe.json").read_text())
    L = []
    for k, d in D.items():
        c = [f(d[x]["dette_pib"]["2047"], 0) for x in ("sans", "avec_prime0", "avec", "avec_prime5")]
        c += [f(d[x]["interets_pib"]["2047"], 1) for x in ("avec_prime0", "avec", "avec_prime5")]
        L.append(STRAT[k] + " & " + " & ".join(c) + " \\\\")
    t = ("\\par\\medskip{\\centering\\scriptsize\\begin{tabular}{lrrrrrrr}\\toprule\n & \\multicolumn{4}{c}{Dette 2047 (points)} & \\multicolumn{3}{c}{Intérêts 2047 (points de PIB)} \\\\"
         "\\cmidrule(lr){2-5}\\cmidrule(lr){6-8}\n & sans M11 & prime 0 & 0,03 & 0,05 & prime 0 & 0,03 & 0,05 \\\\ \\midrule\n" + "\n".join(L)
         + "\n\\bottomrule\\end{tabular}\\par}\\medskip\n")
    s3 = D["S3_productivite"]
    txt = (" La réaction de la BCE et le commerce avec la zone euro comptent peu (colonne « prime 0 ») : 1 à 4 points de dette. "
           "L'essentiel vient de la \\emph{prime de risque} sur les taux français, de 0,03 point de taux long par point de dette (hypothèse "
           "de niveau C, au milieu des estimations de la littérature, 0,02 à 0,05) : un écart de dette se renchérit ou s'allège par les "
           f"intérêts, et l'effet se cumule sur vingt ans. Pour S3, la dette de 2047 passe de {s3['avec_prime0']['dette_pib']['2047']:+.0f} points sans prime à "
           f"{s3['avec']['dette_pib']['2047']:+.0f} avec la prime centrale et {s3['avec_prime5']['dette_pib']['2047']:+.0f} avec une prime de 0,05. Cette hypothèse n'était pas "
           "variée dans les configurations faible et forte ; elle est désormais traitée comme une incertitude structurelle à part entière.").replace(".", ",", 0)
    ecrire("europe_texte.tex", t + txt.replace("+", "$+$") + "\n")


if __name__ == "__main__":
    for fn in sys.argv[1:]:
        globals()[fn]()
        print(fn, "ok")
