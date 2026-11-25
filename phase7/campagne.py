"""Phase 7 (finalisation) : campagne de simulations des programmes présidentiels, par candidat.

Usage : python3 phase7/campagne.py <candidat> [--rapide]
Candidats : melenchon, le_pen, philippe (m27_corpus.CANDIDATS).

Pour le candidat, avec l'environnement de référence (P4, convention « part constante ») et le régime principal
(R2 figé, taux exogènes, jeu central), sauf mention contraire :
  A    lecture par mesures documentées (variante européenne « conforme ») ;
  A_i  chaque mesure isolée ;
  A_r  dix régimes de robustesse ;
  A_e  environnements alternatifs (σ 0,3 / 0,6, équation de prix v0.9) ;
  A_u  variantes européennes sous régime BCE + prime (conforme, contentieux, tension) ;
  A_p  mise en œuvre partielle (50 %) ; A_d mise en œuvre retardée (+2 ans) ;
  B    lecture par objectifs budgétaires (A + effort pour atteindre la trajectoire annoncée).
Sorties : phase7/resultats/<candidat>.pkl (écarts complets) et <candidat>_synthese.csv (horizons 5, 10, 20 ans).
Aucun résultat n'est interprété ici.
"""
import copy, json, pathlib, pickle, sys, time, warnings
warnings.filterwarnings("ignore")
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src"), str(R)]
import numpy as np, pandas as pd
import m23_regimes as G, m25_programmes as P, m26_europe_institutions as U, m27_corpus as C

OUT = pathlib.Path(__file__).parent / "resultats"; OUT.mkdir(exist_ok=True)
HORIZONS = {5: 2031, 10: 2036, 20: 2046}
cand = sys.argv[1]
rapide = "--rapide" in sys.argv
t0 = time.time()
log = lambda *a: print(f"[{cand} {time.time() - t0:6.0f} s]", *a, flush=True)  # noqa: E731


def indicateurs(e) -> pd.DataFrame:
    a, b = e["variante"]["trajectoire"], e["reference"]["trajectoire"]
    lg = lambda x, y: 100 * np.log(x / y)  # noqa: E731
    d = pd.DataFrame({
        "PIB (%)": lg(a.pib, b.pib),
        "emploi (milliers)": a.emploi - b.emploi,
        "chômage (pt)": a.chomage - b.chomage,
        "salaire réel (%)": lg(a.salaire / a.pc, b.salaire / b.pc),
        "prix (%)": lg(a.pc, b.pc),
        "pouvoir d'achat (%)": lg(a.rdb / a.pc, b.rdb / b.pc),
        "consommation (%)": lg(a.c, b.c),
        "taux d'épargne (pt)": a.taux_epargne - b.taux_epargne,
        "investissement (%)": lg(a.fbcf, b.fbcf),
        "taux de marge (pt)": a.taux_marge - b.taux_marge,
        "exportations (%)": lg(a.x, b.x),
        "importations (%)": lg(a.m, b.m),
        "solde (pt PIB)": a.solde_pib - b.solde_pib,
        "dette (pt PIB)": a.dette_pib - b.dette_pib,
        "intérêts (pt PIB)": 100 * (a.interets / a.pib_nominal - b.interets / b.pib_nominal),
        "recettes (pt PIB)": 100 * (a.recettes / a.pib_nominal - b.recettes / b.pib_nominal),
        "dépenses (pt PIB)": 100 * (a.depenses / a.pib_nominal - b.depenses / b.pib_nominal),
        "effort règle (pt PIB)": a.impose_effort - b.impose_effort,
        "effort objectif (pt PIB)": a.impose_effort_objectif - b.impose_effort_objectif,
        "niveau solde (% PIB)": a.solde_pib, "niveau dette (% PIB)": a.dette_pib,
    })
    return d


def evaluer(env, reg, prog, **kw):
    return indicateurs(G.evaluer(env, reg, prog, **kw))


def modifier(liste, facteur=1.0, retard=0):
    """Mise en œuvre partielle (facteur appliqué à l'écart à la législation actuelle) ou retardée."""
    out = []
    for cle, v, d, i in liste:
        if isinstance(v, dict):
            v = dict(v)
            if facteur != 1.0:
                v["age"] = 64 + (float(v["age"]) - 64) * facteur
                if isinstance(v.get("duree"), (int, float)):
                    v["duree"] = 172 + (float(v["duree"]) - 172) * facteur
                if v.get("groupe_part"):
                    v["groupe_part"] = float(v["groupe_part"]) * facteur
        elif cle in C.ABSOLUS:
            v = C.NEUTRES[cle] + (v - C.NEUTRES[cle]) * facteur
        else:
            v = v * facteur
        out.append((cle, v, d + retard, i))
    return out


def traduire(liste, nom):
    return P.traduire([x[:3] for x in liste], env_h, nom, microsimulation="calcul")


env_h = G.Environnement.charger("p4", "historique")
env = G.Environnement.charger("p4", "part_constante")
REG = G.regime("R2")
res, trads, meta = {}, {}, {}

liste, hors = C.mesures(cand, env.reference, "conforme")
meta["mesures"] = [list(x) for x in liste]
meta["hors_modele"] = hors
trads["A"] = traduire(liste, f"{cand}_A")
pA = P.programme(trads["A"])
res["A"] = evaluer(env, REG, pA)
log("A")

