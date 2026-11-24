"""Compte de référence « à politique inchangée » (version 1.0, novembre 2026).

Remplace le compte central conventionnel de `m8_modele.exogenes_projection` (exogènes prolongés à rythmes moyens,
non recalé) par une trajectoire :
1. recalée sur les comptes observés 2023-2025 (Insee, comptes annuels publiés en mai 2026) : des termes de calage
   (`Exogenes.calage`) sont ajoutés aux équations de consommation, d'investissement, d'exportations, d'importations,
   d'emploi, de prix et de salaires, et aux recettes, dépenses et à la dette publiques, pour reproduire l'observé ;
2. calée de 2026 à 2031 sur les projections du FMI (Perspectives de l'économie mondiale, octobre 2026) pour la
   croissance, le chômage et l'inflation (solde public : 2026 seulement), puis sur les hypothèses de long terme du COR
   (productivité +0,7 %/an, chômage convergeant vers 7 %) ; les finances publiques sont calculées par le modèle ;
3. sans nouvelle mesure après la loi de finances 2026, avec les exogènes suivants :
   - démographie (Insee, projection centrale 2021) : population active et masse des pensions de droit direct par
     génération (module M9, législation actuelle, revalorisation sur les prix) ;
   - environnement international : croissance de la zone euro et inflation selon le FMI (2027-2031, puis dernier
     rythme), demande adressée = 1,5 × croissance de la zone euro (hypothèse) ;
   - taux de l'OAT à 10 ans maintenu au dernier niveau mensuel observé (Eurostat), le taux apparent de la dette le
     rejoignant progressivement ;
   - consommation publique en volume et prestations hors pensions à leur rythme moyen 2011-2019 ;
   - les termes de calage des recettes et des dépenses (en points de PIB) restent à leur valeur de 2026 ;
   - termes de rappel des équations ancrés sur l'écart à l'équilibre constaté fin 2025 (`Exogenes.ancrage`).
Documentation : doc/M8_reference.md.
Ce n'est pas une prévision : c'est le point de comparaison commun à toutes les mesures, avec ses propres incertitudes.
"""
from __future__ import annotations

import copy
import json
import pathlib

import numpy as np
import pandas as pd

import m8_modele as M8
from telechargement import telecharger

RACINE = pathlib.Path(__file__).resolve().parents[1]
FIN_OBSERVE = 2025
ANNEE_FMI = 2026               # première année projetée (calage du solde public)
FIN_FMI = 2031                 # dernière année des projections du FMI
ELAST_COMMERCE = 1.5           # demande adressée / croissance de la zone euro (hypothèse D)
CALER_PIB_FMI = False          # 2026 : calage sur la croissance du FMI (sinon : chômage, inflation et solde seulement)
PRODUCTIVITE_LT = 0.7          # croissance de long terme de la productivité par tête, % (hypothèse centrale du COR, 2025-2026)
CONVERGENCE_PRODUCTIVITE = 4   # années pour passer du rythme 2026 à la cible
INDICATEURS_FMI = ["NGDP_RPCH", "LUR", "PCPIPCH", "GGXCNL_NGDP", "GGXWDG_NGDP"]
LIBELLES_FMI = {"NGDP_RPCH": "Croissance du PIB (%)", "LUR": "Taux de chômage (%)", "PCPIPCH": "Inflation (IPCH, %)",
                "GGXCNL_NGDP": "Solde public (% du PIB)", "GGXWDG_NGDP": "Dette publique (% du PIB)"}


# ------------------------------------------------------------------------------------------------------------------
# Données externes
# ------------------------------------------------------------------------------------------------------------------
def fmi(pays=("FRA", "EURO")) -> dict:
    """Projections du FMI (WEO d'octobre 2026, API DataMapper) : {indicateur: {pays: {année: valeur}}}."""
    out = {}
    for i in INDICATEURS_FMI:
        f = telecharger(f"https://www.imf.org/external/datamapper/api/v1/{i}/{'/'.join(pays)}", f"fmi_weo_2026_10_{i}.json")
        v = json.loads(f.read_text())["values"][i]
        out[i] = {p: {int(a): float(x) for a, x in v.get(p, {}).items()} for p in pays}
    return out


