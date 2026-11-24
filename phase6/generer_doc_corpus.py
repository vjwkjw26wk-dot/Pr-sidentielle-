"""Régénère doc/25_corpus_programmes.md à partir de src/m27_corpus.py (tables, règles, couverture, sources)."""
import pathlib, sys
R = pathlib.Path(__file__).resolve().parents[1]; sys.path[:0] = [str(R / "src"), str(R)]
import m27_corpus as C, m26_europe_institutions as U


def _canal(m):
    if not m.canal:
        return "régime : " + m.regime if m.regime else "—"
    out = []
    for k, v in m.canal:
        if v is None:
            out.append(f"`{k}` à préciser")
        elif isinstance(v, tuple):
            out.append(f"`{k}` {v[1]:.3g} Md€" + (" (IS)" if v[0] == "is_md" else ""))
        else:
            out.append(f"`{k}` {v:.3g}")
    return "; ".join(out)


tabs = []
for c, n in C.CANDIDATS.items():
    tabs.append(f"\n### {n}\n\n| id | mesure | montant (Md€, signe solde) | chiffrage | calendrier | début modèle | canal du modèle | "
                "quantifiable | UE |\n|---|---|---|---|---|---|---|---|---|")
    for m in C.M:
        if m.candidat != c:
            continue
        ue = f"{m.ue} (niv. {U.QUALIFICATIONS[m.ue].niveau})" if m.ue else "—"
        mt = "—" if m.montant is None else f"{m.montant:+.1f} ({m.annee})"
        tabs.append(f"| {m.id} | {m.intitule} | {mt} | {m.chiffrage} | {m.calendrier or '—'} | {m.debut} | {_canal(m)} | "
                    f"{m.quantifiable} | {ue} |")
cov = ["| Candidat | mesures | quantifiables | partielles | non quantifiables | montants chiffrés (Md€, hors composantes) | "
       "dont avec canal | enveloppe globale annoncée |", "|---|---|---|---|---|---|---|---|"]
COMPOSANTES = {"P06", "P07"}
ENV = {"melenchon": "solde 2027 : +24,7 Md€", "le_pen": "140 Md€ d'économies nettes d'ici 2032",
       "philippe": "≈ 150 Md€ d'économies, déficit < 2,5 % en 2032"}
for c, n in C.CANDIDATS.items():
    ms = [m for m in C.M if m.candidat == c]
    q = {k: sum(1 for m in ms if m.quantifiable == k) for k in ("oui", "partiel", "non")}
    ch = [m for m in ms if m.montant is not None and m.regime is None and m.id not in COMPOSANTES]
    tot = sum(abs(m.montant) for m in ch)
    av = sum(abs(m.montant) for m in ch if m.canal and all(v is not None for _, v in m.canal))
    cov.append(f"| {n} | {len(ms)} | {q['oui']} | {q['partiel']} | {q['non']} | {tot:.1f} | {av:.1f} | {ENV[c]} |")
gab = (R / "phase6" / "gabarit_doc25.md").read_text()
doc = gab.replace("{TABLES}", "\n".join(tabs)).replace("{REGLES}", "\n".join(f"- **{m.id}** : {m.regle}" for m in C.M if m.regle))
doc = doc.replace("{COUVERTURE}", "\n".join(cov)).replace("{SOURCES}", "\n".join(f"- `{k}` : {v}" for k, v in C.SOURCES.items()))
(R / "doc" / "25_corpus_programmes.md").write_text(doc)
print("doc 25 régénéré")
