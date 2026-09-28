<!-- LTeX: language=fr-FR -->

# S3 — Processus de relecture : du détecteur à la PR

**Objectif** : le processus hebdomadaire (détection, tri, correction) repose
sur `ocots-lint` pour tout ce qui est déterministe, avec des tests. Les
agents ne font que ce qui demande un jugement, et **une décision prise n'est
jamais redemandée**.

**Pourquoi avant l'arbre syntaxique (S4)** : S4 va volontairement changer
beaucoup de trouvailles. Il faut d'abord des empreintes stables, `comparer`
et les exemptions dans la boucle, pour que ce changement arrive dans les
cours sans raz-de-marée d'issues.

**Contrainte** : la détection ne change pas dans ce sprint. La sortie texte
et les codes de sortie de `verifier` restent identiques (parité).

**Version livrée** : `v0.3.0`. Architecture : [décision 0003](../decisions/0003-processus.md).

## État des lieux (2026-09-28)

```text
lundi   cours/check.yml ─► agents/check.yml ─► checkers/conventions.sh (bash)
                                                  └─ conventions/bin/verifier ─► ocots-lint v0.2.0
                                                  └─ une issue « conventions-candidate » par fichier
nuit    agents/queue.yml ─► conventions-reviewer (modèle) ─► ferme, ou promeut « conventions-style »
                         ─► conventions-fixer (modèle)   ─► PR Draft, relue par l'auteur
```

| # | Défaut | Conséquence |
|---|---|---|
| D1 | le détecteur lit la sortie texte avec une regex bash | contrat implicite, fragile à tout changement de format |
| D2 | le détecteur ne regarde que les issues *ouvertes* | une trouvaille rejetée par le tri revient chaque lundi, et coûte un nouveau tri |
| D3 | les avertissements d'exemption partent sur stderr | une exemption inutile ou sans raison reste invisible |
| D4 | toutes les trouvailles passent par le tri | un modèle juge ce qu'un outil sait déjà (correction mécanique `C4 ~:`) |
| D5 | une nouvelle version d'`ocots-lint` change les trouvailles d'un coup | beaucoup d'issues créées, modifiées ou fermées sans qu'on l'ait vu venir |
| D6 | rien ne tourne sur les PR du cours | un écart se voit le lundi suivant, pas à l'écriture |
| D7 | le détecteur est en bash, sans tests | deux bugs trouvés en une journée (code de sortie ignoré ; `.agents-ignore` sans motif) |

## Processus cible

```text
PR du cours ─► ocots-lint verifier --nouvelles <base> --format github   (secondes, fichiers modifiés)

lundi ─► ocots-lint synchroniser   (plan calculé, testé ; --dry-run)
          └─ une issue par fichier ; chaque trouvaille porte empreinte, garantie, voie
               ├─ voie « mécanique » (nettoyer sait corriger) ─► ocots-lint nettoyer ─► PR, sans modèle
               ├─ voie « correction » (garantie exact)        ─► conventions-fixer
               └─ voie « tri » (heuristique, signal)          ─► conventions-reviewer
                     ├─ confirmée ─► conventions-fixer
                     └─ rejetée   ─► ocots-lint exempter ─► PR qui n'ajoute qu'un commentaire
toute PR ─► relue par l'auteur
```

Une trouvaille rejetée reçoit une exemption **dans la source**, avec sa
raison : le lundi suivant, elle n'est plus signalée. La mémoire du processus
est le dépôt lui-même, pas l'historique des issues.

## Stories

- [x] **S3.1** — Décision [0003](../decisions/0003-processus.md) écrite et
  acceptée : le déterministe dans `ocots-lint`, le jugement dans `agents`,
  un contrat JSON versionné entre les deux.
- [x] **S3.2** — En tant que *mainteneur*, je veux une **empreinte stable**
  par trouvaille (règle, fichier, contenu normalisé de la ligne signalée,
  rang parmi les lignes identiques), afin qu'une trouvaille garde son
  identité quand le fichier bouge au-dessus d'elle.
  - Critère : fixtures où l'on insère des lignes avant une trouvaille ;
    empreinte inchangée. Exposée en JSON et en SARIF (`partialFingerprints`).
