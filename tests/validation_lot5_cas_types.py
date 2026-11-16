"""Lot 5 — vérification d'OpenFisca-France sur cas types.

Chaque valeur attendue est recalculée ici indépendamment d'OpenFisca, à partir des barèmes officiels
(loi de finances pour 2026, revalorisations du 1er avril 2026, taux de cotisations 2026). Un écart
supérieur à la tolérance fait échouer le cas.
Sortie : outputs/validation_lot5.md
"""
from __future__ import annotations

import pathlib

from openfisca_core.simulation_builder import SimulationBuilder
from openfisca_france import FranceTaxBenefitSystem

RACINE = pathlib.Path(__file__).resolve().parents[1]
TBS = FranceTaxBenefitSystem()

# --- Barèmes officiels utilisés pour les valeurs attendues (sources dans le rapport) ---------------
BAREME_IR_REV2025 = [(0, 0.0), (11_600, 0.11), (29_579, 0.30), (84_577, 0.41), (181_917, 0.45)]
DECOTE = {"seul": 897, "couple": 1_483, "taux": 0.4525}
PLAFOND_QF_DEMI_PART = 1_807
BMAF_AVRIL_2026 = 478.16
RSA_SEUL_AVRIL_2026 = 651.69
SMIC_HORAIRE_JANV_2026 = 12.02


def impot_bareme(revenu_par_part: float) -> float:
    imp = 0.0
    for (s, t), suiv in zip(BAREME_IR_REV2025, BAREME_IR_REV2025[1:] + [(float("inf"), None)]):
        if revenu_par_part > s:
            imp += (min(revenu_par_part, suiv[0]) - s) * t
    return imp


def ir_attendu(rni: float, parts: float, couple: bool) -> float:
    parts_base = 2 if couple else 1
    brut = impot_bareme(rni / parts) * parts
    sans_enf = impot_bareme(rni / parts_base) * parts_base
    plafonne = max(brut, sans_enf - PLAFOND_QF_DEMI_PART * 2 * (parts - parts_base))
    seuil = DECOTE["couple" if couple else "seul"]
    decote = max(0.0, seuil - DECOTE["taux"] * plafonne)
    net = max(0.0, plafonne - min(decote, plafonne))
    return round(net)


def net_smic_non_cadre(brut: float) -> float:
    """Cotisations salariales 2026 au SMIC, non-cadre, secteur privé, sous le plafond de la Sécurité sociale."""
    taux = 0.0690 + 0.0040 + 0.0315 + 0.0086  # vieillesse plafonnée, déplafonnée, Agirc-Arrco T1, CEG T1
    csg_crds = (0.068 + 0.024 + 0.005) * 0.9825
    return brut * (1 - taux - csg_crds)


# --- Construction des situations -----------------------------------------------------------------
def simuler(individus: dict, couple: bool = False, enfants: tuple = ()):
    parents = ["a", "b"] if couple else ["a"]
    sit = {
        "individus": individus,
        "foyers_fiscaux": {"f": {"declarants": parents, "personnes_a_charge": list(enfants)}},
        "menages": {"m": {"personne_de_reference": ["a"], **({"conjoint": ["b"]} if couple else {}), "enfants": list(enfants)}},
        "familles": {"fa": {"parents": parents, "enfants": list(enfants)}},
    }
    return SimulationBuilder().build_from_entities(TBS, sit)


def adulte(**kw):
    return {"date_naissance": {"ETERNITY": "1985-01-01"}, **kw}


def enfant(annee: int):
    return {"date_naissance": {"ETERNITY": f"{annee}-06-01"}}


CAS = []


def cas(nom, source, attendu, tol):
    def deco(f):
        CAS.append((nom, source, attendu, tol, f))
        return f
    return deco


ABATTEMENT_PLAFOND_REV2025 = 14_555  # abattement de 10 % plafonné (revenus 2025)


def salaire_pour_rni(rni: float) -> float:
    return rni / 0.9 if rni / 0.9 * 0.1 <= ABATTEMENT_PLAFOND_REV2025 else rni + ABATTEMENT_PLAFOND_REV2025


for rni in (15_000, 20_000, 30_000, 250_000):
    @cas(f"IR revenus 2025, célibataire, RNI {rni:_} €".replace("_", " "), "LF 2026 art. 4 (barème, décote, plafond de l'abattement de 10 %)",
         ir_attendu(rni, 1, False), 1.0)
    def _(rni=rni):
        s = simuler({"a": adulte(salaire_imposable={"2025": salaire_pour_rni(rni)})})
        return float(s.calculate("ip_net", "2025")[0])


