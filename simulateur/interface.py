"""Génère l'interface de test (page HTML autonome) à partir des variantes élémentaires précalculées.
Usage : python3 -m simulateur.interface → outputs/interface_test.html
"""
from __future__ import annotations

import datetime
import json
import pathlib
import sys

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from simulateur import catalogue as CAT  # noqa: E402

HYPOTHESES = [
    "Compte de référence conventionnel (pas une prévision) : législation inchangée, demande mondiale +3 %/an, prix mondiaux et "
    "d'importation +1,5 %/an, consommation publique +1 %/an en volume, chômage structurel 7,5 %, taux long 3,2 %, population active "
    "issue du module retraites (législation actuelle).",
    "Production déterminée par la demande à court terme ; retour progressif vers le chômage structurel à moyen terme "
    "(fermeture d'offre ρ = 0,15, hypothèse calibrée).",
    "Rétroactions européennes incluses : règle de taux de la BCE estimée, transmission aux taux longs, prime de risque de 3 points "
    "de base par point de dette, demande des partenaires.",
    "Mesures socio-fiscales : effets statiques (sans réaction de l'offre de travail ni du recours), calculés ménage par ménage "
    "avec OpenFisca-France sur les revenus 2024, puis transmis au modèle macroéconomique.",
    "Incertitude des paramètres : pour une mesure de 1 point de PIB, environ ±0,1 point sur le solde public à 2-3 ans, "
    "beaucoup plus sur l'activité à moyen terme (voir le rapport de validation).",
]


def main():
    d = json.loads((RACINE / "outputs" / "variantes_elementaires.json").read_text(encoding="utf-8"))
    for cle, v in d["variantes"].items():
        for k, x in v.items():
            x["ecarts"] = {i: {a: round(float(val), 4) for a, val in s.items()} for i, s in x["ecarts"].items()}
            x["distribution"] = [{"decile": r["decile"], "niveau_de_vie_moyen": round(r["niveau_de_vie_moyen"]),
                                  "variation_euros_par_uc": round(r["variation_euros_par_uc"], 2)} for r in (x.get("distribution") or [])]
            x["profils"] = [{"profil": p["profil"], "libelle": p["libelle"], "revenu_disponible_approche_actuel": round(p["revenu_disponible_approche_actuel"]),
                             "variation_revenu_disponible": round(p["variation_revenu_disponible"], 1)} for p in (x.get("profils") or [])]
            x["europe"] = [{k2: round(float(v2), 4) for k2, v2 in e.items()} for e in (x.get("europe") or [])]
    d["catalogue"] = {k: {"preuve": m["preuve"], "limites": m["limites"]} for k, m in CAT.MESURES.items()}
    d["hypotheses"] = HYPOTHESES
    n = sum(len(v) for v in d["variantes"].values())
    d["pied"] = (f"Modèle « Présidentielle », données ouvertes (Insee, Eurostat, DGFiP, DREES, FMI, OpenFisca-France). {n} simulations "
                 f"élémentaires du modèle complet, calculées le {datetime.date.today().strftime('%d/%m/%Y')}. Documentation : 07_validation_integrale.md, 08_simulateur.md.")
    gabarit = (RACINE / "simulateur" / "interface_modele.html").read_text(encoding="utf-8")
    page = gabarit.replace("__DONNEES__", json.dumps(d, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
    out = RACINE / "outputs" / "interface_test.html"
    out.write_text(page, encoding="utf-8")
    print(out, len(page) // 1024, "Ko", n, "variantes")


if __name__ == "__main__":
    main()
