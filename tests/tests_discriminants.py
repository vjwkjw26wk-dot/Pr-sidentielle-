"""Tests discriminants des mécanismes de transmission (contre-expertise, version 0.6).

Six expériences construites pour séparer des mécanismes que les variantes usuelles confondent. Mesures en vigueur en
2028, trajectoire de référence « politique inchangée », rétroactions de la zone euro désactivées (identiques pour
toutes les expériences), horizon 2035 (le modèle n'est pas projeté au-delà). Montants en euros de 2025, indexés ensuite
sur le PIB nominal. Sortie : outputs/tests_discriminants.md et .json.
Usage : python3 tests/tests_discriminants.py
"""
from __future__ import annotations

import copy
import json
import pathlib
import sys

import numpy as np
import pandas as pd

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
sys.path.insert(0, str(RACINE))
import m8_modele as M  # noqa: E402
import m8_reference as RF  # noqa: E402
import m14_heterogeneite as H14  # noqa: E402
from simulateur import sensibilite as S, executer as X, catalogue as CAT  # noqa: E402

DEBUT, ANS, VUES = 2028, range(2023, 2036), (2028, 2032, 2035)
IND = [("pib", "PIB %"), ("c", "Conso. %"), ("fbcf", "FBCF %"), ("m", "Import. %"), ("emploi", "Emploi (k)"), ("chomage", "Chômage pt"),
       ("taux_epargne", "Épargne pt"), ("pc", "Prix %"), ("solde_pib", "Solde pt"), ("dette_pib", "Dette pt"),
       ("solde_exterieur_pib", "Ext. pt"), ("rnb_md", "RNB Md€"), ("pib_nom_md", "PIB nom. Md€")]
RENDEMENT = 0.03   # rendement nominal supposé d'un placement financier (calcul hors modèle, signalé)


def ecarts(mod, c, v):
    out = {}
    for d in (c, v):
        d["solde_exterieur_pib"] = d.solde_exterieur / d.pib_nominal * 100
        d["rnb_md"] = d.rnb / 1e3
        d["pib_nom_md"] = d.pib_nominal / 1e3
    for k, _ in IND:
        out[k] = {t: float(v[k][t] - c[k][t]) if k in ("emploi", "chomage", "taux_epargne", "solde_pib", "dette_pib", "solde_exterieur_pib",
                                                        "rnb_md", "pib_nom_md")
                  else float((v[k][t] / c[k][t] - 1) * 100) for t in VUES}
    return out


