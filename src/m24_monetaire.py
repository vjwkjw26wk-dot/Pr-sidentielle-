"""M24 — Politique monétaire et conditions financières (phase 5, lot 5.2).

Réutilise M11 (règle de la BCE estimée 1999-2019 ; transmission au taux long) et complète :
  1. règle de la BCE appliquée dans la boucle annuelle (forme retardée : information de l'année précédente), en écart à
     une trajectoire exogène de référence du taux directeur (le taux neutre r* n'est pas identifiable sur 1999-2019) ;
  2. transmission aux taux de financement : ménages (crédits à l'habitat, coût composite) et sociétés non financières
     (coût composite des crédits nouveaux), MIR de la BCE 2003-2025, ajustement partiel estimé ; État : cohortes M17 ;
     stock de dette des sociétés : M21 ;
  3. taux souverain : OAT = Bund + écart ; Bund = taux long de référence + transmission du taux directeur (estimée, ou
     anticipations « rationnelles » : moyenne des écarts attendus sur 10 ans sous la règle) ; écart OAT-Bund = écart de
     référence + prime liée à la dette et au déficit (panel de la zone euro, effets fixes pays et années) ;
  4. charges d'intérêts : inchangées dans leur principe (M17 pour l'État, M21 pour les sociétés) ; elles reçoivent les
     nouveaux taux ;
  5. chocs exogènes paramétrables : taux directeur, Bund, écart souverain, inflation et activité du reste de la zone.

Tout est en écart à la trajectoire de référence à taux exogènes (même environnement) : en l'absence de choc et
d'écart d'inflation ou d'activité, le régime « bce » reproduit exactement le régime « exogene ».
Statuts : [E] estimé ici ou dans M11 ; [C] calibré (part de la France, loi d'Okun du modèle) ; [S] hypothèse de scénario.
"""
from __future__ import annotations

import io
import json
import pathlib
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import statsmodels.api as sm

RACINE = pathlib.Path(__file__).resolve().parents[1]
PAYS_PANEL = ["FR", "IT", "ES", "BE", "NL", "AT", "PT", "IE", "FI"]
POIDS_FR = 0.20          # [C] part de la France dans le PIB et l'IPCH de la zone euro (comme M11)


# --------------------------------------------------------------------------------------------------------- données
def _eurostat(url, nom):
    from telechargement import telecharger, jsonstat_dict
    return pd.Series(jsonstat_dict(json.loads(telecharger(url, nom).read_text())))


def _mir(cle, nom):
    from telechargement import telecharger
    f = telecharger(f"https://data-api.ecb.europa.eu/service/data/MIR/{cle}?format=csvdata&startPeriod=2003-01", nom)
    d = pd.read_csv(io.StringIO(f.read_text()))
    s = pd.Series(d.OBS_VALUE.values, index=pd.to_datetime(d.TIME_PERIOD))
    return s.groupby(s.index.year).mean()


def donnees() -> pd.DataFrame:
    import m11_europe as M11
    d = M11.series()
    base = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
    y = _eurostat(base + "irt_lt_mcby_a?format=JSON&lang=en&" + "&".join(f"geo={g}" for g in ["DE"] + PAYS_PANEL),
                  "eurostat_irt_lt_mcby_a_panel_ZE.json")
    lab = lambda g: pd.Series({int(k[-1]): float(v) for k, v in y.items() if k[-2] == g})  # noqa: E731
    d = d.reindex(range(1995, 2027))
    d["bund"] = lab("DE").reindex(d.index)
    d["oat"] = lab("FR").reindex(d.index)
    d["ecart_oat_bund"] = d.oat - d.bund
    d["credit_habitat"] = _mir("M.FR.B.A2C.AM.R.A.2250.EUR.N", "ecb_mir_fr_menages_habitat.csv").reindex(d.index)
    d["credit_snf"] = _mir("M.FR.B.A2I.AM.R.A.2240.EUR.N", "ecb_mir_fr_snf_composite.csv").reindex(d.index)
    return d


