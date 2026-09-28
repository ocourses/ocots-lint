<!-- LTeX: language=fr-FR -->

# 0001 — Un dépôt à part pour l'outil

**Date** : 2026-09-28 — **État** : acceptée

## Contexte

Le vérificateur vivait dans `ocots-conventions/bin/verifier` : un script de
regex, sans tests, dont une partie (masques, parcours des sources) était
recopiée dans `bin/nettoyer`. Il code en dur la liste des boîtes du template.

## Décision

Un troisième dépôt, `ocots-lint`, développé comme un logiciel : paquet
Python, tests unitaires et de non-régression, CI, releases.

- **Les conventions** restent la source des règles (texte et identifiants).
- **Le template** reste la source du vocabulaire (environnements, macros).
- **L'outil** lit les deux, épinglés en sous-modules, et vérifie en CI qu'il
  reste cohérent avec eux : une règle citée par un vérificateur doit exister,
  un vocabulaire d'un schéma inconnu est refusé.

L'instrumentation LaTeX (S5) vit dans l'outil, pas dans le template : une
compilation normale d'un cours n'est pas touchée.

## Conséquence acceptée

Ajouter une règle outillée demande deux PR : la règle dans les conventions,
puis le vérificateur ici. Le rapport de couverture (S2) rend visible une
règle sans vérificateur ; toutes ne sont pas outillables de toute façon.
