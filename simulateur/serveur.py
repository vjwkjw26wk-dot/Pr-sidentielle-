"""Serveur local de test : sert l'interface et exécute un scénario exact à la demande.

Usage : python3 -m simulateur.serveur [port] [--hote 0.0.0.0]  → http://localhost:8765
Points d'accès : GET / (interface), GET /sante (version), POST /executer (page de résultats), POST /api/executer (JSON).
Les calculs sont faits un par un (verrou) : un calcul complet prend de 15 s à quelques minutes.
- GET  /              : interface de test (variantes élémentaires additionnées, réponse immédiate) ;
- POST /executer      : corps = scénario JSON ; renvoie la page de restitution du calcul complet (avec interactions
                        entre mesures et, si demandé, incertitude). Quelques secondes à quelques minutes.
Usage local uniquement (aucune authentification, un calcul à la fois).
"""
from __future__ import annotations

import json
import pathlib
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

RACINE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from simulateur import executer as X, restitution  # noqa: E402

VERROU = threading.Lock()


class Gestionnaire(BaseHTTPRequestHandler):
    def _envoyer(self, code, corps: bytes, type_="text/html; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", type_)
        self.send_header("Content-Length", str(len(corps)))
        self.end_headers()
        self.wfile.write(corps)

    def do_GET(self):
        p = RACINE / "outputs" / "interface_test.html"
        if self.path == "/sante":
            return self._envoyer(200, json.dumps({"etat": "ok", **X.empreintes()}).encode(), "application/json")
        if self.path in ("/", "/index.html") and p.exists():
            self._envoyer(200, p.read_bytes())
        else:
            self._envoyer(404, "Interface absente : lancer python3 -m simulateur.precalcul puis python3 -m simulateur.interface".encode())

    def do_POST(self):
        if self.path not in ("/executer", "/api/executer"):
            return self._envoyer(404, b"")
        sc = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        with VERROU:
            res = X.executer(sc)
        if self.path == "/api/executer":
            return self._envoyer(200, json.dumps(res, ensure_ascii=False, default=float).encode(), "application/json")
        out = RACINE / "outputs" / "serveur_dernier_resultat.html"
        restitution.ecrire_html(res, out)
        self._envoyer(200, out.read_bytes())


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Serveur de calcul exact du simulateur")
    ap.add_argument("port_pos", nargs="?", type=int, default=None)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--hote", default="127.0.0.1", help="0.0.0.0 pour un déploiement (conteneur)")
    a = ap.parse_args()
    port = a.port_pos or a.port
    print(f"Interface de test : http://{a.hote}:{port}  (GET /sante ; POST /executer → page ; POST /api/executer → JSON)")
    ThreadingHTTPServer((a.hote, port), Gestionnaire).serve_forever()


if __name__ == "__main__":
    main()
