<!-- LTeX: language=fr-FR -->

# S0 — Versions du template et des conventions

**Objectif** : qu'un cours épingle des versions *nommées* du template et des
conventions, et que `ocots-lint` puisse déclarer avec lesquelles il est
compatible.

**Hors de ce dépôt** : les PR se font dans `ocots-latex-template` et
`ocots-conventions`. Ce fichier en garde le suivi.

## Stories

- [ ] **S0.1** — En tant qu'*auteur de cours*, je veux une politique SemVer
  écrite dans le README des conventions, afin de savoir si une mise à jour peut
  rendre fausses les citations de règles de mes traces de relecture.
  - Critère : le README dit ce qui fait monter majeur (identifiant renuméroté,
    fusionné, retiré), mineur (règle ajoutée, durcie, assouplie), correctif
    (reformulation, exemples).
- [ ] **S0.2** — En tant qu'*auteur de cours*, je veux une politique SemVer
  écrite dans le README du template, afin de savoir si une mise à jour peut
  casser la compilation de mon cours.
  - Critère : le README dit ce qui fait monter majeur (environnement, macro ou
    option retirés ou renommés sans alias), mineur (ajout, alias déprécié),
    correctif (rendu corrigé sans toucher aux sources).
- [ ] **S0.3** — Release `ocots-conventions v1.1.0` : la section « Non publié »
  du CHANGELOG devient une version, tag et release GitHub.
- [ ] **S0.4** — Premier tag `ocots-latex-template`, avec un CHANGELOG
  initial et une release GitHub.
- [ ] **S0.5** — En tant que *mainteneur*, je veux qu'un tag poussé crée la
  release GitHub à partir du CHANGELOG, afin de ne pas oublier de publier.
  - Critère : workflow `release.yml` dans chacun des deux dépôts.

## Décision en attente

Faut-il supprimer le tag `v1.0.0` des conventions et repartir de `v0.1.0` ?
Avis de l'agent : **non**. Des traces de relecture le citent déjà
(`v1.0.0-53-g88c6a56` dans `mesure-integration-slides-ch2`), et un `v0.1.0`
postérieur à un `v1.0.0` inverserait l'ordre des versions pour
`git describe` et `git tag --sort=v:refname`. Voir la
[décision 0002](../decisions/0002-semver.md).

## Bilan

*À écrire en fin de sprint.*
