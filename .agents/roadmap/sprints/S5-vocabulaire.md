<!-- LTeX: language=fr-FR -->

# S5 — Le vocabulaire vient du template

**Objectif** : plus aucun nom d'environnement du template codé en dur dans
`ocots-lint`. Le template publie la description de ses environnements
(`vocabulaire.json`) ; l'outil la lit, par *famille* (résultat, exemple,
remarque, preuve…), et vérifie qu'il en connaît le schéma.

**Source du vocabulaire** : [décision 0005](../decisions/0005-vocabulaire.md)
— **acceptée** (option B) : le template du cours, avec repli sur une copie
embarquée.

**Versions livrées** : `ocots-lint` `v0.6.0`, `ocots-latex-template`
`v1.2.0`, `ocots-conventions` `v2.5.0` (relais).

## État des lieux (mesuré le 2026-09-30)

Ce que l'outil code en dur aujourd'hui, et qui vient du template :

| Où | Quoi |
|---|---|
| `lecture.py`, `BOX` (lu par P2, P3, P5) | `definition`, `theorem`, `proposition`, `corollary`, `lemma`, `example`, `remark`, `assumption`, `exercisecb`, `exercise`, préfixe `my`, étoile |
| `regles/p2.py` | tolérances : série d'`exercise`, entrée en `remark` |
| `regles/p5.py` | `remark` |
| `regles/c6.py` | `proof`, `proofend`, `example` |

Ce qui reste dans l'outil, parce que cela ne vient pas du template :
environnements de maths et verbatim (`arbre.py`), commandes de mise en page
de LaTeX et figures standard (`regles/p2.py`), mots du renvoi en bas de
casse (C4, du français).

Sur les quatre cours du corpus :

- **boîtes employées, toutes déjà reconnues** — `exercise` 266,
  `remark` 180, `definition` 149, `example` 145, `theorem` 114,
  `proposition` 106… et les alias `my…` ;
- **boîtes du template que l'outil ignore, aucune employée** :
  `conjecture`, `citedtheorem`, `hypothesis`, `openquestion`, `difficulty`.
  Passer au vocabulaire du template ne doit donc **changer aucune
  trouvaille** du corpus : c'est le critère principal ;
- **environnements du template qui ne sont pas des boîtes au sens de P2** :
  `question` 488, `slide` 294, `proof` 199, `myframe` 133, `correction`
  128, `subquestion` 98, `docpart` 29, `proofbegin`/`proofmiddle`/`proofend`,
  `instructions`, `chapterintro` ;
- **templates épinglés** : mesure et la démo `v1.1.0` ; automatique et
  calcul-diff `6ccd939`, antérieur à `v1.0.0` (sans fichier de
  vocabulaire possible : ils passent par le repli).

## Corpus de référence

Les instantanés de S4, refigés avec `v0.5.0` aux mêmes commits (mesure
`e96a199`, automatique `b6d30a0`, calcul-diff `192ea3c`, démo `0f508d6` —
242 trouvailles). **Défaut à corriger d'abord (S5.0)** : `figer` passe par
`git archive`, qui n'inclut pas les sous-modules ; un instantané ne verrait
donc jamais le `template/` du cours, ni son vocabulaire.

## Critères d'acceptation

Valables pour chaque PR de S5 qui touche la lecture ou une règle ; la PR
cite le résultat de `instantane verifier`.

1. **Aucune trouvaille ne change sur le corpus**, empreinte et message
   compris : le corpus n'emploie aucune boîte que l'outil ignore
   aujourd'hui. Un écart est un bogue, sauf justification écrite.
2. **Plus aucun nom du template en dur dans `src/`** hors de la copie
   embarquée du vocabulaire. Un test le vérifie : il cherche dans `src/`
   les noms du vocabulaire écrits comme chaînes.
3. **Jamais de silence** : un vocabulaire au schéma inconnu, ou illisible,
   arrête l'outil (sortie `2`, message qui dit quoi faire). Un vocabulaire
   absent fait lire la copie embarquée, avec **un** avertissement par
   exécution, sur la sortie d'erreur — pas dans le corps des issues.
4. **Le vocabulaire du template est testé contre ses `.sty`**, dans les deux
   sens : un environnement listé est défini ; un environnement défini est
   listé, ou exclu explicitement (avec sa raison).
5. **Le contrat ne bouge pas** : JSON au schéma 1 (un ajout compatible au
   plus), sortie texte et codes de sortie inchangés ; `test_contrat.py`
   passe sans régénérer.
6. **Pas de ralentissement sensible** : `instantane verifier` sous 30 s
   (5,2 s en `v0.5.0`).

## Stories

