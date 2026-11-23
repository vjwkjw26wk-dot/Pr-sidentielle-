"""Figures du rapport v0.8 : écart de production, réponses impulsionnelles, backtest (données exécutées)."""
import json
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

R = pathlib.Path(__file__).resolve().parents[2]
RES = R / "phase31" / "resultats"
FIG = R / "phase31" / "rapport" / "figures"
FIG.mkdir(parents=True, exist_ok=True)
sys.path[:0] = [str(R / "phase31"), str(R / "src"), str(R)]
BLEU, ORANGE, VERT, ROUGE, GRIS = "#1F4E79", "#C55A11", "#2C7C3C", "#A61B1B", "#777777"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})


def ecart():
    import estimation_theta as E
    fig, ax = plt.subplots(figsize=(10, 3))
    for src, c in (("AMECO", BLEU), ("FMI", ORANGE)):
        g, _ = E.donnees(src)
        a = sorted(t for t in g if 1980 <= t <= 2025)
        ax.plot(a, [g[t] for t in a], color=c, lw=1.6, label=f"{src}")
    ax.axhline(0, color="#999", lw=0.6)
    ax.axvspan(2019.5, 2021.5, color="#eee")
    ax.set_ylabel("% du PIB potentiel")
    ax.legend(frameon=False)
    ax.set_title("Écart de production de la France (Commission européenne et FMI)", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG / "ecart_production.pdf")
    plt.close(fig)


def irf():
    d = {}
    for f in ("irf_i.json", "irf_j.json", "irf_k.json"):
        d.update(json.loads((RES / f).read_text()))
    est = json.loads((RES / "estimation_theta.json").read_text())
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.4))
    ans = list(range(0, 13))
    for k, v in d.items():
        rho, th, pk, am = map(float, k.split("|"))
        if am != 0.0 or pk != 1.0 or rho != 0.2:
            continue
        g = np.array(v["offre"]["gap"][:13])
        st = dict(lw=2.2, color=ROUGE) if th == 0.75 else dict(lw=1.0, color=GRIS if th in (0.0, 1.5) else BLEU)
        ax[0].plot(ans, g / g[0], label=f"θ = {th}".replace(".", ","), **st)
    # AR(2) empirique (AMECO)
    p1, p2 = est["duree_empirique"]["AMECO"]["phi"]
    x = [0.0, 1.0]
    for _ in range(12):
        x.append(p1 * x[-1] + p2 * x[-2])
    ax[0].plot(ans, x[1:], "k--", lw=1.2, label="AR(2) AMECO (écart observé)")
    ax[0].axhline(0, color="#999", lw=0.5)
    ax[0].set_xlabel("années après le choc")
    ax[0].set_title("Écart de production après un choc d'offre (ρ = 0,2)", fontsize=9)
    ax[0].legend(frameon=False, fontsize=7)
    c = est["configurations"]
    xs = [v["duree"] for v in c.values()]
    ys = [v["dette_2047_choc_offre"] for v in c.values()]
    col = [VERT if v["plausible"] else GRIS for v in c.values()]
    lo, hi = est["intervalle_cible"]
    ax[1].axvspan(lo, hi, color="#e8f2ea", zorder=0)
    ax[1].scatter(xs, ys, c=col, s=18, zorder=3)
    ax[1].axvline(est["cible_centrale"], color=VERT, lw=1)
    ax[1].set_xlabel("durée de l'écart (années)")
    ax[1].set_ylabel("dette 2047 (points de PIB)")
    ax[1].set_title("Durée de l'écart et effet sur la dette (vert : plausibles)", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG / "irf_theta.pdf")
    plt.close(fig)


def backtest():
    b = json.loads((RES / "backtest.json").read_text())
    import backtest as BT
    import m8_modele as M
    mod = M.Modele(2010, 2010)
    o = BT.observe(mod)
    fig, ax = plt.subplots(2, 3, figsize=(10.5, 5.6))
    spec = [("pib", "PIB en volume (indice 2010 = 100)", "niv"), ("emploi", "Emploi (indice 2010 = 100)", "niv"), ("chomage", "Chômage (%)", "pt"),
            ("pc", "Prix à la consommation (indice 2010 = 100)", "niv"), ("salaire_reel", "Salaire réel par tête (indice)", "niv"),
            ("dette_pib", "Dette publique (% du PIB)", "pt")]
    for i, (k, lib, typ) in enumerate(spec):
        a = ax[i // 3, i % 3]
        ans = list(range(2010, 2026))
        if typ == "pt":
            a.plot(ans, [float(o[k][t]) for t in ans], "k-", lw=1.8, label="observé")
        else:
            a.plot(ans, [100 * float(o[k][t] / o[k][2010]) for t in ans], "k-", lw=1.8, label="observé")
        for var, c, lab in (("v06", GRIS, "v0.6"), ("v07", ORANGE, "v0.7"), ("v08", BLEU, "v0.8")):
            for per in ("2010-2019", "2021-2025"):
                r = b.get(f"{var}|{per}")
                if not r or "erreur" in r:
                    continue
                B = int(per[:4])
                if typ == "pt":
                    s = r[k]["sim"]
                    xs = [B] + [int(t) for t in s]
                    ys = [float(o[k][B])] + list(s.values())
                else:
                    lv = r[k]["erreur_niveau_pct"]
                    xs = [B] + [int(t) for t in lv]
                    base = 100 * float(o[k][B] / o[k][2010])
                    ys = [base] + [100 * float(o[k][int(t)] / o[k][2010]) * (1 + e / 100) for t, e in lv.items()]
                a.plot(xs, ys, color=c, lw=1.2, label=lab if per == "2010-2019" else None)
        a.axvspan(2019.5, 2021.5, color="#eee")
        a.set_xticks([2010, 2015, 2020, 2025])
        a.set_title(lib, fontsize=8.5)
    ax[0, 0].legend(frameon=False, fontsize=7)
    fig.suptitle("Rétrosimulations en temps réel : origines 2010 (jusqu'en 2019) et 2021 (jusqu'en 2025)", fontsize=9.5)
    fig.tight_layout()
    fig.savefig(FIG / "backtest.pdf")
    plt.close(fig)


if __name__ == "__main__":
    for f in sys.argv[1:] or ["ecart", "irf", "backtest"]:
        globals()[f]()
        print(f, "ok")
