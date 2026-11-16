"""Validation des prestations (version 1.1) sur la population M4 : RSA, prime d'activité, allocations familiales,
aides au logement, mois d'octobre 2024 (× 12 pour l'année).

Les montants simulés sont des DROITS (recours de 100 %). Les références sont les montants VERSÉS par les CAF en 2024 ;
le rapport versé / simulé est un taux de recours apparent, à comparer aux estimations publiées de la DREES
(non-recours au RSA de 33 à 37 % des foyers éligibles ; à la prime d'activité, environ la moitié des foyers éligibles
et 43 à 46 % de la masse, fin 2021).

Version 1.1 :
- revenus mensuels variables pour les contrats non permanents (p_emploi central 0,75 ; sensibilité 1,0 et 0,6) ;
- incertitude d'échantillonnage : l'échantillon M4 de 2 % est partagé en 4 sous-échantillons indépendants de 0,5 %
  (tirage par ménage) ; chacun est simulé séparément. L'estimation retenue est la moyenne des 4 (équivalent 2 %),
  son erreur type est l'écart type entre sous-échantillons divisé par 2 ;
- cohérence entre recours en nombre et recours en masse : montants moyens par bénéficiaire, modèle et réel.
Sortie : outputs/validation_prestations.md
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
import time
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
TMP = pathlib.Path("/tmp/validation_prestations")
MOIS = "2024-10"
K = 4                 # sous-échantillons indépendants de 0,5 % (contrainte de mémoire d'OpenFisca)
P_EMPLOI = 0.75       # probabilité mensuelle d'emploi des titulaires de contrats non permanents (hypothèse D)
SENSIBILITE = (1.0, 0.6)
REF = {
    "rsa": (11.9e9, 1.83e6, "CNAF : 11,9 Md€ versés en 2024, 1,83 M de foyers en moyenne"),
    "ppa": (10.3e9, 4.55e6, "CNAF : ≈ 10,3 Md€ (2,37 + 2,46 + 2,71 Md€ aux trois premiers trimestres, T4 estimé), ≈ 4,55 M de foyers"),
    "af": (None, 4.7e6, "CNAF : 4,7 M de familles bénéficiaires"),
    "aide_logement": (16.0e9, 5.8e6, "DREES : APL 7,1 Md€ = 44,3 % des aides au logement, soit ≈ 16 Md€ ; ≈ 5,8 M de foyers"),
}
DREES = {"rsa": "63 à 67 % des foyers", "ppa": "≈ 50 % des foyers ; 54 à 57 % de la masse", "af": "proche de 100 %",
         "aide_logement": "élevé (non publié)"}
NOMS = {"rsa": "RSA", "ppa": "Prime d'activité", "af": "Allocations familiales", "aide_logement": "Aides au logement"}


def _travailleur(tache: str, k: int = 0, var: str = "", p: float = P_EMPLOI):
    if tache == "prep":
        import m4_population as m4
        ind, fo, ir = m4.construire(f=0.02)
        men = ind.men.unique()
        grp = pd.Series(np.random.default_rng(5).integers(0, K, len(men)), index=men)
        ind["sous_ech"] = grp.reindex(ind.men).to_numpy()
        ind["poids"] = ind.poids * K
        for j in range(K):
            ind[ind.sous_ech == j].to_pickle(TMP / f"ind_{j}.pkl")
    else:
        import m4_prestations as mp
        r = mp.prestations(pd.read_pickle(TMP / f"ind_{k}.pkl"), MOIS, variables=(var,), p_emploi=p)
        r.to_pickle(TMP / f"res_{k}_{var}_{p}.pkl")


def _lancer(*args):
    code = (f"import sys; sys.path.insert(0, {str(RACINE / 'tests')!r}); import validation_prestations as v; "
            f"v._travailleur(*{args!r})")
    subprocess.run([sys.executable, "-c", code], check=True)


def stats(r: pd.DataFrame, v: str) -> tuple[float, float]:
    w = r.poids
    return float((w * (r[v] > 0)).sum()), float((w * r[v]).sum() * 12)


def rapide():
    """Re-simulation du RSA et de la prime d'activité seulement, après modification des règles de famille."""
    out = {}
    for v in ("rsa", "ppa"):
        r = [stats((_lancer("simul", k, v, P_EMPLOI), pd.read_pickle(TMP / f"res_{k}_{v}_{P_EMPLOI}.pkl"))[1], v) for k in range(K)]
        out[v] = (np.mean([x[0] for x in r]), np.mean([x[1] for x in r]))
        print(v, f"éligibles {out[v][0] / 1e6:.2f} M, droits {out[v][1] / 1e9:.1f} Md€, recours foyers {REF[v][1] / out[v][0]:.0%}, masse {REF[v][0] / out[v][1]:.0%}")
    return out