- [x] **S5.0** — En tant que *mainteneur*, je veux que les instantanés
  incluent le sous-module `template/` du cours à son commit épinglé, afin
  que le corpus de référence voie le vocabulaire qu'il lira.
  - Critère : `figer` extrait aussi `template/` (et `conventions/`) ; les
    quatre cours refigés avec `v0.5.0` ; `verifier` muet (les dossiers
    `template/` et `conventions/` sont déjà exclus de l'analyse : aucune
    trouvaille ne doit changer).
- [ ] **S5.1** — Dans `ocots-latex-template` : `vocabulaire.json`, au schéma
  1, et le test qui le confronte aux `.sty` (critère 4). Release `v1.2.0`.
  - Contenu, à valider avec l'auteur dans la PR : chaque environnement du
    template avec sa **famille**, ses variantes (étoilée), ses **alias**
    (`my…`, marqués dépréciés), et les classes de document avec leur
    support (`ocots-book` → polycopié…). Esquisse :

    ```json
    {
      "schema": 1,
      "familles": {
        "resultat": "théorème, proposition, corollaire, lemme, conjecture…",
        "definition": "…", "hypothese": "…", "exemple": "…",
        "remarque": "…", "exercice": "…", "preuve": "…", "question": "…"
      },
      "environnements": {
        "theorem": {"famille": "resultat", "etoilee": true},
        "mytheorem": {"alias_de": "theorem", "deprecie": true},
        "proof": {"famille": "preuve"}
      },
      "classes": {"ocots-book": "poly", "ocots-td": "td", "ocots-exam": "exam"}
    }
    ```

  - Tranché par l'auteur (2026-09-30) : `openquestion` et `difficulty`
    (blocs étiquetés Q1, D1) **sont des boîtes** au sens de P2 et P3 — elles
    mettent quelque chose en avant, et se préparent comme toute autre
    boîte. Même famille que `assumption` (bloc étiqueté H1), à nommer dans
    la PR.
- [x] **S5.2** — En tant que *mainteneur*, je veux qu'`ocots-lint` lise ce
  vocabulaire (décision 0005), et que chaque règle désigne des familles et
  non des noms, afin qu'un environnement ajouté au template soit vu sans
  modifier l'outil.
  - Critères 1, 2 et 3 (repli). Copie embarquée du vocabulaire de
    `v1.2.0`, testée égale au fichier du template épinglé en sous-module.
  - Étapes : lecture et repli (sans toucher aux règles) ; puis P2, P3, P5 ;
    puis C6 — une PR chacune, corpus sans écart à chaque fois.
- [x] **S5.3** — En tant que *relecteur*, je veux que l'outil s'arrête avec
  un message clair devant un vocabulaire qu'il ne sait pas lire, plutôt que
  de rendre zéro trouvaille.
  - Critère 3, par fixtures : schéma `2`, JSON invalide, famille inconnue.
- [x] **S5.4** — En tant qu'*auteur*, je veux que P3 reconnaisse un
  transparent à sa classe de document, pas seulement à son dossier
  `slides/`, afin de ne plus recevoir P3 sur un transparent rangé ailleurs
  (backlog, cas réel en S4.0 : automatique, `td/td4/`).
  - Critère : la limite `P3/limites/beamer_hors_dossier_slides.tex` passe
    en `accepte/`. *À confirmer en S5.1* : les transparents ne sont pas
    une classe du template (`beamer` + thème) ; la story tombe si le
    vocabulaire ne permet pas de les reconnaître proprement.
- [x] **S5.5** — CI programmée d'`ocots-lint` contre le `main` du template
  et des conventions, pour voir une incompatibilité avant leur release.
- [x] **S5.6** — Releases `v0.6.0` et conventions `v2.5.0` ; montée de
  mesure et de la démo (template `v1.2.0` et conventions `v2.5.0`), avec
  `comparer` et `synchroniser --dry-run` (sous-modules initialisés) dans
  chaque PR. Automatique et calcul-diff : ajouter la cible à #322 et #83.

## Journal

- 2026-09-30 — Préparation : état des lieux mesuré sur le corpus et le
  template `v1.1.0`, critères écrits. Décision 0005 : option B acceptée.
  `openquestion` et `difficulty` sont des boîtes (aucun emploi dans le
  corpus : critère 1 inchangé).