def taux_oat_recent() -> tuple[str, float]:
    """Dernier taux mensuel de l'OAT à 10 ans (critère de Maastricht, Eurostat irt_lt_mcby_m)."""
    f = telecharger("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/irt_lt_mcby_m?geo=FR&sinceTimePeriod=2025-01&format=JSON&lang=en",
                    "eurostat_irt_lt_mcby_m_FR_2026_11.json")
    d = json.loads(f.read_text())
    inv = {i: k for k, i in d["dimension"]["time"]["category"]["index"].items()}
    obs = sorted((inv[int(k)], v) for k, v in d["value"].items())
    return obs[-1]


# ------------------------------------------------------------------------------------------------------------------
# Exogènes
# ------------------------------------------------------------------------------------------------------------------
def _taux_moyen(s: pd.Series, a0=2011, a1=2019) -> float:
    return float((s[a1] / s[a0]) ** (1 / (a1 - a0)) - 1)


def hypotheses(mod) -> dict:
    m, men = mod.macro, mod.men
    F = fmi()
    mois, oat = taux_oat_recent()
    import m9_retraites as R
    pens = R.pensions_observees()
    prest_vol = (men.d62 / m.p_c.reindex(men.index).shift(1))
    # prestations hors pensions de droit direct (comptes nationaux − Eurostat SESPROS), en volume
    autres = (men.d62 - pens.masse_droit_direct.reindex(men.index)) / m.p_c.reindex(men.index).shift(1)
    return {"fmi": F, "oat": (mois, oat), "g_conso_publique": _taux_moyen(m.g), "g_autres_prestations": _taux_moyen(autres.dropna()),
            "g_prestations_total_2011_2019": _taux_moyen(prest_vol.dropna()), "g_autres_investissements": 0.01,
            "chomage_structurel": 7.5, "elast_commerce": ELAST_COMMERCE}


def chomage_structurel(t: int, H: dict) -> float:
    """Chômage structurel (v0.7) : 7,5 % jusqu'en 2026 (ancienne hypothèse du projet), puis convergence linéaire vers le
    chômage de long terme de la référence (CHOMAGE_LT = 7 %, hypothèse COR) atteint en 2031. En v0.6, u* restait à 7,5 %
    alors que la référence convergeait vers 7 % : un écart permanent de −0,5 point que les termes de calage compensaient
    (variable endogène artificiellement contrainte, audit phase 3)."""
    u0 = H["chomage_structurel"]
    if t <= 2026:
        return u0
    if t >= 2031:
        return CHOMAGE_LT
    return u0 + (CHOMAGE_LT - u0) * (t - 2026) / 5


# Phase 5 : convention de dépense de la référence « politique inchangée ».
#   "historique" (défaut, versions antérieures) : consommation publique et prestations hors pensions en volume à leur
#     rythme 2011-2019 ;
#   "part_constante" : consommation publique et prestations hors pensions en volume à la croissance du PIB potentiel
#     conventionnel (population active × (1 − u*) × productivité de long terme), donc à part constante du PIB potentiel ;
#     pensions (M9) et allocations chômage (stabilisateur, M8) inchangées.
CONVENTIONS_DEPENSE = ("historique", "part_constante")


def croissance_potentielle_conventionnelle(mod, H, annees) -> dict:
    """Croissance du PIB potentiel conventionnel (hypothèses de la référence, non simulée) : emploi structurel
    (population active × (1 − u*)) × productivité par tête de long terme (PRODUCTIVITE_LT)."""
    import m9_retraites as R
    act = R.ActiviteSeniors()
    out = {}
    for t in annees:
        if t <= FIN_OBSERVE:
            continue
        n1 = act.population_active(t, "actuelle") * (1 - chomage_structurel(t, H) / 100)
        n0 = act.population_active(t - 1, "actuelle") * (1 - chomage_structurel(t - 1, H) / 100)
        out[t] = (n1 / n0) * (1 + PRODUCTIVITE_LT / 100) - 1
    return out