def main():
    t0 = time.time()
    TMP.mkdir(exist_ok=True)
    _lancer("prep")
    res = {}
    for k in range(K):
        for v in REF:
            _lancer("simul", k, v, P_EMPLOI)
            res[(k, v)] = stats(pd.read_pickle(TMP / f"res_{k}_{v}_{P_EMPLOI}.pkl"), v)
    sens = {}
    for p in SENSIBILITE:
        for k in range(K):
            _lancer("simul", k, "ppa", p)
            sens[(k, p)] = stats(pd.read_pickle(TMP / f"res_{k}_ppa_{p}.pkl"), "ppa")
    L = ["# Validation des prestations (version 1.1) — droits simulés et montants versés, 2024", "",
         f"Généré par `tests/validation_prestations.py` : {K} sous-échantillons indépendants de 0,5 % des ménages du recensement 2022 "
         f"(ensemble = 2 %), mois de calcul {MOIS} annualisé × 12, probabilité mensuelle d'emploi des contrats non permanents "
         f"{P_EMPLOI} ; durée {time.time() - t0:.0f} s. Les intervalles sont ± 2 erreurs types d'échantillonnage.", "",
         "## Droits simulés et montants versés", "",
         "| Prestation | Éligibles simulés (M) | Bénéficiaires réels (M) | Droits simulés (Md€/an) | Versé (Md€) | Recours apparent, foyers | Recours apparent, masse | Recours estimé par la DREES |",
         "|---|---|---|---|---|---|---|---|"]
    tab = {}
    for v, (masse, n, src) in REF.items():
        nb = np.array([res[(k, v)][0] for k in range(K)])
        mm = np.array([res[(k, v)][1] for k in range(K)])
        tab[v] = (nb.mean(), nb.std(ddof=1) / np.sqrt(K), mm.mean(), mm.std(ddof=1) / np.sqrt(K), nb.std(ddof=1), mm.std(ddof=1))
        nbm, nbs, mmm, mms = tab[v][:4]
        rec_n = f"{n / nbm:.0%} ({n / (nbm + 2 * nbs):.0%}–{n / (nbm - 2 * nbs):.0%})"
        rec_m = f"{masse / mmm:.0%} ({masse / (mmm + 2 * mms):.0%}–{masse / (mmm - 2 * mms):.0%})" if masse else "—"
        L.append(f"| {NOMS[v]} | {nbm / 1e6:.2f} ± {2 * nbs / 1e6:.2f} | {n / 1e6:.2f} | {mmm / 1e9:.1f} ± {2 * mms / 1e9:.1f} | "
                 f"{masse / 1e9:.1f} | {rec_n} | {rec_m} | {DREES[v]} |" if masse else
                 f"| {NOMS[v]} | {nbm / 1e6:.2f} ± {2 * nbs / 1e6:.2f} | {n / 1e6:.2f} | {mmm / 1e9:.1f} ± {2 * mms / 1e9:.1f} | — | {rec_n} | — | {DREES[v]} |")
    L += ["", "## Cohérence entre recours en nombre et recours en masse", "",
          "Si les non-recourants ont des droits plus faibles que les recourants (constat de la DREES pour le RSA : 42 % des "
          "non-recourants ont un droit mensuel faible), le recours en masse doit dépasser le recours en nombre, et le montant "
          "moyen réellement versé doit dépasser le droit moyen simulé.", "",
          "| Prestation | Droit moyen simulé (€/mois) | Montant moyen versé (€/mois) | Recours masse − recours foyers |", "|---|---|---|---|"]
    for v, (masse, n, _) in REF.items():
        if not masse:
            continue
        nbm, _, mmm, _ = tab[v][:4]
        L.append(f"| {NOMS[v]} | {mmm / 12 / nbm:.0f} | {masse / 12 / n:.0f} | {(masse / mmm - n / nbm) * 100:+.0f} points |")
    L += ["", "## Sensibilité de la prime d'activité à la variabilité des revenus", "",
          "| Probabilité mensuelle d'emploi (contrats non permanents) | Éligibles (M) | Droits (Md€/an) | Recours apparent foyers | Recours apparent masse |",
          "|---|---|---|---|---|"]
    for p in (1.0, P_EMPLOI, 0.6):
        if p == P_EMPLOI:
            nbm, mmm = tab["ppa"][0], tab["ppa"][2]
        else:
            nbm = np.mean([sens[(k, p)][0] for k in range(K)])
            mmm = np.mean([sens[(k, p)][1] for k in range(K)])
        L.append(f"| {p} | {nbm / 1e6:.2f} | {mmm / 1e9:.1f} | {REF['ppa'][1] / nbm:.0%} | {REF['ppa'][0] / mmm:.0%} |")
    L += ["", "## Représentativité du sous-échantillon de 0,5 %", "",
          "Écart type entre sous-échantillons de 0,5 % (erreur d'un calcul fait sur un seul sous-échantillon) :", "",
          "| Prestation | Éligibles : écart type relatif | Droits : écart type relatif |", "|---|---|---|"]
    for v in REF:
        L.append(f"| {NOMS[v]} | {tab[v][4] / tab[v][0]:.1%} | {tab[v][5] / tab[v][2]:.1%} |")
    L.append("")
    (RACINE / "outputs" / "validation_prestations.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
