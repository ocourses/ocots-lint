<!-- LTeX: language=fr-FR -->

# S0 — Versions du template et des conventions

**Objectif** : qu'un cours épingle des versions *nommées* du template et des
conventions, et que `ocots-lint` puisse déclarer avec lesquelles il est
compatible.

**Hors de ce dépôt** : les PR se font dans `ocots-latex-template` et
`ocots-conventions`. Ce fichier en garde le suivi.

## Stories

- [x] **S0.1** — En tant qu'*auteur de cours*, je veux une politique SemVer
  écrite dans le README des conventions, afin de savoir si une mise à jour peut
  rendre fausses les citations de règles de mes traces de relecture.
  - Critère : le README dit ce qui fait monter majeur (identifiant renuméroté,
    fusionné, retiré), mineur (règle ajoutée, durcie, assouplie), correctif
    (reformulation, exemples).
- [x] **S0.2** — En tant qu'*auteur de cours*, je veux une politique SemVer
  écrite dans le README du template, afin de savoir si une mise à jour peut
  casser la compilation de mon cours.
  - Critère : le README dit ce qui fait monter majeur (environnement, macro ou
    option retirés ou renommés sans alias), mineur (ajout, alias déprécié),
    correctif (rendu corrigé sans toucher aux sources).
- [x] **S0.3** — Release `ocots-conventions v2.0.0` (et non `v1.1.0`, voir le journal) : la section « Non publié »
  du CHANGELOG devient une version, tag et release GitHub.
- [x] **S0.4** — Premier tag `ocots-latex-template`, avec un CHANGELOG
  initial et une release GitHub.
- [x] **S0.5** — En tant que *mainteneur*, je veux qu'un tag poussé crée la
  release GitHub à partir du CHANGELOG, afin de ne pas oublier de publier.
  - Critère : workflow `release.yml` dans chacun des deux dépôts.

## Journal

- 2026-09-28 — **Décision** (auteur) : on garde le tag `v1.0.0` des
  conventions. Décision 0002 acceptée.
- 2026-09-28 — **Découvert** en complétant le CHANGELOG des conventions :
  `d690b45`, quelques heures après le tag `v1.0.0`, a intercalé un `SL2` et
  décalé `SL2`–`SL7` en `SL3`–`SL8`, sans le consigner. D'après la politique,
  c'est une rupture : la prochaine version est **`v2.0.0`**. Table de
  correspondance ajoutée au CHANGELOG.
- 2026-09-28 — PR ouvertes : S0.1, S0.3 (préparation) et S0.5 dans
  [ocots-conventions#18](https://github.com/ocourses/ocots-conventions/pull/18) ;
  S0.2, S0.4 (préparation) et S0.5 dans
  [ocots-latex-template#58](https://github.com/ocourses/ocots-latex-template/pull/58).
  Restent, après fusion : tags `conventions v2.0.0` et `template v1.0.0`.

- 2026-09-28 — PR fusionnées. Releases publiées par la CI :
  [conventions v2.0.0](https://github.com/ocourses/ocots-conventions/releases/tag/v2.0.0)
  et [template v1.0.0](https://github.com/ocourses/ocots-latex-template/releases/tag/v1.0.0).

## Bilan

Sprint clos le 2026-09-28.

- **Livré** : politique SemVer écrite dans les deux dépôts, CHANGELOG
  complets, releases publiées par la CI à chaque tag (le workflow refuse un
  tag que le CHANGELOG ne décrit pas).
- **Appris** : écrire la politique a suffi à révéler une rupture passée
  inaperçue (renumérotation `SL`). Sans table de correspondance, les traces
  qui citent `SL3` sous `v1.0.0` étaient ambiguës.
- **Pour la suite** : les cours peuvent épingler `template v1.0.0` et
  `conventions v2.0.0` au lieu d'un commit. `ocots-lint` peut désormais
  déclarer sa compatibilité par version (S5.3).
