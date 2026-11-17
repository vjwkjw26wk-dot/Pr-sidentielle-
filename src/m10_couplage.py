"""M10 — Couplage de la microsimulation des ménages (M4, OpenFisca) et du modèle bouclé (M8), version 0.1.

Sens micro → macro (réforme socio-fiscale) :
1. La réforme est décrite par des paramètres OpenFisca modifiés (`m4_openfisca.appliquer_reforme`) : barème de
   l'impôt sur le revenu, montants du RSA, de la prime d'activité, des allocations familiales, etc.
2. M4 calcule, ménage par ménage, l'impôt sur le revenu (échantillon de 2 % des ménages, chaîne de calcul validée de
   `validation_M4`, avec les mêmes imputations et calages qu'en législation actuelle) et les prestations (deux
   sous-échantillons de 0,5 %), en législation actuelle et après réforme. Effet statique (comportements inchangés),
   revenus 2024.
3. Passage aux montants versés : impôt ramené aux foyers de la DGFiP ; prestations multipliées par le taux de recours
   apparent en masse mesuré en législation actuelle (RSA 0,68 ; prime d'activité 0,66 ; allocations familiales et
   aides au logement 1).
4. Effets distributifs par décile de niveau de vie (revenu disponible approché / unités de consommation, échelle de
   l'OCDE modifiée).
5. Les variations d'impôt et de prestations (M€ de 2024) entrent dans M8 (`Exogenes.mesure_menages`), indexées sur le
   PIB nominal simulé : revenu disponible des ménages et comptes publics, puis tout le bouclage macroéconomique.

Sens macro → micro (non fait dans cette version) : les revenus de M4 ne sont pas encore revalorisés avec les salaires,
l'emploi et les prix simulés par M8 ; l'effet statique est calculé sur les revenus de 2024 puis indexé.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys

import numpy as np
import pandas as pd

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))
sys.path.insert(0, str(RACINE / "tests"))
TMP = pathlib.Path("/tmp/m10")
K_PREST = 2                      # sous-échantillons de 0,5 % pour les prestations
MOIS = "2024-10"
RECOURS_MASSE = {"rsa": 0.68, "ppa": 0.66, "af": 1.0, "aide_logement": 1.0}
PRESTATIONS = ("rsa", "ppa", "af", "aide_logement")


# ------------------------------------------------------------------------------------------------------------------
# Travailleurs (un processus par simulation OpenFisca, contrainte de mémoire)
# ------------------------------------------------------------------------------------------------------------------
def _travailleur(tache: str, nom: str = "base", k: int = 0, var: str = ""):
    if tache == "ir":
        import validation_M4 as v4
        d = pd.read_pickle(v4.TMP / "prep.pkl")
        r = v4.simuler(d["ind"], d["fo"], d["tot"], d["f8tk"], d["reste"], d["dep"], 0.8)
        r.to_pickle(TMP / f"ir_{nom}.pkl")
    elif tache == "prep_prest":
        import m4_population as m4
        ind, fo, ir = m4.construire(f=0.02)
        men = ind.men.unique()
        grp = pd.Series(np.random.default_rng(5).integers(0, 4, len(men)), index=men)
        ind["sous_ech"] = grp.reindex(ind.men).to_numpy()
        ind["poids"] = ind.poids * 4
        for j in range(K_PREST):
            ind[ind.sous_ech == j].to_pickle(TMP / f"prest_ind_{j}.pkl")
    elif tache == "prest":
        import m4_prestations as mp
        r = mp.prestations(pd.read_pickle(TMP / f"prest_ind_{k}.pkl"), MOIS, variables=(var,), p_emploi=0.75)
        r.to_pickle(TMP / f"prest_{nom}_{k}_{var}.pkl")


def preparer():
    """Données de la chaîne IR (celles de validation_M4, 2 % des ménages) et sous-échantillons des prestations."""
    import validation_M4 as v4
    TMP.mkdir(exist_ok=True)
    v4.TMP.mkdir(exist_ok=True)
    p = v4.TMP / "prep.pkl"
    if not (p.exists() and "dep" in pd.read_pickle(p)):
        v4._lancer("prep")
    if not (TMP / f"prest_ind_{K_PREST - 1}.pkl").exists():
        _lancer("prep_prest")


def _lancer(*args, reforme: dict | None = None):
    env = dict(os.environ)
    env.pop("M4_REFORME", None)
    if reforme:
        f = TMP / f"reforme_{args[1]}.json"
        f.write_text(json.dumps(reforme), encoding="utf-8")
        env["M4_REFORME"] = str(f)
    code = f"import sys; sys.path.insert(0, {str(RACINE / 'src')!r}); import m10_couplage as c; c._travailleur(*{args!r})"
    subprocess.run([sys.executable, "-c", code], check=True, env=env)


# ------------------------------------------------------------------------------------------------------------------
# Évaluation d'une réforme
# ------------------------------------------------------------------------------------------------------------------
def _ir_net(r, nom_base="base"):
    """Impôt net par foyer (chaîne de validation_M4) ; résidus de réductions et crédits non modélisés repris de la
    législation actuelle (ce sont des données calées, pas des résultats de la législation)."""
    import m4_population as m4
    import validation_M4 as v4
    d = pd.read_pickle(v4.TMP / "prep.pkl")
    fo = d["fo"]
    dg = m4.lire_deciles_dgfip(2024)
    avant = r.ip_net_of + r.prelevement_forfaitaire_unique_ir_of + v4.cehr(fo)
    avant = avant.where(avant >= 61, 0.0)
    rici = r.credits_impot_of + r.reductions_of
    f = TMP / f"resid_{nom_base}.pkl"
    if not f.exists():
        dec = m4.deciles_rfr_par_part(fo, r.nbptr_of)
        resid = m4.caler_rici_residuelles(fo, avant - rici, rici, r.nbptr_of, dec, dg)
        resid.to_pickle(f)
    resid = pd.read_pickle(f)
    return avant - rici - resid, fo


def evaluer(nom: str, reforme: dict | None, prestations=PRESTATIONS, refaire=False, calculer=("ir", "prest")) -> dict:
    """Effets statiques d'une réforme paramétrique (législation 2024, revenus 2024).
    reforme : {"debut": ..., "parametres": {chemin: valeur ou {"facteur": x, "debut": ...}}} ; None = législation actuelle."""
    import m4_population as m4
    import shutil
    preparer()
    # « calculer » : blocs touchés par la réforme ; les autres sont repris de la législation actuelle (copie)
    if refaire or not (TMP / f"ir_{nom}.pkl").exists():
        if "ir" in calculer or nom == "base":
            _lancer("ir", nom, reforme=reforme)
        else:
            shutil.copy(TMP / "ir_base.pkl", TMP / f"ir_{nom}.pkl")
    for k in range(K_PREST):
        for v in prestations:
            if refaire or not (TMP / f"prest_{nom}_{k}_{v}.pkl").exists():
                if "prest" in calculer or nom == "base":
                    _lancer("prest", nom, k, v, reforme=reforme)
                else:
                    shutil.copy(TMP / f"prest_base_{k}_{v}.pkl", TMP / f"prest_{nom}_{k}_{v}.pkl")
    r = pd.read_pickle(TMP / f"ir_{nom}.pkl")
    if nom == "base":
        _ir_net(r)
    net, fo = _ir_net(r)
    ir_tot = m4.charger_ircom().foyers.sum()
    k_ir = ir_tot / fo.poids.sum()
    out = {"_nom": nom, "ir_net": float((net * fo.poids).sum() * k_ir), "net_foyer": net}
    for v in prestations:
        tot = 0.0
        for k in range(K_PREST):
            p = pd.read_pickle(TMP / f"prest_{nom}_{k}_{v}.pkl")
            tot += float((p[v] * p.poids).sum() * 12) / K_PREST
        out[v] = tot
    return out


def distribution(base: dict, ref: dict, prestations=PRESTATIONS) -> pd.DataFrame:
    """Variation du niveau de vie par décile (sous-échantillons des prestations ; impôt du foyer rattaché au ménage).
    Niveau de vie approché = (revenu fiscal de référence des foyers − impôt net + prestations) / unités de consommation."""
    import validation_M4 as v4
    d = pd.read_pickle(v4.TMP / "prep.pkl")
    fo = d["fo"]
    lignes = []
    for k in range(K_PREST):
        ind = pd.read_pickle(TMP / f"prest_ind_{k}.pkl")
        men = ind.groupby("men").agg(poids=("poids", "first"))
        ordre = ind.sort_values(["men", "age"], ascending=[True, False])
        rang = ordre.groupby("men").cumcount()
        uc = np.where(rang == 0, 1.0, np.where(ordre.age >= 14, 0.5, 0.3))
        men["uc"] = pd.Series(uc, index=ordre.index).groupby(ordre.men).sum()
        foyers = ind.groupby("foyer").men.first()
        rfr = fo.rfr.reindex(foyers.index).fillna(0).groupby(foyers).sum()
        irb = base["net_foyer"].reindex(foyers.index).fillna(0).groupby(foyers).sum()
        irr = ref["net_foyer"].reindex(foyers.index).fillna(0).groupby(foyers).sum()
        pb, pr = pd.Series(0.0, index=men.index), pd.Series(0.0, index=men.index)
        for v in prestations:
            for nom, acc in (("base", pb), ("ref", pr)):
                p = pd.read_pickle(TMP / f"prest_{base['_nom'] if nom == 'base' else ref['_nom']}_{k}_{v}.pkl")
                m_ = pd.Series(p.index.str.rsplit("_", n=1).str[0], index=p.index)
                acc += (p[v] * 12 * RECOURS_MASSE[v]).groupby(m_).sum().reindex(men.index).fillna(0)
        men["nv_base"] = (rfr.reindex(men.index).fillna(0) - irb.reindex(men.index).fillna(0) + pb) / men.uc
        men["delta"] = (-(irr - irb).reindex(men.index).fillna(0) + (pr - pb)) / men.uc
        lignes.append(men)
    m = pd.concat(lignes)
    m["poids"] = m.poids / K_PREST
    m = m.sort_values("nv_base")
    cum = m.poids.cumsum() / m.poids.sum()
    m["decile"] = np.minimum((cum * 10).astype(int) + 1, 10)
    g = m.groupby("decile")
    return pd.DataFrame({"niveau_de_vie_moyen": g.apply(lambda x: np.average(x.nv_base, weights=x.poids)),
                         "variation_euros_par_uc": g.apply(lambda x: np.average(x.delta, weights=x.poids)),
                         "variation_pct": g.apply(lambda x: np.average(x.delta, weights=x.poids) / np.average(x.nv_base, weights=x.poids) * 100),
                         "part_gagnants": g.apply(lambda x: np.average(x.delta > 1, weights=x.poids)),
                         "part_perdants": g.apply(lambda x: np.average(x.delta < -1, weights=x.poids))})


def mesure_pour_m8(base: dict, ref: dict, prestations=PRESTATIONS) -> dict:
    """Variations (M€ de 2024, montants versés) à passer à `m8_modele.Exogenes.mesure_menages`."""
    dp = sum((ref[v] - base[v]) * RECOURS_MASSE[v] for v in prestations) / 1e6
    return {"impots": (ref["ir_net"] - base["ir_net"]) / 1e6, "prestations": dp, "annee": 2024}
