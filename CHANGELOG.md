<!-- LTeX: language=fr-FR -->

# Journal des versions

Format : une section par version, la plus récente en haut. La section
« Non publié » reçoit les changements au fil des PR ; elle devient une version
au moment du tag.

---

## Non publié

---

## v0.6.0 — 2026-09-30

Le vocabulaire vient du template (sprint S5) : plus aucun nom
d'environnement du template dans l'outil. Il lit `template/vocabulaire.json`
du cours (`ocots-latex-template` ≥ `v1.2.0`), par familles, avec repli sur
une copie embarquée. Contrat inchangé (JSON au schéma 1, sortie texte,
codes de sortie ; une nouvelle cause de sortie `2` : vocabulaire illisible).
Sur les quatre cours du corpus : 242 → 252 trouvailles — 11 C6 apparues
(des `myexample` finis sans `\qedhere`, que l'ancienne liste ignorait), 1
faux positif P3 disparu (transparent rangé hors de `slides/`) ; aucune
autre trouvaille ne change d'empreinte ni de message (bilan dans
`.agents/roadmap/sprints/S5-vocabulaire.md`).

- CI **Amont**, chaque lundi (et à la demande) : la suite de tests contre le
  `main` du template, `couverture` contre le `main` des conventions. En
  échec, une issue `[amont] …` est ouverte. Outil inchangé.
- **Un transparent se reconnaît à sa classe** (S5.4) : P3 ne s'applique
  pas à un fichier qui déclare `\documentclass{beamer}` (support
  « slides » du vocabulaire du template), où qu'il soit rangé ; un fichier
  qui déclare une autre classe reçoit P3, même sous `slides/`. Sans
  `\documentclass` (chapitre inclus), le dossier `slides/` décide, comme
  avant. Limite levée (`limites/` → `accepte/`) :
  `beamer_hors_dossier_slides`. Sur le corpus : un faux positif P3 en
  moins (automatique, `td/td4/slides-td4-rk.tex`).
- **C6 lit le vocabulaire** (S5.2, étape 3) : les environnements qui posent
  un symbole de fin sont ceux que le template marque `symbole_de_fin` —
  preuves, exemples, **et leurs alias** (`myexample`, `prooffin`…), que
  l'ancienne liste ignorait. Sur le corpus : 11 trouvailles C6 nouvelles,
  toutes des `myexample` finis par une équation hors texte ou une liste sans
  `\qedhere` (transparents de calcul-diff) — le même défaut que C6 signale
  déjà pour `example`. Plus aucun nom d'environnement du template dans le
  code de l'outil.
- **P2, P3, P5 lus par familles** (S5.2, étape 2) : une boîte est un
  environnement d'une famille marquée boîte dans le vocabulaire du template,
  plus une liste de noms codée en dur. Sont désormais vues : `conjecture`,
  `citedtheorem`, `hypothesis`, `openquestion`, `difficulty` (et variantes) ;
  un environnement ajouté au template du cours l'est sans modifier l'outil.
  Tolérances de P2 par famille : une série d'exercices, alias compris
  (`exercise` puis `myexercisecb`), et l'entrée dans une remarque. P5 compte
  `remark*` comme une remarque (l'ancien code ne comptait que `remark`).
  Mesure C3 « ancienne syntaxe » : résultats et définitions du vocabulaire,
  sans leurs alias. Sur le corpus : aucune trouvaille ni mesure ne change.
- **Vocabulaire du template** (S5.2, étape 1 ; S5.3) : `ocots-lint` lit
  `template/vocabulaire.json` dans le dossier courant — les environnements du
  template du cours, par famille. À défaut, sa copie embarquée (celle du
  template `main` à cette version) : en silence sans dossier `template/`,
  avec **un** avertissement par exécution sur la sortie d'erreur si le
  `template/` n'a pas de vocabulaire (template antérieur à `v1.2.0`, ou
  sous-module non initialisé). Un vocabulaire illisible ou d'un schéma
  inconnu arrête la commande (sortie `2`, message qui dit quoi faire),
  plutôt que de rendre zéro trouvaille. Les règles n'en dépendent pas
  encore : trouvailles inchangées.
- **`verifier --nouvelles` lit la révision de base avec ses sous-modules**
  (`template/`, `conventions/`), à leur commit épinglé, quand ce commit est
  présent localement. Avant, la base était lue sans template : la voie des
  guillemets (C4) y différait, et le vocabulaire des boîtes, lu dans le
  template à partir de S5, aurait pu faire apparaître de fausses
  trouvailles nouvelles.