def panel_souverain() -> pd.DataFrame:
    base = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
    y = _eurostat(base + "irt_lt_mcby_a?format=JSON&lang=en&" + "&".join(f"geo={g}" for g in ["DE"] + PAYS_PANEL),
                  "eurostat_irt_lt_mcby_a_panel_ZE.json")
    g = _eurostat(base + "gov_10dd_edpt1?format=JSON&lang=en&unit=PC_GDP&sector=S13&na_item=GD&na_item=B9&"
                  + "&".join(f"geo={c}" for c in ["DE"] + PAYS_PANEL), "eurostat_gov_10dd_edpt1_panel_ZE.json")
    Y = {(k[-2], int(k[-1])): float(v) for k, v in y.items()}
    Gd = {(k[-3], k[-2], int(k[-1])): float(v) for k, v in g.items()}
    rows = []
    for c in PAYS_PANEL:
        for t in range(2000, 2026):
            yt, yd = Y.get((c, t)), Y.get(("DE", t))
            rows.append({"pays": c, "annee": t, "ecart": (yt - yd) if yt is not None and yd is not None else np.nan,
                         "dette_1": Gd.get(("GD", c, t - 1), np.nan), "solde_1": Gd.get(("B9", c, t - 1), np.nan)})
    return pd.DataFrame(rows).dropna()


# -------------------------------------------------------------------------------------------------------- estimation
def _ols(y, X, groupes=None):
    m = sm.OLS(y, sm.add_constant(X), missing="drop")
    if groupes is not None:
        return m.fit(cov_type="cluster", cov_kwds={"groups": groupes})
    return m.fit(cov_type="HAC", cov_kwds={"maxlags": 1})


_EST = {}


def estimer() -> dict:
    if _EST:
        return _EST
    import m11_europe as M11
    d = donnees()
    out = {"donnees": d}
    eu = M11.Europe()
    out["taylor_contemporaine"] = eu.taylor
    # règle sous forme retardée (information disponible au début de l'année), même échantillon 1999-2019
    ok = (d.index >= 1999) & (d.index <= 2019)
    X = pd.DataFrame({"i_1": d.taux_court.shift(1), "pi_1": d.inflation_ze.shift(1), "ecart_1": d.ecart_ze.shift(1)})
    out["taylor_retardee"] = _ols(d.taux_court[ok], X[ok])
    # Bund : Δ taux à 10 ans allemand sur Δ Euribor (1999-2024)
    ok2 = (d.index >= 1999) & (d.index <= 2024)
    out["bund"] = _ols(d.bund.diff()[ok2], d.taux_court.diff()[ok2].rename("di"))
    # taux des crédits nouveaux : ajustement partiel Δr = a + βc i + βl oat − μ r₋₁ (2004-2025, hors 2020-2021)
    an = [t for t in range(2004, 2026) if t not in (2020, 2021)]
    for k in ("credit_habitat", "credit_snf"):
        Xr = pd.DataFrame({"i": d.taux_court, "oat": d.oat, "r_1": d[k].shift(1)})
        out[k] = _ols(d[k].diff().loc[an], Xr.loc[an])
    # prime souveraine : panel de 9 pays de la zone euro (écart au Bund), effets fixes pays et années, 2000-2025
    p = panel_souverain()
    Xp = pd.get_dummies(p[["pays", "annee"]].astype(str), drop_first=True).astype(float)
    Xp["dette_1"], Xp["solde_1"] = p.dette_1, p.solde_1
    out["prime_panel"] = _ols(p.ecart, Xp, groupes=p.pays)
    # robustesse : hors crise de la zone euro (2010-2013) ; France seule
    q = p[~p.annee.between(2010, 2013)]
    Xq = pd.get_dummies(q[["pays", "annee"]].astype(str), drop_first=True).astype(float)
    Xq["dette_1"], Xq["solde_1"] = q.dette_1, q.solde_1
    out["prime_panel_hors_crise"] = _ols(q.ecart, Xq, groupes=q.pays)
    f = p[p.pays == "FR"]
    out["prime_france"] = _ols(f.ecart.values, f[["dette_1", "solde_1"]].reset_index(drop=True))
    out["panel"] = p
    _EST.update(out)
    return out