def main():
    mod = X.modele(2022)
    ref = RF.exogenes_variante(mod, ANS, "inchangee", journal=lambda *a: None)
    m = mod.macro
    eur = m.pib_cp[mod.B] / m.pib_cp[2025]            # euros de 2025 → euros de l'année de base
    c0 = mod.simuler(ANS, ref)
    rdb0 = float(c0.rdb[2025])
    res, notes = {}, {}

    def run(nom, ex, note=""):
        res[nom] = ecarts(mod, c0.copy(), mod.simuler(ANS, ex))
        notes[nom] = note

    def mm(**kw):
        d = {"impots": 0.0, "prestations": 0.0, "annee": mod.B, "debut": DEBUT}
        d.update(kw)
        return d

    def conso_eff(masses):            # ajustement de revenu effectif pour une répartition par décile (M€ de base)
        rev = [p * rdb0 for p in H14.PARTS_REVENU]
        return H14.ajustement_conso([{"decile": i + 1, "masse_M€": x, "revenu_M€": r} for i, (x, r) in enumerate(zip(masses, rev))])

    M10 = 10_000 * eur

    def invest_plus(ex, md_2025):
        """FBCF « autres » augmentée de md_2025 M€ de 2025 par an à partir de 2028 (même règle que le simulateur)."""
        f = 1 + md_2025 / float(m.p_fbcf[2025]) / float(ex.autres_investissements[2025])
        return pd.Series({a: v * (f if a >= DEBUT else 1.0) for a, v in ex.autres_investissements.items()})
    # ---- Test 1 : redistribution, +10 Md€ de revenu disponible
    bas = [M10 * w for w in (0.5, 0.3, 0.2, 0, 0, 0, 0, 0, 0, 0)]
    haut = [M10 * w for w in (0, 0, 0, 0, 0, 0, 0, 0, 0.3, 0.7)]
    prop = [M10 * w / sum(H14.PARTS_REVENU) for w in H14.PARTS_REVENU]
    for nom, masses, typ in (("T1a transfert aux déciles 1-3", bas, "prestations"), ("T1b baisse d'impôt déciles 9-10", haut, "impots"),
                             ("T1c hausse proportionnelle au revenu", prop, "prestations")):
        e = copy.deepcopy(ref)
        e.mesure_menages = mm(**{typ: (M10 if typ == "prestations" else -M10), "conso": conso_eff(masses)})
        run(nom, e, "Même montant ; seul diffère le profil des propensions à consommer (M14). Contenu importé identique par construction (écart par quintile ≈ 1 point, audit v0.5).")
    # ---- Test 2 : nature de la demande, 10 Md€
    e = copy.deepcopy(ref)
    e.mesure_menages = mm(conso=M10 / 0.83)
    run("T2a consommation des ménages +10 Md€ (baisse de l'épargne)", e, "Baisse durable du taux d'épargne équivalente à 10 Md€ de consommation la première année.")
    sc = {"nom": "ip", "horizon": 2035, "hypotheses": {"europe": False, "profils": False},
          "mesures": [next(c for c in CAT.CURSEURS if c["cle"] == "investissement_public")["mesure"](10)]}
    _, var_ip, _, _ = X.construire(X.depuis_curseurs(sc), mod)
    run("T2b investissement public +10 Md€ (infrastructures)", var_ip, "Effet de demande et effet d'offre du capital public (élasticité 0,08, littérature).")
    sc["hypotheses"]["elasticite_capital_public"] = 0.0
    _, var_ip0, _, _ = X.construire(X.depuis_curseurs(sc), mod)
    run("T2c investissement public +10 Md€, sans effet d'offre", var_ip0, "Contrôle : effet de demande seul.")
    # ---- Test 3 : affectation d'une épargne supplémentaire de 10 Md€
    e = copy.deepcopy(ref)
    e.mesure_menages = mm(conso=-M10 / 0.83)
    run("T3a épargne +10 Md€ placée à l'étranger", e, f"Le modèle n'a pas de bilan financier : le rendement du placement ({RENDEMENT:.0%}) est ajouté au RNB hors modèle dans le rapport.")
    run("T3b épargne +10 Md€ en actifs français existants", e, "Transfert de propriété : aucun effet réel dans le modèle (pas d'effet de prix des actifs ni de richesse) ; identique à T3a hors revenus.")
    e = copy.deepcopy(ref)
    e.mesure_menages = mm(conso=-M10 / 0.83)
    e.autres_investissements = invest_plus(ref, 10_000)
    run("T3c épargne +10 Md€ finançant un investissement nouveau en France", e,
        "Investissement de 10 Md€ par an (approximation : FBCF « autres », sans effet sur le capital productif des branches).")
    # ---- Test 4 : baisse de l'IS, cinq comportements
    tau0 = float(ref.taux_is.get(DEBUT, ref.taux_is.iloc[-1]))
    G = 0.15 * float(mod.apu.d5rec[mod.B]) * (tau0 - 20.0) / tau0
    base = copy.deepcopy(ref)
    base.taux_is = pd.Series({t: (x if t < DEBUT else 20.0) for t, x in ref.taux_is.items()})
    for nom, part, invest, note in (
            ("T4a investissement majoritaire (70 % investis)", 0.3, 0.7, "70 % du gain investi en France (FBCF « autres »)."),
            ("T4b distribution majoritaire (80 %)", 0.8, 0.0, ""),
            ("T4c désendettement ou trésorerie (rien distribué)", 0.0, 0.0, "Seul subsiste l'effet du coût d'usage du capital (estimé)."),
            ("T4d central du modèle (50 % distribués)", 0.5, 0.0, ""),
            ("T4e investissement à l'étranger (rien distribué)", 0.0, 0.0, f"Identique à T4c dans le modèle ; revenus futurs ({RENDEMENT:.0%}) ajoutés au RNB hors modèle.")):
        e = copy.deepcopy(base)
        e.mesure_menages = mm(profits=G)
        if invest:
            e.autres_investissements = invest_plus(ref, invest * G / eur)
        old = H14.DISTRIBUTION_PROFITS["central"]
        H14.DISTRIBUTION_PROFITS["central"] = part
        try:
            run(nom, e, note)
        finally:
            H14.DISTRIBUTION_PROFITS["central"] = old
    notes["_gain_IS_M€"] = G
    # ---- Test 5 : salaires
    e = copy.deepcopy(ref)
    e.choc_salaire = pd.Series({DEBUT: 0.02})
    run("T5a hausse uniforme de 2 %", e, "")
    masse = 0.02 * float(c0.rdb[DEBUT]) * 0.6        # ordre de grandeur du supplément de salaires nets (M€)
    for nom, w in (("T5b même hausse de la masse salariale, ciblée sur les bas salaires (déciles 1-4)", (0.15, 0.25, 0.3, 0.3, 0, 0, 0, 0, 0, 0)),
                   ("T5c même hausse, salaires intermédiaires (déciles 4-7)", (0, 0, 0, 0.25, 0.25, 0.25, 0.25, 0, 0, 0))):
        e = copy.deepcopy(ref)
        e.choc_salaire = pd.Series({DEBUT: 0.02})
        prop_w = [masse * x / sum(H14.PARTS_REVENU) for x in H14.PARTS_REVENU]
        e.mesure_menages = mm(conso=conso_eff([masse * x for x in w]) - conso_eff(prop_w))
        run(nom, e, "Équations de salaires et de prix agrégées : seule la propension à consommer des bénéficiaires diffère ; les allègements "
                    "de cotisations sur les bas salaires (coût public) ne sont pas comptés ici.")
    sc = {"nom": "pi", "horizon": 2035, "hypotheses": {"europe": False, "profils": False},
          "mesures": [next(c for c in CAT.CURSEURS if c["cle"] == "point_indice")["mesure"](2)]}
    _, var_pi, _, _ = X.construire(X.depuis_curseurs(sc), mod)
    run("T5d rémunérations publiques +2 % (point d'indice)", var_pi, "")
    e = copy.deepcopy(ref)
    e.choc_salaire = pd.Series({DEBUT: 0.02})
    alt = S.alternatifs(mod, {"prix_clu": 0.0})
    r_ = copy.deepcopy(ref)
    r_.parametres_alternatifs = e.parametres_alternatifs = alt
    res["T5e hausse de 2 % absorbée par les marges (prix de VA ne réagissant pas au coût salarial)"] = ecarts(mod, mod.simuler(ANS, r_), mod.simuler(ANS, e))
    notes["T5e hausse de 2 % absorbée par les marges (prix de VA ne réagissant pas au coût salarial)"] = "Transmission du coût salarial unitaire aux prix mise à zéro (référence comprise)."
    # ---- Test 6 : énergie
    e = copy.deepcopy(ref)
    for p in M.NON_CONCURRENTS:
        e.prix_import[p] = [x * (1.5 if t >= DEBUT else 1.0) for t, x in zip(e.prix_import.index, e.prix_import[p])]
    run("T6a prix de l'énergie importée +50 %", e, "")
    e = copy.deepcopy(ref)
    e.marges_branche = {"D": {t: float(np.log(1.5)) for t in ANS if t >= DEBUT}}
    run("T6b prix de l'électricité et du gaz produits en France +50 % (marge, branche D)", e,
        "Prix de marché : supplément persistant du prix de VA de la branche D sans hausse des coûts ; le profit supplémentaire "
        "revient aux producteurs (dont l'État actionnaire), non représenté au-delà des impôts sur les sociétés.")
    e = copy.deepcopy(ref)
    for p in M.NON_CONCURRENTS:
        e.prix_import[p] = [x * (1.5 if t >= DEBUT else 1.0) for t, x in zip(e.prix_import.index, e.prix_import[p])]
    e.marges_branche = {"D": {t: float(np.log(1.5)) for t in ANS if t >= DEBUT}}
    run("T6c les deux (marché européen intégré)", e, "")
    # ---- sorties
    (RACINE / "outputs" / "tests_discriminants.json").write_text(json.dumps({"resultats": res, "notes": notes}, ensure_ascii=False, indent=1))
    L = ["# Tests discriminants (version 0.6)", "", "Écarts à la référence « politique inchangée » ; mesures en 2028 ; zone euro désactivée. "
         "Colonnes : 2028 / 2032 / 2035.", ""]
    for nom, d in res.items():
        L += [f"## {nom}", "", notes.get(nom, ""), "", "| " + " | ".join(l for _, l in IND) + " |", "|" + "---|" * len(IND)]
        L.append("| " + " | ".join(" / ".join(f"{d[k][t]:+.0f}" if k in ("emploi",) else f"{d[k][t]:+.2f}" for t in VUES) for k, _ in IND) + " |")
        L.append("")
    L.append(f"Gain d'IS statique (test 4) : {G / 1e3:.1f} Md€ de l'année de base.")
    (RACINE / "outputs" / "tests_discriminants.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("ok")


if __name__ == "__main__":
    main()