# --- B : objectifs budgétaires
ob = C.OBJECTIFS[cand]
if ob["cibles"] == "stabilisation:2032":
    a = G.simuler(env, REG, pA, effort_impose=G.simuler(env, REG)["effort"])["trajectoire"]
    gnom = float(np.mean([np.log(a.pib_nominal[t] / a.pib_nominal[t - 1]) for t in range(2028, 2033)]))
    cible_2032 = -float(a.dette_pib[2031]) * gnom / (1 + gnom)
    cibles = {2027: float(a.solde_pib[2027]), 2032: cible_2032}
    meta["objectif_calcule"] = {"croissance_nominale": gnom, "solde_stabilisant_2032": cible_2032}
else:
    a = G.simuler(env, REG, pA, effort_impose=G.simuler(env, REG)["effort"])["trajectoire"]
    cibles = {2027: float(a.solde_pib[2027]), **ob["cibles"]}
obj = G.ObjectifBudgetaire(cibles=cibles, parts=ob["parts"], debut=2028, nom=f"{cand}_B")
meta["objectif"] = {"cibles": cibles, "parts": ob["parts"], "texte": ob["texte"]}
eB = G.evaluer(env, REG, pA, objectif=obj)
res["B"] = indicateurs(eB)
meta["B_ecart_cible"] = eB["variante"]["ecart_cible"]
if cand == "philippe":
    obj2 = copy.deepcopy(obj); obj2.cibles = {2027: cibles[2027], 2032: -2.0}
    res["B_variante_2pc"] = evaluer(env, REG, pA, objectif=obj2)
log("B")
# --- hypothèse de taux longs : OAT ramenée à sa moyenne des douze derniers mois (3,82 %) au lieu du dernier mois (4,89 %)
voat = G.variante_oat()
res["A:oat_382"] = evaluer(env, REG, pA, variante_env=voat)
res["B:oat_382"] = evaluer(env, REG, pA, objectif=obj, variante_env=voat)
log("OAT")

if not rapide:
    # --- mesures isolées
    for mid in sorted({x[3] for x in liste}):
        sous = [x for x in liste if x[3] == mid]
        try:
            trads[mid] = traduire(sous, f"{cand}_{mid}")
            res[f"mesure:{mid}"] = evaluer(env, REG, P.programme(trads[mid]))
        except Exception as ex_:                   # consigné, jamais remplacé par une valeur
            meta.setdefault("echecs", {})[mid] = f"{type(ex_).__name__}: {ex_}"
        log("mesure", mid)
    # --- régimes
    for nom, k in G.REGIMES_ROBUSTESSE.items():
        kk = dict(k); code = kk.pop("code")
        res[f"regime:{nom}"] = evaluer(env, G.regime(code, **kk), pA)
    log("régimes")
    # --- environnements (programme transféré par écarts)
    for conf in ("p4_sigma03", "p4_sigma06", "p4_prix_v09"):
        e2 = G.Environnement.charger(conf, "part_constante")
        res[f"environnement:{conf}"] = evaluer(e2, REG, pA)
    env.activer()
    log("environnements")
    # --- variantes européennes, même régime monétaire (BCE + prime) pour les trois
    for scen in ("conforme", "contentieux", "tension"):
        sc = U.SCENARIOS[scen]
        ls, _ = C.mesures(cand, env.reference, scen)
        ps = pA if ls == liste else P.programme(traduire(ls, f"{cand}_{scen}"))
        reg = G.regime("R2", monetaire=U.regime_monetaire(sc))
        # la référence ne subit pas le choc de prime : il est une réponse au programme (correction du 25 novembre 2026 ;
        # auparavant le choc figurait aussi dans la référence et s'annulait dans l'écart)
        sc0 = copy.deepcopy(sc); sc0.choc_ecart_pb = {}
        ref0 = G.simuler(env, G.regime("R2", monetaire=U.regime_monetaire(sc0)))
        res[f"europe:{scen}"] = indicateurs(G.evaluer(env, reg, U.programme(sc, ps), ref=ref0))
    log("europe")
    # --- additionnalité de l'investissement hors APU (L33, LFI) : 100 % (lecture A), 50 %, 25 %, 0 % [H]
    if any(x[0] == "investissement_hors_apu" for x in liste):
        for part in (0.5, 0.25, 0.0):
            ls = [(c_, v * part, d, i) if c_ == "investissement_hors_apu" else (c_, v, d, i) for c_, v, d, i in liste]
            ls = [x for x in ls if not (x[0] == "investissement_hors_apu" and x[1] == 0.0)]
            res[f"additionnalite:{int(part * 100)}"] = evaluer(env, REG, P.programme(traduire(ls, f"{cand}_add{int(part * 100)}")))
        log("additionnalité")
    # --- mise en œuvre partielle et retardée
    for nom, f, r_ in (("partielle_50", 0.5, 0), ("retard_2ans", 1.0, 2)):
        res[f"mise_en_oeuvre:{nom}"] = evaluer(env, REG, P.programme(traduire(modifier(liste, f, r_), f"{cand}_{nom}")))
    log("mise en œuvre")

pickle.dump({"resultats": res, "meta": meta,
             "traductions": {k: {kk: vv for kk, vv in v.items() if kk in ("distribution", "inegalites", "groupes",
                                                                          "statique", "comportements", "mesure_menages",
                                                                          "regle_age", "curseurs")}
                             for k, v in trads.items()}},
            open(OUT / f"{cand}.pkl", "wb"))
syn = pd.concat({k: v.loc[list(HORIZONS.values())].rename(index={y: h for h, y in HORIZONS.items()})
                 for k, v in res.items()}, names=["simulation", "horizon"])
syn.to_csv(OUT / f"{cand}_synthese.csv")
json.dump(meta, open(OUT / f"{cand}_meta.json", "w"), indent=1, ensure_ascii=False, default=str)
log("terminé")
