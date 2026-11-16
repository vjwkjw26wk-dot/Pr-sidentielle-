"""M1 — Démographie par cohortes (version 2, méthode des projections Insee 2026).

Convention de Lexis : population au 1er janvier par âge révolu a (0..AMAX, AMAX = 120) ;
quotients, fécondité et solde migratoire indicés par l'« âge atteint dans l'année » A
(génération g = t − A), comme dans les fichiers de l'Insee.

Équations, pour l'année t → t+1 et chaque sexe s :
 (1) P[s,A,t+1] = P[s,A−1,t]·(1 − q[s,A,t]) + SM[s,A,t]·(1 − q[s,A,t]/2) + AJ[s,A,t]      A = 1..AMAX
     (au dernier âge, le groupe AMAX accumule aussi les survivants de AMAX)
 (2) N[t]       = Σ_A f[A,t] · (PF[A−1,t] + PF[A,t+1]) / 2                                   A = 15..50
 (3) P[s,0,t+1] = N[t]·π_s·(1 − q[s,0,t]) + SM[s,0,t]·(1 − q[s,0,t]/2) + AJ[s,0,t]
 (4) D[s,A,t]   = P[s,A−1,t]·q[s,A,t] + SM[s,A,t]·q[s,A,t]/2   ;   D[s,0,t] = N[t]·π_s·q[s,0,t] + SM·q/2
 Identité : Ptot[t+1] − Ptot[t] = N[t] − Dtot[t] + SMtot[t] + AJtot[t]   (contrôlée à chaque pas)

(2) est implicite (PF[A,t+1] dépend de PF[A−1,t]) mais se calcule après (1) puisque les femmes de 15 à 50 ans
au 1er janvier t+1 ne dépendent pas des naissances de l'année t.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

AMAX = 120
AGES = np.arange(AMAX + 1)
PI_F = 100 / 205  # part des filles à la naissance (Insee : 105 garçons pour 100 filles)


@dataclass
class Hypotheses:
    """Hypothèses annuelles : DataFrames âges × années (âges atteints dans l'année)."""
    qF: pd.DataFrame
    qH: pd.DataFrame
    fec: pd.DataFrame          # taux de fécondité par âge (par femme), âges 15..50
    smF: pd.DataFrame          # solde migratoire par âge atteint
    smH: pd.DataFrame
    ajF: pd.DataFrame | None = None
    ajH: pd.DataFrame | None = None
    pi_f: float = PI_F


@dataclass
class Resultat:
    popF: pd.DataFrame
    popH: pd.DataFrame
    naissances: pd.Series
    decesF: pd.DataFrame
    decesH: pd.DataFrame
    ecart_identite: pd.Series = field(default_factory=pd.Series)

    @property
    def pop(self) -> pd.DataFrame:
        return self.popF + self.popH

    def total(self) -> pd.Series:
        return self.pop.sum()

    def groupe(self, a0: int, a1: int | None = None) -> pd.Series:
        a1 = AMAX if a1 is None else a1
        return self.pop.loc[a0:a1].sum()


def _col(df: pd.DataFrame | None, t: int, n: int = AMAX + 1) -> np.ndarray:
    if df is None or t not in df.columns:
        return np.zeros(n)
    v = df[t].reindex(range(n)).fillna(0.0).to_numpy()
    return v


def repartir_groupe_ouvert(p_ouvert: float, q: np.ndarray, a0: int = 105) -> np.ndarray:
    """Répartit l'effectif du groupe « a0 ans ou plus » sur a0..AMAX selon une survie stationnaire."""
    surv = np.ones(AMAX - a0 + 1)
    for i in range(1, len(surv)):
        surv[i] = surv[i - 1] * (1 - min(q[a0 + i], 1.0))
    return p_ouvert * surv / surv.sum()


def etendre_population(p: np.ndarray, q: np.ndarray, a0: int = 105) -> np.ndarray:
    """Population publiée 0..a0+ → vecteur 0..AMAX."""
    out = np.zeros(AMAX + 1)
    out[:a0] = p[:a0]
    out[a0:] = repartir_groupe_ouvert(p[a0], q, a0)
    return out


def projeter(pF0: np.ndarray, pH0: np.ndarray, t0: int, t1: int, h: Hypotheses) -> Resultat:
    """Projette du 1er janvier t0 au 1er janvier t1 ; pF0, pH0 : vecteurs 0..AMAX."""
    ans = list(range(t0, t1 + 1))
    PF = np.zeros((AMAX + 1, len(ans)))
    PH = np.zeros_like(PF)
    DF = np.zeros((AMAX + 1, len(ans) - 1))
    DH = np.zeros_like(DF)
    N = np.zeros(len(ans) - 1)
    ecart = np.zeros(len(ans) - 1)
    PF[:, 0], PH[:, 0] = pF0, pH0
    for i, t in enumerate(ans[:-1]):
        for P, D, q_df, sm_df, aj_df in ((PF, DF, h.qF, h.smF, h.ajF), (PH, DH, h.qH, h.smH, h.ajH)):
            q = np.clip(_col(q_df, t), 0, 1)
            sm, aj = _col(sm_df, t), _col(aj_df, t)
            prev = P[:, i]
            nouv = np.zeros(AMAX + 1)
            nouv[1:] = prev[:-1] * (1 - q[1:]) + sm[1:] * (1 - q[1:] / 2) + aj[1:]
            nouv[AMAX] += prev[AMAX] * (1 - q[AMAX])  # groupe terminal
            D[1:, i] = prev[:-1] * q[1:] + sm[1:] * q[1:] / 2
            D[AMAX, i] += prev[AMAX] * q[AMAX]
            P[:, i + 1] = nouv
        f = _col(h.fec, t)
        A = np.arange(15, 51)
        N[i] = float((f[A] * (PF[A - 1, i] + PF[A, i + 1]) / 2).sum())
        for P, D, q_df, sm_df, aj_df, part in ((PF, DF, h.qF, h.smF, h.ajF, h.pi_f), (PH, DH, h.qH, h.smH, h.ajH, 1 - h.pi_f)):
            q0 = min(_col(q_df, t)[0], 1)
            sm0, aj0 = _col(sm_df, t)[0], _col(aj_df, t)[0]
            P[0, i + 1] = N[i] * part * (1 - q0) + sm0 * (1 - q0 / 2) + aj0
            D[0, i] = N[i] * part * q0 + sm0 * q0 / 2
        flux = N[i] - DF[:, i].sum() - DH[:, i].sum() + (_col(h.smF, t) + _col(h.smH, t) + _col(h.ajF, t) + _col(h.ajH, t)).sum()
        ecart[i] = (PF[:, i + 1].sum() + PH[:, i + 1].sum()) - (PF[:, i].sum() + PH[:, i].sum()) - flux
        if abs(ecart[i]) > 1e-3:
            raise AssertionError(f"identité démographique violée en {t} : {ecart[i]}")
    df = lambda M, cols: pd.DataFrame(M, index=AGES, columns=cols)  # noqa: E731
    return Resultat(df(PF, ans), df(PH, ans), pd.Series(N, index=ans[:-1]), df(DF, ans[:-1]), df(DH, ans[:-1]),
                    pd.Series(ecart, index=ans[:-1]))


# ---------------------------------------------------------------------------
# Générateur de scénarios paramétriques (pour les politiques et variantes hors Insee)
# ---------------------------------------------------------------------------

class GenerateurScenarios:
    """Scénarios démographiques paramétriques construits sur les directions de variation de l'Insee.

    - Fécondité : calendrier par âge du central conservé, niveau remis à l'échelle de l'ICF visé.
    - Migrations : SM = SM_central + (S − S_central) · profil marginal, où le profil marginal est
      (SM_haut − SM_central) / (S_haut − S_central) ; l'Insee construit ses deux variantes
      exactement ainsi (écart haut − central = central − bas à toutes les années et tous les âges).
    - Mortalité : log q = log q_central + λ · (log q_variante − log q_central), variante = haute si λ > 0,
      basse si λ < 0 (|λ| = 1 reproduit la variante) ; λ est résolu pour une espérance de vie visée.
    """

    def __init__(self, central: Hypotheses, sm_haut: tuple, q_haute: tuple, q_basse: tuple):
        self.c = central
        dF, dH = sm_haut[0] - central.smF, sm_haut[1] - central.smH
        tot = float(dF[2030].sum() + dH[2030].sum())
        self.margF, self.margH = dF / tot, dH / tot
        self.q_h, self.q_b = q_haute, q_basse

    def sm_central_total(self, t: int) -> float:
        return float(self.c.smF[t].sum() + self.c.smH[t].sum())

    def construire(self, t0: int, t1: int, *, icf: dict | None = None, sm_total: dict | None = None,
                   lambda_ev: float = 0.0, ev_femmes_2070: float | None = None,
                   rythme_gains_mortalite: float | None = None, an_ref_mortalite: int = 2025,
                   mortalite_facteur: dict | None = None) -> Hypotheses:
        """rythme_gains_mortalite : alternative à λ ; multiplie la baisse des log-quotients du central
        depuis an_ref_mortalite (0 = mortalité figée, 1 = central, 2 = baisse deux fois plus rapide)."""
        ans = list(range(t0, t1 + 1))

        def serie(points: dict) -> pd.Series:
            s = pd.Series(points, dtype=float).sort_index()
            return s.reindex(sorted(set(ans) | set(s.index))).interpolate("index").ffill().bfill().reindex(ans)

        c = self.c
        fec = c.fec.copy()
        if icf:
            cible = serie(icf)
            for t in ans:
                if t in fec.columns and t >= min(icf):
                    fec[t] = fec[t] * cible[t] / fec[t].sum()
        smF, smH = c.smF.copy(), c.smH.copy()
        if sm_total:
            cible = serie(sm_total)
            for t in ans:
                if t in smF.columns and t >= min(sm_total):
                    delta = cible[t] - self.sm_central_total(t)
                    smF[t] = c.smF[t] + delta * self.margF[t]
                    smH[t] = c.smH[t] + delta * self.margH[t]
        if ev_femmes_2070 is not None:
            from scipy.optimize import brentq
            f = lambda L: esperance_de_vie(self._q(L)[0][2070].reindex(AGES).to_numpy()) - ev_femmes_2070  # noqa: E731
            lambda_ev = brentq(f, -4, 4)
        qF, qH = self._q(lambda_ev)
        if rythme_gains_mortalite is not None:
            if lambda_ev != 0:
                raise ValueError("choisir λ (ou une EV visée) ou un rythme de gains, pas les deux")
            k, r = rythme_gains_mortalite, an_ref_mortalite
            qF, qH = qF.copy(), qH.copy()
            for q in (qF, qH):
                ref = np.log(q[r].clip(lower=1e-12))
                for t in ans:
                    if t > r and t in q.columns:
                        q[t] = np.exp(ref + k * (np.log(q[t].clip(lower=1e-12)) - ref)).clip(upper=1)
        if mortalite_facteur:
            qF, qH = qF.copy(), qH.copy()
            for t, k in mortalite_facteur.items():
                for q in (qF, qH):
                    if t in q.columns:
                        q[t] = (q[t] * k).clip(upper=1)
        h = Hypotheses(qF, qH, fec, smF, smH, c.ajF, c.ajH, c.pi_f)
        h.lambda_ev = lambda_ev
        return h

    def _q(self, L: float):
        if L == 0:
            return self.c.qF, self.c.qH
        var = self.q_h if L > 0 else self.q_b
        out = []
        for qc, qv in zip((self.c.qF, self.c.qH), var):
            lc = np.log(qc.clip(lower=1e-12))
            out.append(np.exp(lc + abs(L) * (np.log(qv.clip(lower=1e-12)) - lc)).clip(upper=1))
        return tuple(out)


def esperance_de_vie(q: np.ndarray, age: int = 0) -> float:
    """Espérance de vie du moment à partir de quotients (approximation : décès en milieu d'année)."""
    q = np.clip(q[age:], 0, 1)
    l = np.concatenate([[1.0], np.cumprod(1 - q)])
    return float(((l[:-1] + l[1:]) / 2).sum())


def population_active(res: Resultat, tauF: pd.Series, tauH: pd.Series) -> pd.Series:
    """Population active au 1er janvier par application de taux d'activité par âge (indice = âge)."""
    tF = tauF.reindex(AGES).fillna(0).to_numpy()[:, None]
    tH = tauH.reindex(AGES).fillna(0).to_numpy()[:, None]
    return pd.Series((res.popF.to_numpy() * tF + res.popH.to_numpy() * tH).sum(axis=0), index=res.popF.columns)