def exogenes(mod, annees, H=None, convention="historique") -> M8.Exogenes:
    """Exogènes observés jusqu'en 2025, projetés ensuite (voir l'en-tête)."""
    assert convention in CONVENTIONS_DEPENSE, convention
    H = H or hypotheses(mod)
    fin = max(annees)
    obs = M8.exogenes_observes(mod, range(mod.B + 1, FIN_OBSERVE + 1))
    m = mod.macro
    ans = list(range(mod.B - 3, fin + 1))
    ze = H["fmi"]["NGDP_RPCH"]["EURO"]
    infl = H["fmi"]["PCPIPCH"]["EURO"]
    def g_ze(t):
        return ze.get(t, ze[max(ze)]) / 100
    def pi_ze(t):
        return infl.get(t, infl[max(infl)]) / 100
    def prol(serie, g):
        s = pd.Series({t: float(serie[t]) for t in ans if t <= FIN_OBSERVE and t in serie.index})
        for t in ans:
            if t > FIN_OBSERVE:
                s[t] = s[t - 1] * (1 + (g(t) if callable(g) else g))
        return s.sort_index()
    pm = obs.prix_import.copy()
    for t in range(FIN_OBSERVE + 1, fin + 1):
        pm.loc[t] = pm.loc[t - 1] * (1 + pi_ze(t))
    import m9_retraites as R
    act = R.ActiviteSeniors()
    pa = {t: float(obs.population_active[t]) for t in ans if t <= FIN_OBSERVE}
    pa_ref = act.population_active(FIN_OBSERVE, "actuelle")
    for t in ans:
        if t > FIN_OBSERVE:
            pa[t] = pa[FIN_OBSERVE] * act.population_active(t, "actuelle") / pa_ref
    tl = pd.Series({t: (float(m.taux_long[t]) if t <= FIN_OBSERVE else H["oat"][1]) for t in ans})
    if convention == "part_constante":
        gp = croissance_potentielle_conventionnelle(mod, H, ans)
        g_cp = g_pr = (lambda t: gp[t])  # noqa: E731
    else:
        g_cp, g_pr = H["g_conso_publique"], H["g_autres_prestations"]
    ex = M8.Exogenes(demande_mondiale=prol(m.ue_m, lambda t: H["elast_commerce"] * g_ze(t)),
                     prix_mondial=prol(m.p_ue_m, pi_ze), prix_import=pm.sort_index(),
                     conso_publique=prol(m.g, g_cp),
                     autres_investissements=prol(obs.autres_investissements, H["g_autres_investissements"]),
                     population_active=pd.Series(pa).sort_index(),
                     chomage_structurel=pd.Series({t: chomage_structurel(t, H) for t in ans}), taux_long=tl,
                     taux_is=pd.Series({t: float(M8.S.taux_is().get(t, 25.83)) for t in ans}),
                     prestations_volume=prol(obs.prestations_volume.dropna(), g_pr),
                     autres_depenses_pib=obs.autres_depenses_pib, fermeture_offre=M8.RHO_DEFAUT)
    return ex


# ------------------------------------------------------------------------------------------------------------------
# Pensions (démographie, M9)
# ------------------------------------------------------------------------------------------------------------------
def pensions(mod, central, regle="actuelle", pens=None):
    """Masse des pensions de droit direct (M€) et nombre de retraités (milliers) par année, avec les prix et salaires
    simulés par `central` (et observés avant)."""
    import m9_retraites as R
    pens = pens or R.Pensions(R.ActiviteSeniors())
    prix, sal = R.trajectoires_m8(pens, central, mod.macro.p_c[mod.B], mod.B)
    out = {}
    for t in central.index:
        nb, ma = pens.masse(int(t), regle, salaires=sal, prix=prix)
        out[int(t)] = (ma / 1e6, nb / 1e3)
    return out, pens


def ajust_pensions(mod, ex, central, P):
    """Terme `ajust_prestations` qui remplace, après 2025, la part des pensions incluse dans la croissance
    conventionnelle des prestations par la masse de M9 : d62(t) = autres prestations (rythme 2011-2019) + pensions M9."""
    B = mod.B
    pc = lambda t: (float(central.pc[t]) if t in central.index else float(mod.macro.p_c[t]))  # noqa: E731
    vol = ex.prestations_volume
    p0 = P[FIN_OBSERVE][0]
    aj = {}
    for t in central.index:
        t = int(t)
        if t <= FIN_OBSERVE:
            continue
        inclus = p0 * (pc(t - 1) / pc(FIN_OBSERVE - 1)) * float(vol[t]) / float(vol[FIN_OBSERVE])
        aj[t] = P[t][0] - inclus
    return pd.Series(aj)


# ------------------------------------------------------------------------------------------------------------------
# Calage
# ------------------------------------------------------------------------------------------------------------------
CLES_CROISSANCE = ["c", "investissement", "x", "m", "emploi", "prix", "salaire"]
CLES_NIVEAU = ["stocks", "pib_nominal"]   # niveaux (part du PIB de base ; log du PIB nominal), maintenus après 2025


CHOMAGE_LT = 7.0               # chômage de long terme (scénario de référence du COR, stabilisé à 7 % dès 2032)


