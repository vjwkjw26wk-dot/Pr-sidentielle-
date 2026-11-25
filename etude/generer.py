"""Génère les tableaux, figures et chapitres dépendant des résultats de l'étude, à partir des gabarits
(etude/gabarits/*.md) et des résultats de simulation (phase7/resultats, phase5/resultats). Aucun résultat n'est saisi à
la main : toute valeur des chapitres 6, 7, 9, 10, 12 et des annexes A, C, E, F, K vient de ce script.

Usage : python3 etude/generer.py
"""
import json, pathlib, pickle, re, sys, warnings
warnings.filterwarnings("ignore")
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src"), str(R)]
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import m26_europe_institutions as U, m27_corpus as C, m23_regimes as G

E = R / "etude"; CH = E / "chapitres"; GA = E / "gabarits"; FIG = E / "figures"; FIG.mkdir(exist_ok=True)
RES = R / "phase7" / "resultats"
NOMS = {"melenchon": "Mélenchon (LFI)", "le_pen": "Le Pen (RN)", "philippe": "Philippe (Horizons)"}
COUL = {"melenchon": "#c0392b", "le_pen": "#2c3e7a", "philippe": "#e09b2d"}
H = {5: 2031, 10: 2036, 20: 2046}


def fr(x, d=1, signe=True):
    """Nombre au format français."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    s = f"{x:+.{d}f}" if signe else f"{x:.{d}f}"
    s = s.replace("-", "−").replace(".", ",")
    return s


def tab(df, d=1, signe=True, index=True):
    cols = list(df.columns)
    lignes = ["| " + (" | ".join([df.index.name or ""] if index else []) + (" | " if index else "")) + " | ".join(map(str, cols)) + " |"]
    lignes[0] = lignes[0].replace("|  | ", "| ")
    lignes.append("|" + "---|" * (len(cols) + (1 if index else 0)))
    for i, r in df.iterrows():
        cells = [fr(v, d, signe) if isinstance(v, (int, float, np.floating)) else str(v) for v in r.values]
        lignes.append("| " + ((str(i) + " | ") if index else "") + " | ".join(cells) + " |")
    return "\n".join(lignes)


def charger():
    out = {}
    for c in NOMS:
        f = RES / f"{c}.pkl"
        if f.exists():
            out[c] = pickle.load(open(f, "rb"))
    return out


D = charger()


# ------------------------------------------------------------------------------------------------- chapitre 6
def tables_corpus():
    cov = []
    for c in NOMS:
        ms = [m for m in C.M if m.candidat == c]
        q = {k: sum(1 for m in ms if m.quantifiable == k) for k in ("oui", "partiel", "non")}
        ch = [m for m in ms if m.montant is not None and m.regime is None and m.id not in ("P06", "P07")]
        tot = sum(abs(m.montant) for m in ch)
        av = sum(abs(m.montant) for m in ch if m.canal and all(v is not None for _, v in m.canal))
        cov.append(f"| {NOMS[c]} | {len(ms)} | {q['oui']} | {q['partiel']} | {q['non']} | {fr(tot, 1, False)} | {fr(av, 1, False)} |")
    tables = {}
    for c in NOMS:
        l = [f"\n**Tableau : mesures du corpus — {NOMS[c]}.** Montants en Md€ (signe du point de vue du solde public), "
             "année de référence entre parenthèses ; « début » : première année d'application dans le modèle ; UE : niveau "
             "de qualification (chapitre \\ref{sec:europe}).\n",
             "| id | mesure | montant | chiffrage | début | traduction dans le modèle | quant. | UE |", "|---|---|---|---|---|---|---|---|"]
        for m in C.M:
            if m.candidat != c:
                continue
            can = []
            for k, v in m.canal:
                if v is None:
                    can.append(f"`{k}` (montant à préciser)")
                elif isinstance(v, dict):
                    can.append(f"`retraites` : " + ", ".join(f"{a}={fr(b, 2, False) if isinstance(b, float) else b}" for a, b in v.items()))
                elif isinstance(v, tuple):
                    can.append(f"`{k}` {fr(v[1], 1)} Md€")
                else:
                    can.append(f"`{k}` {fr(v, 2)}")
            can = "; ".join(can) or (f"régime ({m.regime})" if m.regime else "—")
            ue = str(U.QUALIFICATIONS[m.ue].niveau) if m.ue else "—"
            mt = "—" if m.montant is None else f"{fr(m.montant)} ({m.annee})"
            l.append(f"| {m.id} | {m.intitule} | {mt} | {m.chiffrage} | {m.debut} | {can} | {m.quantifiable} | {ue} |")
        tables[c] = "\n".join(l)
    obj = []
    for c in NOMS:
        o = C.OBJECTIFS[c]
        cib = "solde stabilisant la dette en 2032 (calculé dans le modèle)" if isinstance(o["cibles"], str) else \
            "; ".join(f"{fr(v, 1)} % du PIB en {k}" for k, v in o["cibles"].items())
        parts = ", ".join(f"{k.replace('_', ' ')} {int(round(100 * v))} %" for k, v in o["parts"].items())
        obj.append(f"| {NOMS[c]} | {o['texte']} | {cib} | {parts} |")
    g = (GA / "06_programmes.md").read_text()
    g = g.replace("{COUVERTURE}", "\n".join(cov)).replace("{OBJECTIFS}", "\n".join(obj))
    for c in NOMS:
        g = g.replace("{TABLE_" + c + "}", tables[c])
    (CH / "06_programmes.md").write_text(g)


# ------------------------------------------------------------------------------------------------- chapitre 7
def chapitre7():
    f = RES / "multiplicateurs.csv"
    g = (GA / "07_transmission.md").read_text()
    if not f.exists():
        g = g.replace("{MULT}", "*Simulation non exécutée au moment de la génération du document.*").replace("{MULT_LECTURE}", "—")
    else:
        m = pd.read_csv(f)
        p = m[m["horizon (ans)"].isin([1, 3, 5, 10])].pivot_table(index=["choc", "régime"], columns="horizon (ans)", values="multiplicateur")
        p.columns = [f"multiplicateur à {c} an{'s' if c > 1 else ''}" for c in p.columns]
        p2 = m[m["horizon (ans)"].isin([1, 5, 10])].pivot_table(index=["choc", "régime"], columns="horizon (ans)", values="dette (pt PIB)")
        p2.columns = [f"dette à {c} an{'s' if c > 1 else ''} (pt)" for c in p2.columns]
        t = pd.concat([p, p2], axis=1)
        t.index = [f"{a} — {b}" for a, b in t.index]
        t.index.name = "choc — régime"
        g = g.replace("{MULT}", "**Tableau : multiplicateurs simulés (variation du PIB / coût ex ante, en part du PIB) et effet sur le "
                      "ratio de dette.** Chocs permanents à partir de 2028 ; environnement P4 ; source : `phase7/multiplicateurs.py`.\n\n" + tab(t, 2))
        cp = m[(m.choc.str.startswith("consommation")) & (m["régime"].str.startswith("principal"))].set_index("horizon (ans)")
        tr = m[(m.choc.str.startswith("transferts")) & (m["régime"].str.startswith("principal"))].set_index("horizon (ans)")
        bce = m[(m.choc.str.startswith("consommation")) & (m["régime"] == "BCE + prime")].set_index("horizon (ans)")
        lect = (f"une hausse permanente de la consommation publique a un multiplicateur de {fr(cp.multiplicateur[1], 2, False)} la "
                f"première année, {fr(cp.multiplicateur[5], 2, False)} à cinq ans et {fr(cp.multiplicateur[10], 2, False)} à dix ans "
                f"(régime principal) ; sous le régime BCE + prime, {fr(bce.multiplicateur[1], 2, False)}, {fr(bce.multiplicateur[5], 2, False)} "
                f"et {fr(bce.multiplicateur[10], 2, False)}. Les transferts aux ménages ont un multiplicateur plus faible "
                f"({fr(tr.multiplicateur[1], 2, False)} la première année), une partie étant épargnée. Les multiplicateurs diminuent avec "
                f"l'horizon sous l'effet de la fermeture d'offre et de la hausse des prix.")
        def mu(prefixe, h):
            x = m[(m.choc.str.startswith(prefixe)) & (m["régime"].str.startswith("principal"))].set_index("horizon (ans)")
            return fr(x.multiplicateur[h], 2, False)
        lect += (f" Les baisses de prélèvements sur les entreprises ont des effets d'activité plus faibles et plus lents : "
                 f"{mu('cotisations', 1)} la première année pour les cotisations employeurs (effet sur le coût du travail et "
                 f"l'emploi), {mu('impôts de production', 1)} pour les impôts de production (dont la moitié est répercutée sur "
                 f"les prix et une partie conservée en marges) ; la baisse du taux normal de TVA a un multiplicateur de "
                 f"{mu('TVA', 1)}, parce que les baisses ne sont répercutées qu'à moitié sur les prix. L'investissement public a "
                 f"un effet de première année plus faible que la consommation publique ({mu('investissement', 1)}, contenu en "
                 f"importations plus élevé) mais croissant ({mu('investissement', 10)} à dix ans) grâce à l'accumulation de "
                 f"capital public.")
        g = g.replace("{MULT_LECTURE}", lect)
        # figure
        fig, ax = plt.subplots(figsize=(7, 3.6))
        for nom, gg in m[m["régime"].str.startswith("principal")].groupby("choc"):
            gg = gg.sort_values("horizon (ans)")
            ax.plot(gg["horizon (ans)"], gg["multiplicateur"], marker="o", ms=3, label=nom)
        ax.axhline(0, color="k", lw=0.5); ax.set_xlabel("années après le choc (2028 = 1)"); ax.set_ylabel("multiplicateur")
        ax.legend(fontsize=7, frameon=False); ax.set_title("Multiplicateurs simulés, régime principal (P4)", fontsize=9)
        fig.text(0.01, 0.01, "Source : modèle du projet, phase7/multiplicateurs.py ; chocs permanents ≈ 0,5 pt de PIB.", fontsize=6)
        fig.tight_layout(); fig.savefig(FIG / "multiplicateurs.pdf"); plt.close(fig)
        g = g.replace("Ces valeurs sont à comparer", "```{=latex}\n\\begin{figure}[htbp]\\centering\\includegraphics[width=0.9\\textwidth]{figures/multiplicateurs.pdf}"
                      "\\caption{Multiplicateurs simulés selon l'horizon (régime principal).}\\end{figure}\n```\n\nCes valeurs sont à comparer", 1)
    (CH / "07_transmission.md").write_text(g)


if __name__ == "__main__":
    tables_corpus()
    chapitre7()
    import resultats_etude as RE  # noqa: E402  (chapitres de résultats)
    RE.generer(D)
    print("génération terminée")
