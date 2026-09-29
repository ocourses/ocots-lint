<!-- LTeX: language=fr-FR -->

# 0004 — Analyseur LaTeX : `pylatexenc` 2, strict, avec repli

**Date** : 2026-09-28, amendée le 2026-09-29 (S4.0) — **État** : acceptée

## Contexte

Les règles lisent aujourd'hui le texte brut à travers des masques par
expressions régulières (`lecture.py` : commentaires, maths, `BOX`). D'où les
limites connues, écrites en `xfail` dans `tests/fixtures/*/limites/` : C4
signale `~:` dans `\verb`, `\url` et `\ensuremath` ; P2 ne voit pas deux
boîtes séparées par `\medskip` ou une figure ; P3 prend une phrase finie par
une formule hors texte pour une amorce inachevée.

S4 remplace cette lecture par un arbre : environnements, macros, maths,
commentaires et prose, chacun avec sa position exacte.

## Candidats mesurés

Sur le corpus réel — les 40 fichiers `.tex` du cours de mesure et de
`ocourses/ocots-demo`, 0,8 Mo — et sur les 54 fixtures d'`ocots-lint` :

| | `pylatexenc` 2.11 | tree-sitter (`tree-sitter-language-pack`) |
|---|---|---|
| Corpus, mode strict | 0 fichier en erreur, 1,0 s | 6 fichiers avec un nœud `ERROR` (transparents du chapitre 8, cinq examens), 0,08 s |
| Fixtures, mode strict | 53 / 54 (refuse `\newcommand{\x}{\begin{theorem}}` : ce fichier est lu par le repli) | — |
| `\verb\|a~:b\|` | un nœud macro qui englobe l'argument | une commande suivie de mots : l'argument est lu comme du texte |
| `\url{…}`, `verbatim` | nœuds distincts, contenu non analysé | reconnus |
| `lstlisting`, `minted` | analysés comme du LaTeX ordinaire : à déclarer | — |
| Installation | Python pur, 0,8 Mo, sans dépendance, MIT | binaires compilés, 5 Mo ; le paquet `tree-sitter-latex` n'est pas publié sur PyPI |
| Positions | décalage exact dans la source | décalage exact dans la source |

### Complément sur le corpus complet (S4.0, 2026-09-29)

La mesure ci-dessus ne couvrait que deux cours. Sur les trois cours
enseignants et la démo — 120 fichiers sources —, `pylatexenc` en mode strict
en refuse **un**, du LaTeX pourtant valide : une spécification de colonnes
`>{$}l<{$}` dans un `longtable` (`calcul-differentiel-edo-enseignants`,
`poly/frontmatter/notations.tex`). Le `$` y est pris pour une entrée en mode
mathématique. En mode tolérant, cette seule erreur en produit **32** en
cascade : passé la première erreur, l'arbre n'est plus fiable, et rien ne le
signale.

## Décision

**`pylatexenc` 2**, épinglé `>=2.10,<3`, en **mode strict, avec repli** :

- l'arbre est construit une fois par fichier, dans une couche de lecture
  commune (`arbre.py`), derrière une interface propre à `ocots-lint` — les
  règles ne manipulent pas les classes de `pylatexenc` directement, pour
  pouvoir changer d'analyseur sans les réécrire ;
- le contexte d'analyse déclare ce que les valeurs par défaut ignorent :
  `lstlisting`, `minted`, `Verbatim` comme verbatim ; `\ensuremath` comme
  mode mathématique ;
- **repli** : si l'analyse stricte d'un fichier échoue, ce fichier garde
  la lecture actuelle (masques par regex) pour toutes les règles, et un
  **avertissement** donne la position de la première erreur, comme pour une
  exemption invalide. Jamais d'arbre partiel : un fichier est lu en entier
  par l'arbre, ou en entier comme aujourd'hui. Aucune trouvaille ne
  disparaît en silence, et `verifier` n'échoue pas pour autant ;
- la lecture actuelle reste donc dans le code, comme lecture de secours.
  Elle n'évolue plus : les limites levées en S4 ne le sont que pour les
  fichiers lus par l'arbre, ce que dit l'avertissement.

**Distribution** : une dépendance ordinaire du paquet. `uvx` l'installe avec
`ocots-lint` ; rien ne change pour les cours ni pour le relais des
conventions.

**Pourquoi pas le mode tolérant** (première version de cette décision) : un
arbre partiellement faux, sans signal, est pire que la lecture actuelle —
32 erreurs en cascade pour un seul `$` (voir le complément ci-dessus).

**Pourquoi pas tree-sitter** : plus rapide, mais le gain ne sert pas (1 s
pour tout un cours), il se trompe sur `\verb` — l'une des limites visées — et
échoue sur six fichiers réels ; la grammaire LaTeX n'est pas distribuée seule
sur PyPI.

**`pylatexenc` 3** est en bêta (`3.0b2`) : meilleure spécification des
macros, mais une API qui change encore. À réévaluer quand il sera stable ;
l'interface `arbre.py` rend le changement local.

## Conséquences

- Les règles migrent **une à une** vers l'arbre ; tant qu'une règle n'a pas
  migré, elle garde sa lecture actuelle.
- La parité avec `conventions v2.0.0` cesse d'être la référence dès qu'une
  règle migrée s'écarte volontairement de l'ancien outil. Elle est remplacée
  par `ocots-lint comparer` sur le corpus (mesure + démo) : chaque trouvaille
  qui apparaît ou disparaît est relue et justifiée (S4.5).
- Limites attendues **levées** : C4 `url`, `verb`, `ensuremath` ; P2
  `medskip_entre`, `figure_entre` ; P3 `amorce_en_maths`.
- Limites qui **restent** : P2 `boite_par_macro` (un analyseur ne développe
  pas les macros) ; P3 `amorce_non_motivee` (c'est un jugement, pas une
  lecture).
- La démo `ocourses/ocots-demo` sert de test de bout en bout avant la
  montée : `comparer` entre `v0.4.1` et `v0.5.0` sur elle et sur le cours de
  mesure.
