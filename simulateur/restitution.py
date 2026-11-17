"""Restitution d'un scénario : page HTML autonome (tableaux, graphiques SVG, fiche de transparence).

Principes (cahier des charges § 17) : présenter des écarts conditionnels à un compte de référence, jamais une note
globale ; montrer les hypothèses, les données, les modèles, les paramètres sensibles, les incertitudes et les limites ;
appliquer la même présentation à toutes les mesures.
"""
from __future__ import annotations

import html
import pathlib

PRINCIPAUX = ["pib", "emploi", "chomage", "pc", "rdb", "solde_pib", "dette_pib"]
LIB = {"pib": "PIB en volume", "emploi": "Emploi", "chomage": "Taux de chômage", "pc": "Prix à la consommation",
       "rdb": "Revenu disponible des ménages", "solde_pib": "Solde public", "dette_pib": "Dette publique",
       "c": "Consommation", "fbcf": "Investissement", "x": "Exportations", "m": "Importations", "salaire": "Salaire moyen",
       "tuc_industrie": "Utilisation des capacités (industrie)", "recettes": "Recettes publiques", "depenses": "Dépenses publiques"}


def _fmt(v, unite):
    if unite == "emploi":
        return f"{v:+,.0f}".replace(",", " ")
    return f"{v:+.2f}"


def _svg(series: dict, titre: str, unite: str) -> str:
    """Petit graphique en ligne de l'écart au compte de référence (SVG autonome)."""
    xs = sorted(series)
    ys = [series[x] for x in xs]
    w, h, m = 320, 150, 34
    lo, hi = min(ys + [0]), max(ys + [0])
    if hi - lo < 1e-9:
        hi, lo = hi + 1, lo - 1
    sx = lambda x: m + (x - xs[0]) / max(xs[-1] - xs[0], 1) * (w - 2 * m)  # noqa: E731
    sy = lambda y: h - m + (lo - y) / (hi - lo) * (h - 2 * m) + 0  # noqa: E731
    pts = " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in zip(xs, ys))
    zero = sy(0)
    return (f'<figure><svg viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(titre)}">'
            f'<line x1="{m}" x2="{w - m}" y1="{zero:.1f}" y2="{zero:.1f}" class="zero"/>'
            f'<polyline points="{pts}" class="ligne"/>'
            f'<text x="{m}" y="14" class="t">{html.escape(titre)} ({html.escape(unite)})</text>'
            f'<text x="{m}" y="{h - 8}" class="a">{xs[0]}</text><text x="{w - m}" y="{h - 8}" class="a" text-anchor="end">{xs[-1]}</text>'
            f'<text x="4" y="{sy(hi) + 4:.1f}" class="a">{hi:+.2f}</text><text x="4" y="{sy(lo) + 4:.1f}" class="a">{lo:+.2f}</text>'
            f'</svg></figure>')


