<!-- LTeX: language=fr-FR -->

# S6 — Labels et renvois

**Objectif** : outiller C5 (« la clé qu'on écrit est la clé qu'on
référence ») et P12 (un label ne se pose que si l'objet est cité), en
croisant les labels et les renvois de **tout le cours** — polycopié, TD,
transparents, examens.

**Lecture** : [décision 0006](../decisions/0006-labels.md) — **acceptée**
(option B) : labels et renvois lus dans la source (arbre, fichiers inclus
suivis), `??` et labels dupliqués dans le `.log` que la CI des cours
produit déjà ; pas de `.sty` d'instrumentation (l'ébauche de ce sprint),
faute de cas réel que la source manque.

**Version livrée** : `v0.7.0`.

## État des lieux (mesuré le 2026-09-30)

- La source donne tous les labels : 148 sur 148 (polycopié de mesure,
  comparé au `.aux`), 10 sur 10 (transparents, chapitre 5).
- La CI des cours compile chaque document touché par une PR, mais les
  références non résolues et labels dupliqués n'y sont que des
  avertissements : ils passent. Sur `main` (poly et chapitre 5 de mesure) :
  aucun.
- Prototype sur le corpus (commits figés) :

  | Cours | Labels | De résultats | Jamais cités | Préfixe ≠ objet | `\ref{hyp:…}` |
  |---|---|---|---|---|---|
  | mesure | 107 | 67 | 7 | 38 | 0 |
  | automatique | 80 | 37 | 8 | 1 | 0 |
  | calcul-diff | 142 | 77 | 18 | 0 | 0 |
  | démo | 14 | 10 | 7 | 0 | 0 |

  Les 38 de mesure sont des exercices étiquetés `exo:` quand C5 écrit
  `ex:`. **Tranché par l'auteur** : C5 ne change pas, les 38 labels (et
  leurs renvois) seront signalés puis corrigés.

## Critères d'acceptation

1. **Les trouvailles existantes ne bougent pas** (empreinte, message) :
   `instantane verifier` n'a que des apparitions, des nouvelles règles.
2. **Chaque nouvelle trouvaille est relue** sur le corpus : liste par
   règle dans le journal, avec les faux positifs corrigés ou écrits en
   limites.
3. **Garantie déclarée** pour chaque vérificateur (registre S2), et
   exemptions opérantes (`% ocots-lint: ignore P12 — raison`).
4. **Une information, un propriétaire** : la table des préfixes est celle
   de C5 dans les conventions, lue par l'outil (comme les identifiants de
   règle) ; le préfixe que le template ajoute à l'ancienne syntaxe vient
   de `vocabulaire.json`.
5. **Effet sur les issues mesuré** avant la montée d'un cours
   (`synchroniser --dry-run`) : de nouvelles règles ouvrent de nouvelles
   issues, le volume doit être annoncé.
6. Contrat inchangé (JSON schéma 1) ; temps sous l'alarme de 30 s.

## Stories

- [x] **S6.1** — Lecture des labels et des renvois (`labels.py`) : sur
  l'arbre, pour chaque fichier du cours — `\label{…}`, `label=…` des boîtes,
  ancienne syntaxe `{titre}{clé}` avec le préfixe du vocabulaire ; renvois
  `\ref`, `\eqref`, `\cref`, `\Cref`, `\autoref`, `\pageref`, `\nameref`,
  `\hyperref[…]`, listes `\cref{a,b}`. Index des renvois bâti sur **tout le
  cours** (dossier courant), quel que soit le périmètre vérifié.
  - Critère : sur le polycopié et un chapitre de transparents de mesure,
    labels lus = labels du `.aux`.
  - Dans le template : `prefixe` dans `vocabulaire.json` pour les
    environnements à ancienne syntaxe (ajout compatible au schéma 1).
- [x] **S6.2** — En tant qu'*auteur*, je veux que l'outil signale un label
  jamais cité dans le cours (P12, C5), afin de ne pas maintenir des clés
  pour rien.
- [x] **S6.3** — En tant qu'*auteur*, je veux que l'outil signale un
  préfixe qui ne correspond pas à l'objet étiqueté (C5 : `thm:` pour un
  théorème…), la table étant lue dans les conventions.
- [x] **S6.4** — En tant qu'*auteur*, je veux qu'une hypothèse citée par
  `\ref` au lieu de `\eqref` soit signalée (C5) — aucune au corpus
  aujourd'hui : la règle verrouille l'usage.
- [x] **S6.5** — Dans `ocourses/agents`, `latex-pr.yml` : les références
  non résolues et labels multiplement définis du `.log` **font échouer la
  PR** (tranché par l'auteur ; C5 : « un `??` est un bug »), avec la liste
  dans le rapport.
- [x] **S6.6** — Release `v0.7.0`, relais des conventions, montée des
  cours, avec `comparer` et `synchroniser --dry-run`.

## Journal

- 2026-09-30 — Préparation : mesures (labels du `.aux` contre la source,
  coût de compilation, prototype C5/P12 sur le corpus), décision 0006
  proposée, sprint réécrit. Tranché par l'auteur : 0006 option B (le
  journal instrumenté passe au backlog) ; C5 garde `ex:` ; `??` en échec de
  PR.
