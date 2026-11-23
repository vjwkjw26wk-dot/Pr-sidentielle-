"""Re-télécharge toutes les sources du registre (resultats/registre_telechargements.json) vers data/raw."""
import json, pathlib, sys
R = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / "src"))
import telechargement as T
reg = json.loads((R / "resultats" / "registre_telechargements.json").read_text())
for nom, v in reg.items():
    try:
        T.telecharger(v["url"], nom)
    except Exception as e:  # noqa: BLE001
        print("échec", nom, e)
