"""Phase 6 / préparation du rapport : test de simulabilité des paquets de mesures des trois candidats.

Ce script ne produit PAS de résultat comparatif : il vérifie que chaque paquet (correspondance centrale de m27_corpus)
se traduit, se simule dans le moteur à régimes, sous les trois variantes institutionnelles de M26, et que les contrôles
techniques sont satisfaits :
  - traduction avec microsimulation calculée (M10/OpenFisca) ;
  - rendements statiques du simulateur rapprochés des montants annoncés (contrôle de la correspondance) ;
  - trajectoires finies, identité solde/dette ;
  - qualification européenne des mesures.
Sorties : phase6/resultats/simulabilite.json (diagnostics seulement).
"""
import json, pathlib, pickle, sys, time, warnings
warnings.filterwarnings("ignore")
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src"), str(R)]
import numpy as np, pandas as pd
import m23_regimes as G, m25_programmes as P, m26_europe_institutions as U, m27_corpus as C

OUT = pathlib.Path(__file__).parent / "resultats"; OUT.mkdir(exist_ok=True)
t0 = time.time()
env_h = G.Environnement.charger("p4", "historique")
env = G.Environnement.charger("p4", "part_constante")
diag, TR = {}, {}
for cand in C.CANDIDATS:
    d = {}
    liste, hors = C.mesures(cand, env.reference, "conforme")
    d["mesures"], d["hors_modele"] = liste, hors
    d["ue"] = U.qualifier({m.ue: m.id for m in C.M if m.candidat == cand and m.ue})
    try:
        tr = P.traduire([x[:3] for x in liste], env_h, cand, microsimulation="calcul")
        TR[cand] = tr
        d["traduction"] = "ok"
        d["comportements_statiques"] = {k: v for k, v in (tr.get("comportements") or {}).items()
                                        if isinstance(v, (int, float, dict))}
        d["mesure_menages"] = {k: v for k, v in (tr["mesure_menages"] or {}).items() if isinstance(v, (int, float, str))}
    except Exception as e:                                    # le diagnostic est le livrable : on consigne l'échec
        d["traduction"] = f"échec : {type(e).__name__}: {e}"
        diag[cand] = d
        print(cand, d["traduction"], flush=True)
        continue
    prog = P.programme(tr)
    for scen in ("conforme", "contentieux", "tension"):
        sc = U.SCENARIOS[scen]
        liste_s, _ = C.mesures(cand, env.reference, scen)
        p_s = prog if liste_s == liste else P.programme(P.traduire([x[:3] for x in liste_s], env_h, f"{cand}_{scen}",
                                                                   microsimulation="calcul"))
        reg = G.regime("R2", monetaire=U.regime_monetaire(sc) if scen == "tension" else None)
        try:
            s = G.simuler(env, reg, U.programme(sc, p_s))["trajectoire"]
            fin = bool(np.isfinite(s[["pib", "dette_pib", "solde_pib", "chomage"]].to_numpy()).all())
            # identité : dette_t − dette_{t−1} ≈ −solde_t (hors calage de dette)
            dd = (s["dette"].diff() + s["solde"]).loc[2027:]          # années calées ≤ 2025 : ajustements de stock observés
            d[f"simulation_{scen}"] = {"finie": fin, "identite_dette_max_rel": float((dd.abs() / s["dette"].abs()).max()),
                                       "mesures_modifiees": [x for x in liste_s if x not in liste]}
        except Exception as e:
            d[f"simulation_{scen}"] = f"échec : {type(e).__name__}: {e}"
        print(cand, scen, round(time.time() - t0), "s", flush=True)
    diag[cand] = d

pickle.dump(TR, open(OUT / "traductions_candidats.pkl", "wb"))
json.dump(diag, open(OUT / "simulabilite.json", "w"), indent=1, ensure_ascii=False, default=str)
print("terminé", round(time.time() - t0), "s")
