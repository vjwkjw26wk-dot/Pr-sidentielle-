"""Tests unitaires des mécanismes ajoutés par l'audit de novembre 2026 et tests d'identités comptables du modèle bouclé.

Usage : python3 tests/test_m14_identites.py  (code de sortie 1 en cas d'échec)
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
import m14_heterogeneite as H  # noqa: E402

ECHECS = []


def verifier(cond, msg):
    print(("ok    " if cond else "ÉCHEC ") + msg)
    if not cond:
        ECHECS.append(msg)


def distribution(masses, revenus=None):
    revenus = revenus or [x * 1e5 for x in H.PARTS_REVENU]
    return [{"decile": d + 1, "masse_M€": m, "revenu_M€": r} for d, (m, r) in enumerate(zip(masses, revenus))]


def tests_m14():
    # profil plat : aucune correction
    verifier(abs(H.ajustement_conso(distribution([100] * 10), "plat")) < 1e-9, "profil plat : pas de correction")
    # gain proportionnel au revenu : correction nulle par construction (normalisation par la moyenne pondérée)
    rev = [x * 1e5 for x in H.PARTS_REVENU]
    verifier(abs(H.ajustement_conso(distribution([r * 0.01 for r in rev], rev))) < 1e-6, "gain proportionnel au revenu : pas de correction")
    # transfert au premier décile : consommation plus forte que la moyenne
    verifier(H.ajustement_conso(distribution([1000] + [0] * 9)) > 0, "transfert au 1er décile : revenu effectif accru")
    # impôt sur le dernier décile : consommation moins réduite que la moyenne (correction positive)
    verifier(H.ajustement_conso(distribution([0] * 9 + [-1000])) > 0, "impôt sur le 10e décile : baisse de consommation atténuée")
    # ordre des profils
    a = [H.ajustement_conso(distribution([1000] + [0] * 9), v) for v in ("plat", "central", "accentue")]
    verifier(a[0] < a[1] < a[2], "sensibilité : plat < central < accentué")
    # dividendes : conservation des montants
    d = H.dividendes_menages(1000.0, 0.5)
    verifier(abs(sum(d.values()) - 1000.0) < 1e-9, "répartition des profits : somme conservée")
    verifier(H.facteur_top1() < 0.5, "propension du dernier centile inférieure à la moitié de la moyenne")
    rp = H.revenus_primaires_nets(2022)
    verifier(0.0 < rp < 0.06, f"revenus primaires nets du reste du monde 2022 : {rp * 100:.1f} % du PIB (positif, < 6 %)")


def tests_modele():
    import m8_modele as M
    mod = M.Modele(2022)
    ans = range(2023, 2029)
    ex = M.exogenes_projection(mod, ans)
    r = mod.simuler(ans, ex)
    # identités
    for t in ans:
        verifier(abs(r.taux_epargne[t] - 100 * (r.rdb[t] - r.c[t] * r.pc[t]) / r.rdb[t]) < 1e-9, f"{t} : taux d'épargne = (RDB − C) / RDB")
        verifier(abs(r.rnb[t] - r.pib_nominal[t] - r.revenus_primaires_nets[t]) < 1e-6, f"{t} : RNB = PIB + revenus primaires nets")
        verifier(abs(r.capacite_menages[t] - (r.epargne_menages[t] - r.investissement_menages[t])) < 1e-6,
                 f"{t} : capacité de financement des ménages = épargne − investissement")
    # dette publique : Δdette = −solde (hors calage de la dette)
    for t in list(ans)[1:]:
        verifier(abs((r.dette[t] - r.dette[t - 1]) + r.solde[t]) < 1e-3 * abs(r.dette[t]), f"{t} : variation de la dette = −solde public")
    # Leontief : production = consommations intermédiaires domestiques + demande finale domestique
    mod.dem = dict(mod.tot)
    x, Mtot, Ad, Am = mod._leontief(1.0, np.ones(len(mod.P)))
    fd = sum(mod.struct[k] * mod.dem[k] * (1 - np.clip(mod.part_imp[k], 0, 1)) for k in M.CAT)
    verifier(np.allclose(x, Ad @ x + fd, rtol=1e-8), "Leontief : x = Ad x + demande finale domestique")
    # importations non concurrentes : parts inchangées quand φ varie
    nc = mod.concurrent == 0
    _, _, _, Am_bas = mod._leontief(0.5, np.ones(len(mod.P)))
    _, _, _, Am_haut = mod._leontief(1.5, np.ones(len(mod.P)))
    verifier(np.allclose((Am_bas / np.where(mod.Atot > 0, mod.Atot, 1))[nc], (Am_haut / np.where(mod.Atot > 0, mod.Atot, 1))[nc]),
             "énergie : parts importées indépendantes du facteur commun φ")
    verifier(not np.allclose(Am_bas[~nc], Am_haut[~nc]), "produits concurrents : parts importées sensibles à φ")
    # équilibre ressources-emplois à l'année de base (prix de base) : demande finale = VA + importations + impôts nets sur produits
    tot_df = sum(mod.tot.values())
    va = float((mod.av * x).sum())
    tx = float((mod.at * x).sum())
    verifier(abs(tot_df - (va + Mtot + tx)) / tot_df < 0.02, f"ERE de base : demande finale {tot_df:,.0f} ≈ VA + M + impôts {va + Mtot + tx:,.0f} (écart < 2 %)")


if __name__ == "__main__":
    tests_m14()
    if "--rapide" not in sys.argv:
        tests_modele()
    print(f"\n{len(ECHECS)} échec(s)")
    sys.exit(1 if ECHECS else 0)