- [x] **S3.3** — En tant qu'*agent*, je veux un **contrat JSON versionné**
  (`"schema": 1`) : trouvailles avec empreinte, garantie, exemption, voie ;
  avertissements (exemptions invalides ou inutiles), afin de ne plus dépendre
  d'une regex sur du texte (D1, D3).
  - Critère : test qui fige le schéma ; test qui fige aussi le format texte
    et les codes de sortie, tant que l'ancien détecteur existe.
- [x] **S3.4** — En tant qu'*agent de tri*, je veux `ocots-lint exempter
  FICHIER:LIGNE RÈGLE "raison"`, qui n'ajoute qu'une ligne de commentaire,
  afin de consigner un rejet sans pouvoir toucher au contenu (D2).
  - Critère : `ocots-lint exempter --controler <diff>` échoue si un diff
    fait autre chose qu'ajouter des directives ; la trouvaille exemptée
    disparaît de `verifier`.
- [x] **S3.5** — En tant que *mainteneur*, je veux `ocots-lint
  synchroniser`, qui calcule le plan des issues (créer, mettre à jour,
  fermer) à partir des trouvailles et des issues existantes, afin de
  remplacer `checkers/conventions.sh` par du code testé (D7).
  - Critère : le plan est une fonction pure, testée (issues promues
    intactes, `.agents-ignore`, fichier sans trouvaille) ; `--dry-run`
    affiche le plan ; les empreintes sont inscrites dans l'issue, et une
    issue fermée sans exemption avec les mêmes empreintes n'est pas recréée
    mais signalée ; les avertissements d'exemption remontent dans l'issue.
- [x] **S3.6** — En tant que *mainteneur*, je veux que chaque trouvaille
  porte sa **voie** (`mecanique`, `correction`, `tri`), déduite de sa
  garantie et de l'existence d'une correction dans `nettoyer`, afin de ne
  payer un modèle que pour ce qui demande un jugement (D4). Une mesure
  n'ouvre jamais d'issue.
- [ ] **S3.7** — Dans `ocourses/agents` : `check.yml` appelle
  `ocots-lint synchroniser` ; la file envoie la voie `mecanique` à
  `nettoyer` sans modèle ; `conventions-reviewer` consigne un rejet par
  `ocots-lint exempter` ; `conventions-fixer` lit le JSON.
  - [x] Étape 1 — détecteur : `synchroniser` si le cours épingle
    `ocots-conventions` ≥ v2.2.0, chemin historique sinon.
  - [ ] Étape 2 — voie mécanique : `synchroniser` pose un label
    `voie:mecanique` ; la file (`next-task.sh`) l'envoie à un workflow sans
    modèle qui lance `./conventions/bin/ocots-lint nettoyer C4 <fichier>
    --appliquer`, compile, et ouvre une PR Draft liée à l'issue.
  - [ ] Étape 3 — tri : `conventions-reviewer` ignore les lignes
    `mecanique`, consigne chaque rejet par `ocots-lint exempter` (PR
    contrôlée par `exempter --controler`) ; `conventions-fixer` lit le bloc
    JSON de l'issue.
- [x] **S3.8** — En tant qu'*auteur*, je veux `verifier --nouvelles <réf>`,
  qui ne signale que les trouvailles absentes de `<réf>` (par empreinte),
  et un workflow de PR pour le cours, afin de voir un écart au moment où je
  l'écris (D6).
  - Critère : `runs-on` paramétrable (runner de l'auteur) ; quelques
    secondes sur une PR qui touche un chapitre.
- [x] **S3.9** — En tant que *mainteneur*, je veux `ocots-lint comparer`,
  qui liste les trouvailles qui apparaissent et disparaissent entre deux
  versions de l'outil (ou deux révisions du cours), afin de savoir avant une
  montée de version combien d'issues vont bouger (D5).
  - Critère : utilisé dans la PR qui monte `conventions` dans un cours ;
    sert de référence à S4.5.
- [ ] **S3.10** — Démo sur `mesure-integration-enseignants` : le plan de
  `synchroniser --dry-run` correspond à ce que fait `conventions.sh` ; puis
  un rejet consigné par exemption ne revient pas au lundi suivant.
- [ ] **S3.11** — Release `v0.3.0`, puis relais des conventions et
  épinglage du cours mis à jour.

## Découpage en PR

1. S3.2, S3.3 — empreintes et contrat JSON (`ocots-lint`).
2. S3.4 — `exempter` (`ocots-lint`).
3. S3.5, S3.6 — `synchroniser` et voies (`ocots-lint`).
4. S3.8, S3.9 — `--nouvelles` et `comparer` (`ocots-lint`).
5. S3.7 — branchement dans `ocourses/agents`, un rôle à la fois.
6. S3.10, S3.11 — démo, release, montée dans le cours.

## Hors de ce sprint

- Où tournent les jobs (runner de l'auteur) : réglé par l'auteur ; ce sprint
  rend seulement `runs-on` paramétrable là où il ajoute un workflow.
- Monter `ocots-lint` dans un cours demande trois étapes (release, relais
  des conventions, sous-module du cours) : automatisation au backlog.

## Journal

- 2026-09-28 — S3.1 à S3.3. Empreinte : contexte (ligne signalée et voisines
  non vides, sans commentaires) plutôt que la ligne seule, trop générique
  pour `\end{theorem}`. Sur `mesure-integration-enseignants` : 21
  trouvailles, 21 empreintes distinctes, inchangées après insertion de trois
  lignes en tête de chaque fichier. Limite connue : une trouvaille dont une
  ligne voisine change reçoit une nouvelle empreinte.
- 2026-09-28 — S3.4. Défaut trouvé en concevant `exempter` : deux
  directives empilées au-dessus d'une ligne, la première couvrait la seconde.
  Corrigé (une directive seule saute les commentaires seuls). Démo sur une
  copie du cours de mesure : 7 exemptions P3 posées par empreinte, P3 à 0
  (+ 7 exemptées), diff de 7 lignes ajoutées et 0 retirée accepté par
  `--controler`, empreintes inchangées.
- 2026-09-28 — S3.5 et S3.6. `synchroniser --dry-run` sur le vrai dépôt du
  cours de mesure (lecture seule) : 7 issues à créer, les mêmes 7 fichiers
  que l'ancien `conventions.sh` (simulé avec un faux `gh`). Voies : 13
  trouvailles sur 21 sont `mecanique` (12 `~:`, 1 paire de guillemets), 8 au
  `tri` (7 P3, 1 renvoi C4) — 13 tris de modèle évités.
- 2026-09-28 — S3.8 et S3.9. Sur une copie du cours de mesure, trois
  trouvailles ajoutées dans `td1.tex` : `--nouvelles HEAD` ne signale
  qu'elles (pas les 21 existantes), aussi depuis un sous-dossier ;
  `comparer` sur les deux états : +3, −0, 21 inchangées.
- 2026-09-28 — `v0.3.0` publiée avant S3.7, comme en S2 : les agents et le
  relais des conventions ont besoin d'une version à épingler. Correctif
  préalable : `nettoyer` respecte les exemptions.
- 2026-09-28 — S3.7 étape 1. `ocots-conventions` v2.2.0 : relais générique
  `bin/ocots-lint`, seul endroit où la version est épinglée.
  `ocourses/agents#30` : le détecteur délègue à `synchroniser` ; simulé sur
  le cours de mesure avec un faux `gh`, les deux chemins créent les 7 mêmes
  issues. Le cours de mesure épingle `conventions v2.2.0` (#305) et
  `template v1.1.0` (#304, par l'auteur) : il est le premier sur le nouveau
  chemin. Les autres cours restent sur l'ancien.

## Bilan

*À écrire en fin de sprint.*
