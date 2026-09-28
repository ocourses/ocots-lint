<!-- LTeX: language=fr-FR -->

# 0003 — Le déterministe dans `ocots-lint`, le jugement dans `agents`

**Date** : 2026-09-28 — **État** : acceptée (à affiner en début de S3)

## Contexte

Le processus hebdomadaire des cours enchaîne un détecteur en bash
(`ocourses/agents/scripts/checkers/conventions.sh`), qui ouvre une issue par
fichier à partir de la sortie texte de `verifier`, puis deux agents à modèle :
`conventions-reviewer` trie, `conventions-fixer` corrige.

Défauts constatés (détail dans [S3](../sprints/S3-processus.md)) : contrat
texte implicite, trouvailles rejetées qui reviennent chaque semaine,
avertissements perdus, garanties ignorées, montées de version sans préavis,
rien sur les PR, et un détecteur non testé où deux bugs ont été trouvés en
une journée.

## Décision

**Tout ce qui se décide sans jugement va dans `ocots-lint`, testé** :

- détecter, identifier une trouvaille (empreinte), décider de sa voie ;
- calculer le plan des issues (`synchroniser`), en fonction pure ;
- consigner un rejet (`exempter`, qui n'ajoute qu'un commentaire) ;
- corriger ce qui est mécanique (`nettoyer`) ;
- comparer deux versions (`comparer`), ne signaler que le nouveau sur une
  PR (`--nouvelles`).

**Ce qui demande un jugement reste dans `ocourses/agents`** : trier une
trouvaille heuristique ou un signal, corriger quand le remède se rédige.
Les agents consomment le **contrat JSON versionné** d'`ocots-lint`, jamais
sa sortie texte.

**La décision vit dans la source** : un rejet devient une exemption avec sa
raison, dans le fichier. Le dépôt du cours est la seule mémoire du
processus ; les issues n'en sont qu'une vue.

## Conséquences

- `checkers/conventions.sh` est remplacé par un appel à
  `ocots-lint synchroniser` ; la logique GitHub (issues) entre dans
  `ocots-lint`, derrière un `--dry-run`.
- Le rôle `conventions-reviewer` peut désormais modifier le dépôt, mais
  seulement par `ocots-lint exempter`, et un contrôle mécanique du diff le
  garantit.
- Un modèle n'est payé que pour la voie `tri` ; la voie `mecanique` ne
  consomme ni budget Albert ni tri.
