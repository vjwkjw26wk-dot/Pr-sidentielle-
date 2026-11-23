"""Effets de seuil : revenu disponible de ménages types en fonction du salaire (OpenFisca-France, législation 2024).

Calcule, pour trois configurations familiales et des salaires de 0 à 2,5 SMIC, le revenu disponible approché (salaire
net + RSA + prime d'activité + allocations familiales + aides au logement − impôt sur le revenu), et le gain net d'une
hausse de salaire de 2 % (taux marginal effectif de prélèvement). Sortie : rapport/resultats/seuils_salaires.json
"""
import json, pathlib, sys
RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
import m4_openfisca as mo  # noqa: E402
from openfisca_core.simulation_builder import SimulationBuilder  # noqa: E402

SMIC = 17_900
TYPES = {"celibataire": ("Personne seule, locataire", False, 0, False),
         "parent_isole_1": ("Parent isolé, un enfant, locataire", False, 1, False),
         "couple_1_salaire_2_enfants": ("Couple, un seul salaire, deux enfants, locataire", True, 2, True)}


def calc(T, salaire, couple, n_enf):
    ind = {"a0": {"date_naissance": {"ETERNITY": "1989-01-01"}}}
    if salaire > 0:
        ind["a0"]["salaire_imposable"] = {"2024": salaire}
        ind["a0"]["salaire_net"] = {f"2024-{m:02d}": salaire / 12 * 0.98 for m in range(1, 13)}
        ind["a0"]["salaire_net"].update({"2023": salaire * 0.98, "2022": salaire * 0.98})
    if couple:
        ind["a1"] = {"date_naissance": {"ETERNITY": "1990-01-01"}}
    for j in range(n_enf):
        ind[f"e{j}"] = {"date_naissance": {"ETERNITY": f"{2018 - 2 * j}-01-01"}}
    par = [k for k in ind if k.startswith("a")]
    enf = [k for k in ind if k.startswith("e")]
    sit = {"individus": ind, "foyers_fiscaux": {"f": {"declarants": par, "personnes_a_charge": enf}},
           "familles": {"fa": {"parents": par, "enfants": enf}},
           "menages": {"m": {"personne_de_reference": [par[0]], **({"conjoint": [par[1]]} if couple else {}), "enfants": enf,
                             "statut_occupation_logement": {"2024-10": "locataire_vide"}, "loyer": {"2024-10": 550 + 100 * n_enf},
                             "zone_apl": {"2024-10": "zone_2"}}}}
    if couple:
        for p in par:
            ind[p]["statut_marital"] = {"2024": "marie"}
    sim = SimulationBuilder().build_from_entities(T, sit)
    out = {"ir": float(sim.calculate("ip_net", "2024")[0])}
    for v in ("rsa", "ppa", "af", "aide_logement"):
        out[v] = float(sim.calculate(v, "2024-10")[0]) * 12
    out["salaire_net"] = salaire * 0.98
    out["revenu_disponible"] = out["salaire_net"] - out["ir"] + sum(out[v] for v in ("rsa", "ppa", "af", "aide_logement"))
    return out


def main():
    T = mo.tbs()
    res = {}
    for k, (lib, couple, n, _) in TYPES.items():
        pts = []
        for i in range(0, 51):
            s = SMIC * i * 0.05
            a, b = calc(T, s, couple, n), calc(T, s * 1.02, couple, n)
            gain = b["revenu_disponible"] - a["revenu_disponible"]
            hausse = (b["salaire_net"] - a["salaire_net"])
            pts.append({"smic": i * 0.05, "salaire": s, **a, "gain_hausse_2pc": gain,
                        "taux_marginal_effectif": (1 - gain / hausse) * 100 if hausse > 0 else None})
        res[k] = {"libelle": lib, "points": pts}
        print(k, "ok", flush=True)
    d = RACINE / "rapport" / "resultats"
    d.mkdir(parents=True, exist_ok=True)
    (d / "seuils_salaires.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
