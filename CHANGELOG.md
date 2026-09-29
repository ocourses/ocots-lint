<!-- LTeX: language=fr-FR -->

# Journal des versions

Format : une section par version, la plus récente en haut. La section
« Non publié » reçoit les changements au fil des PR ; elle devient une version
au moment du tag.

---

## Non publié

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
- Test de parité restreint aux règles encore lues par les masques.
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
