"""Synthèse de la contre-expertise : tableau de robustesse des programmes et des variantes de contrôle.

Lit outputs/contre_expertise/*.json (tests/contre_expertise.py) et produit outputs/robustesse_programmes.md et .json.
Définitions :
- valeur centrale : jeu de paramètres central ;
- intervalle statistique : 5e-95e centiles des tirages conjoints des coefficients estimés (incertitude d'estimation
  seulement, tirages violant les contraintes de signe écartés) ;
- plage de sensibilité : enveloppe (minimum-maximum) de toutes les évaluations à paramètres modifiés (sensibilités
  univariées aux bornes, criblage de Morris multivarié, scénarios cohérents) ; ce n'est pas un intervalle de probabilité ;
- configurations instables : évaluations dont l'écart de dette en 2032 dépasse 25 points ou celui du PIB 10 % (dynamique
  explosive de la boucle prix-salaires ou de la dette), écartées et comptées ;
- robustesse du signe : « robuste » si toutes les évaluations finies ont le signe du résultat central, « plutôt
  robuste » si au moins 90 %, « fragile » sinon ; « indéterminé » si la valeur centrale est inférieure au seuil de
  pertinence (0,05 point ou 0,05 %, 5 000 emplois).
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

import numpy as np

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
sys.path.insert(0, str(RACINE / "src"))
from simulateur import programmes as PG, sensibilite as S  # noqa: E402

DOS = RACINE / "outputs" / "contre_expertise"
LIB = {"pib": "PIB réel (%)", "croissance": "Croissance (pt)", "emploi": "Emploi (milliers)", "chomage": "Chômage (pt)",
       "rdb": "Revenu disponible nominal (%)", "c": "Consommation (%)", "fbcf": "Investissement (%)", "taux_epargne": "Taux d'épargne (pt)",
       "inflation": "Inflation (pt)", "pc": "Niveau des prix (%)", "solde_pib": "Solde public (pt de PIB)", "dette_pib": "Dette (pt de PIB)",
       "solde_exterieur_pib": "Solde extérieur (pt de PIB)", "rnb": "RNB nominal (%)"}
SEUIL = {"emploi": 5.0}
FACTEUR_LIB = {f[0]: f[6] for f in S.FACTEURS}


def finite(x):
    return x is not None and isinstance(x, (int, float)) and math.isfinite(x)


INSTABLE = {"dette_pib": 25.0, "pib": 10.0}   # écarts en 2032 au-delà desquels la configuration est jugée instable


def stable(p):
    try:
        return all(finite(p[k]["2032"]) and abs(p[k]["2032"]) <= v for k, v in INSTABLE.items())
    except (KeyError, TypeError):
        return False


def analyse(d):
    c = d["central"]
    out = {}
    pts = []
    for u in d["univarie"].values():
        pts += [u["bas"], u["haut"]]
    pts += list(d["coherents"].values())
    pts += [e["y"] for e in d["morris"]["evaluations"]]
    stat = d.get("statistique", [])
    n_inst = sum(1 for p in pts if not stable(p)) + sum(1 for p in stat if not stable(p))
    pts = [p for p in pts if stable(p)]
    stat = [p for p in stat if stable(p)]
    for ind in S.INDICATEURS:
        out[ind] = {}
        for t in ("2027", "2028", "2030", "2032"):
            if t not in c[ind]:
                continue
            v0 = c[ind][t]
            vals = [p[ind][t] for p in pts if finite(p[ind].get(t))]
            sv = [s[ind][t] for s in stat if finite(s[ind].get(t))]
            nonfin = sum(1 for p in pts if not finite(p[ind].get(t)))
            seuil = SEUIL.get(ind, 0.05)
            alls = vals + sv
            if abs(v0) < seuil:
                rob = "indéterminé"
            else:
                same = np.mean([np.sign(x) == np.sign(v0) for x in alls]) if alls else 1.0
                rob = "robuste" if same == 1.0 else ("plutôt robuste" if same >= 0.9 else "fragile")
            out[ind][t] = {"central": v0, "stat": [float(np.percentile(sv, 5)), float(np.percentile(sv, 95))] if len(sv) > 5 else None,
                           "plage": [float(min(vals)), float(max(vals))] if vals else None, "robustesse": rob, "non_finis": nonfin,
                           "part_meme_signe": float(np.mean([np.sign(x) == np.sign(v0) for x in alls])) if alls else None}
    # facteurs dominants (Morris, μ*) en 2032
    dom = {}
    for ind in ("pib", "emploi", "solde_pib", "dette_pib", "rnb", "c"):
        m = d["morris"]["indices"].get(ind, {}).get("2032", {})
        dom[ind] = sorted([(k, v["mu_etoile"], v["sigma"]) for k, v in m.items() if finite(v["mu_etoile"])], key=lambda x: -x[1])[:3]
    # mesures responsables de l'incertitude
    mes = []
    for k, x in (d.get("mesures") or {}).items():
        vals = {ind: [x["central"][ind]["2032"]] + [u[s][ind]["2032"] for u in x["univarie"].values() for s in ("bas", "haut")]
                for ind in ("pib", "dette_pib", "emploi")}
        mes.append({"mesure": k, "valeur": x["valeur"], **{f"{ind}_central": x["central"][ind]["2032"] for ind in ("pib", "dette_pib", "emploi")},
                    **{f"{ind}_etendue": float(np.nanmax(v) - np.nanmin(v)) for ind, v in vals.items()}})
    mes.sort(key=lambda z: -z["dette_pib_etendue"])
    return {"indicateurs": out, "dominants": dom, "mesures": mes, "tirages_rejetes": d.get("tirages_rejetes"), "instables": n_inst,
            "n_stat": len(stat), "n_eval": len(pts)}


def fmt(x, ind):
    return f"{x:+.0f}" if ind == "emploi" else f"{x:+.2f}"


def main():
    res = {}
    for f in sorted(DOS.glob("*.json")):
        d = json.loads(f.read_text())
        res[d["id"]] = analyse(d)
    progs = {p["id"]: p for p in PG.PROGRAMMES}
    L = ["# Robustesse des résultats des programmes (contre-expertise, version 0.6)", "",
         "Écarts à la trajectoire « politique inchangée » (mêmes traductions de mesures et même référence pour tous). Les mesures "
         "entrent en vigueur en 2028 (premier budget après l'élection) : les écarts de 2027 sont nuls par construction, le modèle "
         "ne représentant pas d'effets d'anticipation.", "",
         "**Central** : paramètres centraux. **Stat. 90 %** : 5e-95e centiles des tirages conjoints des coefficients estimés "
         "(incertitude d'estimation seule). **Plage** : minimum-maximum de toutes les évaluations à hypothèses modifiées "
         "(univariées, Morris, scénarios cohérents) : intervalle de sensibilité, non probabiliste. **Signe** : robuste (signe du "
         "central dans toutes les évaluations), plutôt robuste (≥ 90 %), fragile (< 90 %), indéterminé (effet central "
         "inférieur au seuil de pertinence).", "",
         "Aucun classement des candidats n'est établi : les tableaux ne se comparent qu'indicateur par indicateur, avec leurs "
         "plages.", ""]
    ordre = sorted([k for k in res if k in progs], key=lambda k: progs[k]["tri"]) + sorted(k for k in res if k not in progs)
    # tableau synthétique
    L += ["## Tableau de synthèse (2032)", "", "| Scénario | PIB (%) | Emploi (milliers) | Solde (pt) | Dette (pt) | RNB (%) |", "|---|---|---|---|---|---|"]
    for k in ordre:
        nom = f"{progs[k]['candidat']}" if k in progs else k.replace("controle_", "contrôle : ")
        cells = []
        for ind in ("pib", "emploi", "solde_pib", "dette_pib", "rnb"):
            x = res[k]["indicateurs"][ind]["2032"]
            pl = x["plage"]
            cells.append(f"{fmt(x['central'], ind)} [{fmt(pl[0], ind)} ; {fmt(pl[1], ind)}] {x['robustesse']}")
        L.append(f"| {nom} | " + " | ".join(cells) + " |")
    L.append("")
    for k in ordre:
        r = res[k]
        if k in progs:
            p = progs[k]
            L += [f"## {p['candidat']} ({p['parti']})", "", "Curseurs : " + ", ".join(f"{a} = {b:g}" for a, b in p["curseurs"].items()), ""]
        else:
            L += [f"## Contrôle : {k.replace('controle_', '')}", ""]
        L += ["| Indicateur | 2028 central | 2030 central | 2032 central | 2032 stat. 90 % | 2032 plage | Signe 2032 |", "|---|---|---|---|---|---|---|"]
        for ind in S.INDICATEURS:
            x = r["indicateurs"][ind]
            if "2032" not in x:
                continue
            st = x["2032"]["stat"]
            pl = x["2032"]["plage"]
            L.append(f"| {LIB[ind]} | {fmt(x['2028']['central'], ind)} | {fmt(x['2030']['central'], ind)} | {fmt(x['2032']['central'], ind)} | "
                     + (f"{fmt(st[0], ind)} à {fmt(st[1], ind)}" if st else "–") + " | "
                     + (f"{fmt(pl[0], ind)} à {fmt(pl[1], ind)}" if pl else "–") + f" | {x['2032']['robustesse']} |")
        L += ["", "Paramètres les plus influents en 2032 (criblage de Morris, μ*) :"]
        for ind, lst in r["dominants"].items():
            L.append(f"- {LIB[ind]} : " + " ; ".join(f"{FACTEUR_LIB.get(n, n)} ({m:.2f})" for n, m, _ in lst))
        if r["mesures"]:
            L += ["", "Mesures et incertitude (simulées seules ; étendue = écart maximal entre hypothèses, 2032) :", "",
                  "| Mesure | PIB central | étendue | Dette central | étendue | Emploi central | étendue |", "|---|---|---|---|---|---|---|"]
            for m in r["mesures"]:
                L.append(f"| {m['mesure']} = {m['valeur']:g} | {m['pib_central']:+.2f} | {m['pib_etendue']:.2f} | {m['dette_pib_central']:+.2f} | "
                         f"{m['dette_pib_etendue']:.2f} | {m['emploi_central']:+.0f} | {m['emploi_etendue']:.0f} |")
        robustes = [LIB[i] for i in S.INDICATEURS if r["indicateurs"][i]["2032"]["robustesse"] == "robuste"]
        fragiles = [LIB[i] for i in S.INDICATEURS if r["indicateurs"][i]["2032"]["robustesse"] == "fragile"]
        L += ["", f"Effets robustes en 2032 : {', '.join(robustes) or 'aucun'}.", f"Effets dont le signe change selon les hypothèses : {', '.join(fragiles) or 'aucun'}."]
        if k in progs:
            L.append("Non évaluable avec le modèle : " + " ; ".join(progs[k]["non_represente"]) + ".")
        L.append(f"Évaluations retenues : {r['n_eval']} à hypothèses modifiées, {r['n_stat']} tirages statistiques ; {r['instables']} configurations "
                 f"instables ou explosives écartées (dette > 25 points ou PIB > 10 % d'écart) ; {r['tirages_rejetes']} tirages écartés pour violation des contraintes de signe.")
        L.append("")
    (RACINE / "outputs" / "robustesse_programmes.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (RACINE / "outputs" / "robustesse_programmes.json").write_text(json.dumps(res, ensure_ascii=False, default=float))
    print(len(res), "scénarios")


if __name__ == "__main__":
    main()
