"""La table des préfixes de label, lue dans les conventions (C5, S6.3).

    table = prefixes.charger()      # {"theorem": "thm:", "section": "sec:", …}

C5 (`communes.md`) donne, pour chaque objet, son nom LaTeX entre
parenthèses et son préfixe :

    | théorème (`theorem`) | `thm:` | section (`\\section`) | `sec:` |

L'outil lit la table des conventions du cours (`./conventions`), sinon une
copie embarquée (`donnees/prefixes.json`) : conventions antérieures à la
table lisible, ou sous-module non initialisé. La copie est comparée chaque
semaine au `main` des conventions (workflow `amont`).
"""

import functools
import json
import os
import re
import sys
from pathlib import Path

FICHIER = os.path.join("conventions", "communes.md")
EMBARQUE = Path(__file__).parent / "donnees" / "prefixes.json"

RE_SECTION_C5 = re.compile(r"^## C5 — .*?(?=^## |\Z)", re.M | re.S)
RE_NOM = re.compile(r"`\\?([A-Za-z]+\*?)`")
RE_PREFIXE = re.compile(r"^`([a-z]+:)`$")


def lire(texte):
    """{nom LaTeX: préfixe} de la table de C5 dans ce `communes.md` ; vide si
    la section manque, ou si un objet n'a pas de nom LaTeX (conventions
    antérieures : seule l'hypothèse avait le sien — la table serait
    incomplète)."""
    m = RE_SECTION_C5.search(texte)
    if not m:
        return {}
    table = {}
    for ligne in m.group(0).splitlines():
        cellules = [c.strip() for c in ligne.strip().strip("|").split("|")]
        if not ligne.lstrip().startswith("|") or len(cellules) % 2:
            continue
        for objet, prefixe in zip(cellules[::2], cellules[1::2], strict=True):
            p = RE_PREFIXE.match(prefixe)
            if not p:
                continue
            noms = RE_NOM.findall(objet)
            if not noms:
                return {}
            for nom in noms:
                table[nom] = p.group(1)
    return table


@functools.lru_cache(maxsize=8)
def _lire_fichier(chemin, _date):
    return lire(Path(chemin).read_text(encoding="utf-8"))


_averti = set()


def charger():
    """La table des conventions du dossier courant, sinon la copie embarquée."""
    if os.path.isfile(FICHIER):
        chemin = os.path.abspath(FICHIER)
        table = _lire_fichier(chemin, os.stat(chemin).st_mtime_ns)
        if table:
            return table
        if chemin not in _averti:
            _averti.add(chemin)
            print(f"ocots-lint : pas de table des préfixes lisible dans "
                  f"{FICHIER} (conventions antérieures) — table embarquée "
                  f"utilisée", file=sys.stderr)
    return embarquee()


@functools.lru_cache(maxsize=1)
def embarquee():
    return json.loads(EMBARQUE.read_text(encoding="utf-8"))