def rapport() -> str:
    e = estimer()
    L = []
    for k in ("taylor_contemporaine", "taylor_retardee", "bund", "credit_habitat", "credit_snf"):
        m = e[k]
        L.append(f"[{k}] n={int(m.nobs)} R²={m.rsquared:.2f} " + " ; ".join(f"{n} {m.params[n]:+.3f} ({m.bse[n]:.3f})" for n in m.params.index))
    for k in ("prime_panel", "prime_panel_hors_crise", "prime_france"):
        m = e[k]
        L.append(f"[{k}] n={int(m.nobs)} : dette_1 {m.params['dette_1']:+.4f} ({m.bse['dette_1']:.4f}) ; solde_1 {m.params['solde_1']:+.4f} ({m.bse['solde_1']:.4f})")
    return "\n".join(L)


def parametres() -> dict:
    """Paramètres retenus et leur statut."""
    e = estimer()
    t = e["taylor_retardee"].params
    pc = e["taylor_contemporaine"].params
    # la forme retardée est retenue si ses réponses sont du bon signe ; sinon : coefficients de la forme contemporaine
    # appliqués aux écarts de l'année précédente (statut [E*] : estimés sous une autre datation)
    retard = t["pi_1"] > 0 and t["ecart_1"] > 0
    rho, b, c = (t["i_1"], t["pi_1"], t["ecart_1"]) if retard else (pc["i_1"], pc["pi"], pc["ecart"])
    out = {"bce_lissage": float(rho), "bce_inflation": float(b), "bce_activite": float(c),
           "bce_forme": "retardée [E]" if retard else "contemporaine appliquée à t − 1 [E*]",
           "bund_transmission": float(e["bund"].params["di"])}
    for k, nom in (("credit_habitat", "menages"), ("credit_snf", "entreprises")):
        p = e[k].params
        mu = -float(p["r_1"])
        out[f"{nom}_vitesse"] = mu
        out[f"{nom}_court"] = float(p["i"])           # impact de l'année (part de 1 − μ dans l'écart retardé)
        out[f"{nom}_long"] = float(p["oat"])
        out[f"{nom}_transmission_lt"] = float((p["i"] + p["oat"]) / mu)
    # prime souveraine : panel hors crise de la zone euro (2010-2013 exclues : risque de redénomination et contagion, que
    # des coefficients linéaires sur la dette et le solde ne décrivent pas). Dette : 1,3 pb par point (± 0,4), robuste
    # (0,7 à 1,3 pb selon l'échantillon) ; solde : non significatif hors crise (−1,5 pb ± 2,1), −11,8 pb avec la crise.
    pp = e["prime_panel_hors_crise"].params
    out["prime_dette"] = float(pp["dette_1"])         # points de taux par point de dette (% du PIB) [E]
    out["prime_solde"] = float(pp["solde_1"])         # points de taux par point de solde (négatif : déficit → prime) [E, fragile]
    out["prime_dette_avec_crise"] = float(e["prime_panel"].params["dette_1"])
    out["prime_solde_avec_crise"] = float(e["prime_panel"].params["solde_1"])
    return out


