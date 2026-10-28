<!-- LTeX: language=fr-FR -->

# S8 — TD, examens et transparents

**Objectif** : `verifier` lit tout le cours, mais seules les règles communes
et celles du polycopié sont outillées. Outiller les règles mécaniques des TD,
des examens et des transparents (`TD3`, `TD8`, `EX3`, `SL8`), et donner aux
règles de jugement `TD*` et `EX*` leur matériau, comme `extraire` le fait
pour le polycopié. Suivi : [#70](https://github.com/ocourses/ocots-lint/issues/70).

**Lecture** : [décision 0009](../decisions/0009-td-examens-transparents.md) —
**acceptée**.

**Version visée** : `v0.12.0`.

## État des lieux (mesuré le 2026-10-28)

- `couverture` (conventions v2.11.0) : `TD1`–`TD9`, `EX1`–`EX7`,
  `SL1`–`SL11` non outillées ; `extraire` ne lit que le polycopié.
- Préalable ocots-conventions#26 fermé : `TD7`/`TD8` réécrites, la
  `correction` est sœur de la `question`. La candidate `TD8` du backlog
  (`\solution`) n'a plus d'objet.
- Corpus (`main`, 4 cours) : 191 exercices, 293 `correction`, 0 `\solution`
  dans `td/` et `exams/` ; voir la décision 0009 pour le constat règle par
  règle.

## Critères d'acceptation

1. Chaque vérificateur a ses fixtures `signale/` et `accepte/`, et ses
   limites connues dans `limites/`.
2. Les règles déjà outillées ne bougent pas : sur les quatre cours, mêmes
   trouvailles `C*` et `P*` avant et après (par empreinte).
3. Sur le corpus, chaque trouvaille des nouvelles règles est relue : aucune
   à tort pour `TD8` (`exact`) ; les écarts des autres sont des limites
   écrites.
4. `extraire --exercices` : autant d'exercices et de `correction` extraits
   que comptés indépendamment ; contrat JSON publié et testé.
5. `couverture --support td|exam|slides` montre les règles outillées.

## Stories

- [x] **S8.0** — En tant que *vérificateur*, je veux connaître le support
  d'un fichier (classe, sinon dossier), afin de ne lire que les fichiers de
  ma règle.
- [x] **S8.1** — `TD8` : une `correction` hors de tout `exercise`, ou
  imbriquée dans une `question`, est signalée (TD et examens).
- [x] **S8.2** — `TD3` : un `enumerate` qui numérote les questions d'un
  `exercise`, un « 1) » saisi à la main, un titre libre passé à `exercise`
  sont signalés (TD et examens).
- [x] **S8.3** — `EX3` : un barème écrit dans le texte d'un sujet
  (« (7 points) », « barème : 8 points ») est signalé ; la répartition des
  points dans une `correction` (`EX6`) ne l'est pas.
- [x] **S8.4** — `SL8` : une couleur en dur, ou un réglage de thème, posé
  dans le corps d'un transparent est signalé.