def taux_epargne_cible(t: int) -> float:
    """Taux d'épargne des ménages de la trajectoire de référence (% du RDB, définition du modèle) : 17,9 % observé en 2025,
    17,3 % en 2027 (hypothèse du projet de loi de finances pour 2027), puis retour progressif vers 15,5 %, entre ce niveau
    et la moyenne d'avant la crise sanitaire (environ 15 %), atteint en 2031 (hypothèse D)."""
    points = {2025: 17.9, 2026: 17.6, 2027: 17.3, 2028: 16.85, 2029: 16.4, 2030: 15.95, 2031: 15.5}
    return points.get(t, 15.5 if t > 2031 else 17.9)


def _cibles(mod, H, fin=2035):
    """Cibles de calage : comptes observés 2023-2025 ; FMI (octobre 2026) pour 2026-2031 : croissance, chômage
    (écart de définition de 2025 entre FMI et Eurostat neutralisé), inflation ; solde public 2026 seulement (les
    projections de solde du FMI incluent des mesures de redressement non encore votées)."""
    m, apu, em = mod.macro, mod.apu, mod.emp
    p = mod.panel.groupby("annee")[["wb", "ns"]].sum()
    w = p.wb / p.ns
    c = {}
    for t in range(mod.B + 1, FIN_OBSERVE + 1):
        c[t] = {"c": m.c[t], "investissement": m.fbcf[t], "x": m.x[t], "m": m.m[t], "emploi": em.emploi[t], "prix": m.p_c[t],
                "salaire": (w[t] if t <= 2024 else None), "recettes": apu.tr[t] / m.pib_cp[t] * 100,
                "depenses": apu.te[t] / m.pib_cp[t] * 100, "dette": apu.dette[t], "pib": m.pib[t], "pib_cp": m.pib_cp[t]}
    F = H["fmi"]
    d_u = F["LUR"]["FRA"][FIN_OBSERVE] - m.chomage[FIN_OBSERVE]
    for a in range(FIN_OBSERVE + 1, FIN_FMI + 1):
        c[a] = {"pib_croissance": F["NGDP_RPCH"]["FRA"][a], "chomage": F["LUR"]["FRA"][a] - d_u,
                "inflation": F["PCPIPCH"]["FRA"][a], "solde": (F["GGXCNL_NGDP"]["FRA"][a] if a == ANNEE_FMI else None)}
    # au-delà : productivité de long terme, chômage convergeant vers CHOMAGE_LT, inflation du FMI de 2031
    import m9_retraites as R
    act = R.ActiviteSeniors()
    for a in range(FIN_FMI + 1, fin + 1):
        u1 = c[a - 1]["chomage"]
        u = u1 + max(-0.3, min(0.3, CHOMAGE_LT - u1))
        g_pa = act.population_active(a, "actuelle") / act.population_active(a - 1, "actuelle") - 1
        g_emp = (1 + g_pa) * (1 - u / 100) / (1 - u1 / 100) - 1
        c[a] = {"pib_croissance": ((1 + g_emp) * (1 + PRODUCTIVITE_LT / 100) - 1) * 100, "chomage": u,
                "inflation": F["PCPIPCH"]["FRA"][FIN_FMI], "solde": None}
    return c


