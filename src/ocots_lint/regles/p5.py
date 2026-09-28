"""P5 — plus de trois remarques d'affilée."""

import re

from ocots_lint.lecture import BOX, ligne_de, lire, sans_commentaires, sources

# Au-delà de trois remarques d'affilée, le contenu a quitté le fil.
CHAINE_REMARQUES_MAX = 3

RE_BOITE = re.compile(r"\\(begin|end)\{(" + BOX + r")\}")


def boites_de_premier_niveau(texte):
    """Les boîtes non imbriquées, dans l'ordre : (nom, ligne)."""
    profondeur, suite = 0, []
    for m in RE_BOITE.finditer(texte):
        if m.group(1) == "begin":
            if profondeur == 0:
                suite.append((m.group(2).replace("my", ""),
                              ligne_de(texte, m.start())))
            profondeur += 1
        else:
            profondeur -= 1
    return suite


def regle_P5(racines):
    """P5 — plus de trois remarques d'affilée : le contenu a quitté le fil."""
    for chemin in sources(racines):
        texte = sans_commentaires(lire(chemin))
        longueur, depart = 0, None
        for nom, ligne in boites_de_premier_niveau(texte) + [("", 0)]:
            if nom == "remark":
                longueur += 1
                if depart is None:
                    depart = ligne
                continue
            if longueur > CHAINE_REMARQUES_MAX:
                yield chemin, depart, (
                    f"{longueur} remarques d'affilée — vérifier qu'elles sont "
                    f"toutes optionnelles")
            longueur, depart = 0, None
