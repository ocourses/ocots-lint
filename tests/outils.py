"""Lecture des fixtures : les trouvailles attendues sont marquées dans la
source, sur la ligne où l'outil doit les signaler.

    \\end{theorem} % attendu: P2
    Le sous ensemble~: voir ``ici''. % attendu: C4 C4 C4

Un identifiant répété compte autant de trouvailles sur la même ligne.
"""

import re
from collections import Counter
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"

RE_ATTENDU = re.compile(r"%\s*attendu:\s*(.*)$")
RE_IDENTIFIANT = re.compile(r"\b[A-Z]{1,2}\d+\b")


def attendus(chemin, regle):
    """Compteur {ligne: nombre} des trouvailles `regle` marquées dans le fichier."""
    compte = Counter()
    lignes = Path(chemin).read_text(encoding="utf-8").split("\n")
    for no, ligne in enumerate(lignes, start=1):
        m = RE_ATTENDU.search(ligne)
        if m:
            for ident in RE_IDENTIFIANT.findall(m.group(1)):
                if ident == regle:
                    compte[no] += 1
    return compte


def marques(chemin):
    """Tous les identifiants marqués dans le fichier, toutes règles confondues."""
    texte = Path(chemin).read_text(encoding="utf-8")
    return [i for m in RE_ATTENDU.finditer(texte, re.M) if m
            for i in RE_IDENTIFIANT.findall(m.group(1))]