def caler(mod, ex, annees, H, iterations=7, journal=print):
    """Termes de calage année par année (toutes les années de `_cibles`). Renvoie une copie de ex et le diagnostic.
    Les termes des recettes et des dépenses restent à leur valeur de 2026 ; les termes en niveau à leur valeur de 2025."""
    ex = copy.deepcopy(ex)
    ex.ancrage = FIN_OBSERVE
    cal = {k: pd.Series(dtype=float) for k in CLES_CROISSANCE + CLES_NIVEAU + ["recettes", "depenses", "dette"]}
    ex.calage = cal
    cibles = _cibles(mod, H, max(annees))
    diag = {}
    for t in sorted(cibles):
        if t > max(annees):
            break
        ci = cibles[t]
        for k in cal:
            cal[k][t] = cal[k].get(t - 1, 0.0) if ((t > ANNEE_FMI and k in ("recettes", "depenses")) or (t > FIN_OBSERVE and k in CLES_NIVEAU)) else 0.0
        for it in range(iterations + (8 if t <= FIN_OBSERVE else 4)):
            r = mod.simuler(range(mod.B + 1, t + 1), ex)
            s = r.loc[t]
            if t <= FIN_OBSERVE:
                ec = {"c": np.log(ci["c"] / s.c), "investissement": np.log(ci["investissement"] / s.fbcf), "x": np.log(ci["x"] / s.x),
                      "m": np.log(ci["m"] / s.m), "emploi": np.log(ci["emploi"] / s.emploi), "prix": np.log(ci["prix"] / s.pc)}
                if ci["salaire"] is not None:
                    ec["salaire"] = np.log(ci["salaire"] / s.salaire)
                for k, v in ec.items():
                    cal[k][t] += 0.9 * v
                cal["stocks"][t] += 0.6 * (ci["pib"] / s.pib - 1)
                cal["pib_nominal"][t] += 0.9 * np.log(ci["pib_cp"] / s.pib_nominal)
                pibn = s.pib_nominal
                cal["recettes"][t] += ci["recettes"] - s.recettes / pibn * 100
                cal["depenses"][t] += ci["depenses"] - s.depenses / pibn * 100
                cal["dette"][t] += ci["dette"] - s.dette
            else:
                d = ci["pib_croissance"] - (s.pib / r.pib[t - 1] - 1) * 100
                # Audit de novembre 2026 : la consommation suit une cible de taux d'épargne (TAUX_EPARGNE_CIBLE) ; l'écart de
                # croissance est comblé par l'investissement et les parts de marché à l'exportation. Auparavant, l'écart était
                # comblé par la consommation et l'investissement, ce qui faisait tomber le taux d'épargne de 17,9 % (2025) à
                # 11 % (2032), sans fondement.
                cal["c"][t] += 0.8 * (s.taux_epargne - taux_epargne_cible(t)) / 100
                cal["investissement"][t] += 1.6 * d / 100
                cal["x"][t] += 1.6 * d / 100
                cal["emploi"][t] += 0.8 * (s.chomage - ci["chomage"]) / 100
                inf = (s.pc / r.pc[t - 1] - 1) * 100
                cal["prix"][t] += 0.8 * (ci["inflation"] - inf) / 100
                if ci["solde"] is not None:
                    cal["recettes"][t] += 0.8 * (ci["solde"] - s.solde_pib)
        r = mod.simuler(range(mod.B + 1, t + 1), ex)
        s = r.loc[t]
        p1 = r.pib[t - 1] if t - 1 in r.index else mod.macro.pib[t - 1]
        c1 = r.pc[t - 1] if t - 1 in r.index else mod.macro.p_c[t - 1]
        diag[t] = {"croissance": float((s.pib / p1 - 1) * 100), "chomage": float(s.chomage),
                   "inflation": float((s.pc / c1 - 1) * 100), "solde_pib": float(s.solde_pib), "dette_pib": float(s.dette_pib)}
        journal(f"calage {t} : " + ", ".join(f"{k} {v:.2f}" for k, v in diag[t].items()))
    return ex, diag


_CACHE = {}


def compte_reference(mod, annees, journal=print, convention="historique"):
    """Exogènes de référence calés (avec pensions M9) et trajectoire. Mis en cache par (base, horizon), en mémoire et
    sur disque (outputs/compte_reference_<base>_<horizon>.pkl), invalidé si le code de ce module ou de M8 change."""
    import hashlib
    import pickle
    import json as _json
    import m7_equations as _E
    spec_txt = _json.dumps(getattr(M8, "SPEC", {}), sort_keys=True) + f"|sigma={_E.SIGMA_TRAVAIL}"   # v0.9 : la spécification fait partie de la clé
    if convention != "historique":                       # phase 5 : la convention fait partie de la clé
        spec_txt += f"|depense={convention}"
    cle = (mod.B, max(annees), spec_txt)
    if cle in _CACHE:
        return _CACHE[cle]
    emp = hashlib.sha1((pathlib.Path(__file__).read_bytes() + (RACINE / "src" / "m8_modele.py").read_bytes() + spec_txt.encode())).hexdigest()[:12]
    f = RACINE / "outputs" / f"compte_reference_{mod.B}_{max(annees)}_{hashlib.sha1(spec_txt.encode()).hexdigest()[:8]}.pkl"
    if f.exists():
        d = pickle.loads(f.read_bytes())
        if d.get("empreinte") == emp:
            d["trajectoire"] = mod.simuler(annees, d["exogenes"])
            _CACHE[cle] = d
            return d
    H = hypotheses(mod)
    ex = exogenes(mod, annees, H, convention=convention)
    central = mod.simuler(annees, ex)
    pens = None
    for passe in range(2):
        P, pens = pensions(mod, central, pens=pens)
        ex.ajust_prestations = ajust_pensions(mod, ex, central, P)
        ex, diag = caler(mod, ex, annees, H, journal=journal)
        central = mod.simuler(annees, ex)
    P, _ = pensions(mod, central, pens=pens)
    # v0.7 : productivité globale des facteurs implicite de la référence (bloc d'offre). L'écart de production de la
    # référence est, par construction, −OKUN × (u − u*) ; les variantes se mesurent ensuite à ce potentiel.
    ex.lpgf = central["lpgf_implicite"].copy()
    ex.fermeture_mode = "production"
    central = mod.simuler(annees, ex)
    ex.lpot_ref = np.log(central["pib_potentiel"]).copy()   # potentiel de référence (anticipation des chocs d'offre)
    ex.lk_ref = np.log(central["capital_marchand"]).copy()  # capital et PIB de référence (emploi de long terme)
    ex.ly_ref = np.log(central["pib"]).copy()
    central = mod.simuler(annees, ex)
    d = {"exogenes": ex, "trajectoire": central, "pensions": P, "hypotheses": H, "diagnostic": diag, "empreinte": emp}
    f.parent.mkdir(exist_ok=True)
    f.write_bytes(pickle.dumps({k: v for k, v in d.items() if k != "trajectoire"}))
    _CACHE[cle] = d
    return d


