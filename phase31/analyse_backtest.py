"""Phase 3.1 — analyse du backtest : tableaux d'erreurs, comparaison aux références naïves, périodes de divergence,
décomposition de l'erreur sur les dépenses publiques (test par bloc), et confrontation des effets simulés des
politiques à des évaluations empiriques.
Sorties : phase31/resultats/analyse_backtest.json"""
import json
import pathlib
import sys

import numpy as np

R = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R / "src"), str(R), str(R / "phase31")]
OUT = R / "phase31" / "resultats"


def main():
    b = json.loads((OUT / "backtest.json").read_text())
    tab = {}
    for k, v in b.items():
        if "erreur" in v:
            continue
        var, per = k.split("|")
        tab.setdefault(per, {})[var] = {x: {"rmse": d.get("rmse"), "biais": d.get("biais"), "rmse_naif": d.get("rmse_naif"),
                                            "fin": (list(d["erreur_niveau_pct"].values())[-1] if "erreur_niveau_pct" in d else list(d["erreur"].values())[-1])}
                                       for x, d in v.items() if isinstance(d, dict) and "rmse" in d}
    # erreurs par horizon (origine 2010, variante retenue)
    hor = {}
    v = b["v08|2010-2019"]
    for x in ("pib", "emploi", "pc", "c", "fbcf", "x", "m", "productivite", "salaire_reel"):
        hor[x] = {h: v[x]["erreur_niveau_pct"].get(str(2010 + h)) for h in (1, 3, 5, 9)}
    for x in ("chomage", "solde_pib", "dette_pib", "recettes_pib", "depenses_pib"):
        hor[x] = {h: v[x]["erreur"].get(str(2010 + h)) for h in (1, 3, 5, 9)}
    # test par bloc des dépenses publiques : décomposition à partir d'une simulation de la variante retenue
    import backtest as BT
    mod, ex, ans = BT.construire(2010, 2019, 0.2, 0.0, 0.75, "production", True, 0.0, False, False)
    r = mod.simuler(ans, ex)
    apu, m = mod.apu, mod.macro
    bloc = {}
    for t in (2012, 2015, 2019):
        pn, po = r.pib_nominal[t], m.pib_cp[t]
        bloc[t] = {"erreur_pib_nominal_pct": 100 * (pn / po - 1),
                   "interets_sim": 100 * r.interets[t] / pn, "interets_obs": 100 * apu.d41pay[t] / po,
                   "prestations_sim": 100 * r.prestations[t] / pn, "prestations_obs": 100 * apu.d62pay[t] / po,
                   "depenses_sim": 100 * r.depenses[t] / pn, "depenses_obs": 100 * apu.te[t] / po,
                   "recettes_sim": 100 * r.recettes[t] / pn, "recettes_obs": 100 * apu.tr[t] / po,
                   "taux_apparent_sim": float(r.taux_apparent[t]), "taux_apparent_obs": 100 * apu.d41pay[t] / apu.dette[t - 1]}
    out = {"tableau": tab, "horizons_2010": hor, "bloc_finances_publiques": bloc}
    (OUT / "analyse_backtest.json").write_text(json.dumps(out, indent=1, default=float))
    for per in tab:
        print(per)
        for var in ("demande", "v06", "v07", "v08", "v08_prix_fiscal", "v08_sans_politiques"):
            if var in tab[per]:
                d = tab[per][var]
                print("  ", var, {x: round(d[x]["rmse"], 2) for x in ("pib", "emploi", "chomage", "pc", "dette_pib", "recettes_pib", "depenses_pib")},
                      "naïf PIB", round(d["pib"]["rmse_naif"], 2))
    print(json.dumps(bloc, indent=0, default=lambda x: round(float(x), 2))[:1500])


if __name__ == "__main__":
    main()
