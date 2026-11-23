import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
fig, ax = plt.subplots(figsize=(10, 6.2)); ax.set_xlim(0, 100); ax.set_ylim(0, 62); ax.axis("off")
B, O = "#1F4E79", "#C55A11"
def box(x, y, w, h, t, c=B, fs=8.5):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2", fc=("#FDF1E7" if c == O else "#EEF3F8"), ec=c, lw=1.3))
    ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, color="#222", wrap=True)
def arr(x1, y1, x2, y2, c="#555"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", color=c, lw=1.1))
box(2, 47, 22, 11, "Mesures de politique\npublique (43 curseurs)")
box(30, 47, 30, 11, "Microsimulation des ménages\n(M10, OpenFisca)\nrevenus par décile, âge,\ncatégorie, région, famille")
box(66, 47, 30, 11, "Offre de travail (M15, nouveau)\nparticipation et heures\npar configuration familiale", O)
box(2, 28, 22, 13, "Retraites (M9)\npopulation active\nseniors, pensions")
box(30, 26, 30, 17, "Bloc macroéconomique (M8)\ndemande : consommation,\ninvestissement, commerce\nprix, salaires, emploi\n64 produits × 25 branches")
box(66, 26, 30, 17, "Bloc d'offre (nouveau)\nPIB potentiel Cobb-Douglas\nécart de production\nfermeture + anticipation", O)
box(2, 6, 22, 13, "Zone euro (M11)\ndemande, taux")
box(30, 4, 30, 15, "Comportements (nouveau)\nprécaution, taux réel, TVA\nasymétrique, transfert de\nbénéfices, trésorerie, énergie", O)
box(66, 4, 30, 15, "Finances publiques\nstabilisateur chômage (nouveau)\nsolde, dette, intérêts")
arr(24, 52.5, 30, 52.5); arr(60, 52.5, 66, 52.5); arr(45, 47, 45, 43); arr(81, 47, 81, 43, O)
arr(60, 36, 66, 36, O); arr(66, 31, 60, 31, O); arr(24, 34.5, 30, 34.5); arr(24, 12.5, 30, 30)
arr(45, 19, 45, 26, O); arr(60, 30, 70, 19); arr(13, 47, 13, 41)
ax.text(63, 37.5, "Y, K, N", fontsize=7, color=O, ha="center"); ax.text(63, 29.2, "écart g, Z", fontsize=7, color=O, ha="center")
fig.savefig("figures/architecture_v07.pdf", bbox_inches="tight"); print("ok")