# --------------------------------------------------------------------------------------------------------- régime
@dataclass
class RegimeMonetaire:
    type: str = "exogene"                  # "exogene" | "bce"
    anticipations: str = "adaptatives"     # transmission au Bund : "adaptatives" (estimée) | "rationnelles" (règle)
    prime: str = "aucune"                  # "aucune" | "ecart_reference" (dette et solde relatifs à la référence) | "niveau"
    prime_dette: float | None = None       # None : estimée (panel) ; sinon hypothèse de scénario [S]
    prime_solde: float | None = None
    niveau_dette_seuil: float = 0.0        # mode "niveau" : prime sur la dette au-delà de ce seuil (% du PIB) [S]
    mesure_activite: str = "production"    # activité française vue par la BCE : "production" (écart du PIB à la référence,
    #                                        analogue de l'écart au filtre HP de la règle estimée) ou "chomage" (loi d'Okun,
    #                                        convention de M11 ; amplifie la réaction quand le chômage dévie durablement)
    taux_court_reference: str = "observe"  # trajectoire exogène de référence du taux directeur : "observe" (Euribor 3 mois,
    #                                        dernier mois) ou "derive" (taux long − écart 2018-2022, convention antérieure)
    chocs_directeur: dict = field(default_factory=dict)      # {année: points}
    chocs_bund: dict = field(default_factory=dict)
    chocs_ecart_souverain: dict = field(default_factory=dict)
    chocs_inflation_ze: dict = field(default_factory=dict)   # reste de la zone euro (points)
    chocs_activite_ze: dict = field(default_factory=dict)
    debut: int = 2027

    def __post_init__(self):
        assert self.type in ("exogene", "bce") and self.anticipations in ("adaptatives", "rationnelles")
        assert self.prime in ("aucune", "ecart_reference", "niveau") and self.taux_court_reference in ("observe", "derive")
        assert self.mesure_activite in ("production", "chomage")


