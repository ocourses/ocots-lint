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
   entier reste sous 5 s (1,9 s en `v0.4.1`).
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

- [ ] **S4.0** — Préparation, avant tout code : corpus figé et outil
  d'instantanés, critères d'acceptation, règle de repli, tests des
  constructions du corpus.
  - [x] Étape 1 — outil `python -m ocots_lint.instantane` (#31).
  - [x] Étape 2 — corpus figé : 4 cours, 231 trouvailles (#32).
  - [x] Étape 3 — critères d'acceptation ; décision 0004 amendée (strict,
    avec repli).
  - [ ] Étape 4 — fixtures des constructions relevées dans le corpus
    (`longtable` et `>{$}l<{$}`, TikZ, `\%`, `align` dans une liste,
    `\pause`), en `accepte/` ou `signale/` selon la lecture actuelle.
- [x] **S4.1** — Décision écrite : choix de l'analyseur et mode de
  distribution de la dépendance ([0004](../decisions/0004-analyseur.md)).
- [ ] **S4.2** — Couche de lecture `arbre.py` : nœuds typés (genre, nom,
  début, fin, ligne, colonne, enfants), contexte déclaré (`lstlisting`,
  `minted`, `Verbatim` en verbatim ; `\ensuremath` en maths), erreurs
  d'analyse stricte ; repli sur la lecture actuelle pour un fichier refusé,
  avec un avertissement. Aucune règle migrée : sorties inchangées, parité
  intacte, corpus sans écart.
  - Critère : tout le corpus s'analyse ; positions vérifiées contre la
    source sur les fixtures.
- [ ] **S4.3** — En tant qu'*auteur*, je veux que C4 ignore `\verb`, `\url`,
  `\ensuremath` et les environnements verbatim, afin de ne plus être
  signalé à tort.
  - Critère : les limites C4 `url`, `verb`, `ensuremath` passent en
    `accepte/`.
- [ ] **S4.4** — En tant que *relecteur*, je veux que P2 signale deux boîtes
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

## Bilan

*À écrire en fin de sprint.*
