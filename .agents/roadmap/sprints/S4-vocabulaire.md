<!-- LTeX: language=fr-FR -->

# S4 — Le vocabulaire vient du template

**Objectif** : plus aucune liste de boîtes codée en dur dans `ocots-lint`.
Le template publie la description de ses environnements ; l'outil la lit et
vérifie qu'il en connaît le format.

**Version livrée** : `v0.4.0` (et une version mineure du template).

## Stories (à affiner en début de sprint)

- [ ] **S4.1** — Dans `ocots-latex-template` : un `vocabulaire.json` versionné
  (`"schema": 1`) — boîtes et familles (résultat, exemple, remarque, preuve),
  alias dépréciés, macros de mise en page — testé contre les `.sty`.
- [ ] **S4.2** — En tant que *mainteneur*, je veux que `ocots-lint` lise ce
  vocabulaire (template en sous-module, ou celui du cours), afin qu'un
  environnement ajouté au template soit vu sans modifier l'outil.
- [ ] **S4.3** — En tant que *relecteur*, je veux que l'outil s'arrête avec un
  message clair devant un schéma qu'il ne connaît pas, plutôt que de rendre
  zéro trouvaille.
- [ ] **S4.4** — CI programmée contre le `main` du template et des
  conventions, pour voir une incompatibilité avant une release.
- [ ] **S4.5** — Release `v0.4.0`.

## Bilan

*À écrire en fin de sprint.*
