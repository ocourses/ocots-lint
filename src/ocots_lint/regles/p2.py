"""P2 — enchaînements de boîtes sans texte entre elles."""

import re

from ocots_lint.lecture import BOX, ligne_de, lire, sans_commentaires, sources

# Une série d'exercices est une liste, pas une narration (P2).
CHAINE_TOLEREE = {("exercise", "exercise"), ("exercisecb", "exercisecb")}

# Entrer dans une remarque ne demande pas de phrase de liaison : elle se
# rattache à ce qui précède (P5). Ce qui en *sort* reste soumis à P2 — une
# boîte collée après une remarque perd son amorce dès qu'on saute la remarque.
ENTREE_TOLEREE = "remark"

RE_CHAINE = re.compile(
    r"\\end\{(" + BOX + r")\}"
    r"((?:[^\S\n]*\n|[^\S\n]*%[^\n]*\n)*)"
    r"[^\S\n]*\\begin\{(" + BOX + r")\}")


def regle_P2(racines):
    """P2 — enchaînements de boîtes sans texte entre elles."""
    for chemin in sources(racines):
        texte = sans_commentaires(lire(chemin))
        for m in RE_CHAINE.finditer(texte):
            avant, apres = m.group(1), m.group(3)
            nus = (avant.replace("my", ""), apres.replace("my", ""))
            if nus in CHAINE_TOLEREE or nus[1] == ENTREE_TOLEREE:
                continue
            yield chemin, ligne_de(texte, m.start()), f"{avant} -> {apres}"
