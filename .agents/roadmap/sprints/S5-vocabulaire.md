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

- [ ] **S5.0** — En tant que *mainteneur*, je veux que les instantanés
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
- [ ] **S5.2** — En tant que *mainteneur*, je veux qu'`ocots-lint` lise ce
  vocabulaire (décision 0005), et que chaque règle désigne des familles et
  non des noms, afin qu'un environnement ajouté au template soit vu sans
  modifier l'outil.
  - Critères 1, 2 et 3 (repli). Copie embarquée du vocabulaire de
    `v1.2.0`, testée égale au fichier du template épinglé en sous-module.
  - Étapes : lecture et repli (sans toucher aux règles) ; puis P2, P3, P5 ;
    puis C6 — une PR chacune, corpus sans écart à chaque fois.
- [ ] **S5.3** — En tant que *relecteur*, je veux que l'outil s'arrête avec
  un message clair devant un vocabulaire qu'il ne sait pas lire, plutôt que
  de rendre zéro trouvaille.
  - Critère 3, par fixtures : schéma `2`, JSON invalide, famille inconnue.
- [ ] **S5.4** — En tant qu'*auteur*, je veux que P3 reconnaisse un
  transparent à sa classe de document, pas seulement à son dossier
  `slides/`, afin de ne plus recevoir P3 sur un transparent rangé ailleurs
  (backlog, cas réel en S4.0 : automatique, `td/td4/`).
  - Critère : la limite `P3/limites/beamer_hors_dossier_slides.tex` passe
    en `accepte/`. *À confirmer en S5.1* : les transparents ne sont pas
    une classe du template (`beamer` + thème) ; la story tombe si le
    vocabulaire ne permet pas de les reconnaître proprement.
- [ ] **S5.5** — CI programmée d'`ocots-lint` contre le `main` du template
  et des conventions, pour voir une incompatibilité avant leur release.
- [ ] **S5.6** — Releases `v0.6.0` et conventions `v2.5.0` ; montée de
  mesure et de la démo (template `v1.2.0` et conventions `v2.5.0`), avec
  `comparer` et `synchroniser --dry-run` (sous-modules initialisés) dans
  chaque PR. Automatique et calcul-diff : ajouter la cible à #322 et #83.

## Journal

- 2026-09-30 — Préparation : état des lieux mesuré sur le corpus et le
  template `v1.1.0`, critères écrits. Décision 0005 : option B acceptée.
  `openquestion` et `difficulty` sont des boîtes (aucun emploi dans le
  corpus : critère 1 inchangé).

## Bilan

*À écrire en fin de sprint.*