- 2026-09-30 — S6.1 : `ancienne_syntaxe` dans le vocabulaire du template
  (ocots-latex-template#71 : forme, préfixe, `sans_doublon`, vérifiés
  contre `tex/`, éprouvés par 6 mutations ; les boîtes étoilées ignorent le
  label). `labels.py` dans l'outil. **Critère tenu** : labels lus =
  labels du `.aux`, 148 sur 148 (polycopié de mesure, 10 fichiers inclus)
  et 10 sur 10 (transparents, chapitre 5), sans les faux `label=\alph*)`
  des listes. Tout le cours de mesure : 308 labels, 534 renvois, lus en
  2 s. Le template est passé en v1.4.0 entre-temps, vocabulaire inchangé.
- 2026-09-30 — S6.2 : règle C5 (`regles/c5.py`), label jamais cité dans
  le cours. Les fixtures sont vérifiées depuis leur dossier, comme un cours
  depuis sa racine ; la parité avec l'ancien outil retire de `--list` les
  règles qu'il ne connaît pas. **Critère 1 tenu** : `instantane verifier` —
  252 inchangées, 109 C5 apparues (et le nom C5 ajouté à l'avertissement du
  fichier refusé de calcul-diff). **Relecture** (critère 2) :

  | Cours | C5 | Sections, chapitres, parties | Boîtes | Figures, tableaux, équations |
  |---|---|---|---|---|
  | mesure | 42 | 34 (dont 17 recopiées dans les transparents) | 8 (6 exercices d'examen) | 0 |
  | automatique | 22 | 5 | 6 | 11 (dont 7 dans les transparents du TD 4) |
  | calcul-diff | 34 | 16 | 18 | 0 |
  | démo | 11 | 4 | 7 | 0 |

  Clés cherchées au `grep` dans tout le dépôt (tous fichiers) : aucune
  citée ailleurs. Aucun cours ne définit de macro de renvoi ni n'utilise
  `xr` : **aucun faux positif**. Limite écrite
  (`C5/limites/renvoi_par_macro.tex`). Le vocabulaire des cours n'a pas
  encore `ancienne_syntaxe` (template > v1.4.0) : les labels de
  l'ancienne syntaxe ne sont pas lus — 6 de plus (4 calcul-diff, 2 mesure)
  quand les cours monteront le template. 2,3 s sur le cours de mesure
  actuel ; 8 s pour les quatre cours du corpus.
- 2026-09-30 — **Tranché par l'auteur** : C5 reste tel quel pour les
  sections — un label de section jamais cité est signalé comme les autres
  (les 17 clés de section recopiées dans les transparents de mesure
  comprises). Template `v1.5.0` (ocots-latex-template#73) : publie
  `ancienne_syntaxe`.
- 2026-09-30 — S6.3 : préfixe ≠ objet, dans C5. La table vient des
  conventions (ocots-conventions#28 : nom LaTeX de chaque objet, et
  conjecture → `conj:`, que le template posait déjà), lue par
  `prefixes.py`, avec copie embarquée comparée au `main` des conventions
  par `amont`. Une table sans nom LaTeX pour chaque objet est illisible :
  celle des conventions ≤ v2.5.0 n'en avait que pour l'hypothèse (piège
  vu sur mesure : table d'une ligne, aucune trouvaille). **Critère 1
  tenu** : 252 inchangées, 90 apparues. **Relecture** :

  | Cours | Préfixe ≠ objet | Sans préfixe | Principaux cas |
  |---|---|---|---|
  | mesure | 44 | 10 | 38 `exo:` (exercices d'examen), `sec:` sur 3 sous-sections, `ex:` sur un exemple |
  | automatique | 11 | 13 | `table:` (→ `tab:`), `ex:`/`exem:` sur des exemples, `fig1:`, `ivp:` sur des équations |
  | calcul-diff | 12 | 0 | `exe:` (exercices), `rmk:`/`rmq:` (remarques), `ex:` sur des exemples |
  | démo | 0 | 0 | |

  Toutes conformes à la lettre de la table ; aucun objet mal attribué.
  Confusion récurrente : `ex:` pour un exemple (C5 : `exa:`, `ex:` étant
  l'exercice). Un label à la fois jamais cité et mal préfixé donne deux
  trouvailles sur la même ligne.
- 2026-09-30 — Template `v1.5.0` publié ; copie embarquée du vocabulaire
  et sous-module `tests/amont` montés. Corpus : 6 C5 « jamais cité » de
  plus, les labels de l'ancienne syntaxe annoncés en S6.2 (4 calcul-diff,
  2 mesure), rien d'autre ne bouge.
- 2026-09-30 — S6.4 : C5 signale `\ref` sur une hypothèse (label posé
  dans la famille `hypothese`, `myassumption` compris) ; `\eqref`,
  `\pageref` passent. Corpus inchangé, aucun `\ref{hyp:…}` dans les cours
  (`git grep` sur les quatre `HEAD`).

- 2026-09-30 — S6.5 : `latex-pr.yml` (ocourses/agents#41) lit le `.log`
  final d'une compilation réussie : référence non résolue ou label
  multiplement défini → PR en échec, clés dans le commentaire. Testé en
  extrayant le `run` du step (propre ✅, `??` et doublon ❌, erreur ❌
  inchangée). Impact mesuré en compilant tout `main` : mesure 44
  documents, démo 3, automatique 53 — aucun cas ; calcul-diff : 4
  transparents à labels `def:`, `prop:`… dupliqués, venus de l'ancienne
  syntaxe à clé vide. Corrigé dans le template (ocots-latex-template#74,
  `v1.5.1`), témoin négatif au harnais.
- 2026-10-01 — S6.6 : `v0.7.0` ; conventions `v2.6.0` (relais, P12 et C5
  donnent la commande) ; mesure (#380) et démo (#18) montés en template
  `v1.5.1` et conventions `v2.6.0` ; cibles relevées dans automatique#322
  et calcul-diff#83. Corpus refigé avec `v0.7.0` (457 trouvailles).

## Bilan (2026-10-01)

**Livré.**

- [`ocots-lint` v0.7.0](https://github.com/ocourses/ocots-lint/releases/tag/v0.7.0) :
  `labels.py` (labels et renvois lus sur l'arbre, objet de chaque label,
  index de tout le cours) ; **règle C5** — label jamais cité, préfixe qui ne
  nomme pas l'objet, hypothèse citée par `\ref` ; table des préfixes lue
  dans les conventions (`prefixes.py`), copie embarquée comparée chaque
  semaine au `main` des conventions.
- [`ocots-latex-template` v1.5.0](https://github.com/ocourses/ocots-latex-template/releases/tag/v1.5.0)
  (`ancienne_syntaxe` dans le vocabulaire) et
  [v1.5.1](https://github.com/ocourses/ocots-latex-template/releases/tag/v1.5.1)
  (clé vide sans étiquette).
- [`ocots-conventions` v2.6.0](https://github.com/ocourses/ocots-conventions/releases/tag/v2.6.0) :
  table de C5 lisible par l'outil (nom LaTeX de chaque objet, `conj:`
  ajouté), relais sur v0.7.0.
- `ocourses/agents#41` : `??` et labels dupliqués font échouer la PR.
- Cours montés : mesure (#380), démo (#18).

**Critères d'acceptation.**

1. Trouvailles existantes inchangées : 252 inchangées à chaque étape,
   seulement des apparitions C5 (109, puis 90, puis 6).
2. Chaque nouvelle trouvaille relue (tableaux du journal) : aucun faux
   positif ; une limite écrite (`C5/limites/renvoi_par_macro.tex`).
3. Garantie `heuristique` déclarée ; exemptions `% ocots-lint: ignore C5`
   par le mécanisme commun.
4. Une information, un propriétaire : préfixes lus dans C5 (conventions),
   préfixe de l'ancienne syntaxe dans `vocabulaire.json` (template) ; les
   copies embarquées sont vérifiées par `amont`.
5. Volume d'issues annoncé avant chaque montée (`synchroniser --dry-run`,
   v0.6.0 contre v0.7.0) : mesure 20, démo 2, automatique 6, calcul-diff 1.
6. Contrat inchangé (JSON schéma 1 ; une règle de plus) ; `verifier` sur
   mesure : 2,3 s, comme v0.6.0.

**Démo.** `check.yml` lancé à la main après la montée : `conventions :
v2.6.0`, 2 à créer — ocots-demo#19 (`suites.tex`) et #20 (`td1.tex`),
exactement le plan annoncé — et aucun avertissement de repli : la table
des préfixes est lue dans les conventions du cours.

**Ce qui a bien marché.** Mesurer d'abord : comparer les labels lus au
`.aux` (148/148) a écarté le journal instrumenté ; compiler tout `main`
avant d'activer l'échec sur `??` a trouvé les clés vides de calcul-diff,
corrigées à la source (le template) plutôt qu'en 50 retouches.

**Ce qui a coûté.** La table des conventions ≤ v2.5.0 n'avait le nom
LaTeX que pour l'hypothèse : lue telle quelle, une table d'une ligne et
aucune trouvaille de préfixe, sans erreur — d'où la règle « une table
incomplète est illisible ». Un premier correctif du template qui posait
un label vide (`label=` vide reste un label).

**Reporté au backlog.** Renvoi écrit par une macro propre au cours (limite
C5) ; la CI du template ne compile pas `examples/` — le harnais, témoin
négatif compris, n'a tourné qu'en local.
