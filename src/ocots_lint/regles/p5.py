"""P5 — plus de trois remarques d'affilée."""

import re

from ocots_lint import vocabulaire
from ocots_lint.lecture import ligne_de, lire, motif, sans_commentaires, sources

# Au-delà de trois remarques d'affilée, le contenu a quitté le fil.
CHAINE_REMARQUES_MAX = 3

REMARQUE = "remarque"          # famille du vocabulaire du template


def boites_de_premier_niveau(texte, v):
    """Les boîtes non imbriquées, dans l'ordre : (famille, ligne)."""
    re_boite = re.compile(r"\\(begin|end)\{(" + motif(v.boites) + r")\}")
    profondeur, suite = 0, []
    for m in re_boite.finditer(texte):
        if m.group(1) == "begin":
            if profondeur == 0:
                suite.append((v.famille(m.group(2)),
                              ligne_de(texte, m.start())))
            profondeur += 1
        else:
            profondeur -= 1
    return suite


def regle_P5(racines):
    """P5 — plus de trois remarques d'affilée : le contenu a quitté le fil."""
    v = vocabulaire.charger()
    for chemin in sources(racines):
        texte = sans_commentaires(lire(chemin))
        longueur, depart = 0, None
        for famille, ligne in boites_de_premier_niveau(texte, v) + [("", 0)]:
            if famille == REMARQUE:
                longueur += 1
                if depart is None:
                    depart = ligne
                continue
            if longueur > CHAINE_REMARQUES_MAX:
                yield chemin, depart, (
                    f"{longueur} remarques d'affilée — vérifier qu'elles sont "
                    f"toutes optionnelles")
            longueur, depart = 0, None
