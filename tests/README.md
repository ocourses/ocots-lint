<!-- LTeX: language=fr-FR -->

# Tests

```bash
uv run pytest                    # tout
uv run pytest -k P2              # une règle
OCOTS_LINT_CORPUS=<cours> uv run pytest tests/test_parite.py   # parité sur un cours
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

## Parité (sprint S1)

`test_parite.py` compare `ocots-lint verifier` à
`conventions/bin/verifier` (sous-module épinglé) : même sortie standard,
même sortie d'erreur, même code de sortie. À partir de S4, l'outil
s'écartera volontairement de l'ancien, et ce test sera retiré.

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
