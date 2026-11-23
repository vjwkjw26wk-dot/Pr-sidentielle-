"""Phase 3 — gagnants, perdants et acceptabilité sociale des programmes vérifiés (v0.7).

Données : phase3/resultats/verification_v07_<programme>.json (simulation complète : microsimulation par décile et par
groupe de ménages, trajectoires macroéconomiques). Sortie : phase3/resultats/acceptabilite_v07.json.

Règle de classement (explicite, appliquée mécaniquement) :
- perte maximale d'un décile L_d (en % du niveau de vie, microsimulation statique) ;
- perte maximale d'un groupe L_g (âge, catégorie sociale, région, configuration familiale) ;
- R : nombre de leviers qui réduisent des droits sociaux (âge légal relevé, sous-indexation des pensions, baisse des
  allocations chômage, du RSA, des aides au logement, des allocations familiales ou de la prime d'activité) ;
- D3 : nombre de leviers de difficulté 3 (réforme structurelle, forte opposition ou risque juridique).
Élevée : L_d ≤ 0,5 % et L_g ≤ 1 % et R = 0 et D3 = 0.
Faible : L_d > 2 % ou L_g > 3 % ou R ≥ 2 ou D3 ≥ 3.
Intermédiaire : les autres cas.
La règle ne mesure pas l'efficacité économique : un programme peut être efficace et peu acceptable, ou l'inverse.
"""
import json
import pathlib
import sys

R = pathlib.Path(__file__).resolve().parents[1]
RES = R / "phase3" / "resultats"
sys.path[:0] = [str(R / "phase3")]
import optimisation as O  # noqa: E402

DROITS = {("age_legal", 1), ("indexation_pensions", -1), ("assurance_chomage", -1), ("rsa", -1), ("aides_logement", -1),
          ("allocations_familiales", -1), ("prime_activite", -1)}
ACTUEL = {"ir_t1": 11, "ir_t4": 45, "taux_is": 25.8, "temps_travail": 35, "age_legal": 64}


def sens(lev, val):
    d = val - ACTUEL.get(lev, 0.0)
    return 1 if d > 0 else -1 if d < 0 else 0


def analyser(nom, v):
    cur = v["curseurs"]
    c = v["complet"]
    dist = c.get("distribution") or []
    grp = c.get("groupes") or {}
    deciles = {d["decile"]: {"euros_par_uc": d["variation_euros_par_uc"], "pct": d["variation_pct"], "gagnants": d["part_gagnants"],
                             "perdants": d["part_perdants"], "masse_M€": d["masse_M€"]} for d in dist}
    Ld = max([0.0] + [-x["pct"] for x in deciles.values()])
    pertes_groupes = []
    for dim, gs in grp.items():
        for g, x in gs.items():
            if x["poids"] < 0.005:      # groupes trop petits dans l'échantillon (moins de 0,5 % des ménages)
                continue
            pertes_groupes.append((dim, g, x["variation_pct"], x["variation_euros_par_uc"], x["part_perdants"]))
    Lg = max([0.0] + [-p[2] for p in pertes_groupes])
    droits = [lev for lev, val in cur.items() if (lev, sens(lev, val)) in DROITS]
    d3 = [lev for lev, val in cur.items() if lev in O.LEVIERS and O.LEVIERS[lev][6] == 3 and sens(lev, val) != 0]
    if Ld <= 0.5 and Lg <= 1.0 and not droits and not d3:
        niveau = "élevée"
    elif Ld > 2.0 or Lg > 3.0 or len(droits) >= 2 or len(d3) >= 3:
        niveau = "faible"
    else:
        niveau = "intermédiaire"
    # coût d'une compensation des pertes des trois premiers déciles (masse négative, M€ par an)
    comp = -sum(min(0.0, x["masse_M€"]) for d, x in deciles.items() if d <= 3)
    perdants = sorted([p for p in pertes_groupes if p[2] < -0.1], key=lambda p: p[2])[:8]
    gagnants = sorted([p for p in pertes_groupes if p[2] > 0.1], key=lambda p: -p[2])[:8]
    return {"curseurs": cur, "niveau": niveau, "perte_max_decile_pct": Ld, "perte_max_groupe_pct": Lg, "droits_reduits": droits,
            "leviers_difficulte_3": d3, "deciles": deciles, "groupes": grp,
            "principaux_perdants": [{"dimension": a, "groupe": b, "pct": c_, "euros_par_uc": d_, "part_perdants": e} for a, b, c_, d_, e in perdants],
            "principaux_gagnants": [{"dimension": a, "groupe": b, "pct": c_, "euros_par_uc": d_, "part_perdants": e} for a, b, c_, d_, e in gagnants],
            "cout_compensation_D1_D3_M€": comp, "inegalites": c.get("inegalites")}


def main():
    out = {}
    for f in sorted(RES.glob("verification_v07_*.json")):
        nom = f.stem.replace("verification_v07_", "")
        out[nom] = analyser(nom, json.loads(f.read_text()))
        print(nom, out[nom]["niveau"], round(out[nom]["perte_max_decile_pct"], 2), round(out[nom]["perte_max_groupe_pct"], 2),
              out[nom]["droits_reduits"], out[nom]["leviers_difficulte_3"])
    (RES / "acceptabilite_v07.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main()
