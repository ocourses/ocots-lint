<!-- LTeX: language=fr-FR -->

# `ocots-lint` — vérifier les conventions de rédaction des cours

Outil d'analyse des sources LaTeX des cours `ocourses`. Il outille les règles
de [`ocots-conventions`](https://github.com/ocourses/ocots-conventions)
(comment on **rédige**) sur des documents composés avec
[`ocots-latex-template`](https://github.com/ocourses/ocots-latex-template)
(comment on **compose**).

| Dépôt | Question à laquelle il répond |
|---|---|
| `ocots-latex-template` | quelle commande, quel environnement, quel rendu ? |
| `ocots-conventions` | quel texte autour, dans quel ordre, avec quelles notations ? |
| `ocots-lint` (ici) | le document respecte-t-il ces règles, et avec quelle garantie ? |

> **État : `v0.1.0`.** L'outil reproduit à l'identique
> `conventions/bin/verifier`, avec des tests. Voir la [roadmap](.agents/roadmap/README.md).

---

## Utilisation

Sans installation, depuis la racine d'un cours :

```bash
uvx --from git+https://github.com/ocourses/ocots-lint ocots-lint verifier
uvx --from git+https://github.com/ocourses/ocots-lint ocots-lint verifier P2 poly/
uvx --from git+https://github.com/ocourses/ocots-lint ocots-lint verifier --list
uvx --from git+https://github.com/ocourses/ocots-lint ocots-lint verifier --mesure poly/
uvx --from git+https://github.com/ocourses/ocots-lint ocots-lint couverture
```

Épingler une version : `git+https://github.com/ocourses/ocots-lint@v0.1.0`.

Sortie `1` s'il y a au moins une infraction, `2` pour un argument inconnu,
`0` sinon — utilisable en CI.

## Ce que l'outil garantit — et ce qu'il ne garantit pas

Un vérificateur peut se tromper de deux façons :

- **faux positif** — il signale du correct (mesure : la *précision*) ;
- **faux négatif** — il rate une infraction (mesure : le *rappel*).

Zéro trouvaille ne veut donc pas dire règle respectée. Chaque vérificateur
déclare sa **garantie** :

| Garantie | Ce qu'elle promet |
|---|---|
| `exact` | aucun faux négatif ni faux positif connu dans le périmètre déclaré |
| `heuristique` | une trouvaille est presque toujours une infraction, mais l'outil en rate |
| `signal` | une trouvaille dit *où regarder* ; elle n'est pas forcément une faute |
| `mesure` | compte, ne bloque jamais (`--mesure`) |

`ocots-lint couverture` liste chaque règle des conventions du cours
(`./conventions`) avec sa garantie, ou « non outillée ». Il sort `2` si
l'outil cite une règle que ces conventions ne connaissent pas.
 Chaque limite connue
d'un vérificateur est écrite comme un **test attendu en échec**
([`tests/fixtures/*/limites/`](tests/fixtures/)) : la liste de ce que l'outil
rate est lisible, et le jour où il ne le rate plus, le test le signale.

### Exempter une trouvaille justifiée

Une trouvaille relue et jugée correcte s'exempte dans la source, **avec sa
raison** :

```latex
\end{theorem} % ocots-lint: ignore P2 — la proposition en est un corollaire immédiat

% ocots-lint: ignore P5 — quatre vrais apartés, relus avec l'auteur
\begin{remark}
```

- En fin de ligne, la directive couvre sa ligne. Seule sur sa ligne, elle
  couvre la ligne suivante.
- Sans raison, elle est ignorée et signalée.
- Une directive qui n'exempte plus rien est signalée : pas d'exemption morte.
- `verifier --sans-exemptions` montre tout, pour une revue des exemptions.

---

## Développement

```bash
uv sync                      # environnement de développement
uv run pytest                # tests unitaires et de non-régression
uvx ruff check               # style
```

Voir [`AGENTS.md`](AGENTS.md) pour la méthode de travail, et
[`tests/README.md`](tests/README.md) pour écrire une fixture.

## Versions

`ocots-lint` suit [SemVer](https://semver.org/lang/fr/) :

| | Ce qui la fait monter |
|---|---|
| **majeur** | CLI ou format de sortie incompatible |
| **mineur** | nouveau vérificateur, nouvelle option, nouvelle garantie |
| **correctif** | correction d'un faux positif ou d'un faux négatif |

Tant que la version est en `0.x`, la CLI peut encore changer d'un mineur à
l'autre. Chaque version est un tag `vX.Y.Z` avec son entrée dans
[`CHANGELOG.md`](CHANGELOG.md).