# ------------------------------------------------------------------------------------------------------------------
# Variantes de la trajectoire de référence (version 1.1)
# ------------------------------------------------------------------------------------------------------------------
VARIANTES_REFERENCE = {
    "inchangee": "Politique inchangée, OAT à 10 ans au dernier niveau observé",
    "oat_bas": "Politique inchangée, OAT à 10 ans 1 point plus bas à partir de 2027",
    "oat_haut": "Politique inchangée, OAT à 10 ans 1 point plus haut à partir de 2027",
    "redressement": "Redressement d'ampleur FMI : effort ex ante égal à l'écart entre le solde projeté par le FMI et "
                    "celui de la trajectoire inchangée (2027-2031, puis maintenu), moitié par la consommation publique, "
                    "moitié par les impôts des ménages ; l'activité et les recettes réagissent à ce redressement",
}


def exogenes_variante(mod, annees, nom, journal=print):
    """Exogènes de la trajectoire de référence `nom` (voir VARIANTES_REFERENCE), dérivés de la trajectoire inchangée."""
    R = compte_reference(mod, annees, journal=journal)
    ex = copy.deepcopy(R["exogenes"])
    if nom == "inchangee":
        return ex
    if nom in ("oat_bas", "oat_haut"):
        d = -1.0 if nom == "oat_bas" else 1.0
        ex.taux_long = pd.Series({t: v + (d if t >= ANNEE_FMI + 1 else 0.0) for t, v in ex.taux_long.items()})
        return ex
    if nom == "redressement":
        import hashlib
        import pickle
        f = RACINE / "outputs" / f"reference_redressement_{mod.B}_{max(annees)}.pkl"
        emp = R["empreinte"]
        if f.exists():
            d = pickle.loads(f.read_bytes())
            if d.get("empreinte") == emp:
                return d["exogenes"]
        F = R["hypotheses"]["fmi"]["GGXCNL_NGDP"]["FRA"]
        g0 = ex.conso_publique.copy()
        part_g = float(mod.macro.g_cp[FIN_OBSERVE] / mod.macro.pib_cp[FIN_OBSERVE]) if "g_cp" in mod.macro else 0.235
        effort = {t: 0.0 for t in annees}
        ex.niveaux = {"impots_menages_pib": pd.Series({t: 0.0 for t in annees})}
        def appliquer(t):
            ex.niveaux["impots_menages_pib"][t] = effort[t] / 2
            ex.conso_publique[t] = g0[t] * (1 - effort[t] / 2 / 100 / part_g)
        ref_s = R["trajectoire"].solde_pib
        for t in sorted(annees):
            if t <= ANNEE_FMI:
                continue
            # effort ex ante : écart entre le solde projeté par le FMI et celui de la trajectoire inchangée
            effort[t] = max(0.0, F[t] - float(ref_s[t])) if t <= FIN_FMI else effort[t - 1]
            appliquer(t)
            journal(f"redressement {t} : effort ex ante {effort[t]:.2f} pt de PIB")
        f.write_bytes(pickle.dumps({"exogenes": ex, "empreinte": emp, "effort": effort}))
        return ex
    raise ValueError(nom)
