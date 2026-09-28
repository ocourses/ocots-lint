# Instructions pour les agents

## Avant toute modification

1. Lire [`.agents/roadmap/README.md`](.agents/roadmap/README.md) : où en est
   le projet, quel sprint est en cours, ce que « fini » veut dire.
2. Lire le fichier du sprint en cours dans `.agents/roadmap/sprints/`.
3. Lire les décisions dans `.agents/roadmap/decisions/` avant de remettre en
   cause un choix d'architecture.

## Règles de développement

- Tout changement de comportement d'un vérificateur passe par une **fixture** :
  un faux négatif ou un faux positif trouvé devient d'abord un test qui échoue.
- Une limite connue qu'on ne corrige pas maintenant s'écrit dans
  `tests/fixtures/<règle>/limites/` : elle reste visible et testée.
- Ne jamais citer une règle par un nombre nu : toujours son identifiant
  préfixé (`P2`, `C4`, `SL6`), tel qu'il figure dans `ocots-conventions`.
- Pas de dépendance d'exécution sans décision écrite dans
  `.agents/roadmap/decisions/`.

## Vérifications

Avant chaque commit :

```bash
uv run pytest
uvx ruff check
```

## Méthode de travail

- Une branche par story ou par petit groupe de stories, une PR par branche.
- Messages de commit Conventional Commits en français, par exemple
  `feat(P2): ignore les commandes d'espacement entre deux boîtes`.
- Toute PR qui change le comportement visible ajoute une entrée à la section
  « Non publié » de `CHANGELOG.md`.
- En fin de sprint : cocher les stories, écrire le bilan dans le fichier du
  sprint, mettre à jour l'état dans `.agents/roadmap/README.md`.
