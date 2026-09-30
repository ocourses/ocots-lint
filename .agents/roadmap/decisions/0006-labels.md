<!-- LTeX: language=fr-FR -->

# 0006 — Labels et renvois : lus dans la source, pas par un journal instrumenté

**Date** : 2026-09-30 — **État** : proposée

## Contexte

L'ébauche de S6 prévoyait un `.sty` d'instrumentation, injecté à une
compilation de vérification, qui écrirait un journal JSON (boîtes, `\label`,
`\ref`) : voir le document « tel que LaTeX l'a composé ». Motif : outiller
C5 et P12, et voir les boîtes ouvertes par une macro (limite
`P2/limites/boite_par_macro.tex`).

Mesuré le 2026-09-30, avant de construire :

- **La source suffit pour les labels.** Polycopié de mesure (`main`, 10
  fichiers inclus) : 148 labels dans le `.aux` après compilation, 148 lus
  dans la source — aucun manqué. Transparents du chapitre 5 : 10 sur 10. Le
  seul label engendré par une macro, l'ancienne syntaxe
  `\begin{theorem}{Titre}{clé}` (le template ajoute `thm:`, `def:`,
  `prop:`, `cor:`, `conj:` s'il manque), se reproduit à la lecture si le
  template publie ce préfixe ; elle a d'ailleurs presque disparu (0 emploi
  dans les deux documents mesurés sur `main`).
- **Les renvois se lisent aussi dans la source** (`\ref`, `\eqref`,
  `\cref`, `\autoref`, `\pageref`, `\nameref`, `\hyperref[…]`), et P12 exige
  de les croiser sur **tout le cours** (poly, TD, transparents, examens) :
  un journal par document compilé ne le donnerait pas mieux.
- **Ce que seule la compilation dit** — référence non résolue (`??`),
  label multiplement défini — est dans le `.log` standard de LaTeX, sans
  instrumentation. Et la CI des cours compile déjà chaque document touché
  par une PR (`latex-pr.yml` d'`ocourses/agents`), mais n'échoue que sur
  une erreur : ces avertissements passent. Mesure (`main`, poly et
  transparents du chapitre 5) : 0 et 0 — propre.
- **Compiler coûte** : 31 s pour le polycopié, 13 s pour un chapitre de
  transparents ; une trentaine de documents par cours, sur des dépôts privés
  au quota de minutes compté. Une compilation hebdomadaire de tout le corpus
  pour un journal serait chère pour ce qu'elle ajoute.

Prototype sur les quatre cours du corpus (commits figés) :

| Cours | Labels | De résultats | Jamais cités (P12) | Préfixe ≠ objet (C5) |
|---|---|---|---|---|
| mesure | 107 | 67 | 7 | 38 (exercices en `exo:`) |
| automatique | 80 | 37 | 8 | 1 (`exem:`) |
| calcul-diff | 142 | 77 | 18 | 0 |
| démo | 14 | 10 | 7 | 0 |

## Options

| | A. Journal instrumenté (ébauche) | B. Source + `.log` standard |
|---|---|---|
| Labels, renvois | `.sty` qui écrit un journal à la compilation | lus sur l'arbre, fichiers inclus suivis, sur tout le cours |
| `??`, labels dupliqués | dans le journal | dans le `.log` de LaTeX, déjà produit par `latex-pr.yml` |
| Coût en CI | une compilation de tout le cours pour vérifier | aucune compilation de plus |
| Boîte ouverte par une macro | vue | reste une limite (`boite_par_macro`) |
| Maintenance | un `.sty` à tenir à jour avec le template | le préfixe de l'ancienne syntaxe publié dans `vocabulaire.json` |

## Recommandation

**B.** La mesure ne montre aucun label que la source manque ; le seul
bénéfice propre à A est la boîte ouverte par une macro, une limite sans cas
réel au corpus. Le journal instrumenté passe au backlog, avec son critère de
retour : un cas réel que la source ne peut pas lire.

## Décision

*À prendre par l'auteur avant S6.1.*
