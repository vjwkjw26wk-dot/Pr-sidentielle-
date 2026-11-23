# Phase 3.2 — expériences de diagnostic (historique)

Scripts exécutés pendant la phase 3.2 sur une copie instrumentée de `m8_modele.py` (`exp_src/`, points d'injection
`EXP` désactivés par défaut ; la v0.8 de `src/` n'est pas modifiée). Banc d'essai réutilisable : `lab.py`.

- `depenses.py`, `exp_depenses.py`, `denom.py` : décomposition des dépenses publiques, tests E1-E3.
- `emploi.py`, `exp_emploi.py`, `cout.py`, `productivite.py` : emploi marchand / non marchand, coût réel, productivité.
- `coherence.py`, `coherent.py`, `heures.py`, `okun.py`, `robust_h.py` : fermetures v0.6/v0.8, durée par tête.
- `are.py` : double compte des allocations chômage dans le backtest.
- `predictif.py`, `predictif2.py` : backtest conditionnel vs ex ante.
Données : `data/raw` (séries Eurostat/DBnomics ; re-téléchargement : `python3 phase34/recuperer_donnees.py`).
