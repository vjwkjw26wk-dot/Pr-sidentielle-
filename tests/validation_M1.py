"""Validation de M1 v2 face aux projections de population 2026 de l'Insee.

Test A — réplication : avec les hypothèses de l'Insee, M1 doit reproduire chaque scénario publié
         (population par sexe et âge, naissances, décès) de 2023 à 2070.
Test B — générateur paramétrique : à partir du seul scénario central, M1 doit reproduire les
         variantes de l'Insee en ne fixant que l'ICF, le solde migratoire total ou l'espérance de vie
         visée (ce que fera un utilisateur du simulateur).
Sortie : outputs/validation_M1.md et outputs/validation_M1.json.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
from scipy.optimize import brentq

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
import insee_projections as ip  # noqa: E402
import m1_demographie as m1  # noqa: E402

T0, T1 = 2023, 2070
TB = 2026  # départ du test B
SCENARIOS = ["00_central"] + [s for v in ip.SCENARIOS_ZIP.values() for s in v]


def hyp(d) -> m1.Hypotheses:
    return m1.Hypotheses(d["qF"], d["qH"], d["fec"], d["smF"], d["smH"], d["ajF"], d["ajH"])


def demarrer(d, h, t0=T0):
    pF = m1.etendre_population(d["popF"][t0].to_numpy(), h.qF[t0].reindex(m1.AGES).to_numpy())
    pH = m1.etendre_population(d["popH"][t0].to_numpy(), h.qH[t0].reindex(m1.AGES).to_numpy())
    return pF, pH


def comparer(res: m1.Resultat, d, t0: int = T0) -> dict:
    ans = list(range(t0 + 1, T1 + 1))
    pop_m = res.pop.loc[:104, ans]
    pop_i = (d["popF"] + d["popH"]).loc[:104, ans]
    tot_m = res.total()[ans]
    tot_i = (d["popF"] + d["popH"])[ans].sum()
    ecart_age = (pop_m - pop_i).abs() / pop_i.clip(lower=1000)
    nais_i = d["naiss_age"].sum()[list(range(t0, T1))]
    dec_i = (d["decesF"] + d["decesH"]).sum()[list(range(t0, T1))]
    dec_m = (res.decesF + res.decesH).sum()
    groupes = {}
    for nom, a0, a1 in (("0-19", 0, 19), ("20-64", 20, 64), ("65+", 65, None), ("80+", 80, None), ("100+", 100, None)):
        gm = res.groupe(a0, a1)[[2040, 2070]]
        gi = (d["popF"] + d["popH"]).loc[a0:(a1 if a1 is not None else 105)].sum()[[2040, 2070]]
        groupes[nom] = {str(t): float(gm[t] / gi[t] - 1) for t in (2040, 2070)}
    return {
        "pop_totale_ecart_rel_max": float(((tot_m - tot_i).abs() / tot_i).max()),
        "pop_par_age_ecart_rel_max_0_104": float(ecart_age.to_numpy().max()),
        "naissances_ecart_rel_max": float(((res.naissances - nais_i).abs() / nais_i).max()),
        "deces_ecart_rel_max": float(((dec_m - dec_i).abs() / dec_i).max()),
        "pop_2070_modele": float(tot_m[2070]), "pop_2070_insee": float(tot_i[2070]),
        "groupes": groupes,
        "identite_ecart_max": float(res.ecart_identite.abs().max()),
    }


def test_A():
    out = {}
    for s in SCENARIOS:
        d = ip.charger(s)
        h = hyp(d)
        res = m1.projeter(*demarrer(d, h), T0, T1, h)
        out[s] = comparer(res, d)
        print(f"A {s:24s} pop max {out[s]['pop_totale_ecart_rel_max']:.2e}  âge max {out[s]['pop_par_age_ecart_rel_max_0_104']:.2e}")
    return out


def ev_2070(h, s="F"):
    return m1.esperance_de_vie(getattr(h, "q" + s)[2070].reindex(m1.AGES).to_numpy())


def generateur(central) -> m1.GenerateurScenarios:
    """Apprend les directions de variation sur 3 scénarios seulement : smi_haut, ev_haute, ev_basse."""
    sh, eh, eb = ip.charger("15_smi_haut"), ip.charger("13_ev_haute"), ip.charger("14_ev_basse")
    return m1.GenerateurScenarios(hyp(central), (sh["smF"], sh["smH"]), (eh["qF"], eh["qH"]), (eb["qF"], eb["qH"]))


def parametres_utilisateur(d) -> dict:
    """Ce qu'un utilisateur du simulateur fixerait : trajectoire d'ICF, solde total, EV des femmes en 2070."""
    return {"icf": {t: float(d["fec"][t].sum()) for t in range(2026, 2031)},
            "sm_total": {2026: float(d["smF"][2030].sum() + d["smH"][2030].sum())},
            "ev_femmes_2070": ev_2070(hyp(d), "F")}


def test_B(central):
    g = generateur(central)
    hc = hyp(central)
    apprentissage = {"15_smi_haut", "13_ev_haute", "14_ev_basse"}
    out = {}
    for s in SCENARIOS[1:]:
        if s in apprentissage:
            continue
        d = ip.charger(s)
        par = parametres_utilisateur(d)
        if s == "52_ev_constante":  # hors des directions Insee : paramètre « rythme des gains » = 0
            par = {"rythme_gains_mortalite": 0.0}
        # départ au 1er janvier 2026 sur la population du scénario (les variantes Insee divergent dès 2023,
        # le solde 2023-2025 n'étant pas observé) ; l'effet est mesuré sur la variation 2026-2070
        h = g.construire(TB, T1, **par)
        res = m1.projeter(*demarrer(d, h, TB), TB, T1, h)
        ref = m1.projeter(*demarrer(d, h, TB), TB, T1, hyp(central))
        c = comparer(res, d, TB)
        c["effet_2070_insee"] = float(c["pop_2070_insee"] - ref.total()[2070])
        c["effet_2070_modele"] = float(c["pop_2070_modele"] - ref.total()[2070])
        c["effet_ratio"] = c["effet_2070_modele"] / c["effet_2070_insee"] if abs(c["effet_2070_insee"]) > 2e5 else float("nan")
        c["description"] = ("rythme des gains de mortalité = 0" if "rythme_gains_mortalite" in par else
                            (f"ICF {par['icf'][2030]:.2f} ; solde {par['sm_total'][2026]:+,.0f} ; "
                             f"EV F 2070 {par['ev_femmes_2070']:.1f} (λ = {h.lambda_ev:+.2f})").replace(",", " "))
        c["ev_hommes_2070_ecart"] = float(ev_2070(h, "H") - ev_2070(hyp(d), "H"))
        out[s] = c
        print(f"B {s:36s} effet modèle/Insee {c['effet_ratio']:.3f}  pop max {c['pop_totale_ecart_rel_max']:.1e}  âge max {c['pop_par_age_ecart_rel_max_0_104']:.3f}  EV H {c['ev_hommes_2070_ecart']:+.2f}")
    return out


def rapport(A, B):
    L = ["# Validation de M1 v2 (démographie) face aux projections de population 2026 de l'Insee", "",
         "Généré par `tests/validation_M1.py`. Période 2023-2070. Écarts relatifs.", "",
         "## Test A — réplication des 29 scénarios publiés (27 scénarios et 2 scénarios de travail) (hypothèses de l'Insee en entrée)", "",
         "| Scénario | Population totale, écart max | Population par âge 0-104 ans, écart max | Naissances | Décès | Identité |",
         "|---|---|---|---|---|---|"]
    for s, c in A.items():
        L.append(f"| {s} | {c['pop_totale_ecart_rel_max']:.1e} | {c['pop_par_age_ecart_rel_max_0_104']:.1e} | "
                 f"{c['naissances_ecart_rel_max']:.1e} | {c['deces_ecart_rel_max']:.1e} | {c['identite_ecart_max']:.1e} |")
    L += ["", "Écarts par grand groupe d'âge, scénario central :", "",
          "| Groupe | 2040 | 2070 |", "|---|---|---|"]
    for g, v in A["00_central"]["groupes"].items():
        L.append(f"| {g} | {v['2040']:+.2%} | {v['2070']:+.2%} |")
    L += ["", "## Test B — scénarios paramétriques construits à partir du seul scénario central", "",
          "Départ au 1er janvier 2026 sur la population de chaque scénario ; effet = écart en 2070 à une projection centrale partant du même point (rapport non calculé si l'effet Insee est inférieur à 200 000).", "",
          "Le générateur n'apprend que sur le central et trois variantes (15_smi_haut, 13_ev_haute, 14_ev_basse) ; "
          "chaque autre scénario est reconstruit à partir des seuls paramètres qu'un utilisateur fixerait.", "",
          "| Scénario Insee | Paramètres transmis | Effet 2070 Insee | Effet 2070 M1 | Rapport | Population, écart max | Par âge, écart max | EV hommes 2070, écart (ans) |",
          "|---|---|---|---|---|---|---|---|"]
    for s, c in B.items():
        L.append(f"| {s} | {c['description']} | {c['effet_2070_insee']/1e6:+.2f} M | {c['effet_2070_modele']/1e6:+.2f} M | "
                 f"{c['effet_ratio']:.3f} | {c['pop_totale_ecart_rel_max']:.2%} | {c['pop_par_age_ecart_rel_max_0_104']:.1%} | {c['ev_hommes_2070_ecart']:+.2f} |")
    (RACINE / "outputs").mkdir(exist_ok=True)
    (RACINE / "outputs" / "validation_M1.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (RACINE / "outputs" / "validation_M1.json").write_text(json.dumps({"A": A, "B": B}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    A = test_A()
    B = test_B(ip.charger("00_central"))
    rapport(A, B)
