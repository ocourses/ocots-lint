<!-- LTeX: language=fr-FR -->

# 0009 — TD, examens, transparents : quelles règles outiller, et comment

**Date** : 2026-10-28 — **État** : proposée (#70)

## Contexte

Après S7, seules les règles communes et celles du polycopié sont outillées.
`couverture` (conventions v2.11.0) : `TD1`–`TD9`, `EX1`–`EX7` et
`SL1`–`SL11` ne le sont pas. Le backlog nomme quatre candidates
« probablement mécaniques », à confirmer en lisant la règle : `TD3`, `TD8`,
`EX3`, `SL8`.

Le préalable de #70, ocots-conventions#26, est **tranché** (fermée) : `TD7`
et `TD8` ont été réécrites. Le corrigé d'un TD ou d'un examen est un
environnement `correction`, **frère** de la `question` qu'il corrige, dans
l'`exercise`. La candidate du backlog pour `TD8` (« `question` rouverte dans
un `\solution` ») n'a donc plus d'objet ; la règle réécrite en a un autre.

Mesuré le 2026-10-28 sur `main` des quatre cours (mesure, automatique,
calcul-diff, démo ; `td/`, `exams/`, `slides/`) :

| Règle | Ce que dit la règle | Constat au corpus |
|---|---|---|
| `TD8` | `correction` frère de la question, avant `\end{exercise}` | 39 `correction` **dans** une `question` (automatique, td1) ; 9 **hors** de tout `exercise` (examens d'automatique) |
| `TD3` | questions par `question`, jamais d'`enumerate` détourné ni de « 1) » ; `exercise` sans titre libre | 18 `enumerate` posés directement dans un `exercise` (mesure, examens) ; aucun « 1) » saisi à la main hors listes |
| `EX3` | barème par `points=`, pas dans le texte | 46 barèmes écrits à la main : `\begin{exercise}(7 points)`, « barème prévisionnel : 8 points », « Intégrale de Dirichlet - 7 points » |
| `SL8` | thème et couleurs réglés au préambule | 2 `\color` dans une légende de diapositive (automatique), tous deux sur une couleur du thème (`\ocotscolor{…}`) |

## Décisions

### 1. Quatre vérificateurs, garantie selon ce que la règle laisse au jugement

| Règle | Garantie | Pourquoi |
|---|---|---|
| `TD8` | `exact` | la place d'une `correction` dans l'arbre se lit sans ambiguïté |
| `TD3` | `heuristique` | un `enumerate` dans l'intro d'un exercice peut lister des données, pas des questions : rare, mais pas exclu |
| `EX3` | `heuristique` | « 3 points d'intersection » est de la géométrie, pas un barème : le motif écarte les cas connus, pas tous |
| `SL8` | `heuristique` | ne voit que les commandes de couleur et de thème connues |

Sur `SL8`, une couleur prise dans le thème (`\color{\ocotscolor{link}}`)
**n'est pas signalée** : elle suit le thème choisi au préambule, ce que la
règle protège (« le thème est un réglage global »). Seule une couleur en dur
(`red`, `blue!20`, `\definecolor` dans une diapositive) le casse. C'est une
lecture de la règle : l'auteur la confirme ou la corrige en relisant la PR.

La recomposition de la page de titre (`SL8`, second alinéa) reste au
jugement : un logo en dur se voit, mais la raison (le QR code de mesure,
chapitre 1) ne se voit pas. Backlog.

### 2. Le support d'un fichier, une seule fonction

`est_transparent` (P3, P2) devient un cas de `support_de(chemin, texte, v)` :
la classe déclarée (supports du vocabulaire du template), sinon le dossier
(`slides/`, `td/`, `exams/`), sinon le polycopié. Un vérificateur `TD*`,
`EX*` ou `SL*` ne lit que les fichiers de son support ; un `contenu.tex` sans
classe est reconnu par son dossier, comme un chapitre de transparents l'est
déjà.

### 3. Les règles `TD*` mécaniques valent aussi pour les examens

`exam.md` déclare `td.md` en prérequis, et `EX6` renvoie à `TD6`–`TD8` : « même
mécanique qu'en TD ». `TD3` et `TD8` lisent donc les supports `td` **et**
`exam`, et `couverture --support exam` liste les `TD*`.

### 4. Question ou correction : le nom canonique

Le vocabulaire du template range `question`, `subquestion` et `correction`
dans une même famille (« partie d'un exercice »). `TD8` doit les distinguer :
l'outil compare le **nom canonique** (la cible d'un alias : `mycorr` →
`correction`), seul endroit où il nomme un environnement du template. Si le
template publie un jour un rôle par environnement, l'outil le lira (backlog).

### 5. L'extraction des exercices, un second contrat

`extraire --exercices` : chaque `exercise` des TD et des examens, avec son
label, ses `points`, son intro, ses questions (numéro, énoncé, label), la
correction rattachée à chacune et sa place, ses renvois et ce qu'ils visent ;
et chaque document (classe, `solutions=`, champs d'examen, consignes,
parties). **Sans verdict**, comme `extraire` (décision 0007). Même numéro de
schéma (`"schema": 1`), `"extraction": "exercices"`, schéma publié à part
(`extraire-exercices-1.schema.json`) : deux formats indépendants, qui
évoluent chacun à son rythme.

## Hors de cette PR

Le rôle de relecture dans `ocourses/agents`, l'essai sur Albert, la release,
le relais et la montée des cours (#70, points 3 et 4) demandent l'auteur ou
agissent hors de ce dépôt : stories S8.7 et S8.8.
