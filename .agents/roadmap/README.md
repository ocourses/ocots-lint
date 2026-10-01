<!-- LTeX: language=fr-FR -->

# Roadmap `ocots-lint`

## Vision

À chaque règle ajoutée à `ocots-conventions`, on peut ajouter facilement un
vérificateur, et **savoir ce qu'il garantit** : exact, heuristique, ou simple
mesure. L'outil ne remplace pas la relecture ; il dit *où regarder*, et, pour
les règles qui s'y prêtent, *qu'il n'y a rien à trouver*.

## Principes

1. **Chaque sprint livre quelque chose d'utilisable** : une version taguée
   qu'un cours peut épingler.
2. **La fiabilité se construit par les tests**, pas par la technologie :
   chaque faux positif ou faux négatif trouvé devient une fixture.
3. **Les limites connues sont des tests** (`limites/`, attendus en échec) :
   on sait ce que l'outil rate.
4. **Lire une fois, analyser ensuite** : toutes les règles partagent une même
   lecture du document (texte, puis arbre syntaxique, puis journal de
   compilation).
5. **Cohérence vérifiée avec les deux dépôts sources** : l'outil lit les
   identifiants de règle dans `ocots-conventions` et le vocabulaire dans
   `ocots-latex-template`, et le CI échoue quand ils divergent.

## Définition de « fini » pour un sprint

- toutes les stories du sprint cochées, ou reportées explicitement au backlog
  avec la raison ;
- CI verte ;
- `CHANGELOG.md` à jour et tag `vX.Y.Z` poussé ;
- démo faite sur un vrai cours, résultat noté dans le bilan du sprint ;
- bilan écrit dans le fichier du sprint.

## Sprints

| Sprint | Objectif | Version | État |
|---|---|---|---|
| [S0](sprints/S0-versions.md) | SemVer et releases pour le template et les conventions | — | fini |
| [S1](sprints/S1-parite.md) | l'outil reproduit `bin/verifier` à l'identique, avec des tests | `v0.1.0` | fini |
| [S2](sprints/S2-registre.md) | registre des vérificateurs, garanties, couverture, exemptions | `v0.2.0` | fini |
| [S3](sprints/S3-processus.md) | le processus hebdomadaire repose sur `ocots-lint` : empreintes, exemptions dans la boucle, aiguillage par garantie | `v0.3.0`, `v0.4.0`, `v0.4.1` | fini |
| [S4](sprints/S4-arbre.md) | lecture par arbre syntaxique ; les limites de P2 et C4 tombent | `v0.5.0` | fini |
| [S5](sprints/S5-vocabulaire.md) | le vocabulaire des boîtes vient du template | `v0.6.0` | fini |
| [S6](sprints/S6-journal.md) | labels et renvois (C5, P12), croisés sur tout le cours | `v0.7.0` | fini |
| [S7](sprints/S7-extraction.md) | extraction pour les règles de jugement | `v0.8.0` | à faire |

Les stories non planifiées vivent dans [`backlog.md`](backlog.md). Les choix
durables et leur pourquoi, dans [`decisions/`](decisions/).

## Format d'une story

```markdown
- [ ] **S1.3** — En tant que *relecteur*, je veux *…*, afin de *…*.
  - Critère : *un fait vérifiable (un test qui passe, une sortie identique…)*.
```

Les stories sont numérotées `S<sprint>.<n>` ; une story reportée garde son
numéro et part au backlog.
