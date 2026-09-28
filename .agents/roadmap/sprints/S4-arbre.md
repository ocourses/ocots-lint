<!-- LTeX: language=fr-FR -->

# S4 — Lecture par arbre syntaxique

**Objectif** : remplacer les masques par regex par un vrai analyseur LaTeX
(candidat : `pylatexenc`), derrière la même interface. Les règles voient des
nœuds — environnement, macro, maths, verbatim, commentaire, prose — avec leur
position.

**Version livrée** : `v0.5.0`.

**Parité** : la référence reste `conventions v2.0.0` (dernier `bin/` en
Python). Dès que l'outil s'écarte volontairement de l'ancien, le test de
parité est remplacé par `ocots-lint comparer` (S3.9) sur un corpus : chaque
trouvaille qui apparaît ou disparaît est relue et justifiée (S4.5).

## Stories (à affiner en début de sprint)

- [ ] **S4.1** — Décision écrite : choix de l'analyseur (`pylatexenc`,
  `tree-sitter-latex`…), et mode de distribution de la dépendance.
- [ ] **S4.2** — Lecture commune par arbre, avec positions exactes (ligne,
  colonne) dans la source.
- [ ] **S4.3** — En tant que *relecteur*, je veux que P2 signale deux boîtes
  séparées par autre chose que de la prose (`\medskip`, ligne de `%`, figure),
  afin qu'une ligne de mise en page ne cache plus l'infraction.
  - Critère : les limites P2 correspondantes passent en `signale/`.
- [ ] **S4.4** — En tant qu'*auteur*, je veux que C4 ignore `\verb`, `\url`
  et les environnements verbatim, afin de ne plus être signalé à tort.
- [ ] **S4.5** — Écart de trouvailles sur le corpus de référence relu et
  justifié, une ligne par écart, dans le bilan.
- [ ] **S4.6** — Release `v0.5.0`.

## Bilan

*À écrire en fin de sprint.*
