# Simulateur « Présidentielle » — service de calcul exact (version 0.4)
# Construction : docker build -t presidentielle -f deploiement/Dockerfile .
# Lancement    : docker run -p 8765:8765 -v presidentielle-donnees:/app/data -v presidentielle-cache:/app/outputs presidentielle
# Ressources   : 2 processeurs, 6 Go de mémoire (OpenFisca sur l'échantillon de ménages : environ 3 Go par calcul).
FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ src/
COPY simulateur/ simulateur/
COPY tests/ tests/
COPY scenarios/ scenarios/
# Les données ouvertes sont téléchargées au premier lancement (cache dans /app/data, registre d'intégrité SHA-256),
# puis le compte de référence est recalé (environ 10 minutes) et mis en cache dans /app/outputs.
EXPOSE 8765
CMD ["python", "-m", "simulateur.serveur", "--hote", "0.0.0.0", "--port", "8765"]
