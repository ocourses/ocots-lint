<!-- LTeX: language=fr-FR -->

# S1 — Parité avec `bin/verifier`

**Objectif** : `ocots-lint verifier` produit **exactement** les mêmes
trouvailles que `ocots-conventions/bin/verifier`, et le comportement de
chaque règle est fixé par des tests.

**Pourquoi rien d'autre** : tant que l'outil ne reproduit pas l'ancien, on ne
peut pas savoir si un écart est un progrès ou une régression. Aucune
amélioration de détection dans ce sprint : les défauts connus sont écrits
comme limites (tests attendus en échec), corrigés à partir de S3.

**Version livrée** : `v0.1.0`.

## Stories

- [ ] **S1.1** — En tant que *mainteneur*, je veux un paquet Python
  installable avec une commande `ocots-lint`, afin qu'un cours l'utilise via
  `uvx` sans rien installer.
  - Critère : `uvx --from <dépôt> ocots-lint verifier --list` fonctionne.
- [ ] **S1.2** — En tant que *mainteneur*, je veux les règles `P2`, `P3`,
  `P5`, `C4`, `C6` et les mesures portées sans changement de comportement,
  dans un module par règle, sur une lecture commune (sources, masques).
- [ ] **S1.3** — En tant que *mainteneur*, je veux des fixtures `signale/` et
  `accepte/` pour chaque règle, avec les lignes attendues marquées dans le
  fichier, afin que tout changement de comportement fasse échouer un test.
- [ ] **S1.4** — En tant que *relecteur*, je veux que les limites connues de
  l'outil soient écrites comme tests attendus en échec, afin de savoir ce
  qu'une absence de trouvaille ne garantit pas.
  - Critère : `\medskip` et figure entre deux boîtes (P2), boîte ouverte par
    une macro (P2), `\verb` et `\url` (C4) sont dans `limites/`.
- [ ] **S1.5** — En tant que *mainteneur*, je veux un test de parité qui
  compare `ocots-lint` à `conventions/bin/verifier` (sous-module épinglé)
  sur toutes les fixtures, et sur un corpus local si on le fournit, afin de
  prouver l'identité des sorties.
  - Critère : `OCOTS_LINT_CORPUS=<cours> uv run pytest tests/test_parite.py`
    passe sur `mesure-integration-enseignants`.
- [ ] **S1.6** — En tant que *mainteneur*, je veux une CI (tests sur les
  versions de Python supportées, ruff), afin qu'aucune PR ne casse l'outil.
- [ ] **S1.7** — Release `v0.1.0`.

## Démo

Sur `mesure-integration-enseignants` : les sorties de
`./conventions/bin/verifier` et de `ocots-lint verifier` sont identiques
(stdout, stderr, code de sortie), règle par règle et pour `--mesure`.

## Bilan

*À écrire en fin de sprint.*
