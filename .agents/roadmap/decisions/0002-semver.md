<!-- LTeX: language=fr-FR -->

# 0002 — SemVer pour les trois dépôts

**Date** : 2026-09-28 — **État** : acceptée

## Contexte

Un outil qui dépend de deux dépôts ne peut déclarer sa compatibilité que
contre des versions. Les traces de relecture des cours épinglent déjà la
version des conventions par `git describe` (`v1.0.0-53-g88c6a56`). Le template
n'a aucun tag.

## Décision

Chaque dépôt suit SemVer, avec un sens propre de la rupture :

| | majeur | mineur | correctif |
|---|---|---|---|
| template | un document qui compilait ne compile plus, ou doit changer ses sources | ajout ; ancien nom gardé comme alias déprécié | rendu corrigé sans toucher aux sources |
| conventions | un identifiant de règle change de sens (renuméroté, fusionné, retiré) | règle ajoutée, durcie ou assouplie ; identifiants stables | reformulation, exemples, coquilles |
| ocots-lint | CLI ou format de sortie incompatible | vérificateur, option ou garantie ajoutés | faux positif ou négatif corrigé |

Chaque version est un tag `vX.Y.Z` annoté, avec son entrée de CHANGELOG et
une release GitHub créée par la CI à partir de ce CHANGELOG.

## Repartir des conventions à `v0.1.0` ? Non

Décision de l'auteur : **garder `v1.0.0`**.

- Des traces le citent déjà ; le supprimer rend ces citations ambiguës (le
  hash reste résoluble, mais plus le nom).
- Un `v0.1.0` postérieur à `v1.0.0` inverse l'ordre pour `git describe` et
  `git tag --sort=v:refname`.
- Les identifiants des règles sont relus avec l'auteur et stables : c'est ce
  qu'un `1.x` promet.

`ocots-lint`, lui, démarre à `v0.1.0` : sa CLI est encore jeune.

Conséquence : la renumérotation `SL2`–`SL7` faite juste après `v1.0.0` fait
de la version suivante des conventions une `v2.0.0`.
