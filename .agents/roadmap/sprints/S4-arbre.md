<!-- LTeX: language=fr-FR -->

# S4 — Lecture par arbre syntaxique

**Objectif** : remplacer les masques par regex par un vrai analyseur LaTeX,
derrière la même interface. Les règles voient des nœuds — environnement,
macro, maths, verbatim, commentaire, prose — avec leur position.

**Analyseur** : `pylatexenc` 2, strict, avec repli sur la lecture actuelle
pour un fichier que l'analyse refuse — [décision
0004](../decisions/0004-analyseur.md), mesurée sur le corpus réel.

**Version livrée** : `v0.5.0`.

**Parité** : le test de parité avec `conventions v2.0.0` (dernier `bin/` en
Python) reste en place, **restreint aux règles pas encore migrées** : chaque
règle qui passe sur l'arbre en sort, dans la même PR. Pour les règles
migrées, la référence est le corpus figé (ci-dessous), comparé par
`instantane verifier`.

## Critères d'acceptation

Valables pour chaque PR de S4 qui touche la lecture ou une règle ; la PR
cite le résultat de `instantane verifier` sur le corpus.

1. **Tout écart est justifié.** Chaque trouvaille apparue, disparue ou
   modifiée sur le corpus figé est listée dans la PR, avec sa raison
   (limite levée, défaut de l'ancienne lecture…) ; l'ensemble est repris
   dans le bilan (S4.7). Un écart qu'on ne sait pas justifier est un bogue.
2. **Une trouvaille inchangée garde son empreinte.** Sinon, la montée en
   `v0.5.0` fermerait et rouvrirait des issues dans tous les cours. Pas de
   paire « disparue + apparue » sur la même règle, le même fichier et la
   même ligne.
3. **Une trouvaille inchangée garde son message.** Sinon, chaque issue
   `[conventions]` serait réécrite au lundi suivant. Aucune « modifiée »
   non justifiée.
4. **Aucune erreur d'analyse silencieuse.** Un fichier refusé par l'analyse
   stricte est lu par le repli et produit un avertissement avec la position
   de l'erreur. Critère testé par une fixture : la spécification de colonnes
   `>{$}l<{$}` trouvée dans le corpus.
5. **Le contrat ne bouge pas.** `test_contrat.py` passe sans régénérer les
   références ; le JSON reste au schéma 1 (un ajout compatible au plus) ; la
   sortie texte et les codes de sortie sont inchangés.
6. **Pas de ralentissement sensible.** `instantane verifier` sur le corpus
   entier reste sous **30 s** (1,9 s en `v0.4.1`). C'est une alarme contre
   une erreur qui passerait inaperçue (un fichier relu par chaque règle au
   lieu d'un arbre partagé…), pas une limite d'usage. *Amendé en S4.2* : le
   seuil de 5 s était posé avant mesure ; construire les arbres des 120
   fichiers (1,8 Mo) coûte 3,2 s dans `pylatexenc` lui-même (+ 8 % pour la
   conversion en nœuds), soit 0,5 à 1,5 s de plus par cours pour
   `verifier`.
7. **Une limite levée change de dossier.** Sa fixture passe de `limites/` à
   `signale/` ou `accepte/`, et le CHANGELOG le dit.

## Corpus de référence

Figé le 2026-09-28 avec ocots-lint `0.4.1`, à `origin/main` de chaque cours
(`python -m ocots_lint.instantane`, voir `tests/README.md`). Les instantanés
restent en local (`corpus/`, ignoré par git) : ceux des cours privés citent
leur texte. Ce tableau suffit à les refaire à l'identique.

| Cours | Commit | Trouvailles | dont exemptées | Par règle |
|---|---|---|---|---|
| `mesure-integration-enseignants` | `e96a199` | 21 | 0 | C4 14, P3 7 |
| `automatique-enseignants` | `b6d30a0` | 24 | 0 | C4 3, C6 10, P2 9, P3 2 |
| `calcul-differentiel-edo-enseignants` | `192ea3c` | 184 | 0 | C4 156, C6 14, P2 5, P3 9 |
| `ocots-demo` | `0f508d6` | 2 | 2 | P3 1, P5 1 |
| **Total** | | **231** | **2** | |

Contrôles faits en figeant : `instantane verifier` rejoue les quatre
instantanés sans écart (analyse déterministe, 1,9 s) ; toutes les empreintes
sont distinctes dans chaque cours (231 pour 231), donc la comparaison par
empreinte ne confond aucune trouvaille.

## Stories

- [x] **S4.0** — Préparation, avant tout code : corpus figé et outil
  d'instantanés, critères d'acceptation, règle de repli, tests des
  constructions du corpus.
  - [x] Étape 1 — outil `python -m ocots_lint.instantane` (#31).
  - [x] Étape 2 — corpus figé : 4 cours, 231 trouvailles (#32).
  - [x] Étape 3 — critères d'acceptation ; décision 0004 amendée (strict,
    avec repli).
  - [x] Étape 4 — fixtures des constructions relevées dans le corpus
    (`longtable` et `>{$}l<{$}`, TikZ, `\%`, `align` dans une liste,
    `\pause`), en `accepte/` ou `signale/` selon la lecture actuelle, et
    une limite réelle en `limites/`.
- [x] **S4.1** — Décision écrite : choix de l'analyseur et mode de
  distribution de la dépendance ([0004](../decisions/0004-analyseur.md)).
- [x] **S4.2** — Couche de lecture `arbre.py` : nœuds typés (genre, nom,
  début, fin, ligne, colonne, enfants), contexte déclaré (`lstlisting`,
  `minted`, `Verbatim` en verbatim ; `\ensuremath` en maths), erreurs
  d'analyse stricte ; repli sur la lecture actuelle pour un fichier refusé,
  avec un avertissement. Aucune règle migrée : sorties inchangées, parité
  intacte, corpus sans écart.
  - Critère : tout le corpus s'analyse ; positions vérifiées contre la
    source sur les fixtures.
- [x] **S4.3** — En tant qu'*auteur*, je veux que C4 ignore `\verb`, `\url`,
  `\ensuremath` et les environnements verbatim, afin de ne plus être
  signalé à tort.
  - Critère : les limites C4 `url`, `verb`, `ensuremath` passent en
    `accepte/`.
  - [x] Étape 1 — C4 sur l'arbre, avec repli et avertissement.
  - [x] Étape 2 — `nettoyer` sur l'arbre, avec le même repli : sinon un `~:`
    que C4 voit désormais (cas réel : mesure, `slides_chapitre_8.tex:305`)
    part au tri au lieu de la voie mécanique, parce que `nettoyer` ne le
    voit pas.
- [x] **S4.4** — En tant que *relecteur*, je veux que P2 signale deux boîtes
  séparées par autre chose que de la prose (`\medskip`, ligne de `%`,
  figure), afin qu'une ligne de mise en page ne cache plus l'infraction.
  - Critère : les limites P2 `medskip_entre` et `figure_entre` passent en
    `signale/` ; `boite_par_macro` reste une limite (pas de développement
    de macros).
- [ ] **S4.5** — En tant qu'*auteur*, je veux que P3 reconnaisse une phrase
  finie par une formule hors texte, afin de ne plus avoir à l'exempter.
  - Critère : la limite P3 `amorce_en_maths` passe en `accepte/` ;
    `amorce_non_motivee` reste une limite (jugement).
- [ ] **S4.6** — P5 et C6 lus sur l'arbre, si cela simplifie leur code sans
  changer leurs trouvailles.
- [ ] **S4.7** — Écart de trouvailles sur le corpus relu et justifié, une
  ligne par écart, dans le bilan ; le test de parité devient un instantané
  des trouvailles du corpus.
- [ ] **S4.8** — Release `v0.5.0`, relais des conventions, montée des cours
  (mesure, démo), avec `comparer` dans la PR de montée.

## Journal

- 2026-09-28 — S4.0, étapes 1 et 2 : outil d'instantanés (#31), corpus figé
  (4 cours, 231 trouvailles). Remarque : `verifier` lancé sur une copie de
  travail lit aussi les copies de cours rangées dans des dossiers ignorés par
  git (ex. `.claude/worktrees/`) — 42 trouvailles au lieu de 21 sur le cours
  de mesure. Figer par `git archive` n'a pas ce défaut ; pour `verifier`,
  voir le backlog.

- 2026-09-29 — S4.0 étape 4, inventaire des constructions dans le corpus
  figé (occurrences) :
  - `\pause` entre deux boîtes : **35** (surtout calcul-diff). Idiome de
    SL6 : P2 ne le signale pas aujourd'hui, et S4.4 ne doit pas se mettre à
    le signaler → fixture `P2/accepte/pause_entre_boites.tex`.
  - `$` dans un nœud TikZ : 197 ; `align` dans une liste : 20 ; `\%` : 6 ;
    `>{$}l<{$}` : 8 (un fichier, refusé par l'analyse stricte → repli).
  - `\verb`, `\url`, `lstlisting` : **0**. Les limites C4 que S4.3 lève ne
    touchent aucune trouvaille réelle aujourd'hui : S4.3 garde son intérêt
    (justesse, cours à venir), mais ne fera pas bouger le corpus.
  - Faux positif réel trouvé : un transparent beamer rangé hors d'un dossier
    `slides/` (automatique, `td/td4/`) reçoit P3, que SL4 exclut. Écrit en
    limite (`P3/limites/beamer_hors_dossier_slides.tex`) ; l'arbre permet de
    reconnaître `\documentclass{beamer}` (voir backlog).
- 2026-09-29 — S4.2 : `arbre.py` en place, aucune règle ne l'utilise
  encore. `pylatexenc` 2 ne sait lire tel quel que `verbatim` et `\verb` ;
  `lstlisting`, `minted`, `Verbatim` et `\url` passent par un lecteur
  d'arguments propre à ocots-lint. Sur le corpus : 120 fichiers, 1 refusé
  (`notations.tex`, attendu), aucun trou (les nœuds de premier niveau pavent
  chaque fichier). Coût mesuré : 3,2 s pour tout le corpus, dans
  `pylatexenc` → critère 6 amendé (30 s). `instantane verifier` : aucun
  écart.
- 2026-09-29 — S4.3 : C4 sur l'arbre. `instantane verifier` sur le corpus
  (4 cours) — les 231 trouvailles existantes sont inchangées (empreintes et
  messages : critères 2 et 3) ; deux écarts, justifiés :

  | Cours | Écart | Justification |
  |---|---|---|
  | calcul-diff | + avertissement, `poly/frontmatter/notations.tex:17` | fichier refusé par l'analyse (`>{$}l<{$}`), C4 lu par le repli : critère 4, voulu |
  | mesure | + C4 `~:`, `slides/chapitre8/slides_chapitre_8.tex:305` | vrai `~:`, jusqu'ici masqué : un `\\[0.2em]` à la ligne 273 était pris pour `\[` par les masques, qui cachaient 37 lignes de prose ; fixture `C4/signale/saut_de_ligne_espace.tex` |

  Temps : 6,1 s pour le corpus entier (critère 6 : 30 s). Le même défaut de
  `\\[…]` touche encore P3 (S4.5) et `nettoyer`, qui lisent par les masques
  de maths.
- 2026-09-29 — S4.3, étape 2 : `nettoyer` lit le même texte que C4
  (`arbre.prose_ou_repli`, partagé). Le `~:` de mesure
  `slides_chapitre_8.tex:305` passe de la voie `tri` à `mecanique`. Écarts
  de `nettoyer` sur le corpus, tous justifiés : 17 corrections en moins, **toutes
  dans du texte commenté** (automatique 5, calcul-diff 8 dont une paire de
  guillemets, mesure 4), que C4 n'a jamais signalé ; 1 en plus, le `~:` de
  la ligne 305. Test ajouté : sur toutes les fixtures, `nettoyer` corrige
  un `~:` exactement là où C4 le signale — il échoue avec l'ancien
  `nettoyer`. Parité de `nettoyer` avec l'ancien outil : toujours tenue sur
  ses fixtures.
- 2026-09-29 — S4.4 : P2 sur l'arbre. Les trouvailles existantes sont
  inchangées. 24 P2 nouvelles au premier passage, toutes des boîtes sœures
  séparées seulement par un espacement ou une figure ; 8 d'entre elles
  révélaient un oubli de l'ancien code, qui comparait les noms étoile
  comprise : entrer dans une `remark*` n'était pas toléré. Corrigé
  (`remark*` est une remarque, `exercise*` un exercice), avec fixtures.
  Restent **16 écarts, tous voulus** (la cible de S4.4) :

  | Cours | Fichier:ligne | Enchaînement | Séparé par |
  |---|---|---|---|
  | calcul-diff | `poly/mainmatter/edo-existence.tex:584` | example → example | une figure |
  | calcul-diff | `slides/chap4/slides_chapitre_4.tex:545` | mycorollary → mycorollary | `\vspace` |
  | calcul-diff | `slides/chap7/slides_equations_lineaires.tex:336` | mydefinition → myproposition | `\vspace` |
  | calcul-diff | `slides/chap7/slides_equations_lineaires.tex:344` | myproposition → mycorollary | `\vspace` |
  | mesure | `poly/mainmatter/theorems-limites.tex:1241` | example → example | `\medskip` |
  | mesure | `slides/chapitre2/slides_chapitre_2.tex:310` | definition → example* | `\medskip` |
  | mesure | `slides/chapitre2/slides_chapitre_2.tex:782` | example* → example* | `\bigskip` |
  | mesure | `slides/chapitre2/slides_chapitre_2.tex:1242` | example* → example* | `\bigskip` |
  | mesure | `slides/chapitre3/slides_chapitre_3.tex:200` | remark* → example* | `\medskip` |
  | mesure | `slides/chapitre3/slides_chapitre_3.tex:278` | remark → example* | `\medskip` |
  | mesure | `slides/chapitre4/slides_chapitre_4.tex:955` | theorem → example | `\bigskip` |
  | mesure | `slides/chapitre4/slides_chapitre_4.tex:1028` | definition → example | `\medskip` |
  | mesure | `slides/chapitre5/slides_chapitre_5.tex:1340` | example → example | `\bigskip` |
  | mesure | `td/td3/td3.tex:101` | remark* → exercise | `\vspace*` |
  | mesure | `td/td3/td3.tex:152` | remark* → exercise | `\vspace*` |
  | mesure | `td/td4/td4.tex:68` | remark* → exercise | `\vspace*` |

  Sur les transparents (11 des 16), le remède attendu est l'idiome SL6 —
  `\pause` entre les deux objets d'une même idée — ou deux diapositives
  (SL3) : le tri le dira. Choix conservateur fixé par fixtures : un titre,
  une formule, `\pause` ou une commande inconnue rompent la chaîne.
  `test_exempter` : le garde-fou « verbatim » d'`exempter` est désormais
  testé avec P5, puisque P2 ne voit plus dans un verbatim.

## Bilan

*À écrire en fin de sprint.*
