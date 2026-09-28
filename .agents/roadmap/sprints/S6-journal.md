<!-- LTeX: language=fr-FR -->

# S6 — Journal de compilation

**Objectif** : voir le document tel que LaTeX l'a composé — macros
développées, `\input` suivis, conditionnels tranchés — grâce à un `.sty`
d'instrumentation injecté seulement à la compilation de vérification.

**Version livrée** : `v0.6.0`.

## Stories (à affiner en début de sprint)

- [ ] **S6.1** — Décision écrite : format du journal, mode d'injection
  (`latexmk -usepretex`), ce que le journal enregistre.
- [ ] **S6.2** — `ocots-lint.sty` : hooks `env/<boîte>/begin|end` et
  `\label`/`\ref`, qui écrivent un journal JSON (fichier, ligne, boîte, label).
  Testé par compilation de fixtures et comparaison à un journal de référence.
- [ ] **S6.3** — En tant que *relecteur*, je veux que P2 et P5 lisent aussi le
  journal, afin de voir une boîte ouverte par une macro.
- [ ] **S6.4** — En tant qu'*auteur*, je veux une vérification de `P12`
  (label posé mais jamais cité) et de `C5`, afin d'outiller des règles
  aujourd'hui manuelles.
- [ ] **S6.5** — Release `v0.6.0`.

## Bilan

*À écrire en fin de sprint.*
