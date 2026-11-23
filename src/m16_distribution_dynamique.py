"""M16 — Distribution dynamique des effets (version 0.8).

Passe de l'incidence fiscale immédiate (microsimulation M10, revenus de l'année de base) au revenu disponible réel de
chaque ménage après propagation des effets macroéconomiques du modèle M8, à plusieurs horizons.

Méthode hybride (document 19, § 3) : les ≈ 41 000 ménages pondérés de la microsimulation conservent leurs
caractéristiques (revenus, statuts, composition, âge, catégorie sociale, statut d'occupation, région) ; chaque canal
macroéconomique, mesuré en écart du scénario à la référence, est appliqué au revenu de chaque ménage selon son
exposition à ce canal. Les effets d'emploi sont calculés en espérance (probabilité de retour à l'emploi ou de perte
d'emploi par personne), sans tirage aléatoire.

Canaux (sans double compte : chaque composante du revenu n'est modifiée que par un canal) :
1. direct : prélèvements et prestations (M10), y compris le coût des taxes sur la consommation (TVA, carbone) imputé
   selon les profils de consommation ;
2. salaires : variation du salaire brut par tête (coût salarial du modèle macroéconomique, net de la variation des
   cotisations employeurs), appliquée aux salaires du ménage, nette d'un taux moyen de prélèvements (12 %) ;
3. emploi : variation du nombre de chômeurs (retours à l'emploi des chômeurs, ou pertes d'emploi des salariés selon un
   risque relatif par âge et catégorie) et de la population active (entrées d'inactifs) ; gain = salaire d'embauche
   (75 % du salaire moyen) net, moins l'allocation chômage perdue en espérance ;
4. revenus du patrimoine et des indépendants : variation des revenus de la propriété et de l'excédent brut des ménages
   du modèle macroéconomique (dividendes, intérêts, revenus mixtes), répartie au prorata d'une approximation des
   revenus non salariaux et non pensions (revenu fiscal de référence − salaires − pensions) ;
5. droits de succession : variation de rendement répartie selon la même assiette, pondérée par l'âge (héritiers
   probables : personne de référence de 45 à 74 ans), en espérance annuelle ;
6. prix : déflateur du ménage = prix à la consommation du modèle, hors composante fiscale (déjà comptée en 1), plus un
   terme d'énergie selon la part de l'énergie dans la consommation du décile ;
7. indexation : pensions et prestations suivent les prix avec un an de retard (perte ou gain réel transitoire) ;
8. résiduel : écart entre la somme des canaux et la variation macroéconomique du revenu disponible brut (contrôle de
   cohérence) ; publié, non réparti.
L'IS, les impôts de production et les cotisations employeurs atteignent les ménages par les canaux 2, 4 et 6 (incidence
modélisée dans M8 : cible de long terme du coût salarial, profits, prix).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

TAUX_NET = 0.88                 # part nette de prélèvements d'un supplément de salaire imposable (IR, ordre de grandeur) [H]
SALAIRE_EMBAUCHE = 0.75         # salaire d'embauche relatif au salaire moyen des personnes en emploi [L : Insee, salaires
#                                 à l'embauche et de début de carrière]
ALLOCATION_PERDUE = 5_200.0     # allocation chômage perdue en espérance par retour à l'emploi (€/an, base 2024 :
#                                 indemnisation moyenne ≈ 13 000 €/an × part indemnisée ≈ 40 %) [L/H]
GAIN_INACTIF = 0.6              # gain relatif d'une entrée d'inactif (temps partiel, salaires plus bas) [H]
RISQUE_AGE = {"<30": 2.0, "30-49": 1.0, "50+": 0.8}   # risque relatif de perte d'emploi (taux de chômage par âge) [L : Insee]
RISQUE_GS = {"1": 0.6, "2": 0.8, "3": 0.5, "4": 0.8, "5": 1.3, "6": 1.6}   # par catégorie sociale [L : Insee]
PART_ENERGIE_IMPORT = 0.4       # part du prix à la consommation de l'énergie suivant les prix d'importation [H]
HORIZONS = (2027, 2030, 2035, 2040, 2047)


def _deciles(m):
    o = m.nv_base.sort_values().index
    cum = m.poids.reindex(o).cumsum() / m.poids.sum()
    return pd.Series(np.minimum((cum * 10).astype(int) + 1, 10), index=o).reindex(m.index)


def _q(x, w, q):
    o = np.argsort(x)
    x, w = np.asarray(x)[o], np.asarray(w)[o]
    c = np.cumsum(w) / w.sum()
    return float(x[np.searchsorted(c, q)])


def _gini(x, w):
    o = np.argsort(x)
    x, w = np.asarray(x)[o], np.asarray(w)[o]
    cw = np.cumsum(w)
    cxw = np.cumsum(x * w)
    return float(1 - 2 * np.sum(w * (cxw - x * w / 2)) / (cw[-1] * cxw[-1]))


def calculer(m: pd.DataFrame, ref: pd.DataFrame, scn: pd.DataFrame, prix_fiscal: pd.Series | None = None,
             cot_employeurs: pd.Series | None = None, energie: pd.Series | None = None, successions_M: float = 0.0,
             debut: int = 2028, energie_decile: list | None = None, horizons=HORIZONS, seniors: dict | None = None,
             transferts: list | None = None) -> dict:
    """m : ménages de la microsimulation (m10_couplage.distribution(...).attrs["menages"]) ;
    ref, scn : trajectoires macroéconomiques (DataFrame indexés par année) de la référence et du scénario ;
    prix_fiscal : composante fiscale (log) du prix à la consommation du scénario (niveaux["prix_conso"]) ;
    cot_employeurs : variation (log) du coût salarial due aux cotisations employeurs (par année) ;
    energie : écart (log) du prix d'importation de l'énergie, scénario / référence ;
    successions_M : variation annuelle du rendement des droits de succession (M€, année de base) ;
    seniors : réforme de l'âge légal (M9) — {"actifs": actifs seniors supplémentaires (milliers), "emploi": part
    maintenue en emploi (milliers), "pensions_M": variation de la masse des pensions (M€ courants)}. Les entrées et
    sorties d'activité des seniors sont attribuées aux ménages dont la personne de référence a 58 à 67 ans, en
    pseudo-cohorte : salaire maintenu pour ceux qui ont des actifs occupés, allocation chômage pour les entrées au
    chômage (uniforme), pension non versée au prorata des pensions perçues ; et non aux inactifs d'âge actif ni aux
    salariés exposés au risque de chômage (correction phase 3.1 : sans cela, le relèvement de l'âge légal apparaissait comme un
    gain pour le premier décile) ;
    transferts : mesures sans équivalent dans la microsimulation, réparties selon une clé — liste de (montant en M€
    de 2025 indexés sur le PIB nominal, clé, début) ; clés : "chomeurs" (allocations chômage, au prorata du nombre de
    chômeurs), "prestations" (transferts aux ménages, au prorata des prestations), "salaires" (point d'indice, au
    prorata des salaires, faute d'identifier les agents publics) ; montant converti en part du revenu disponible
    macroéconomique de 2025 (correction phase 3.1)."""
    m = m.copy()
    m["decile"] = _deciles(m)
    rev0 = (m.nv_base * m.uc).clip(lower=0)                    # revenu disponible du ménage, année de base (€)
    cap = (m.rfr - m.salaires - m.pensions).clip(lower=0)      # revenus du patrimoine et non salariaux (approximation)
    poids = m.poids
    pf = prix_fiscal if prix_fiscal is not None else pd.Series(dtype=float)
    ce = cot_employeurs if cot_employeurs is not None else pd.Series(dtype=float)
    en = energie if energie is not None else pd.Series(dtype=float)
    s_e = pd.Series(energie_decile or [0.075] * 10, index=range(1, 11))
    s_e_moy = float(np.average(s_e.reindex(m.decile).values, weights=(poids * rev0).values))
    # exposition au risque de perte d'emploi (par personne en emploi)
    age_cl = np.where(m.age_pr < 30, "<30", np.where(m.age_pr < 50, "30-49", "50+"))
    risque = pd.Series([RISQUE_AGE[a] for a in age_cl], index=m.index) * m.gs_pr.map(RISQUE_GS).fillna(1.0)
    emp_w = (m.n_emploi * risque * poids)
    sal_moy = float((m.salaires * poids).sum() / max((m.n_emploi * poids).sum(), 1))
    sal_pers = (m.salaires / m.n_emploi.replace(0, np.nan)).fillna(sal_moy)
    n_cho = float((m.n_chomeurs * poids).sum())
    n_ina = float((m.n_inactifs_actifs * poids).sum())
    w_succ = cap * np.where((m.age_pr >= 45) & (m.age_pr < 75), 1.0, 0.3)
    w_succ = w_succ / max(float((w_succ * poids).sum()), 1.0)
    cible_s = ((m.age_pr >= 58) & (m.age_pr < 68)).astype(float)
    n_cible_s = max(float((cible_s * poids).sum()), 1.0)
    # pseudo-cohorte : les emplois maintenus vont aux ménages proches de l'âge légal qui ont des actifs occupés (leur
    # salaire), la pension non versée aux ménages proches de l'âge légal qui perçoivent une pension (au prorata)
    w_emp_s = cible_s * m.n_emploi
    n_emp_s = max(float((w_emp_s * poids).sum()), 1.0)
    w_pen_s = cible_s * m.pensions
    m_pen_s = max(float((w_pen_s * poids).sum()), 1.0)
    rev_tot = float((rev0 * poids).sum())
    cles_tr = {"chomeurs": m.n_chomeurs, "prestations": m.prest_base, "salaires": m.salaires * TAUX_NET}
    a_rdb = min([a for a in ref.index if a >= 2025] or [ref.index[0]])
    out = {}
    for t in horizons:
        if t not in ref.index or t not in scn.index:
            continue
        g = lambda k: float(np.log(scn[k][t] / ref[k][t]))  # noqa: E731
        dp = g("pc") - float(pf.get(t, 0.0))
        dp1 = (float(np.log(scn["pc"][t - 1] / ref["pc"][t - 1])) - float(pf.get(t - 1, 0.0))) if (t - 1) in ref.index else 0.0
        dwn = g("salaire") - float(ce.get(t, 0.0))
        # population active et chômage (milliers)
        pa_r, pa_s = ref["emploi"][t] / (1 - ref["chomage"][t] / 100), scn["emploi"][t] / (1 - scn["chomage"][t] / 100)
        u_r, u_s = pa_r * ref["chomage"][t] / 100, pa_s * scn["chomage"][t] / 100
        dU, dPA = u_s - u_r, pa_s - pa_r
        dPA_s = dE_s = dpens = 0.0
        if seniors:
            dPA_s = float(seniors["actifs"].get(t, 0.0))
            dE_s = min(float(seniors["emploi"].get(t, 0.0)), dPA_s) if dPA_s > 0 else float(seniors["emploi"].get(t, 0.0))
            dpens = float(seniors["pensions_M"].get(t, 0.0))
            dU, dPA = dU - (dPA_s - dE_s), dPA - dPA_s      # le reste suit les règles générales
        ch = pd.DataFrame(index=m.index)
        ch["direct"] = m.delta * m.uc if t >= debut else 0.0
        ch["salaires"] = m.salaires * (np.exp(dwn) - 1) * TAUX_NET
        gain_job = SALAIRE_EMBAUCHE * sal_moy * TAUX_NET
        if dU < 0:          # moins de chômeurs : retours à l'emploi
            p = min(-dU * 1e3 / max(n_cho, 1), 1.0)
            ch["emploi"] = m.n_chomeurs * p * (gain_job - ALLOCATION_PERDUE)
        else:               # plus de chômeurs : pertes d'emploi des salariés, selon le risque
            p = dU * 1e3 / max(float(emp_w.sum()), 1)
            ch["emploi"] = -m.n_emploi * risque * p * (sal_pers * TAUX_NET - ALLOCATION_PERDUE).clip(lower=0)
        q = dPA * 1e3 / max(n_ina, 1)
        ch["emploi"] += m.n_inactifs_actifs * q * GAIN_INACTIF * gain_job
        if seniors:
            # seniors maintenus en activité : salaire (emploi) ou allocation chômage, par ménage cible, en espérance ;
            # pension non versée (direct), convertie en part du revenu disponible macroéconomique
            ch["emploi"] += w_emp_s * sal_pers * TAUX_NET * (np.exp(dwn)) * dE_s * 1e3 / n_emp_s
            ch["emploi"] += cible_s * (dPA_s - dE_s) * 1e3 * ALLOCATION_PERDUE / n_cible_s
            if t >= debut:
                ch["direct"] = ch["direct"] + w_pen_s * (dpens / float(ref["rdb"][t])) * rev_tot / m_pen_s
        dcap = (scn["revenus_patrimoine_menages"][t] + scn["ebe_menages"][t]) / (ref["revenus_patrimoine_menages"][t] + ref["ebe_menages"][t]) - 1
        for mt_, cle_, deb_ in (transferts or []):
            if t >= deb_ and mt_:
                k_ = cles_tr[cle_]
                ch["direct"] = ch["direct"] + k_ * (mt_ / float(ref["rdb"][a_rdb])) * rev_tot / max(float((k_ * poids).sum()), 1.0)
        ch["patrimoine"] = cap * dcap
        ch["successions"] = -successions_M * 1e6 * w_succ if t >= debut else 0.0
        ch["indexation"] = (m.pensions + m.prest_base) * (np.exp(dp1) - 1)
        nominal = ch.sum(axis=1)
        dP = dp + (s_e.reindex(m.decile).values - s_e_moy) * PART_ENERGIE_IMPORT * float(en.get(t, 0.0))
        defl = np.exp(dP)
        reel = (rev0 + nominal) / defl - rev0
        ch["prix"] = reel - nominal
        # contrôle de cohérence : variation relative du revenu disponible macro (nominal) vs somme micro
        d_rdb_macro = float(scn["rdb"][t] / ref["rdb"][t] - 1)
        d_micro = float((nominal * poids).sum() / (rev0 * poids).sum())
        # v0.8 : comparaison en termes réels (la TVA et les accises réduisent le revenu réel par les prix dans le
        # compte macroéconomique, par le canal direct dans la microsimulation) et hors droits de succession (transferts
        # en capital, absents du revenu disponible macroéconomique)
        d_reel_macro = float((scn["rdb"][t] / scn["pc"][t]) / (ref["rdb"][t] / ref["pc"][t]) - 1)
        succ_ = ch["successions"] if not np.isscalar(ch["successions"]) else 0.0
        d_reel_micro = float(((reel - succ_) * poids).sum() / (rev0 * poids).sum())
        res = pd.DataFrame({"poids": poids, "uc": m.uc, "npers": m.npers, "nv0": m.nv_base, "rev0": rev0, "reel": reel})
        nv1 = (rev0 + reel) / m.uc
        seuil = 0.6 * _q(m.nv_base.values, (poids * m.npers).values, 0.5)
        rel = reel / rev0.replace(0, np.nan)
        def agreger(cle):
            out_ = {}
            for k, idx in m.groupby(cle).groups.items():
                w = poids[idx]
                out_[str(k)] = {"euros_par_uc": float(np.average(reel[idx] / m.uc[idx], weights=w)),
                                "pct": float(np.average(reel[idx], weights=w) / np.average(rev0[idx], weights=w) * 100),
                                "part_gagnants": float(np.average(rel[idx].fillna(0) > 0.005, weights=w)),
                                "part_perdants": float(np.average(rel[idx].fillna(0) < -0.005, weights=w)),
                                "canaux_euros_par_uc": {c: float(np.average(ch.loc[idx, c] / m.uc[idx], weights=w)) for c in ch.columns},
                                "poids": float(w.sum() / poids.sum())}
            return out_
        groupes = {"decile": m.decile}
        groupes["age"] = pd.Series(np.where(m.age_pr < 30, "moins de 30 ans", np.where(m.age_pr < 45, "30-44 ans", np.where(m.age_pr < 60, "45-59 ans",
                                   np.where(m.age_pr < 75, "60-74 ans", "75 ans et plus")))), index=m.index)
        statut = np.where(m.tact_pr == "21", "retraité", np.where(m.tact_pr == "12", "chômeur", np.where(m.tact_pr == "11",
                          np.where(m.stat_pr.isin(["21", "22", "23"]), "indépendant", "salarié"), "inactif")))
        groupes["statut"] = pd.Series(statut, index=m.index)
        groupes["occupation"] = m.statut_occ.map({"10": "propriétaire", "21": "locataire (privé)", "22": "locataire HLM", "23": "locataire meublé",
                                                  "30": "logé gratuitement"}).fillna("autre")
        groupes["csp"] = m.gs_pr.map({"1": "Agriculteurs", "2": "Artisans, commerçants, chefs d'entreprise", "3": "Cadres", "4": "Professions intermédiaires",
                                      "5": "Employés", "6": "Ouvriers"}).where(m.tact_pr.isin(["11", "12"]), "Retraités et inactifs")
        groupes["famille"] = pd.Series(np.where(m.adultes <= 1, np.where(m.enfants == 0, "Personne seule", "Famille monoparentale"),
                                                np.where(m.enfants == 0, "Couple sans enfant mineur", np.where(m.enfants <= 2, "Couple, 1-2 enfants",
                                                                                                              "Couple, 3 enfants ou plus"))), index=m.index)
        out[t] = {
            "global": {"euros_par_uc_moyen": float(np.average(reel / m.uc, weights=poids)),
                       "pct_moyen": float((reel * poids).sum() / (rev0 * poids).sum() * 100),
                       "variation_niveau_de_vie_median_pct": float(100 * (_q(nv1.values, (poids * m.npers).values, 0.5) / _q(m.nv_base.values, (poids * m.npers).values, 0.5) - 1)),
                       "part_gagnants": float(np.average(rel.fillna(0) > 0.005, weights=poids)),
                       "part_perdants": float(np.average(rel.fillna(0) < -0.005, weights=poids)),
                       "pauvrete_avant": float(np.average(m.nv_base < seuil, weights=poids * m.npers) * 100),
                       "pauvrete_apres": float(np.average(nv1 < seuil, weights=poids * m.npers) * 100),
                       "gini_avant": _gini(m.nv_base.values, (poids * m.npers).values), "gini_apres": _gini(nv1.values, (poids * m.npers).values),
                       "canaux_pct": {c: float((ch[c] * poids).sum() / (rev0 * poids).sum() * 100) for c in ch.columns},
                       "coherence": {"rdb_macro_nominal_pct": 100 * d_rdb_macro, "somme_micro_nominal_pct": 100 * d_micro,
                                     "residuel_nominal_pct": 100 * (d_rdb_macro - d_micro),
                                     "rdb_macro_reel_pct": 100 * d_reel_macro, "somme_micro_reel_hors_successions_pct": 100 * d_reel_micro,
                                     "residuel_pct": 100 * (d_reel_macro - d_reel_micro)},
                       "macro": {"salaire_brut_pct": 100 * (np.exp(dwn) - 1), "prix_hors_fiscal_pct": 100 * (np.exp(dp) - 1),
                                 "chomeurs_milliers": dU, "population_active_milliers": dPA, "revenus_patrimoine_pct": 100 * dcap}},
            **{k: agreger(v) for k, v in groupes.items()}}
    return out