@cas("IR revenus 2025, couple, 2 enfants, RNI 60 000 €", "LF 2026 (barème, plafonnement QF, décote)", ir_attendu(60_000, 3, True), 1.0)
def _():
    s = simuler({"a": adulte(salaire_imposable={"2025": 30_000 / 0.9}), "b": adulte(salaire_imposable={"2025": 30_000 / 0.9}),
                 "e1": enfant(2015), "e2": enfant(2018)}, couple=True, enfants=("e1", "e2"))
    return float(s.calculate("ip_net", "2025")[0])


@cas("IR revenus 2025, couple, 3 enfants, RNI 150 000 € (plafonnement du QF)", "LF 2026", ir_attendu(150_000, 4, True), 1.0)
def _():
    s = simuler({"a": adulte(salaire_imposable={"2025": 75_000 / 0.9}), "b": adulte(salaire_imposable={"2025": 75_000 / 0.9}),
                 "e1": enfant(2012), "e2": enfant(2015), "e3": enfant(2018)}, couple=True, enfants=("e1", "e2", "e3"))
    return float(s.calculate("ip_net", "2025")[0])


@cas("Salaire net, SMIC temps plein, février 2026", "SMIC 12,02 €/h (janv. 2026) ; taux de cotisations 2026",
     net_smic_non_cadre(SMIC_HORAIRE_JANV_2026 * 151.67), 0.5)
def _():
    s = simuler({"a": adulte(salaire_de_base={"2026-02": SMIC_HORAIRE_JANV_2026 * 151.67}, heures_remunerees_volume={"2026-02": 151.67})})
    return float(s.calculate("salaire_net", "2026-02")[0])


@cas("RSA, personne seule sans ressources ni aide au logement, mai 2026", "Revalorisation du 1er avril 2026",
     RSA_SEUL_AVRIL_2026, 0.5)
def _():
    s = simuler({"a": adulte()})
    return float(s.calculate("rsa", "2026-05")[0])


@cas("RSA, personne seule, salaire net 500 €/mois depuis 3 mois, mai 2026", "Montant forfaitaire − revenus d'activité",
     RSA_SEUL_AVRIL_2026 - 500, 1.0)
def _():
    sal = {f"2026-0{m}": 500 / 0.79 for m in range(1, 6)}
    s = simuler({"a": adulte(salaire_de_base=sal)})
    net = s.calculate("salaire_net", "2026-04")[0]
    return float(s.calculate("rsa", "2026-05")[0]) + (net - 500)  # neutralise l'écart brut/net de la saisie


@cas("Allocations familiales, 2 enfants, revenus modestes, mai 2026 (avant CRDS)", "32 % de la BMAF (478,16 €)",
     0.32 * BMAF_AVRIL_2026, 0.05)
def _():
    s = simuler({"a": adulte(salaire_imposable={"2024": 20_000}), "b": adulte(), "e1": enfant(2015), "e2": enfant(2018)},
                couple=True, enfants=("e1", "e2"))
    return float(s.calculate("af", "2026-05")[0])


@cas("Allocations familiales, 3 enfants, revenus modestes, mai 2026 (avant CRDS)", "73 % de la BMAF",
     0.73 * BMAF_AVRIL_2026, 0.05)
def _():
    s = simuler({"a": adulte(salaire_imposable={"2024": 20_000}), "b": adulte(), "e1": enfant(2012), "e2": enfant(2015), "e3": enfant(2018)},
                couple=True, enfants=("e1", "e2", "e3"))
    return float(s.calculate("af", "2026-05")[0])


def main():
    lignes = ["# Lot 5 — OpenFisca-France sur cas types", "",
              f"OpenFisca-France {__import__('importlib.metadata').metadata.version('OpenFisca-France')} ; "
              f"OpenFisca-Core {__import__('importlib.metadata').metadata.version('OpenFisca-Core')}. "
              "Valeurs attendues recalculées indépendamment (`tests/validation_lot5_cas_types.py`).", "",
              "| Cas | Attendu | OpenFisca | Écart | Tolérance | Résultat | Source de l'attendu |", "|---|---|---|---|---|---|---|"]
    n_ok = 0
    for nom, source, attendu, tol, f in CAS:
        try:
            obtenu = f()
            ok = abs(obtenu - attendu) <= tol
            n_ok += ok
            lignes.append(f"| {nom} | {attendu:.2f} | {obtenu:.2f} | {obtenu - attendu:+.2f} | {tol} | {'conforme' if ok else '**écart**'} | {source} |")
        except Exception as e:  # noqa: BLE001
            lignes.append(f"| {nom} | {attendu:.2f} | erreur | — | {tol} | **erreur** : {str(e)[:80]} | {source} |")
        print(lignes[-1])
    lignes += ["", f"**{n_ok} cas conformes sur {len(CAS)}.**"]
    (RACINE / "outputs").mkdir(exist_ok=True)
    (RACINE / "outputs" / "validation_lot5.md").write_text("\n".join(lignes) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