- Instantanés du corpus (outil de mainteneur) : les sous-modules sont
  extraits et notés ; la **voie** de chaque trouvaille est comparée.

---

## v0.5.1 — 2026-09-30

- **`verifier-pr.yml` suit la bascule de runner d'`ocourses`** : l'entrée
  `runs-on` est désormais vide par défaut. Le job tourne alors sur le runner
  de la variable `OCOURSES_RUNNER` du dépôt appelant si elle est définie,
  sinon sur `ubuntu-latest`, comme avant. Une entrée `runs-on` renseignée
  garde la priorité. Avant, un cours privé basculé sur Occidata par
  `ocourses/agents` (`bin/runner-switch`) gardait ce job sur `ubuntu-latest`,
  où il ne démarrait plus une fois le quota épuisé
  (mesure-integration-enseignants#325). Outil inchangé.

---

## v0.5.0 — 2026-09-29

Lecture par arbre syntaxique (sprint S4). C4, P2 et P3 ne regardent plus que
la prose ; les fichiers que l'analyse refuse sont lus comme avant, avec un
avertissement. Contrat inchangé (JSON au schéma 1, sortie texte, codes de
sortie). Sur les quatre cours du corpus : 231 → 242 trouvailles — 16 P2 et
1 C4 apparues, 6 faux positifs P3 disparus ; aucune trouvaille existante ne
change d'empreinte ni de message (bilan dans
`.agents/roadmap/sprints/S4-arbre.md`). Nouvelle dépendance : `pylatexenc`
2.

- **C6 : `\qedhere` avant un saut de ligne espacé** (S4.6) : pour une
  preuve finie par une formule `\[…\]`, un `\\[1em]` dans la formule
  n'est plus pris pour son ouverture ; un `\qedhere` placé avant lui n'est
  plus ignoré. Trouvailles du corpus inchangées. P5 et C6 restent lus par
  les masques : l'arbre n'y changerait aucune trouvaille du corpus.
- **P3 lu sur l'arbre syntaxique** (S4.5) : une formule hors texte
  **ponctuée** termine la phrase qui l'introduit — « … définie par
  `\[ f(x) = 0. \]` » suivi d'une boîte n'est plus une phrase qui se jette
  dans la boîte. Ponctuation lue en fin de formule, après `\\`, `\quad`,
  `\label`… ou dans un `\text{.}`. Une formule non ponctuée reste
  transparente, comme avant. Limite levée : `amorce_en_maths` (`limites/` →
  `accepte/`). Le saut de ligne espacé `\\[0.2em]` n'est plus pris pour une
  formule. Sur le corpus : aucune trouvaille nouvelle, 6 faux positifs en
  moins. Repli sur les masques pour un fichier refusé.
- **P2 lu sur l'arbre syntaxique** (S4.4) : deux boîtes sœures
  s'enchaînent aussi quand seule une **mise en page** les sépare —
  espacement (`\medskip`, `\bigskip`, `\vspace`…), figure (`figure`,
  `center`, `tikzpicture`), `\label`. Limites levées (`limites/` →
  `signale/`) : `medskip_entre`, `figure_entre`. Choix conservateur : tout le
  reste rompt la chaîne — prose, `\pause` (idiome SL6), titre, formule,
  commande inconnue. Deux boîtes écrites dans un verbatim ne sont plus
  signalées. Sur le corpus : 16 trouvailles de plus, toutes des boîtes
  séparées seulement par un espacement ou une figure.
- **Tolérances de P2 pour les boîtes étoilées** : `remark*` est une
  remarque, `exercise*` un exercice — entrer dans une remarque étoilée et
  enchaîner des exercices étoilés sont tolérés comme leurs versions
  numérotées. L'ancien code comparait les noms étoile comprise.
- **C4 lu sur l'arbre syntaxique** (S4.3) : les contrôles de typographie ne
  portent plus que sur la prose. Limites levées (fixtures passées de
  `limites/` à `accepte/`) : `~:` dans `\ensuremath`, `\url` et `\verb` ;
  `minted` et `Verbatim` sont aussi écartés. Défaut de l'ancienne lecture
  corrigé : `\\[0.2em]` (saut de ligne espacé) n'est plus pris pour le début
  d'une formule hors texte, qui masquait la prose jusqu'au `\]` suivant.
