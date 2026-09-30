<!-- LTeX: language=fr-FR -->

# Tests

```bash
uv run pytest                    # tout
uv run pytest -k P2              # une règle
uv run python -m ocots_lint.instantane verifier                # corpus réel (local)
```

## Écrire une fixture

Une fixture est un petit fichier `.tex` rangé sous
`fixtures/<règle>/<genre>/`. Les trouvailles attendues sont **marquées dans
la source**, sur la ligne où l'outil doit les signaler :

```latex
\end{theorem} % attendu: P2
Le sous ensemble~: voir ``ici''. % attendu: C4 C4 C4
```

Un identifiant répété compte autant de trouvailles sur la même ligne. Le test
compare, pour la règle du dossier, les lignes signalées aux lignes marquées :
ni plus, ni moins.

| Genre | Contenu | Le test |
|---|---|---|
| `signale/` | au moins une infraction, marquée | passe si l'outil trouve exactement les marques |
| `accepte/` | du correct, aucune marque | passe si l'outil ne trouve rien |
| `limites/` | ce que l'outil **devrait** faire : infraction marquée qu'il rate, ou texte correct qu'il signale | attendu en échec (`xfail` strict) |

Quand une limite est levée, son test passe : pytest le signale comme une
erreur (`XPASS(strict)`). La fixture change alors de dossier, vers
`signale/` ou `accepte/`, et le CHANGELOG le dit.

## Quand on trouve un faux positif ou un faux négatif

1. Réduire le cas à quelques lignes, et l'écrire comme fixture.
2. Si on le corrige maintenant : dans `signale/` ou `accepte/`. Le test
   échoue, on corrige, il passe.
3. Sinon : dans `limites/`, avec une phrase dans la fixture qui explique
   pourquoi l'outil se trompe.

## Vocabulaire du template (sprint S5)

`test_vocabulaire.py` : la copie embarquée
(`src/ocots_lint/donnees/vocabulaire.json`) doit être égale au
`vocabulaire.json` du template épinglé en sous-module, sous
`tests/amont/ocots-latex-template` — pas à la racine : un dossier
`template/` à la racine serait pris pour celui d'un cours (le vocabulaire,
mais aussi `csquotes`, y seraient lus). Monter ce sous-module, c'est
recopier son `vocabulaire.json` dans `donnees/`.

### Contre le `main` des dépôts amont

Le workflow `amont.yml` (chaque lundi, ou à la demande) fait passer le
sous-module du template à `main` et relance toute la suite, puis lance
`couverture` sur le `main` des conventions. Il ouvre une issue
`[amont] …` en cas d'échec. Pour le reproduire en local :

```bash
git -C tests/amont/ocots-latex-template fetch origin main
git -C tests/amont/ocots-latex-template checkout FETCH_HEAD
uv run pytest
git -C tests/amont/ocots-latex-template checkout -   # revenir au tag épinglé
```

## Parité (sprint S1)

`test_parite.py` compare `ocots-lint verifier` à
`conventions/bin/verifier` (sous-module épinglé) : même sortie standard,
même sortie d'erreur, même code de sortie. En S4, chaque règle qui passe
sur l'arbre syntaxique sort de ce test, dans la même PR, et sa référence
devient le corpus figé (ci-dessous). Une fixture où une règle encore sur
les masques s'écarte volontairement (défaut corrigé) est déclarée dans
`ECARTS_VOULUS`, avec sa raison ; `test_ecart_voulu_bien_reel` vérifie que
l'écart existe.

## Instantanés du corpus (sprint S4)

Avant de changer la lecture des sources, on fige les trouvailles de chaque
cours du corpus, à un commit donné, avec le code courant :

```bash
uv run python -m ocots_lint.instantane figer mesure ~/cours/mesure-integration-enseignants
uv run python -m ocots_lint.instantane verifier
```

`figer` passe par `git archive` : la copie de travail du cours n'est ni lue
ni touchée. Les sous-modules (`template/`, `conventions/`) sont extraits à
leur commit épinglé, s'ils sont initialisés dans le dépôt du cours :
l'instantané le note, et `verifier` signale un sous-module qui n'est plus
extrait comme au figeage. La voie de chaque trouvaille est comparée. Les instantanés vont dans `corpus/`, **ignoré par git** : ceux des
cours privés citent leur texte.

`verifier` rejoue chaque instantané sur son commit et compare par
empreinte : trouvailles apparues, disparues, et modifiées (même empreinte,
ligne ou message différents). Sortie 1 si quelque chose a bougé. Chaque
écart est relu : voulu (une limite levée, un défaut corrigé) et justifié
dans le journal du sprint, ou non voulu et corrigé.

Depuis S4.7, c'est **la** référence sur un cours réel : la parité avec
l'ancien outil ne se teste plus que sur les fixtures. Une fois les écarts
d'un changement justifiés, on refige (`figer`, même nom, même commit) : le
nouvel instantané devient la base du changement suivant.

## Contrat (`test_contrat.py`)

La sortie de `verifier` est lue par d'autres : les agents (JSON) et
l'ancien détecteur `conventions.sh` (texte, codes de sortie). Le test compare
les sorties sur `contrat/cours.tex` à des références (`contrat/cours.json`,
`contrat/cours.txt`) et valide le JSON contre le schéma publié.

Si une sortie change **volontairement** :

```bash
OCOTS_LINT_REGENERER=1 uv run pytest tests/test_contrat.py
```

puis relire le diff des références : c'est le changement de contrat vu par
les consommateurs. Un changement incompatible du JSON fait monter
`SCHEMA_JSON`.
