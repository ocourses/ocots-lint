<!-- LTeX: language=fr-FR -->

# Journal des versions

Format : une section par version, la plus récente en haut. La section
« Non publié » reçoit les changements au fil des PR ; elle devient une version
au moment du tag.

---

## Non publié

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
- CI : tests sur Python 3.10 à 3.13, ruff.
