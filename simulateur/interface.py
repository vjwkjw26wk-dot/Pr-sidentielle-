"""Génère l'interface de test (page HTML autonome) à partir des variantes élémentaires précalculées (version 0.3).
Usage : python3 -m simulateur.interface → outputs/interface_test.html
"""
from __future__ import annotations

import datetime
import json
import pathlib
import sys

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
sys.path.insert(0, str(RACINE / "src"))
from simulateur import catalogue as CAT  # noqa: E402

HYPOTHESES = [
    "Ce n'est pas une prévision : c'est le point de comparaison commun à toutes les mesures, à politique inchangée (aucune mesure "
    "nouvelle après la loi de finances 2026).",
    "2023-2025 : le modèle reproduit les comptes nationaux observés (Insee, comptes annuels publiés en mai 2026) grâce à des termes de "
    "calage ; les écarts à l'équilibre estimé constatés en 2025 sont supposés durables.",
    "2026-2031 : croissance, chômage et inflation de la France selon le FMI (Perspectives de l'économie mondiale, octobre 2026) ; "
    "croissance et inflation de la zone euro selon le FMI ; demande adressée à la France = 1,5 × croissance de la zone euro.",
    "Au-delà de 2031 : productivité par tête +0,7 % par an et chômage convergeant vers 7 % (hypothèses du scénario de référence du "
    "Conseil d'orientation des retraites, juin 2026) ; inflation de 2031.",
    "Démographie : projection centrale de l'Insee ; population active et masse des pensions de droit direct calculées par génération "
    "(module M9, législation actuelle : âge légal suspendu à 62 ans et 9 mois pour les générations 1963-1964, puis +3 mois par "
    "génération jusqu'à 64 ans ; pensions revalorisées sur les prix).",
    "Taux de l'OAT à 10 ans maintenu à son dernier niveau mensuel (4,89 % en octobre 2026, Eurostat) ; le taux apparent de la dette "
    "le rejoint au rythme du renouvellement de la dette (1/8 par an).",
    "Dépenses publiques de fonctionnement en volume et prestations hors pensions à leur rythme moyen 2011-2019 (+1,3 % et +1,4 % par "
    "an) ; recettes à législation constante, élasticités apparentes.",
    "Les mesures entrent en vigueur au 1er janvier 2028 ; les effets des mesures fiscales et sociales sur les ménages sont calculés "
    "ménage par ménage (OpenFisca-France, revenus 2024) puis transmis au modèle macroéconomique.",
    "Les projections du FMI pour le solde et la dette (−3,9 % et 124 % du PIB en 2031) supposent des mesures de redressement non "
    "encore votées : l'écart avec la trajectoire affichée mesure l'effort que ces mesures représenteraient.",
]


def _arrondir(x, n=4):
    if isinstance(x, float):
        return round(x, n)
    if isinstance(x, dict):
        return {k: _arrondir(v, n) for k, v in x.items()}
    if isinstance(x, list):
        return [_arrondir(v, n) for v in x]
    return x


def main():
    d = json.loads((RACINE / "outputs" / "variantes_elementaires.json").read_text(encoding="utf-8"))
    for cle, v in d["variantes"].items():
        for k, x in v.items():
            x["distribution"] = [{"decile": r["decile"], "variation_euros_par_uc": round(r["variation_euros_par_uc"], 1),
                                  "part_perdants": round(r.get("part_perdants", 0), 3), "part_gagnants": round(r.get("part_gagnants", 0), 3)}
                                 for r in (x.get("distribution") or [])]
            x["profils"] = [{"profil": p["profil"], "libelle": p["libelle"], "revenu_disponible_approche_actuel": round(p["revenu_disponible_approche_actuel"]),
                             "variation_revenu_disponible": round(p["variation_revenu_disponible"], 1)} for p in (x.get("profils") or [])]
            x["europe"] = [e for e in (x.get("europe") or []) if e.get("annee") == 2030]
            st = x.get("statique") or {}
            x["statique"] = {k2: st[k2] for k2 in ("impot_revenu_M€", "prestations_versees_M€", "pensions_M€") if k2 in st}
    d = _arrondir(d)
    d["curseurs"] = [{k: c[k] for k in ("cle", "groupe", "libelle", "unite", "min", "max", "pas", "actuel", "points", "type")} for c in CAT.CURSEURS]
    d["catalogue"] = {k: {"preuve": m["preuve"], "limites": m["limites"], "libelle": m["libelle"]} for k, m in CAT.MESURES.items()}
    import m8_reference as RF
    F = RF.fmi()
    d["fin_observe"] = RF.FIN_OBSERVE
    import m7_series as S
    du = F["LUR"]["FRA"][RF.FIN_OBSERVE] - float(S.macro().chomage[RF.FIN_OBSERVE])
    d["fmi"] = {k: {str(a): v for a, v in F[k]["FRA"].items() if 2023 <= a <= 2032} for k in ("NGDP_RPCH", "PCPIPCH", "GGXCNL_NGDP", "GGXWDG_NGDP")}
    d["fmi"]["LUR_ajuste"] = {str(a): round(v - du, 2) for a, v in F["LUR"]["FRA"].items() if 2023 <= a <= 2032}
    d["hypotheses"] = HYPOTHESES
    n = sum(len(v) for v in d["variantes"].values())
    from simulateur import executer as X
    emp = X.empreintes()
    d["version"] = {k: emp[k] for k in ("version", "code", "donnees")}
    courts = {"inchangee": "Politique inchangée (OAT 4,9 %)", "oat_bas": "Politique inchangée, OAT 3,9 %",
              "oat_haut": "Politique inchangée, OAT 5,9 %", "redressement": "Redressement d'ampleur FMI"}
    for k, v in (d.get("references") or {}).items():
        v["court"] = courts.get(k, k)
        v["niveaux"] = {i: {int(a): x for a, x in s_.items()} for i, s_ in v["niveaux"].items()}
    from simulateur import programmes as PG
    d["programmes"] = {"date": PG.DATE, "regles": PG.REGLES, "liste": PG.PROGRAMMES,
                       "non_traduits": [list(x) for x in PG.NON_TRADUITS]}
    f_inc = RACINE / "outputs" / "incertitude_variantes.json"
    if f_inc.exists():
        d["incertitude"] = json.loads(f_inc.read_text()).get("mediane", {})
    d["pied"] = (f"Modèle « Présidentielle » version {emp['version']} (code {emp['code']}, données {emp['donnees']}), données ouvertes (Insee, Eurostat, DGFiP, DREES, FMI, COR, OpenFisca-France). {n} simulations "
                 f"élémentaires du modèle complet, calculées le {datetime.date.today().strftime('%d/%m/%Y')}. Documentation : 07_validation_integrale.md, "
                 f"08_simulateur.md, M8_reference.md, M13_comportements.md.")
    gabarit = (RACINE / "simulateur" / "interface_modele.html").read_text(encoding="utf-8")
    page = gabarit.replace("__DONNEES__", json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
    out = RACINE / "outputs" / "interface_test.html"
    out.write_text(page, encoding="utf-8")
    print(out, len(page) // 1024, "Ko", n, "variantes")


if __name__ == "__main__":
    main()
