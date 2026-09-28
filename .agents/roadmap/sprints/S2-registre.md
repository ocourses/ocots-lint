<!-- LTeX: language=fr-FR -->

# S2 — Registre, garanties, couverture

**Objectif** : chaque vérificateur déclare ce qu'il garantit, et l'outil sait
quelles règles des conventions il couvre. Un auteur peut exempter une
trouvaille justifiée ; la CI d'un cours peut lire les résultats.

**Contrainte** : la sortie texte par défaut de `verifier` reste identique à
`bin/verifier` (le test de parité reste vert jusqu'à S3). Tout ce qui est
nouveau passe par de nouvelles options ou de nouvelles commandes.

**Version livrée** : `v0.2.0`.

## Vocabulaire des garanties

| Garantie | Ce qu'elle promet |
|---|---|
| `exact` | aucun faux négatif ni faux positif connu dans le périmètre déclaré |
| `heuristique` | une trouvaille est presque toujours une infraction, mais l'outil en rate (voir `tests/fixtures/<règle>/limites/`) |
| `signal` | une trouvaille dit *où regarder* ; elle n'est pas forcément une faute |
| `mesure` | compte, ne bloque jamais (`--mesure`) |

## Stories

- [x] **S2.1** — En tant que *mainteneur*, je veux que chaque vérificateur
  soit déclaré dans un registre avec sa règle, sa garantie et son résumé,
  afin que `--list` et la couverture soient produits à partir d'une seule
  source.
  - Critère : `--list` inchangé (parité) ; test qui échoue si un
    vérificateur n'a pas de garantie du vocabulaire.
- [x] **S2.2** — En tant que *mainteneur*, je veux que la CI échoue si un
  vérificateur ou une mesure cite une règle absente de la version épinglée
  des conventions, afin qu'une renumérotation (comme celle des `SL` en
  `v2.0.0`) ne passe pas inaperçue.
  - Critère : sous-module `conventions` à `v2.0.0` ; test de cohérence.
- [x] **S2.3** — En tant que *relecteur*, je veux `ocots-lint couverture`,
  qui liste chaque règle des conventions du cours avec son vérificateur et sa
  garantie, ou « non outillée », afin d'interpréter une absence de
  trouvaille.
  - Critère : lit `./conventions` (ou `--conventions CHEMIN`) ; sortie texte
    et Markdown.
- [x] **S2.4** — En tant qu'*auteur*, je veux exempter une trouvaille
  justifiée dans la source, afin qu'une règle `signal` puisse bloquer en CI
  sans bruit.
  - Critère : `% ocots-lint: ignore P5 — raison`, sur la ligne signalée ou
    la ligne qui la précède ; raison obligatoire ; `--sans-exemptions` pour
    tout revoir ; fixtures.
- [x] **S2.5** — En tant que *mainteneur de CI*, je veux `--format json` et
  `--format sarif`, afin d'obtenir des annotations dans les PR GitHub.
  - Critère : SARIF 2.1.0 valide avec règles, garanties et lignes.
- [ ] **S2.6** — En tant qu'*auteur*, je veux `ocots-lint nettoyer`,
  identique à `bin/nettoyer`, afin que les deux outils partagent la même
  lecture.
  - Critère : test de parité (aperçu et `--appliquer` sur une copie).
- [ ] **S2.7** — Dans `ocots-conventions`, `bin/verifier` et `bin/nettoyer`
  renvoient vers `ocots-lint` ; README mis à jour. *Décision à prendre avec
  l'auteur : relais, gel ou retrait.*
- [ ] **S2.8** — Release `v0.2.0`.

## Découpage en PR

1. S2.1, S2.2, S2.3 — registre et couverture.
2. S2.4 — exemptions.
3. S2.5 — formats de sortie.
4. S2.6 — `nettoyer`.
5. S2.7 — dans `ocots-conventions`.
6. S2.8 — release.

## Journal

- 2026-09-28 — S2.1 à S2.3. Sur `mesure-integration-enseignants` :
  46 règles, 5 vérifiées, 2 mesurées seulement (C1, C3), 39 non outillées.
  Le cours épingle encore les conventions à `v1.0.0-53-g88c6a56`.
- 2026-09-28 — S2.4 (exemptions). S2.5 : les dépôts de cours sont privés, et
  le code scanning (SARIF) n'y est pas gratuit. Ajout d'un format `github`
  (annotations de workflow), qui marche partout ; SARIF gardé pour les
  dépôts publics.

## Bilan

*À écrire en fin de sprint.*
