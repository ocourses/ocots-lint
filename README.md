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

> **État : `v0.3.0`.** Garanties, exemptions, empreintes, contrat JSON,
> `synchroniser`, `comparer`, vérification des PR. Voir la [roadmap](.agents/roadmap/README.md).

---

## Utilisation

Sans installation, depuis la racine d'un cours :

```bash
uvx --from git+https://github.com/ocourses/ocots-lint ocots-lint verifier
uvx --from git+https://github.com/ocourses/ocots-lint ocots-lint verifier P2 poly/
uvx --from git+https://github.com/ocourses/ocots-lint ocots-lint verifier --list
uvx --from git+https://github.com/ocourses/ocots-lint ocots-lint verifier --mesure poly/
uvx --from git+https://github.com/ocourses/ocots-lint ocots-lint couverture
uvx --from git+https://github.com/ocourses/ocots-lint ocots-lint nettoyer C4 poly/              # aperçu
uvx --from git+https://github.com/ocourses/ocots-lint ocots-lint nettoyer C4 poly/ --appliquer  # écrit
```

`verifier` **analyse** ; `nettoyer` **modifie**, et seulement pour les
corrections dont l'équivalence est vérifiée (`~:`, guillemets si `csquotes`
est chargé). Après `--appliquer` : recompiler, relire le diff, commiter à
part.

Épingler une version : `git+https://github.com/ocourses/ocots-lint@v0.3.0`.

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
  couvre la prochaine ligne qui n'est pas un commentaire seul : on peut en
  empiler plusieurs.
- Sans raison, elle est ignorée et signalée.
- Une directive qui n'exempte plus rien est signalée : pas d'exemption morte.
- `verifier --sans-exemptions` montre tout, pour une revue des exemptions.

Pour poser une exemption sans rien toucher d'autre, par exemple depuis un
agent :

```bash
ocots-lint exempter poly/ch1.tex:42 P2 "la proposition en découle"
ocots-lint exempter poly/ch1.tex@3f9a0c2e71b84d55:0 P2 "…"   # par empreinte
git diff | ocots-lint exempter --controler -                 # le diff n'ajoute que des directives ?
```

`exempter` ajoute une seule ligne de commentaire au-dessus de la trouvaille,
refuse s'il n'y a pas de trouvaille active à cet endroit ou si la ligne est
dans un verbatim, et vérifie après coup que la trouvaille a disparu.

### Dans la CI d'un cours

Sur une PR, ne signaler **que ce qui est nouveau** par rapport à la branche
de base (par empreinte), en annotations dans la PR — quelques secondes, sans
licence, même sur un dépôt privé :

```yaml
# .github/workflows/conventions-pr.yml du cours
on:
  pull_request:
    paths: ["**.tex"]
jobs:
  conventions:
    uses: ocourses/ocots-lint/.github/workflows/verifier-pr.yml@v0.3.0
    with:
      runs-on: '["self-hosted"]'   # facultatif ; défaut : ubuntu-latest
```

À la main : `ocots-lint verifier --nouvelles origin/main`. Retirer une
exemption fait réapparaître la trouvaille.

Formats : `--format github` (annotations de workflow), `--format json`
(pour un script ou un agent — voir ci-dessous) et `--format sarif`
(SARIF 2.1.0, pour le *code scanning* de GitHub — gratuit sur un dépôt
public seulement). Une trouvaille exemptée figure en SARIF comme
suppression, avec sa raison.

### Avant une montée de version : `comparer`

```bash
OL=git+https://github.com/ocourses/ocots-lint
uvx --from $OL@v0.3.0 ocots-lint verifier --format json > avant.json
uvx --from $OL@v0.4.0 ocots-lint verifier --format json > apres.json
ocots-lint comparer avant.json apres.json
```

Trouvailles apparues et disparues (par empreinte), bilan par règle, et les
issues que `synchroniser` créera ou fermera. Sortie `1` s'il y a un
changement, comme `diff`.

### Les issues du cours : `synchroniser`

```bash
ocots-lint synchroniser --dry-run    # le plan des issues, sans rien toucher
ocots-lint synchroniser              # l'applique (gh, dépôt courant ou --depot)
```

Une issue `[conventions] <fichier>` par fichier en infraction, mêmes titres
et labels que l'ancien détecteur des agents, qu'elle remplace. Chaque
trouvaille y porte sa **voie** :

| Voie | Quand | Qui s'en occupe |
|---|---|---|
| `mecanique` | `nettoyer` sait la corriger à cette ligne (guillemets : si `csquotes` est chargé) | `ocots-lint nettoyer`, sans modèle |
| `correction` | garantie `exact` | l'agent de correction, sans tri |
| `tri` | garantie `heuristique` ou `signal` | l'agent de tri, puis correction ou exemption |

Une issue fermée « not planned » qui portait déjà toutes les empreintes
actuelles d'un fichier n'est pas recréée : le rejet n'est pas redemandé, et
le plan rappelle de poser les exemptions. Si l'analyse échoue, rien n'est
touché.

### Le contrat JSON

`verifier --format json` est **le** format à lire pour un programme : la
sortie texte est faite pour un humain. Il porte un numéro de schéma
(`"schema": 1`), et le schéma est publié avec le paquet
([`schemas/verifier-1.schema.json`](src/ocots_lint/schemas/verifier-1.schema.json)).
Un champ ajouté reste compatible ; un changement incompatible crée un
schéma 2.

Chaque trouvaille porte une **empreinte** (`3f9a0c2e71b84d55:0`), son
identité indépendante du numéro de ligne : la règle, le fichier, la ligne
signalée et ses voisines non vides, commentaires retirés. Ajouter des lignes
ailleurs, ou une exemption au-dessus, ne la change pas. La sortie JSON porte
aussi les avertissements sur les exemptions (sans raison, inutiles).

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
