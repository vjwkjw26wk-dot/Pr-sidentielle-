# Hypothèses des scénarios européens {#sec:annexe-g}

| Paramètre | Valeur | Statut | Justification |
|---|---|---|---|
| Amende PDE par semestre | 0,05 % du PIB de l'année précédente (plafond) | [D] | règlement (UE) 2024/1264 |
| Nombre de semestres d'amende (tension) | 4 (2028-2029) | [H] | durée illustrative ; aucune amende n'a été infligée à ce jour |
| Délai d'action après recommandation | 6 mois | [D] | idem |
| Choc d'écart OAT-Bund (tension) | +50 pb, 2027-2029 | [H] | ordre de grandeur des épisodes politiques récents |
| Coefficients de prime (tension) | 0,0122 (dette), −0,118 (solde) | [E] | panel zone euro incluant 2010-2013 |
| Délai de contentieux, niveau 1 | 1 an | [H] | — |
| Délai de contentieux, niveau 2 | 2 ans | [H] | durée typique d'une procédure en manquement jusqu'à l'arrêt |
| Part retirée, TVA sur les carburants | 50 % de la mesure | [H] | part des carburants dans l'assiette, à préciser |
| Part retirée, contribution européenne | 100 % | [H] | réduction unilatérale non réalisable |
| Part non conforme, économies « immigration » | inconnue (mesure conservée) | [H] | modalités non publiées |
| Sanctions de l'article 260 TFUE | non représentées | [D] | somme forfaitaire minimale 12,46 M€, astreinte de base 3 000 €/jour : négligeables |
| Régime monétaire des trois variantes | BCE + prime souveraine en écart à la référence | [H] | isoler l'effet des réactions européennes |

Le code (`src/m26_europe_institutions.py`) permet de définir d'autres scénarios (`ScenarioInstitutionnel`), par
exemple une durée d'amende différente, un choc de prime plus fort ou plus long, ou la neutralisation de la prime par
une intervention de la BCE.