- 2026-09-30 — S5.0 : `reference.extraire` extrait les sous-modules à leur
  commit épinglé, quand il est présent localement — pour les instantanés
  **et** pour `verifier --nouvelles`, dont la base aurait sinon été lue sans
  le vocabulaire du template après S5.2. Les instantanés notent les
  sous-modules extraits ; `verifier` signale un sous-module qui ne l'est
  plus ; la **voie** entre dans la comparaison. Rejeu des instantanés de
  `v0.5.0` : trouvailles et messages inchangés ; **4 voies corrigées**, C4
  guillemets `tri` → `mecanique` (calcul-diff
  `slides/calculDiff/slides_diff.tex:235`, `:236` ×2 ; mesure
  `td/td1/td1.tex:129`) : avec le template, `csquotes` est vu, comme en CI
  — c'est le piège du `--dry-run` de S4.8. Corpus refigé (8 sous-modules
  extraits sur 8), `verifier` muet.
- 2026-09-30 — S5.1 : `vocabulaire.json` dans le template
  (ocots-latex-template#62) : 72 environnements, 13 familles dont 7 boîtes,
  28 alias dépréciés, supports par classe ; vérifié contre `tex/` dans les
  deux sens, éprouvé par 10 mutations. Familles validées par l'auteur
  (`web` n'est pas une boîte ; `hypothesis` avec `assumption`). Release du
  template : par l'auteur, avec d'autres changements en cours.
- 2026-09-30 — S5.2, étape 1, et S5.3 : `vocabulaire.py` lit
  `template/vocabulaire.json` du dossier courant (comme `./conventions`),
  sinon la copie embarquée. Précision sur la décision 0005 : l'avertissement
  de repli n'est émis que si un dossier `template/` existe sans vocabulaire
  — sans `template/` (fichier isolé, fixtures), le repli est silencieux, et
  les sorties comparées par les tests de parité et de contrat ne bougent
  pas. Refus testés (S5.3) : JSON invalide, pas un objet, schéma 2, famille
  inconnue, alias vers rien, famille sans `boite`. Sous-module du template
  dans `tests/amont/` (à la racine, il était pris pour le template d'un
  cours : deux tests de `nettoyer` ont vu `csquotes`). Corpus : trouvailles
  inchangées ; un avertissement par cours, aucun des commits figés n'ayant
  encore un template `v1.2.0`.
- 2026-09-30 — S5.2, étape 2 : P2, P3, P5 et la mesure C3 lisent les
  familles (`lecture.BOX` supprimé ; motifs construits à chaque exécution
  depuis le vocabulaire). Écart avec l'ancienne liste : 12 noms ajoutés
  (`conjecture`, `citedtheorem`, `hypothesis`, `openquestion`, `difficulty`,
  variantes et alias), aucun employé dans le corpus ; retirés, des noms
  absents du template (`exercisecb`, `mytheorem*`…). Changements voulus,
  fixés par fixtures : P5 compte `remark*` (écart déclaré avec l'ancien
  outil dans `test_parite`), P2 tolère une série `exercise` →
  `myexercisecb`, `openquestion` et `conjecture` sont des boîtes. Test du
  critère 2 : aucune chaîne du code (hors docstrings) ne cite un nom
  d'environnement du template ; exceptions écrites — les homographes
  français `proposition` et `correction`, les noms de famille, et C6 en
  attente de l'étape 3. Corpus : trouvailles inchangées ; `--mesure`
  inchangé (mesure C3 : 110, 0, 0, 0). Sous-module du template monté à
  `v1.2.0` (vocabulaire identique à la copie embarquée).
- 2026-09-30 — S5.2, étape 3 : C6 lit `symbole_de_fin`. **11 C6
  nouvelles**, toutes justifiées : des `myexample` (alias de `example`, qui
  pose □ par `\pushQED`/`\popQED`, vérifié aussi dans le template
  `6ccd939` que calcul-diff épingle) finis sans `\qedhere` :

  | Fichier (calcul-diff) | Lignes | Fin |
  |---|---|---|
  | `slides/calculDiff/slides_diff.tex` | 307, 774, 787, 943 | équation hors texte |
  | `slides/chap4/slides_chapitre_4.tex` | 231 | liste |
  | `slides/chap5/slides_equations_lineaires.tex` | 73, 177, 258, 330 | équation hors texte |
  | `slides/chap5/slides_equations_lineaires.tex` | 477 | liste |
  | `slides/chap6/slides_equations_lineaires.tex` | 156 | équation hors texte |

  Mesure emploie `myexample` 24 fois, sans ce défaut. Fixture
  `C6/signale/alias_myexample.tex`, écart voulu avec l'ancien outil déclaré.
  Le test du critère 2 n'a plus d'exception de module.
- 2026-09-30 — S5.4 : `est_transparent` lit la classe déclarée par le
  fichier (supports du vocabulaire) ; sans classe, le dossier `slides/`.
  Sonde du corpus : 17 fichiers sous `slides/`, tous `beamer` ; hors
  `slides/`, un seul `beamer` (automatique `td/td4/slides-td4-rk.tex`,
  autonome, n'inclut rien) ; aucun fichier sous `slides/` d'une autre
  classe. Écart : **1 P3 disparue**, faux positif — la « phrase » citée
  n'était que `\end{myframe} \begin{myframe}{Exemple 2} \scriptsize`.
  Limite `beamer_hors_dossier_slides` levée ; fixture symétrique
  `signale/slides/classe_polycopie.tex`. Limite restante, non constatée au
  corpus : un fichier sans classe, inclus par un transparent rangé hors de
  `slides/`, reçoit P3.
- 2026-09-30 — S5.5 : workflow `amont.yml`, chaque lundi et à la demande.
  Template : sous-module à `main`, toute la suite (vocabulaire illisible,
  schéma inconnu, copie embarquée périmée). Conventions : `couverture` sur
  leur `main` (sortie 2 si une règle outillée disparaît), le sous-module
  `conventions` restant à v2.0.0 pour la parité. En échec, une issue
  `[amont] …`, une seule à la fois. Éprouvé en local : suite verte contre le
  template `main` ; `couverture` rend 2 quand `C4` est renommée dans une
  copie des conventions.

## Bilan (2026-09-30)

**Livré.**

- [`ocots-latex-template` v1.2.0](https://github.com/ocourses/ocots-latex-template/releases/tag/v1.2.0) :
  `vocabulaire.json` (72 environnements, 13 familles dont 7 boîtes, 28
  alias dépréciés, supports par classe), vérifié contre `tex/` dans les
  deux sens à chaque PR.
- [`ocots-lint` v0.6.0](https://github.com/ocourses/ocots-lint/releases/tag/v0.6.0) :
  plus aucun nom d'environnement du template dans le code (test du critère
  2) ; P2, P3, P5, C6 et la mesure C3 lisent des familles ; repli sur une
  copie embarquée, avertissement si le `template/` du cours n'a pas de
  vocabulaire, arrêt (sortie 2) sur un vocabulaire illisible ; transparents
  reconnus à leur classe ; révisions extraites avec leurs sous-modules
  (instantanés et `--nouvelles`) ; CI **Amont** chaque lundi.
- [`ocots-conventions` v2.5.0](https://github.com/ocourses/ocots-conventions/releases/tag/v2.5.0) :
  relais sur v0.6.0.
- Cours montés : mesure (mesure-integration-enseignants#360, conventions
  seules : le template était déjà en v1.2.0) et démo (ocots-demo#15,
  template et conventions). `comparer` : aucun écart dans les deux ;
  `synchroniser --dry-run` identique avant et après la montée.

**Critères d'acceptation.**

1. Trouvailles du corpus : 242 → 252, écarts tous justifiés dans le
   journal — 11 C6 (`myexample`, alias que l'ancienne liste ignorait), 1
   faux positif P3 en moins (transparent hors de `slides/`) ; 4 voies
   corrigées dans les instantanés (S5.0, le template enfin extrait).
2. Aucun nom du template en dur dans `src/` : testé, sans exception de
   module (seuls les homographes français et les noms de famille).
3. Jamais de silence : refus testés (6 cas), repli averti une fois.
4. Vocabulaire testé contre les `.sty` : dans le template, éprouvé par 10
   mutations.
5. Contrat inchangé : JSON au schéma 1, `test_contrat.py` sans régénérer ;
   une cause de sortie `2` en plus, documentée.
6. Temps : inchangé à la seconde près (lecture du vocabulaire en cache).

**Démo.** `check.yml` lancé à la main sur `ocots-demo` après la montée :
`conventions : v2.5.0 — ocots-lint synchroniser`, 0 à créer, 0 à mettre à
jour, 0 à fermer, et aucun avertissement de repli dans le journal du run —
le vocabulaire du template du cours est lu. CI Amont lancée une fois :
verte.

**Ce qui a bien marché.** Mesurer avant de construire : l'inventaire du
template (six mécanismes de définition) a évité un analyseur de `.sty` ;
celui du corpus a fixé le critère principal (aucune boîte ignorée n'y est
employée). Le test du critère 2 a trouvé seul le dernier nom en dur (la
mesure C3).

**Ce qui a coûté.** Le sous-module du template d'abord posé à la racine,
pris pour celui d'un cours (`csquotes`) ; la montée de mesure faite en
parallèle, à constater avant de préparer la PR.

**Reporté au backlog.** La montée d'automatique et de calcul-diff (#322,
#83, cibles mises à jour) ; un fichier sans classe inclus par un
transparent rangé hors de `slides/` (non constaté au corpus).
