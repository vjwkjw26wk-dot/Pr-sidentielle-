"""M9 — Activité des seniors et retraites (version 0.1).

Relie la démographie (M1 : population par âge et sexe, Insee 2026, historique 1962-2025 et projection centrale), les
règles de retraite (âge d'ouverture des droits par génération), la population active, le nombre de retraités et la
masse des pensions de droit direct, puis transmet population active, emploi supplémentaire et pensions au modèle
bouclé M8.

1. Âge d'ouverture des droits (AOD) par génération : législation actuelle (réforme de 2023 suspendue par la LFSS pour
   2026 : 62 ans et 9 mois pour 1963-1964, puis +3 mois par génération jusqu'à 64 ans pour 1969) et variantes.
2. Taux d'activité par âge simple et sexe, de 55 à 74 ans, relatifs au taux d'activité des 50-54 ans :
     a(x, t) = A(t) · h(x + 0,5 − AOD_g) ,   g = t − x − 1 (génération ; âge en années révolues, milieu d'année)
     h(d) = 1 − e(t) · rampe(d)          pour d < 0  (sorties avant l'AOD : carrières longues, invalidité, chômage)
          = s · exp(−k · d) · (1 − e(t)) pour d ≥ 0
   avec rampe(d) = min(1, (d + L)/L)⁺ sur L = 5 ans, e(t) = e0 + e1 (t − 2010) (tendance des sorties précoces).
   Paramètres (e0, e1, s, k) estimés par moindres carrés non linéaires sur les taux d'activité par tranche quinquennale
   (enquête Emploi, Eurostat `lfsa_argan`, 2003-2019), tranches 55-59, 60-64, 65-69, 70-74, pondérées par la population
   par âge simple. Test hors échantillon : 2020-2025 (relèvement de l'AOD de 62 ans à 62 ans et 9 mois).
3. Retraités de droit direct : part retraitée par âge ρ(x) = π · [1 − actifs non retraités], calée sur le nombre de
   bénéficiaires (Eurostat `spr_pns_ben`, OLD_TOT).
4. Pensions : modèle par génération. Pension moyenne de la génération g à la liquidation = ν × moyenne des 25 dernières
   années de salaire moyen par tête revalorisées sur les prix (liquidation en ≈ g + AOD_g) ; ensuite revalorisée sur les prix. Masse = Σ retraités(x, t) · pension(g, t).
   ν calé sur la masse des pensions de vieillesse de droit direct (Eurostat `spr_exp_pens`, OLD) d'une année de base ;
   la dynamique 2010-2024 sert de test (effet de noria, revalorisations, effectifs).
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
import insee_projections as ip  # noqa: E402
import m7_series as S  # noqa: E402
from telechargement import jsonstat_dict  # noqa: E402

L_RAMPE = 5.0
TRANCHES = [(55, 59), (60, 64), (65, 69), (70, 74)]


# ------------------------------------------------------------------------------------------------------------------
# 1. Règles
# ------------------------------------------------------------------------------------------------------------------
# Calage de la boucle de cohérence (17 novembre 2026). M9 attribue aux départs supplémentaires (ou évités) la pension
# moyenne de leur génération : l'abrogation de la réforme de 2023 (règle « 2023 » → « 2010 ») y coûte 17,5 Md€ en
# 2027 et 23,8 Md€ en 2030, contre 8,2 Md€ (Institut Montaigne, scénario médian) et 14,1 Md€ (étude d'impact du
# gouvernement) pour l'ensemble des dispositions. Les départs à l'âge légal concernent surtout des carrières
# incomplètes (décote, pensions plus faibles) et une partie des personnes concernées serait passée par le chômage ou
# l'invalidité. L'écart de masse des pensions dû à une réforme d'âge est donc multiplié par 0,55 (moyenne des deux
# rapports). Les effets sur l'activité ne sont pas modifiés (validés hors échantillon, 2020-2025).
COEF_PENSION_MARGINALE = 0.55

# ------------------------------------------------------------------------------------------------------------------
# Durée d'assurance requise et groupes de départ anticipé (finalisation, 24-25 novembre 2026)
# ------------------------------------------------------------------------------------------------------------------
# Report de l'âge effectif de cessation d'activité par année supplémentaire de durée requise [E, littérature] :
# 9 mois pour les hommes, 5 mois pour les femmes (réforme de 1993 : 37,5 → 40 ans ; Bozio, « La réforme des
# retraites de 1993 : l'impact de l'augmentation de la durée d'assurance », Économie et Statistique n° 441-442, 2011).
# Appliqué symétriquement aux baisses de durée [H].
ELASTICITE_DUREE = {"M": 0.75, "F": 5.0 / 12.0}
# Part de la pension totale soumise à la proratisation et à la décote du régime de base [H] (le régime de base
# représente de l'ordre de la moitié de la pension d'un salarié du privé ; complémentaires en points non affectées).
PART_PENSION_BASE = 0.5
DECOTE_PAR_AN = 0.05            # 1,25 % par trimestre manquant [D, code de la sécurité sociale]
# Part des départs anticipés pour carrière longue parmi les nouveaux retraités du régime général [D] : 114 000 sur
# 658 481 en 2024 (CNAV, recueil statistique, données 2024) ; « environ un nouveau liquidant sur cinq » (DREES 2025).
PART_CARRIERES_LONGUES = 0.17


def duree_requise(g: int, spec: str = "actuelle") -> float:
    """Durée d'assurance requise pour le taux plein (trimestres) de la génération g.
    spec : "actuelle" (loi de 2023 aménagée par la LFSS pour 2026 : 170 trimestres pour 1963-1964, 171 pour 1965,
    172 à partir de 1966), "2014" (loi du 20 janvier 2014 : un trimestre toutes les trois générations de 1958 à
    1973), ou "cible@debut[:mode]" (trimestres ; générations atteignant l'âge légal à partir de `debut` ; mode
    "immediat" ou "progressif" = un trimestre par génération)."""
    if spec in ("actuelle", None, ""):
        if g <= 1957:
            return 166.0
        if g <= 1960:
            return 167.0
        return {1961: 168.0, 1962: 169.0, 1963: 170.0, 1964: 170.0, 1965: 171.0}.get(g, 172.0)
    if spec == "2014":
        if g <= 1957:
            return 166.0
        return float(min(172, 167 + (g - 1958) // 3))
    cible_s, reste = spec.split("@", 1)
    debut_s, _, mode = reste.partition(":")
    cible, debut, mode = float(cible_s), int(debut_s), (mode or "immediat")
    actuel = duree_requise(g, "actuelle")
    if g + aod(g, "actuelle") < debut:
        return actuel
    if mode == "immediat":
        return cible
    g0 = next(gg for gg in range(1940, 2010) if gg + aod(gg, "actuelle") >= debut)
    d0 = duree_requise(g0, "actuelle")
    pas = 1.0 if cible >= d0 else -1.0
    return float(np.clip(d0 + pas * (g - g0 + 1), min(cible, d0), max(cible, d0)))


def decomposer(regle) -> tuple[str, str | None, tuple | None]:
    """Règle complète « âge|D=durée|G=groupe:part » → (règle d'âge, spécification de durée, (groupe, part)).
    Groupe : âge de départ (nombre) d'une fraction `part` de chaque génération (carrières longues), ou « ref » : la
    fraction garde les conditions de la législation actuelle (départs précoces maintenus)."""
    r = str(regle)
    if "|" not in r:
        return r, None, None
    base, *opts = r.split("|")
    dspec, grp = None, None
    for o in opts:
        if o.startswith("D="):
            dspec = o[2:]
        elif o.startswith("G="):
            a, _, p_ = o[2:].partition(":")
            grp = (a, float(p_))
    return base, dspec, grp


def aod(g: int, regle: str = "actuelle") -> float:
    """Âge d'ouverture des droits (années décimales) de la génération g.
    regle : "actuelle" (LFSS 2026), "2023" (loi de 2023 sans suspension), "2010" (62 ans), ou un nombre (cible
    atteinte à +3 mois par génération à partir de la génération 1964)."""
    regle = decomposer(regle)[0]
    hist = {1950: 60.0, 1951: 60.17, 1952: 60.75, 1953: 61.17, 1954: 61.58}
    if g <= 1950:
        return 60.0
    if g in hist:
        return hist[g]
    if g <= 1960:
        return 62.0
    if regle == "2010":
        return 62.0
    base = {1961: 62.08, 1962: 62.5, 1963: 62.75}
    if g in base:
        return base[g]
    if regle == "2023":
        return min(64.0, 62.75 + 0.25 * (g - 1963))
    if regle == "actuelle":
        return 62.75 if g == 1964 else min(64.0, 62.75 + 0.25 * (g - 1964))
    if "@" in str(regle):
        return _aod_reforme(g, str(regle))
    cible = float(regle)
    return min(cible, 62.75 + 0.25 * (g - 1963)) if cible >= 62.75 else max(cible, 62.75 - 0.25 * (g - 1963))


def _aod_reforme(g: int, regle: str) -> float:
    """Réforme de l'âge légal entrant en vigueur au 1er janvier d'une année : "cible@debut[:mode]".
    - Les générations dont l'âge légal actuel est atteint avant `debut` ne sont pas concernées.
    - mode "progressif" (défaut) : l'âge évolue de 3 mois par génération à partir de la première génération concernée
      g0, jusqu'à la cible ; mode "immediat" : la cible s'applique dès `debut` (sans départ rétroactif : âge ≥ debut − g).
    Les conditions de durée d'assurance (taux plein, carrières longues) ne sont pas modélisées."""
    cible_s, reste = regle.split("@", 1)
    debut_s, _, mode = reste.partition(":")
    cible, debut, mode = float(cible_s), int(debut_s), (mode or "progressif")
    actuel = aod(g, "actuelle")
    if g + actuel < debut:
        return actuel
    g0 = next(gg for gg in range(1940, 2010) if gg + aod(gg, "actuelle") >= debut)
    a0 = aod(g0, "actuelle")
    if mode == "immediat":
        nouv = cible
    elif cible >= actuel:
        nouv = min(cible, max(actuel, a0 + 0.25 * (g - g0 + 1)))
    else:
        nouv = max(cible, a0 - 0.25 * (g - g0 + 1))
    if cible < actuel:
        nouv = min(actuel, max(nouv, debut - g))
    return nouv


# ------------------------------------------------------------------------------------------------------------------
# 2. Données
# ------------------------------------------------------------------------------------------------------------------
def _js(nom):
    return pd.Series(jsonstat_dict(json.loads((RACINE / "data" / "raw" / nom).read_text())))


def population():
    """Population au 1er janvier par âge (0-105) et sexe, 1962-2070 (Insee : estimations puis projection centrale)."""
    d = ip.charger("00_central")
    return {"F": d["popF"], "M": d["popH"]}


def activite_observee():
    a = _js("eurostat_lfsa_argan_FR_long.json")
    e = _js("eurostat_lfsa_ergan_FR_long.json")
    out = []
    for (s, g, t), v in a.items():
        a0, a1 = int(g[1:3]), int(g[4:6])
        out.append(dict(sexe=s, a0=a0, a1=a1, annee=int(t), activite=v / 100, emploi=e.get((s, g, t), np.nan) / 100))
    return pd.DataFrame(out)


def pensions_observees():
    e = _js("eurostat_spr_exp_pens_FR.json").xs("TOTAL", level=1).unstack(0)
    b = _js("eurostat_spr_pns_ben_FR.json").xs(("TOTAL", "OLD_TOT", "T"), level=(0, 1, 2))
    d = pd.DataFrame({"masse_droit_direct": e["OLD"], "masse_reversion": e["SRV"]})
    d.index = d.index.astype(int)
    b.index = b.index.astype(int)
    d["retraites"] = b
    return d


# ------------------------------------------------------------------------------------------------------------------
# 3. Activité des seniors
# ------------------------------------------------------------------------------------------------------------------
def h(d, e, s, k):
    d = np.asarray(d, dtype=float)
    rampe = np.clip((d + L_RAMPE) / L_RAMPE, 0, 1)
    return np.where(d < 0, 1 - e * rampe, s * np.exp(-k * np.maximum(d, 0)) * (1 - e))


T_GEL_TENDANCE = 2025   # la tendance de baisse des sorties précoces est arrêtée après la dernière année observée


def sorties_precoces(theta, t):
    e0, e1 = theta[0], theta[1]
    return float(np.clip(e0 + e1 * (min(t, T_GEL_TENDANCE) - 2010), 0, 0.95))


def regle_en_vigueur(regle: str, t: int) -> str:
    """Une réforme "cible@debut" n'agit sur les comportements et les départs qu'à partir de l'année `debut`."""
    base = decomposer(regle)[0]
    if "@" in base and t < int(base.split("@", 1)[1].split(":")[0]):
        return "actuelle"
    return regle


def pivots(g: int, regle, beta: float, sx: str):
    """Âges pivots du profil d'activité de la génération g : (législation actuelle, groupe général de la règle,
    groupe particulier nouveau, groupe particulier en législation actuelle, part du groupe particulier).
    pivot = β · AOD + (1 − β) · 62 + ε_sexe · Δdurée requise (années)."""
    base, dspec, grp = decomposer(regle)
    act = beta * aod(g, "actuelle") + (1 - beta) * 62.0
    dD = 0.0
    if dspec:
        dD = ELASTICITE_DUREE[sx] * (duree_requise(g, dspec) - duree_requise(g, "actuelle")) / 4.0
    reg = beta * aod(g, base) + (1 - beta) * 62.0 + dD
    if grp is None:
        return act, reg, None, None, 0.0
    a, p_ = grp
    if a == "ref":
        return act, reg, act, act, p_
    # carrières longues : âge de départ du groupe en législation actuelle ≈ max(60, AOD − 2) [H] (bornes de 2023 :
    # 58, 60, 62 et 63 ans selon l'âge de début ; « 60 ans et 6 mois » pour 1964 commençant avant 20 ans)
    cl_act = beta * max(60.0, aod(g, "actuelle") - 2.0) + (1 - beta) * 62.0
    cl_new = beta * float(a) + (1 - beta) * 62.0 + dD
    return act, reg, cl_new, cl_act, p_


def melange(fn, x, g, regle, beta, sx):
    """Combine une fonction du décalage d = x + 0,5 − pivot entre le groupe général et le groupe particulier, en
    écart à la législation actuelle (la référence estimée reste exactement reproduite) :
    fn(d_reg) + p [fn(d_grp) − fn(d_reg)] − p [fn(d_grp_act) − fn(d_act)]."""
    act, reg, gn, ga, p_ = pivots(g, regle, beta, sx)
    v = fn(x + 0.5 - reg)
    if p_:
        v = v + p_ * (fn(x + 0.5 - gn) - fn(x + 0.5 - reg)) - p_ * (fn(x + 0.5 - ga) - fn(x + 0.5 - act))
    return v


def facteur_pension(g: int, regle, sx: str) -> float:
    """Effet de la durée requise sur le niveau de pension de la génération g [H] : la fraction (1 − ε) de l'année de
    durée supplémentaire qui n'est pas compensée par un report subit la proratisation (1/durée) et la décote (5 %
    par an) sur la part de base de la pension ; symétrique pour une baisse de durée."""
    _, dspec, _ = decomposer(regle)
    if not dspec:
        return 1.0
    dD = (duree_requise(g, dspec) - duree_requise(g, "actuelle")) / 4.0
    if dD == 0:
        return 1.0
    manque = dD * (1 - ELASTICITE_DUREE[sx])
    return float(1.0 - PART_PENSION_BASE * manque * (4.0 / duree_requise(g, "actuelle") + DECOTE_PAR_AN))


def taux_age(x, t, A, theta, regle="actuelle", sx="M"):
    """beta = theta[4] : part du profil d'activité qui se décale avec l'AOD (le reste reste attaché à l'âge 62 ans).
    Les règles complètes (durée requise, groupes de départ anticipé) passent par `melange` ; sans option, calcul
    identique à la version 0.1."""
    regle = regle_en_vigueur(regle, t)
    _, _, s, k = theta[:4]
    beta = theta[4] if len(theta) > 4 else 1.0
    e = sorties_precoces(theta, t)
    g = t - np.asarray(x) - 1
    if "|" in str(regle):
        xs, gs = np.atleast_1d(np.asarray(x, dtype=float)), np.atleast_1d(g)
        v = np.array([melange(lambda d: float(h(d, e, s, k)), float(xx), int(gg), regle, beta, sx)
                      for xx, gg in zip(xs, gs)])
        return A * v
    aods = np.array([aod(int(gg), regle) for gg in np.atleast_1d(g)])
    d = np.asarray(x) + 0.5 - (beta * aods + (1 - beta) * 62.0)
    return A * h(d, e, s, k)


class ActiviteSeniors:
    def __init__(self, fin_estimation=2019):
        self.pop = population()
        self.obs = activite_observee()
        self.fin = fin_estimation
        self.theta = {}
        for sx in ("F", "M"):
            self.theta[sx] = self._estimer(sx)

    def A(self, sx, t):
        o = self.obs[(self.obs.sexe == sx) & (self.obs.a0 == 50)].set_index("annee").activite
        return float(o.get(t, o.iloc[-1]))

    def tranche(self, sx, t, a0, a1, theta=None, regle="actuelle"):
        theta = self.theta[sx] if theta is None else theta
        ages = np.arange(a0, a1 + 1)
        p = self.pop[sx][t].reindex(ages).to_numpy()
        r = taux_age(ages, t, self.A(sx, t), theta, regle, sx)
        return float((p * r).sum() / p.sum())

    def _estimer(self, sx):
        o = self.obs[(self.obs.sexe == sx) & (self.obs.annee <= self.fin) & self.obs.a0.isin([a for a, _ in TRANCHES])]

        def resid(th):
            return np.array([self.tranche(sx, r.annee, r.a0, r.a1, th) - r.activite for r in o.itertuples()])
        sol = least_squares(resid, x0=[0.3, -0.01, 0.4, 0.3, 0.8], bounds=([0, -0.1, 0, 0, 0], [1, 0.1, 1.5, 3, 1.5]))
        self.__dict__.setdefault("diag", {})[sx] = dict(rmse=float(np.sqrt(np.mean(sol.fun ** 2))), n=len(o))
        return sol.x

    def population_active(self, t, regle="actuelle", ages=range(15, 75)):
        """Population active 15-74 ans (personnes) : taux observés (ou derniers observés) avant 55 ans, modèle au-delà."""
        tot = 0.0
        for sx in ("F", "M"):
            for a0 in range(15, 75, 5):
                a1 = a0 + 4
                pop = self.pop[sx][t].reindex(range(a0, a1 + 1)).to_numpy()
                if a0 >= 55:
                    r = taux_age(np.arange(a0, a1 + 1), t, self.A(sx, t), self.theta[sx], regle, sx)
                else:
                    o = self.obs[(self.obs.sexe == sx) & (self.obs.a0 == a0)].set_index("annee").activite
                    r = float(o.get(t, o.iloc[-1]))
                tot += float((pop * r).sum())
        return tot

    def emploi_seniors_supplementaire(self, t, regle, regle_ref="actuelle", part_emploi=None):
        """Actifs supplémentaires 55-74 ans par rapport à la règle de référence, et part qui occupe un emploi."""
        d = self.population_active(t, regle) - self.population_active(t, regle_ref)
        k = self.part_emploi if part_emploi is None else part_emploi
        return d, d * k

    def estimer_part_emploi(self):
        """Part des actifs supplémentaires de 60-64 ans qui sont en emploi : Δ taux d'emploi / Δ taux d'activité des
        60-64 ans entre 2010 et 2019 (relèvement de l'AOD de 60 à 62 ans), moyenne des deux sexes."""
        o = self.obs
        v = []
        for sx in ("F", "M"):
            x = o[(o.sexe == sx) & (o.a0 == 60)].set_index("annee")
            v.append((x.emploi[2019] - x.emploi[2010]) / (x.activite[2019] - x.activite[2010]))
        self.part_emploi = float(np.mean(v))
        return self.part_emploi


# ------------------------------------------------------------------------------------------------------------------
# 4. Retraités et pensions
# ------------------------------------------------------------------------------------------------------------------
class Pensions:
    """Masse des pensions de droit direct par génération (voir l'en-tête)."""

    def __init__(self, act: ActiviteSeniors, annee_calage=2015):
        self.act = act
        self.pop = act.pop
        self.obs = pensions_observees()
        m = S.macro()
        p = S.panel_branches()
        g = p.groupby("annee")[["wb", "ns"]].sum()
        w = (g.wb / g.ns).loc[1995:2024]
        pc = m.p_c.loc[1980:2025]
        # salaire moyen avant 1995 : croissance réelle de 1 %/an et prix à la consommation (avant 1980 : +3 %/an nominal)
        sal = {}
        for t in range(1940, 2025):
            if t >= 1995:
                sal[t] = float(w[t])
        for t in range(1994, 1939, -1):
            infl = (pc[t + 1] / pc[t]) if (t >= 1980 and t + 1 in pc.index) else 1.03
            sal[t] = sal[t + 1] / (1.01 * infl)
        self.salaire = pd.Series(sal)
        # indice des prix à la consommation hors tabac (Insee, base 2015, moyenne annuelle ; règle légale de
        # revalorisation des pensions) ; avant 1990 : prix de la consommation des comptes nationaux, raccordés
        ipc = S.bdm("001763852")
        ipc = ipc.groupby(ipc.index.str[:4]).mean()
        ipc.index = ipc.index.astype(int)
        ipc = ipc[ipc.index <= 2025]
        av = pc.loc[:1989] * ipc[1990] / pc[1990]
        self.prix = pd.concat([av, ipc]).sort_index()
        self.annee_calage = annee_calage
        self.nu, self.pi = 1.0, 0.95
        self._caler()

    def _prix(self, t):
        if t in self.prix.index:
            return float(self.prix[t])
        if t < self.prix.index.min():
            return float(self.prix.iloc[0]) / 1.03 ** (self.prix.index.min() - t)
        return float(self.prix.iloc[-1]) * 1.017 ** (t - self.prix.index.max())

    def _sal(self, t):
        if t in self.salaire.index:
            return float(self.salaire[t])
        return float(self.salaire.iloc[-1]) * 1.027 ** (t - self.salaire.index.max())

    def _salaire_reference(self, tl, salaires=None, prix=None):
        """Salaire de référence à la liquidation : moyenne des 25 dernières années de salaire moyen, revalorisées sur
        les prix jusqu'à l'année de liquidation (règle des 25 meilleures années du régime général, approchée)."""
        cle = (tl, id(salaires), id(prix))
        cache = self.__dict__.setdefault("_cache_sr", {})
        if cle not in cache:
            sw = (lambda a: salaires.get(a, self._sal(a))) if salaires is not None else self._sal
            pp = (lambda a: prix.get(a, self._prix(a))) if prix is not None else self._prix
            cache[cle] = float(np.mean([sw(a) * pp(tl) / pp(a) for a in range(tl - 24, tl + 1)]))
        return cache[cle]

    def part_retraitee(self, x, t, sx, regle="actuelle"):
        """Part de la population retraitée (droit direct) : π − activité non encore partie, rampe avant l'AOD."""
        regle = regle_en_vigueur(regle, t)
        _, _, s, k, beta = self.act.theta[sx]
        e = sorties_precoces(self.act.theta[sx], t)
        g = t - x - 1
        if "|" in str(regle):
            return float(melange(lambda d: self._part_d(d, e, s, k), x, g, regle, beta, sx))
        d = x + 0.5 - (beta * aod(g, regle) + (1 - beta) * 62.0)
        return self._part_d(d, e, s, k)

    def _part_d(self, d, e, s, k):
        if d < -L_RAMPE:
            return 0.0
        if d < 0:
            return self.pi * e * min(1, (d + L_RAMPE) / L_RAMPE) * 0.5   # moitié des sorties précoces sont des retraites anticipées
        return self.pi * (1 - (1 - e) * s * np.exp(-k * d) * 0.6)         # 40 % des actifs après l'AOD cumulent emploi et retraite

    def masse(self, t, regle="actuelle", salaires=None, prix=None, revalo=None):
        """Retraités (personnes) et masse des pensions de droit direct (M€ courants) en t.
        salaires, prix : trajectoires futures (séries) ; revalo : écart de revalorisation à l'inflation (série, en %)."""
        nb, masse = 0.0, 0.0
        regle = regle_en_vigueur(regle, t)
        for sx in ("F", "M"):
            for x in range(50, 106):
                pop = float(self.pop[sx][t].get(x, 0.0))
                r = self.part_retraitee(x, t, sx, regle)
                if r <= 0 or pop <= 0:
                    continue
                g = t - x - 1
                tl = int(round(g + aod(g, regle)))
                tl = min(tl, t)
                sal = self._salaire_reference(tl, salaires, prix)
                # revalorisation au 1er janvier sur l'inflation de l'année précédente : indice des prix décalé d'un an
                pp = (lambda a: prix.get(a, self._prix(a))) if prix is not None else self._prix
                pa = pp(t - 1) / pp(tl - 1)
                if revalo is not None:
                    pa *= float(np.prod([1 + revalo.get(a, 0.0) / 100 for a in range(tl + 1, t + 1)]))
                pens = self.nu * sal * pa * (facteur_pension(g, regle, sx) if "|" in str(regle) else 1.0)
                nb += pop * r
                masse += pop * r * pens
        return nb, masse

    def _caler(self):
        t = self.annee_calage
        nb, _ = self.masse(t)
        self.pi *= float(self.obs.retraites[t]) / nb
        nb, m = self.masse(t)
        self.nu *= float(self.obs.masse_droit_direct[t]) * 1e6 / m


# ------------------------------------------------------------------------------------------------------------------
# 5. Liens avec le modèle bouclé M8
# ------------------------------------------------------------------------------------------------------------------
def trajectoires_m8(pens, resultat, pc_base, B):
    """Prix (indice des prix hors tabac prolongé par l'évolution des prix à la consommation simulés) et salaires moyens
    simulés par M8 (même définition que l'historique de M9 : rémunérations / salariés des branches marchandes)."""
    prix = {t: pens._prix(t) for t in range(1940, B + 1)}
    sal = {t: pens._sal(t) for t in range(1940, B + 1)}
    for t in resultat.index:
        prix[t] = pens._prix(B) * resultat.pc[t] / pc_base
        sal[t] = float(resultat.salaire[t])
    return prix, sal


def liens_m8(mod, annees, regle="actuelle", regle_ref="actuelle", act=None, pens=None, part_emploi=None, central=None):
    """Séries à passer à `m8_modele.Exogenes` pour une règle de retraite :
    - population_active (milliers) : niveau observé de l'année de base × évolution de la population active 15-74 ans
      de M9 (démographie Insee centrale, taux d'activité par âge, règle de retraite) ;
    - emploi_additionnel (milliers) : part `part_emploi` (estimée sur 2010-2019) des actifs seniors supplémentaires par
      rapport à la règle de référence, maintenus en emploi (hors équations de branche) ;
    - ajust_prestations (M€) : écart de masse des pensions de droit direct par rapport à la règle de référence, calculé
      avec les prix et salaires du compte central de M8 (`central`) s'il est fourni, sinon avec des tendances
      conventionnelles (+1,7 % et +2,7 % par an)."""
    import m8_modele as M8
    act = act or ActiviteSeniors()
    pens = pens or Pensions(act)
    k = act.estimer_part_emploi() if part_emploi is None else part_emploi
    B = mod.B
    obs = M8.exogenes_observes(mod, [B]).population_active
    pa_B = act.population_active(B, "actuelle")
    pa, emp, dp = {}, {}, {}
    kw = {}
    if central is not None:
        prix, sal = trajectoires_m8(pens, central, mod.macro.p_c[B], B)
        kw = {"prix": prix, "salaires": sal}
    for t in range(B - 3, max(annees) + 1):
        if t <= B:
            pa[t] = float(obs[t])
            continue
        pa_r = act.population_active(t, regle)
        pa[t] = float(obs[B]) * pa_r / pa_B
        d = pa_r - act.population_active(t, regle_ref)
        emp[t] = k * d / 1e3
        dp[t] = COEF_PENSION_MARGINALE * (pens.masse(t, regle, **kw)[1] - pens.masse(t, regle_ref, **kw)[1]) / 1e6
    return dict(population_active=pd.Series(pa), emploi_additionnel=pd.Series(emp), ajust_prestations=pd.Series(dp))


# ------------------------------------------------------------------------------------------------------------------
# 6. Effets générationnels d'une règle (finalisation 2026-11)
# ------------------------------------------------------------------------------------------------------------------
def effets_generationnels(regle, act: "ActiviteSeniors | None" = None, generations=range(1960, 1996, 5)) -> pd.DataFrame:
    """Par génération et par sexe : âge d'ouverture des droits, durée requise, âge pivot du profil d'activité
    (législation actuelle et règle), écart de durée de retraite attendue (≈ −écart de pivot, espérance de vie
    inchangée) et facteur de niveau de pension dû à la durée requise. Lecture : effets moyens par génération ; ce
    ne sont pas des trajectoires individuelles."""
    act = act or ActiviteSeniors()
    base, dspec, grp = decomposer(regle)
    rows = []
    for g in generations:
        for sx in ("F", "M"):
            beta = act.theta[sx][4]
            a, r, gn, ga, p_ = pivots(g, regle, beta, sx)
            piv = (1 - p_) * r + p_ * gn if p_ else r
            piv_act = (1 - p_) * a + p_ * ga if p_ else a
            rows.append({"generation": g, "sexe": sx, "aod_actuelle": aod(g, "actuelle"), "aod_regle": aod(g, base),
                         "duree_actuelle_trim": duree_requise(g, "actuelle"),
                         "duree_regle_trim": duree_requise(g, dspec) if dspec else duree_requise(g, "actuelle"),
                         "pivot_actuel": piv_act, "pivot_regle": piv, "ecart_pivot_ans": piv - piv_act,
                         "ecart_duree_retraite_ans": -(piv - piv_act),
                         "facteur_pension": facteur_pension(g, regle, sx) if dspec else 1.0})
    return pd.DataFrame(rows)
