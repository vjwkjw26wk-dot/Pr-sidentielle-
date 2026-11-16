"""Validation des prestations (lot 5, version 1) sur la population M4 : RSA, prime d'activité, allocations
familiales, aides au logement, mois d'octobre 2024 (× 12 pour l'année).

Les montants simulés sont des DROITS (recours de 100 %). Les références sont les montants VERSÉS par les CAF en 2024 ;
le rapport versé / simulé est un taux de recours apparent, à comparer aux estimations publiées de la DREES
(non-recours au RSA de 33 à 37 % des foyers éligibles, à la prime d'activité d'environ la moitié des foyers et de
43 à 46 % de la masse, fin 2021). Sortie : outputs/validation_prestations.md
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
import time
import warnings

import pandas as pd

warnings.filterwarnings("ignore")
RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
TMP = pathlib.Path("/tmp/validation_prestations")
MOIS = "2024-10"
SOUS_ECH = 0.25  # fraction des ménages de l'échantillon M4 (2 %) gardée : 0,5 % des ménages, contrainte de mémoire
# Références 2024 (montants versés par les CAF, foyers bénéficiaires en moyenne ou en fin d'année)
REF = {
    "rsa": (11.9e9, 1.83e6, "CNAF : 11,9 Md€ versés en 2024, 1,83 M de foyers"),
    "ppa": (10.3e9, 4.55e6, "CNAF : ≈ 10,3 Md€ (2,37 + 2,46 + 2,71 Md€ aux trois premiers trimestres), ≈ 4,5 M de foyers"),
    "af": (None, 4.7e6, "CNAF : 4,7 M de familles bénéficiaires"),
    "aide_logement": (16.0e9, 5.8e6, "DREES : APL 7,1 Md€ = 44,3 % des aides au logement, soit ≈ 16 Md€ ; ≈ 5,8 M de foyers"),
}
NOMS = {"rsa": "RSA", "ppa": "Prime d'activité", "af": "Allocations familiales", "aide_logement": "Aides au logement"}


def _travailleur(tache: str):
    """Deux processus séparés : construction de la population, puis simulation (mémoire limitée à environ 7 Go)."""
    if tache == "prep":
        import m4_population as m4
        import numpy as np
        ind, fo, ir = m4.construire(f=0.02)
        men = ind.men.unique()
        garde = set(men[np.random.default_rng(5).random(len(men)) < SOUS_ECH])
        ind = ind[ind.men.isin(garde)].copy()
        ind["poids"] = ind.poids / SOUS_ECH
        ind.to_pickle(TMP / "ind.pkl")
    else:
        import m4_prestations as mp
        r = mp.prestations(pd.read_pickle(TMP / "ind.pkl"), MOIS, variables=(tache,))
        r.to_pickle(TMP / f"res_{tache}.pkl")


def main():
    t0 = time.time()
    TMP.mkdir(exist_ok=True)
    for tache in ("prep", *REF):
        code = f"import sys; sys.path.insert(0, {str(RACINE / 'tests')!r}); import validation_prestations as v; v._travailleur({tache!r})"
        subprocess.run([sys.executable, "-c", code], check=True)
    r = pd.concat([pd.read_pickle(TMP / f"res_{v}.pkl")[[v]] for v in REF], axis=1)
    r["poids"] = pd.read_pickle(TMP / "res_rsa.pkl").poids
    w = r.poids
    L = ["# Validation des prestations (version 1) — droits simulés et montants versés, 2024", "",
         f"Généré par `tests/validation_prestations.py` ({len(r)} familles au sens de la CAF, sous-échantillon de 0,5 % des ménages "
         f"du recensement 2022), mois de calcul {MOIS}, annualisé × 12 ; durée {time.time() - t0:.0f} s.", "",
         "| Prestation | Familles bénéficiaires simulées | Versé : foyers | Droits simulés (Md€/an) | Versé (Md€) | Recours apparent (masse) | Recours apparent (foyers) | Référence |",
         "|---|---|---|---|---|---|---|---|"]
    for v, (masse, n, src) in REF.items():
        nb = (w * (r[v] > 0)).sum()
        mm = (w * r[v]).sum() * 12
        rec_m = f"{masse / mm:.0%}" if masse else "—"
        L.append(f"| {NOMS[v]} | {nb / 1e6:.2f} M | {n / 1e6:.2f} M | {mm / 1e9:.1f} | {masse / 1e9:.1f} | {rec_m} | {n / nb:.0%} | {src} |"
                 if masse else
                 f"| {NOMS[v]} | {nb / 1e6:.2f} M | {n / 1e6:.2f} M | {mm / 1e9:.1f} | — | — | {n / nb:.0%} | {src} |")
    L += ["", "Lecture : un recours apparent proche de 1 − non-recours publié indique un modèle cohérent ; au-dessus de 100 %, "
          "le modèle sous-estime les droits ; très en dessous, il les surestime (ou le non-recours est plus fort qu'estimé).", ""]
    (RACINE / "outputs" / "validation_prestations.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