- [x] **S8.5** — En tant qu'*agent de relecture*, je veux `ocots-lint
  extraire --exercices` : chaque exercice des TD et des examens avec ses
  questions, leurs corrections, son barème et ses renvois, et chaque
  document avec ses consignes, afin de juger `TD4`–`TD6`, `EX1`, `EX2`,
  `EX4`–`EX6` sans relire les fichiers entiers.
- [x] **S8.6** — `couverture --support exam` liste aussi les `TD*`
  (prérequis de `exam.md`).
- [ ] **S8.7** — Dans `ocourses/agents` : rôle de relecture des TD et des
  examens à partir de l'extraction, essayé en local puis sur Albert sur un
  TD et un examen, comparé au jugement de l'auteur. *Demande l'auteur.*
- [ ] **S8.8** — Conventions : `TD3`, `TD8`, `EX3`, `SL8` disent qu'elles
  sont vérifiées ; la méthode renvoie à `extraire --exercices`. Release
  `v0.12.0`, relais, montée des quatre cours.

## Journal

- 2026-10-28 — Préparation : #70 et les règles relues ; corpus mesuré
  (décision 0009). Démarrage en autonomie, PR en brouillon (#90).
- 2026-10-28 — S8.0 : `support_de` (classe, sinon dossier). Référence
  prise sur `main` des quatre cours ; à chaque story, trouvailles `C*`/`P*`
  et avertissements comparés par empreinte : **aucun écart** (critère 2).
- 2026-10-28 — S8.1 `TD8` : 9 trouvailles (automatique, corrigés après
  `\end{exercise}`), toutes justes. Écart trouvé en route : 39 corrigés
  de sous-questions d'automatique (td1), placés dans la question après la
  sous-question, signalés à tort par la première version — ils en sont
  les sœurs, conformes (fixture `accepte/`).
- 2026-10-28 — S8.2 `TD3` : 18 trouvailles (mesure, `enumerate` dans
  l'exercice), échantillon relu, toutes des questions. S8.3 `EX3` :
  automatique 53, mesure 17, tous relus. Écarts écartés par le motif :
  `11pt` du préambule, « 3 points d'intersection » d'un corrigé.
  S8.4 `SL8` : automatique 1 (`\color{red}` dans une formule) ; les deux
  `\color{\ocotscolor{…}}` des légendes d'automatique acceptés.
- 2026-10-28 — S8.5 `extraire --exercices`. **Critère 4 tenu** :
  exercices extraits = `\begin{exercise…}` comptés indépendamment
  (commentaires et verbatims retirés, transparents exclus), fichier par
  fichier — mesure 76, automatique 104, calcul-diff 8, démo 3 ; corrigés
  rattachés = comptés : 183, 109, 1, 0. Écarts trouvés en route et
  corrigés : deux corrigés d'une même question, le second écrasait le
  premier (→ une liste par question) ; 9 corrigés hors exercice absents
  (→ `hors_exercice`) ; une partie de mesure (`docpart`) contient ses
  exercices, son titre embarquait tout (→ paragraphes avant le premier
  exercice) ; les consignes sont dans `contenu.tex`, pas dans le fichier
  qui déclare la classe (→ consignes là où elles sont écrites). Relu
  contre la source : un sujet de mesure (2024-2025, session 1 : 6
  exercices, 2 parties, consignes, labels) et le TD1 d'automatique
  (numérotation 2.1–2.5, place et longueur des corrigés), sans écart.
  En relisant, un `enumerate` dont chaque item porte son corrigé
  (automatique, 3) : `TD3` le voit désormais. Temps : 1,2 s sur
  automatique.
- 2026-10-28 — S8.6 : `couverture --support exam` liste les `TD*`.
  Couverture (conventions v2.11.0) : 67 règles, **10 vérifiées** (6 avant),
  3 mesurées, 34 non outillées, 20 hors ocots-lint.
- 2026-10-28 — Issue au template (famille des corrigés) : la création
  depuis l'agent a été refusée (écriture hors de ce dépôt) ; texte au
  backlog, à ouvrir par l'auteur.

## Bilan d'étape (2026-10-28, avant S8.7 et S8.8)

**Livré dans #90** : `TD8` (exact), `TD3`, `EX3`, `SL8` (heuristiques),
`extraire --exercices` et son contrat, `support_de`, `couverture
--support exam`. 681 tests ; `C*`/`P*` inchangés sur les quatre cours.

**Une montée fait apparaître** : mesure 35 (`TD3` 18, `EX3` 17),
automatique 66 (`EX3` 53, `TD8` 9, `TD3` 3, `SL8` 1), calcul-diff et démo
0. Les 53 `EX3` d'automatique sont surtout des sujets anciens (2014–2023,
dont `archive/`) : une ligne `.agents-ignore` les écarterait si l'auteur
ne compte pas les reprendre.

**À trancher par l'auteur** : la lecture de `SL8` sur les couleurs du
thème (décision 0009, point 1) ; la décision 0009 elle-même.