- **Repli** : pour un fichier que l'analyse syntaxique refuse, C4 garde les
  masques par regex, et `verifier` le signale par un avertissement (position
  de l'erreur), en texte comme en JSON.
- Issues de `synchroniser` : la rubrique « Exemptions à revoir » devient
  « À revoir », puisqu'elle reçoit aussi ces avertissements.
- Test de parité restreint aux règles encore lues par les masques, et aux
  fixtures : sur un cours réel, la référence est désormais le corpus figé
  (`instantane`) ; `OCOTS_LINT_CORPUS` n'est plus lu.
- **`nettoyer` lu sur l'arbre**, avec le même texte que C4 (repli compris) :
  il ne corrige plus que la prose. Il ne touche plus aux commentaires (17
  corrections en moins dans le corpus, toutes dans du texte commenté, que C4
  n'a jamais signalé), ni à `\url`, `\verb` et aux environnements verbatim
  (une URL « nettoyée » ne mène plus nulle part). Un `~:` que C4 signale est
  désormais toujours corrigeable par `nettoyer` : la voie `mecanique` suit
  C4, ce qu'un test vérifie sur toutes les fixtures.
- **Lecture par arbre syntaxique** (S4.2), pas encore utilisée par les
  règles : `ocots_lint.arbre`, sur `pylatexenc` 2 (nouvelle dépendance,
  `>=2.10,<3`), en mode strict. Nœuds typés (texte, commentaire, macro,
  environnement, maths, verbatim, groupe, special) avec leur position ;
  `lstlisting`, `minted`, `Verbatim` et `\url` lus tel quel ; un fichier
  refusé porte l'erreur et sa position (décision 0004). Sorties de
  `verifier` inchangées.
- **Instantanés du corpus** (outil de mainteneur, hors CLI) :
  `python -m ocots_lint.instantane figer|verifier` fige les trouvailles d'un
  cours à un commit, puis vérifie qu'elles n'ont pas bougé — filet de
  sécurité de S4. `reference.extraire` accepte un dépôt autre que le dossier
  courant.

---

## v0.4.1 — 2026-09-28

Correctif trouvé par la démo sur `ocourses/ocots-demo` (sprint S3).

- **`synchroniser` ne recrée pas une issue qu'une PR ouverte cite**
  (« Closes #N », ou « #N » dans son corps). Trouvé par la démo sur
  `ocourses/ocots-demo` : la file ferme l'issue quand l'agent de correction
  ouvre sa PR, et, tant que la PR attend sa relecture, les trouvailles
  restent actives sur la branche de base — le lundi suivant rouvrait l'issue.
  La PR d'exemptions du tri est couverte de la même façon.

---

## v0.4.0 — 2026-09-28

Voie mécanique (sprint S3, étape 2) : ce que `nettoyer` sait corriger ne
passe plus par un tri de modèle.

- **`synchroniser` : une issue `[nettoyer] <fichier>` pour la voie
  mécanique** (label `conventions-mecanique`), à côté de `[conventions]
  <fichier>` qui ne garde que ce qui demande un jugement. La correction se
  fait sans modèle, par PR sur la branche `ocots-lint/nettoyer/<fichier>` ;
  tant qu'une PR est ouverte sur cette branche, l'issue n'est pas recréée.

---

## v0.3.0 — 2026-09-28

Sprint S3, partie outil : tout ce que le processus de relecture demande
de déterministe. La détection ne change pas : sortie texte identique à
`bin/verifier` (conventions `v2.0.0`).

- `nettoyer` ne corrige plus une ligne exemptée pour la règle
  (`% ocots-lint: ignore C4 — …`) : l'exemption dit que la forme est voulue.

- **`verifier --nouvelles <réf>`** : seulement les trouvailles absentes de
  la révision git `<réf>` (par empreinte). Retirer une exemption fait
  réapparaître la trouvaille.
- **Workflow réutilisable `verifier-pr.yml`** pour les PR des cours :
  annotations des seules trouvailles nouvelles ; `runs-on` en paramètre.
  Testé sur ce dépôt à chaque PR.
- **Nouvelle commande `comparer`** : trouvailles apparues et disparues entre
  deux sorties JSON (deux versions de l'outil, ou deux révisions du cours),
  bilan par règle, issues à créer ou à fermer.

- **Nouvelle commande `synchroniser`** : une issue par fichier en
  infraction, à partir d'un plan calculé par une fonction pure et testée
  (`--dry-run` pour le voir). Remplace le détecteur en bash des agents, avec
  les mêmes titres et labels. Chaque issue porte un bloc JSON (empreintes,
  voies) pour les agents et les avertissements d'exemption du fichier ; un
  rejet déjà rendu n'est pas redemandé ; une analyse en échec ne touche rien.
- **Voie de chaque trouvaille** (`mecanique`, `correction`, `tri`), en JSON
  (champ `voie`, ajout compatible au schéma 1) et dans les issues.

- **Nouvelle commande `exempter`** : pose une exemption en n'ajoutant qu'une
  ligne de commentaire (par `FICHIER:LIGNE` ou `FICHIER@EMPREINTE`), refuse
  sans trouvaille active ou dans un verbatim, vérifie le résultat.
  `exempter --controler` vérifie qu'un diff ne fait qu'ajouter des
  directives valides.
- Une directive seule sur sa ligne couvre désormais la prochaine ligne qui
  n'est pas un commentaire seul : plusieurs directives s'empilent au-dessus
  d'une même ligne (auparavant, la seconde cassait la première).

- **Empreintes** : chaque trouvaille a une identité stable, indépendante du
  numéro de ligne (règle, fichier, ligne signalée et voisines non vides,
  commentaires retirés). En JSON (`empreinte`) et en SARIF
  (`partialFingerprints`).
- **Contrat JSON versionné** : `"schema": 1`, schéma publié avec le paquet
  (`schemas/verifier-1.schema.json`). Chaque trouvaille porte sa garantie,
  son empreinte et son exemption ; les avertissements sur les exemptions y
  figurent (`avertissements`). Le champ `fichier` est désormais en POSIX.
- Sorties texte et JSON figées par des références (`tests/contrat/`).

---

## v0.2.0 — 2026-09-28

Sprint S2 : registre des garanties, couverture, exemptions, formats pour la
CI, `nettoyer`. Sans exemption dans les sources, `verifier` reste identique
à `bin/verifier` (conventions `v2.0.0`).

- **Nouvelle commande `nettoyer`**, portée à l'identique de `bin/nettoyer`
  (corrections `C4` : `~:`, guillemets en `\enquote` si `csquotes` est
  chargé), sur la lecture commune. Parité testée en aperçu et en
  `--appliquer`, sur des copies.
- **Formats de sortie** : `verifier --format json|sarif|github`. `github`
  produit des annotations de workflow, affichées dans la PR même sur un dépôt
  privé ; `sarif` (2.1.0, validé contre le schéma) porte les exemptions comme
  suppressions. Un signal est un avertissement, une trouvaille heuristique
  une erreur. La sortie texte reste le défaut.
- **Exemptions** : `% ocots-lint: ignore P5 — raison` exempte une trouvaille
  justifiée (sur sa ligne, ou seule sur la ligne précédente). Raison
  obligatoire ; directives invalides ou inutiles signalées ;
  `--sans-exemptions` pour tout revoir.
- **Registre des vérificateurs** : chaque règle outillée déclare sa garantie
  (`exact`, `heuristique`, `signal`, `mesure`). `P2`, `C4`, `C6` sont
  heuristiques ; `P3`, `P5` des signaux.
- **Nouvelle commande `couverture`** : chaque règle des conventions du cours,
  avec sa garantie ou « non outillée » ; `--markdown` pour un rapport, avec
  un lien vers la règle à la révision exacte. Sortie `2` si l'outil cite une
  règle absente de ces conventions.
- Les tests vérifient que toute règle outillée existe dans les conventions
  épinglées (sous-module passé à `v2.0.0`).

---

## v0.1.0 — 2026-09-28

Première version : parité avec `ocots-conventions/bin/verifier`
(conventions `88c6a56`).

- Commande `ocots-lint verifier`, arguments et sorties identiques à
  `bin/verifier` : règles `P2`, `P3`, `P5`, `C4`, `C6`, options `--list` et
  `--mesure`.
- Un module par règle, sur une lecture commune (`lecture.py`).
- Fixtures `signale/` et `accepte/` pour chaque règle et pour les mesures.
- Limites connues écrites comme tests attendus en échec :
  - `P2` : `\medskip` ou figure seule entre deux boîtes, boîte ouverte par
    une macro ;
  - `P3` : amorce qui se termine par une équation en display, signalée à
    tort ; amorce non motivée (jugement) ;
  - `C4` : `\verb`, `\url` et `\ensuremath`, signalés à tort.
- Test de parité avec l'ancien outil, sur les fixtures et sur un corpus
  local (`OCOTS_LINT_CORPUS`).
- CI : tests sur Python 3.10 à 3.13, ruff ; un tag `vX.Y.Z` crée la release
  GitHub à partir de ce CHANGELOG.
