"""Serveur local de test : sert l'interface et exécute un scénario exact à la demande.

Usage : python3 -m simulateur.serveur [port]  → http://localhost:8765
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
        if self.path in ("/", "/index.html") and p.exists():
            self._envoyer(200, p.read_bytes())
        else:
            self._envoyer(404, "Interface absente : lancer python3 -m simulateur.precalcul puis python3 -m simulateur.interface".encode())

    def do_POST(self):
        if self.path != "/executer":
            return self._envoyer(404, b"")
        sc = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        with VERROU:
            res = X.executer(sc)
        out = RACINE / "outputs" / "serveur_dernier_resultat.html"
        restitution.ecrire_html(res, out)
        self._envoyer(200, out.read_bytes())


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    print(f"Interface de test : http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Gestionnaire).serve_forever()


if __name__ == "__main__":
    main()
