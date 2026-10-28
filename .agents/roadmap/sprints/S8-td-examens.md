<!-- LTeX: language=fr-FR -->

# S8 — TD, examens et transparents

**Objectif** : `verifier` lit tout le cours, mais seules les règles communes
et celles du polycopié sont outillées. Outiller les règles mécaniques des TD,
des examens et des transparents (`TD3`, `TD8`, `EX3`, `SL8`), et donner aux
règles de jugement `TD*` et `EX*` leur matériau, comme `extraire` le fait
pour le polycopié. Suivi : [#70](https://github.com/ocourses/ocots-lint/issues/70).

**Lecture** : [décision 0009](../decisions/0009-td-examens-transparents.md) —
**proposée**.

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
  (décision 0009). Démarrage en autonomie, PR en brouillon.