def ecrire_html(res: dict, chemin: pathlib.Path):
    sc, tr, tp = res["scenario"], res["trajectoires"], res["transparence"]
    ans = sorted(int(a) for a in tr["pib"]["ecart"])
    choix = [a for a in (ans[0], ans[min(2, len(ans) - 1)], ans[-1])]
    choix = sorted(set(choix))
    H = []
    H.append(f"<h1>{html.escape(sc.get('nom', 'Scénario'))}</h1><p class='desc'>{html.escape(sc.get('description', ''))}</p>")
    H.append("<p class='avert'>Résultats conditionnels : écarts entre une trajectoire avec les mesures et un compte de référence "
             "conventionnel (législation inchangée). Ce ne sont pas des prévisions. Aucune note globale n'est attribuée.</p>")
    # mesures
    H.append("<h2>Mesures simulées</h2><table><tr><th>Mesure</th><th>Paramètres</th><th>Niveau de preuve</th><th>Limites</th></tr>")
    for m in tp["mesures"]:
        H.append(f"<tr><td>{html.escape(m['libelle'])}</td><td><code>{html.escape(str(m['parametres']))}</code></td>"
                 f"<td>{html.escape(m['niveau_de_preuve'])}</td><td>{html.escape(m['limites'])}</td></tr>")
    H.append("</table>")
    # effets principaux
    H.append("<h2>Effets macroéconomiques et budgétaires (écart au compte de référence)</h2><table><tr><th>Indicateur</th>"
             + "".join(f"<th>{a}</th>" for a in choix) + "<th>Unité</th></tr>")
    for k in PRINCIPAUX + ["c", "fbcf", "x", "m", "salaire", "tuc_industrie"]:
        if k not in tr:
            continue
        if k == "emploi":
            vals = [tr[k]["scenario"][a] - tr[k]["reference"][a] for a in choix]
            unite = "milliers"
            cel = "".join(f"<td>{v:+,.0f}</td>".replace(",", " ") for v in vals)
        else:
            vals = [tr[k]["ecart"][a] for a in choix]
            unite = "points" if tr[k]["unite_ecart"] == "points" else "%"
            cel = "".join(f"<td>{v:+.2f}</td>" for v in vals)
        H.append(f"<tr><td>{LIB.get(k, k)}</td>{cel}<td>{unite}</td></tr>")
    H.append("</table>")
    if res.get("incertitude"):
        H.append("<h3>Incertitude (intervalle à 90 %)</h3><table><tr><th>Année</th><th>PIB (%)</th><th>Emploi (milliers)</th><th>Prix (%)</th><th>Solde (pt)</th><th>Dette (pt)</th></tr>")
        for a, d in sorted(res["incertitude"].items(), key=lambda x: int(x[0])):
            H.append(f"<tr><td>{a}</td>" + "".join(f"<td>[{d[c][0]:+.2f} ; {d[c][1]:+.2f}]</td>" if c != "emploi" else f"<td>[{d[c][0]:+.0f} ; {d[c][1]:+.0f}]</td>"
                                                   for c in ("pib", "emploi", "prix", "solde", "dette")) + "</tr>")
        H.append("</table>")
    H.append("<div class='graphes'>")
    for k in ("pib", "chomage", "solde_pib", "dette_pib"):
        H.append(_svg(tr[k]["ecart"] if k != "emploi" else {}, LIB[k], "points" if tr[k]["unite_ecart"] == "points" else "%"))
    H.append("</div>")
    # statique et distribution
    if res.get("statique"):
        st = res["statique"]
        H.append("<h2>Effets directs (avant bouclage macroéconomique)</h2><ul>")
        if "impot_revenu_M€" in st:
            H.append(f"<li>Impôt sur le revenu : {st['impot_revenu_M€'] / 1e3:+.2f} Md€ (revenus 2024)</li>")
            H.append(f"<li>Prestations versées : {st['prestations_versees_M€'] / 1e3:+.2f} Md€</li>")
        if "pensions_M€" in st:
            a = max(int(x) for x in st["pensions_M€"])
            H.append(f"<li>Pensions de droit direct en {a} : {st['pensions_M€'][a] / 1e3:+.1f} Md€</li>")
        H.append("</ul>")
    if res.get("distribution"):
        H.append("<h2>Effets par décile de niveau de vie (statiques)</h2><table><tr><th>Décile</th><th>Niveau de vie moyen (€/UC/an, approché)</th>"
                 "<th>Variation (€/UC/an)</th><th>Variation (%)</th><th>Gagnants</th><th>Perdants</th></tr>")
        for d in res["distribution"]:
            H.append(f"<tr><td>{d['decile']}</td><td>{d['niveau_de_vie_moyen']:,.0f}</td><td>{d['variation_euros_par_uc']:+.0f}</td>"
                     f"<td>{d['variation_pct']:+.2f}</td><td>{d['part_gagnants']:.0%}</td><td>{d['part_perdants']:.0%}</td></tr>".replace(",", " "))
        H.append("</table>")
    if res.get("profils"):
        H.append("<h2>Ménages types (cas fictifs, revenus 2024)</h2><table><tr><th>Profil</th><th>Impôt sur le revenu actuel (€/an)</th>"
                 "<th>Prestations actuelles (€/an)</th><th>Revenu disponible approché (€/an)</th><th>Variation avec les mesures (€/an)</th></tr>")
        for p in res["profils"]:
            prest = sum(p[f"{v}_actuel"] for v in ("rsa", "ppa", "af", "aide_logement"))
            H.append(f"<tr><td>{html.escape(p['libelle'])}</td><td>{p['impot_revenu_actuel']:,.0f}</td><td>{prest:,.0f}</td>"
                     f"<td>{p['revenu_disponible_approche_actuel']:,.0f}</td><td>{p['variation_revenu_disponible']:+,.0f}</td></tr>".replace(",", " "))
        H.append("</table>")
    if res.get("europe"):
        e = {int(r["annee"]): r for r in res["europe"]}
        H.append("<h2>Rétroactions européennes</h2><table><tr><th>Année</th><th>Taux BCE (pt)</th><th>Taux long français (pt)</th><th>Demande des partenaires (%)</th></tr>")
        for a in choix:
            if a in e:
                H.append(f"<tr><td>{a}</td><td>{e[a]['taux_bce']:+.2f}</td><td>{e[a]['taux_long_fr']:+.2f}</td><td>{e[a]['demande_ue']:+.2f}</td></tr>")
        H.append("</table>")
    # transparence
    H.append("<h2>Transparence</h2><dl>")
    hyp = tp["hypotheses"]
    H.append(f"<dt>Compte de référence</dt><dd>{html.escape(hyp['compte_de_reference'])}</dd>")
    H.append(f"<dt>Fermeture d'offre</dt><dd>ρ = {hyp['fermeture_offre']}</dd><dt>Couplage européen</dt><dd>{'oui' if hyp['europe'] else 'non'}</dd>")
    H.append(f"<dt>Données</dt><dd>{html.escape(tp['donnees'])}</dd><dt>Modèles mobilisés</dt><dd>{', '.join(tp['modeles'])}</dd>")
    H.append("<dt>Paramètres sensibles</dt><dd><ul>" + "".join(f"<li>{html.escape(x)}</li>" for x in tp["parametres_sensibles"]) + "</ul></dd>")
    H.append(f"<dt>Incertitudes</dt><dd>{html.escape(tp['incertitudes'])}</dd>")
    H.append("<dt>Limites</dt><dd><ul>" + "".join(f"<li>{html.escape(x)}</li>" for x in tp["limites"]) + "</ul></dd></dl>")
    H.append(f"<p class='pied'>Calcul : {res['duree_s']} s. Modèle « Présidentielle », prototype de phase 8 ; code et documentation dans le dépôt du projet.</p>")
    css = """body{font-family:system-ui,-apple-system,'Segoe UI',sans-serif;max-width:980px;margin:2rem auto;padding:0 1rem;color:#1d2433;line-height:1.5}
h1{font-size:1.6rem;margin-bottom:.2rem}h2{font-size:1.15rem;margin-top:2rem;border-bottom:1px solid #d8dde6;padding-bottom:.2rem}
table{border-collapse:collapse;width:100%;font-size:.9rem;margin:.6rem 0}th,td{border-bottom:1px solid #e6e9ef;padding:.35rem .5rem;text-align:right;vertical-align:top}
th:first-child,td:first-child{text-align:left}td code{font-size:.8rem}.avert{background:#f4f6fa;border-left:3px solid #6b7a99;padding:.6rem .8rem;font-size:.9rem}
.desc{color:#4a5468}.graphes{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:1rem}figure{margin:0}
svg{width:100%;height:auto;background:#fafbfd;border:1px solid #e6e9ef;border-radius:6px}.ligne{fill:none;stroke:#2f5aa8;stroke-width:2}
.zero{stroke:#9aa3b5;stroke-dasharray:3 3}.t{font-size:11px;fill:#1d2433}.a{font-size:9px;fill:#6b7385}dt{font-weight:600;margin-top:.6rem}dd{margin-left:0}
.pied{color:#6b7385;font-size:.8rem;margin-top:2rem}
@media (prefers-color-scheme: dark){body{background:#12151c;color:#e3e7ef}th,td{border-color:#2a303c}.avert{background:#1b2030}
svg{background:#181c25;border-color:#2a303c}.t{fill:#e3e7ef}.ligne{stroke:#7aa2ff}h2{border-color:#2a303c}}"""
    page = f"<!DOCTYPE html><html lang='fr'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>" \
           f"<title>{html.escape(sc.get('nom', 'Scénario'))}</title><style>{css}</style></head><body>{''.join(H)}</body></html>"
    pathlib.Path(chemin).write_text(page, encoding="utf-8")
