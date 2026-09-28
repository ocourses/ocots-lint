<!-- LTeX: language=fr-FR -->

# S4 — Lecture par arbre syntaxique

**Objectif** : remplacer les masques par regex par un vrai analyseur LaTeX,
derrière la même interface. Les règles voient des nœuds — environnement,
macro, maths, verbatim, commentaire, prose — avec leur position.

**Analyseur** : `pylatexenc` 2, en mode tolérant — [décision
0004](../decisions/0004-analyseur.md), mesurée sur le corpus réel.

**Version livrée** : `v0.5.0`.

**Parité** : la référence reste `conventions v2.0.0` (dernier `bin/` en
Python) tant qu'aucune règle migrée ne s'en écarte. Ensuite, le test de
parité est remplacé par `ocots-lint comparer` (S3.9) sur un corpus (cours de
mesure, `ocourses/ocots-demo`) : chaque trouvaille qui apparaît ou disparaît
est relue et justifiée (S4.7).

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

- [x] **S4.1** — Décision écrite : choix de l'analyseur et mode de
  distribution de la dépendance ([0004](../decisions/0004-analyseur.md)).
- [ ] **S4.2** — Couche de lecture `arbre.py` : nœuds typés (genre, nom,
  début, fin, ligne, colonne, enfants), contexte déclaré (`lstlisting`,
  `minted`, `Verbatim` en verbatim ; `\ensuremath` en maths), erreurs
  d'analyse en avertissements. Aucune règle migrée : sorties inchangées,
  parité intacte.
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
