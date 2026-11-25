# Avant-propos {-}

Cet ouvrage présente un modèle macroéconométrique de l'économie française construit à partir de données publiques,
et l'utilise pour comparer les programmes économiques de trois candidats à l'élection présidentielle de 2027. Il a
une double ambition : documenter de manière complète un outil de simulation, et permettre au lecteur non spécialiste
mais motivé de comprendre les mécanismes économiques en jeu, les désaccords entre écoles de pensée et ce qu'un modèle
peut — et ne peut pas — dire des choix politiques.

**Statut du document.** Il s'agit d'une **version provisoire**, clairement datée. Les programmes des candidats ne sont
pas définitifs : La France insoumise a annoncé un chiffrage complet pour le début de 2027, Édouard Philippe un
« volume 2 » de son programme pour janvier 2027, et le Rassemblement national n'a ventilé qu'une partie de ses
économies. Le corpus est arrêté au 24 novembre 2026. La procédure de mise à jour (corpus, simulations, régénération du
document) est décrite en annexe \ref{sec:annexe-j}, et la liste des éléments à actualiser figure au chapitre
\ref{sec:conclusion}.

**Ce que ce document n'est pas.** Ce n'est ni une prévision, ni un classement des candidats, ni une prise de
position. Les simulations sont des scénarios conditionnels : elles décrivent les conséquences des programmes *selon
ce modèle et sous des hypothèses explicites*. Aucun « vainqueur » n'est désigné ; les conclusions distinguent les
critères (activité, emploi, finances publiques, distribution, contraintes institutionnelles) et ce qui résiste aux
variantes.

**Comment le lire.** Le lecteur pressé peut lire l'introduction (chapitre \ref{sec:intro}), la présentation des
programmes (chapitre \ref{sec:programmes}), les résultats (chapitre \ref{sec:resultats}), la robustesse (chapitre
\ref{sec:robustesse}) et la conclusion (chapitre \ref{sec:conclusion}). Le lecteur qui souhaite apprendre l'économie
qui sous-tend le modèle lira le chapitre \ref{sec:theorie} (fondements théoriques), le chapitre \ref{sec:transmission}
(mécanismes de transmission) et le chapitre \ref{sec:comportements} (limites des hypothèses comportementales). Le
lecteur technique trouvera l'architecture, les équations, les données et la validation aux chapitres
\ref{sec:architecture} à \ref{sec:donnees} et dans les annexes.

**Conventions.** Statuts des éléments : **[D]** donnée observée ou règle publiée ; **[E]** paramètre estimé par le
projet (ou repris d'une estimation publiée, mention « littérature ») ; **[C]** paramètre calibré ; **[H]** hypothèse
de modélisation ou de scénario ; **[X]** exploratoire. Les nombres sont écrits à la française (virgule décimale) ; les
montants en milliards d'euros (Md€) ; les effets en écart à une trajectoire de référence sans le programme.

**Reproductibilité.** Tous les résultats chiffrés des chapitres de résultats sont produits automatiquement à partir
des simulations archivées ; le code, les données et les commandes de reproduction sont dans le dépôt du projet
(annexe \ref{sec:annexe-j}). L'annexe \ref{sec:annexe-k} relie chaque conclusion aux simulations et aux sources qui la
fondent.
