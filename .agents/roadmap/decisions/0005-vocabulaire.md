<!-- LTeX: language=fr-FR -->

# 0005 — Vocabulaire des boîtes : publié par le template, lu dans le cours

**Date** : 2026-09-30 — **État** : proposée

## Contexte

`ocots-lint` code en dur les noms d'environnements du template : `BOX` dans
`lecture.py` (lu par P2, P3, P5), les tolérances de P2 (`exercise`,
`remark`), P5 (`remark`), C6 (`proof`, `proofend`, `example`). Un
environnement ajouté au template n'est pas vu tant qu'on ne modifie pas
l'outil, et rien ne signale l'écart.

Mesure du 2026-09-30, template `v1.1.0` :

- **Le template définit des boîtes que l'outil ignore** : `conjecture`,
  `citedtheorem`, `hypothesis`, `openquestion`, `difficulty` (et leurs
  variantes). Aucune n'est employée dans les quatre cours du corpus
  aujourd'hui : passer au vocabulaire du template **ne doit changer aucune
  trouvaille** sur le corpus.
- **Six mécanismes de définition** dans les `.sty` : `\NewDocumentEnvironment`,
  `\newenvironment`, `\newtheorem`, `\NewTColorBox`, `\ocots@taggedenv`,
  `\ocotsaliasenv` (alias `my…` de compatibilité). Lire les `.sty` pour en
  déduire la liste n'est pas raisonnable ; le template doit la publier.
- **Tous les environnements du template ne sont pas des boîtes au sens de
  P2** : `proof` (199 emplois), `question` (488), `correction` (128),
  `slide` (294). Chaque règle doit dire à quelles *familles* elle
  s'applique, pas à une liste de noms.
- **Les cours n'ont pas tous le même template** : mesure et la démo
  épinglent `v1.1.0` ; automatique et calcul-diff un commit antérieur à
  `v1.0.0`, sans fichier de vocabulaire possible.

## Options

| | A. Vocabulaire embarqué dans `ocots-lint` | B. Vocabulaire du template du cours, repli embarqué |
|---|---|---|
| Source | copie du `vocabulaire.json` du template, figée à chaque release d'`ocots-lint` | `template/vocabulaire.json` du cours (la version qu'il épingle) ; sinon la copie embarquée, avec un avertissement |
| Nouvel environnement dans le template | vu à la release suivante d'`ocots-lint`, puis à la montée des conventions | vu dès que le cours monte son template |
| Cohérence | la version de l'outil décide ; un cours sur un vieux template est lu avec les noms récents (sans effet : un nom absent n'est pas employé) | le cours est lu avec **son** template ; l'outil et le template du cours peuvent diverger, ce que l'avertissement et le schéma rendent visible |
| Cours sans fichier (template < `v1.2.0`) | rien à faire | copie embarquée + avertissement, en attendant sa montée |
| Complexité | une source | deux sources, un avertissement, un test de plus |

## Recommandation

**B**, pour trois raisons :

1. C'est le principe 5 de la roadmap : l'outil lit le vocabulaire *dans*
   `ocots-latex-template`, et diverger doit se voir.
2. Le template et les conventions ont déjà chacun leur épinglage dans le
   cours ; A ferait dépendre la lecture des boîtes du pin des conventions
   (qui épingle `ocots-lint`), pas de celui du template.
3. Le repli est de toute façon nécessaire : deux cours sur quatre ont un
   template trop ancien pour publier le fichier, un fichier isolé n'a pas
   de `template/`, et un instantané (`git archive`) n'inclut pas les
   sous-modules.

Dans les deux cas :

- **schéma versionné** (`"schema": 1`) ; un schéma inconnu arrête l'outil
  (sortie `2`, message clair), jamais zéro trouvaille silencieuse ;
- ce qui ne vient pas du template reste dans `ocots-lint` : environnements
  de maths et verbatim, commandes de mise en page de LaTeX (`\medskip`…),
  figures standard ;
- l'avertissement de repli est **par dépôt**, sur la sortie d'erreur : il
  n'entre pas dans le corps des issues, pour ne pas les réécrire chaque
  lundi.

## Décision

*À prendre par l'auteur avant S5.2.*
