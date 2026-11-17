"""Téléchargement scripté des données ouvertes, avec cache local et registre d'intégrité.

Chaque fichier brut est conservé dans data/raw/ ; son empreinte SHA-256, sa taille, l'URL
et la date de téléchargement sont consignées dans data/raw/_registre.json. Une nouvelle
exécution réutilise le cache sauf si force=True ; un changement d'empreinte d'une source
déjà enregistrée est signalé (révision de la source).
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import pathlib
import time
import urllib.request

RACINE = pathlib.Path(__file__).resolve().parents[1]
RAW = RACINE / "data" / "raw"
REGISTRE = RAW / "_registre.json"


def _charger_registre() -> dict:
    if REGISTRE.exists():
        return json.loads(REGISTRE.read_text(encoding="utf-8"))
    return {}


def _ecrire_registre(reg: dict) -> None:
    REGISTRE.write_text(json.dumps(reg, indent=1, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def telecharger(url: str, nom: str, force: bool = False, essais: int = 3) -> pathlib.Path:
    """Télécharge url vers data/raw/nom ; renvoie le chemin."""
    RAW.mkdir(parents=True, exist_ok=True)
    chemin = RAW / nom
    reg = _charger_registre()
    if chemin.exists() and not force:
        return chemin
    derniere = None
    for i in range(essais):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; modele-france/0.1)", "Accept": "application/json, */*"})
            with urllib.request.urlopen(req, timeout=180) as r:
                contenu = r.read()
            break
        except Exception as e:  # noqa: BLE001
            derniere = e
            time.sleep(2 * (i + 1))
    else:
        raise RuntimeError(f"échec du téléchargement {url}: {derniere}")
    chemin.write_bytes(contenu)
    empreinte = hashlib.sha256(contenu).hexdigest()
    reg = _charger_registre()  # relu après le téléchargement : un autre téléchargement a pu l'enrichir entre-temps
    ancien = reg.get(nom)
    if ancien and ancien["sha256"] != empreinte:
        print(f"[révision] {nom} : empreinte modifiée depuis {ancien['date']}")
    reg[nom] = {
        "url": url,
        "sha256": empreinte,
        "octets": len(contenu),
        "date": _dt.datetime.now().isoformat(timespec="seconds"),
    }
    _ecrire_registre(reg)
    return chemin


def eurostat(code: str, filtres: dict, nom: str | None = None, force: bool = False) -> dict:
    """Interroge l'API JSON-stat d'Eurostat et renvoie {(clé1, clé2, ...): valeur}."""
    q = "&".join(f"{k}={v}" for k, vs in filtres.items() for v in (vs if isinstance(vs, list) else [vs]))
    url = f"https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{code}?format=JSON&{q}"
    nom = nom or f"eurostat_{code}_{hashlib.md5(q.encode()).hexdigest()[:8]}.json"
    d = json.loads(telecharger(url, nom, force=force).read_text(encoding="utf-8"))
    return jsonstat_dict(d)


def jsonstat_dict(d: dict) -> dict:
    ids, tailles = d["id"], d["size"]
    cats = []
    for dim in ids:
        idx = d["dimension"][dim]["category"]["index"]
        inv = sorted(idx.items(), key=lambda kv: kv[1])
        cats.append([k for k, _ in inv])
    res = {}
    for pos, val in d["value"].items():
        p = int(pos)
        cle = []
        for taille, cs in zip(reversed(tailles), reversed(cats)):
            cle.append(cs[p % taille])
            p //= taille
        res[tuple(reversed(cle))] = val
    # ne garder que les dimensions qui varient
    var = [i for i, t in enumerate(tailles) if t > 1]
    return {tuple(k[i] for i in var) if len(var) != 1 else k[var[0]]: v for k, v in res.items()}