class AppliqueurMonetaire:
    """Au début de l'année t (informations ≤ t − 1) : taux directeur, Bund, écart souverain, OAT, taux des crédits aux
    ménages et aux sociétés. Écrit ex.taux_court, ex.taux_long, ex.taux_prive_menages, ex.taux_prive_entreprises."""

    def __init__(self, reg: RegimeMonetaire, mod, ex_ref, ref_traj: pd.DataFrame | None):
        self.r, self.mod, self.ref = reg, mod, ref_traj
        self.p = parametres()
        self.oat0 = ex_ref.taux_long.copy().astype(float)
        self.tc0 = self._taux_court_reference(ex_ref)
        self.d = {}            # écarts : i, bund, ecart, oat, menages, entreprises
        self.journal = {}
        import m8_modele as M8
        self.okun = M8.OKUN

    def _taux_court_reference(self, ex):
        idx = sorted(ex.taux_long.index)
        if self.r.taux_court_reference == "derive":
            return ex.taux_court.copy() if ex.taux_court is not None else None
        import m23_regimes as G
        moy26, (_m, dernier) = G._taux_court_observe()
        import m17_dette as D
        _lt, st = D.taux_observes()
        return pd.Series({t: (float(st[t]) if t in st.index else (moy26 if t == 2026 else dernier)) for t in idx})

    def _ecarts_france(self, res, t):
        """Écarts de l'année t − 1 à la référence : inflation (pt), activité par la loi d'Okun (pt), dette, solde."""
        if self.ref is None or not res:
            return 0.0, 0.0, 0.0, 0.0
        h = pd.DataFrame(res).set_index("annee")
        a = t - 1
        if a not in h.index or a - 1 not in h.index or a not in self.ref.index:
            return 0.0, 0.0, 0.0, 0.0
        dpi = 100 * (np.log(h.pc[a] / h.pc[a - 1]) - np.log(self.ref.pc[a] / self.ref.pc[a - 1]))
        if self.r.mesure_activite == "chomage":
            dgap = -self.okun * (h.chomage[a] - self.ref.chomage[a])
        else:
            dgap = 100 * np.log(h.pib[a] / self.ref.pib[a])
        return dpi, dgap, float(h.dette_pib[a] - self.ref.dette_pib[a]), float(h.solde_pib[a] - self.ref.solde_pib[a])

    def __call__(self, mod, ex, t, res):
        r, p = self.r, self.p
        if t < r.debut:          # années calées (≤ 2026) : taux de l'environnement inchangés
            return
        prev = self.d.get(t - 1, {"i": 0.0, "bund": 0.0, "ecart": 0.0, "menages": 0.0, "entreprises": 0.0, "oat": 0.0})
        di = 0.0
        dpi_fr, dgap_fr, ddette, dsolde = self._ecarts_france(res, t) if t >= r.debut else (0.0, 0.0, 0.0, 0.0)
        dpi_ze = POIDS_FR * dpi_fr + (1 - POIDS_FR) * float(r.chocs_inflation_ze.get(t - 1, 0.0))
        dgap_ze = POIDS_FR * dgap_fr + (1 - POIDS_FR) * float(r.chocs_activite_ze.get(t - 1, 0.0))
        if r.type == "bce" and t >= r.debut:
            di = p["bce_lissage"] * prev["i"] + p["bce_inflation"] * dpi_ze + p["bce_activite"] * dgap_ze
        di += float(r.chocs_directeur.get(t, 0.0))
        # Bund
        if r.anticipations == "rationnelles":
            rho = p["bce_lissage"]
            dbund = di * (1 - rho ** 10) / (10 * (1 - rho))
        else:
            dbund = prev["bund"] + p["bund_transmission"] * (di - prev["i"])
        dbund_tot = dbund + float(r.chocs_bund.get(t, 0.0))
        # écart souverain
        th_d = p["prime_dette"] if r.prime_dette is None else r.prime_dette
        th_s = p["prime_solde"] if r.prime_solde is None else r.prime_solde
        decart = float(r.chocs_ecart_souverain.get(t, 0.0))
        if r.prime == "ecart_reference" and t >= r.debut:
            decart += th_d * ddette + th_s * dsolde
        elif r.prime == "niveau" and t >= r.debut and res:
            h = pd.DataFrame(res).set_index("annee")
            d1 = float(h.dette_pib.get(t - 1, np.nan)); s1 = float(h.solde_pib.get(t - 1, np.nan))
            d0 = float(h.dette_pib.get(r.debut - 1, d1)); s0 = float(h.solde_pib.get(r.debut - 1, s1))
            decart += th_d * (max(d1, r.niveau_dette_seuil) - max(d0, r.niveau_dette_seuil)) + th_s * (s1 - s0)
        doat = dbund_tot + decart
        # crédits nouveaux : Δr = βc Δi + βl Δoat − μ r₋₁ (en écart, ajustement partiel estimé)
        dm = (1 - p["menages_vitesse"]) * prev["menages"] + p["menages_court"] * di + p["menages_long"] * doat
        de = (1 - p["entreprises_vitesse"]) * prev["entreprises"] + p["entreprises_court"] * di + p["entreprises_long"] * doat
        self.d[t] = {"i": di, "bund": dbund, "ecart": decart, "oat": doat, "menages": dm, "entreprises": de}
        # écriture des taux de l'année t
        tc = ex.taux_court.copy().astype(float) if ex.taux_court is not None else pd.Series(dtype=float)
        if self.tc0 is not None:
            tc[t] = float(self.tc0.get(t, self.tc0.iloc[-1])) + di
            ex.taux_court = tc.sort_index()
        tl = ex.taux_long.copy().astype(float)
        tl[t] = float(self.oat0.get(t, self.oat0.iloc[-1])) + doat
        ex.taux_long = tl
        base_priv = float(self.oat0.get(t, self.oat0.iloc[-1]))          # niveau de calibration des équations privées
        for nom, val in (("taux_prive_menages", dm), ("taux_prive_entreprises", de)):
            s = getattr(ex, nom)
            s = s.copy() if s is not None else pd.Series(dtype=float)
            s[t] = base_priv + val
            setattr(ex, nom, s.sort_index())
        self.journal[t] = {"taux_directeur": float(tc.get(t, np.nan)) if self.tc0 is not None else np.nan, "ecart_directeur": di,
                           "ecart_bund": dbund_tot, "ecart_souverain": decart, "oat": float(tl[t]), "ecart_oat": doat,
                           "ecart_credit_menages": dm, "ecart_credit_entreprises": de,
                           "ecart_inflation_ze": dpi_ze, "ecart_activite_ze": dgap_ze}
