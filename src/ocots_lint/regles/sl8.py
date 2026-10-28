"""SL8 — le thème est un réglage global.

Le thème (`theme=ocots`, `legacy-dark` pour la projection) se choisit au
préambule, une fois (slides.md#sl8). Deux gestes le contournent :

- une couleur posée à la main dans une diapositive (`\\textcolor{red}{…}`,
  `{\\color{blue!20} …}`) : elle ne suit pas un changement de thème ;
- un réglage de thème dans le corps du document (`\\usetheme`,
  `\\setbeamercolor`, `\\definecolor`…), après `\\begin{document}`.

Une couleur **du thème** (`\\color{\\ocotscolor{link}}`) n'est pas
signalée : elle suit le réglage global, ce que la règle protège (décision
0009). `\\slidecolor`, le mécanisme prévu pour une série de diapositives,
non plus.

Garantie `heuristique` : seules les commandes connues sont vues ; une
couleur posée par une macro du cours ne l'est pas. La page de titre
recomposée à la main (second alinéa de SL8) reste au jugement.
"""

import re

from ocots_lint import vocabulaire
from ocots_lint.regles.supports import TRANSPARENTS, arbres, est_diapositive

COULEURS = frozenset({"color", "textcolor", "colorbox", "fcolorbox", "pagecolor"})
REGLAGES = frozenset({"usetheme", "usecolortheme", "useinnertheme",
                      "useoutertheme", "usefonttheme", "setbeamercolor",
                      "definecolor", "colorlet"})

# Le premier argument de couleur, après un modèle facultatif `[rgb]`.
RE_COULEUR_DU_THEME = re.compile(r"\\[A-Za-z]+\s*(?:\[[^\]]*\])?\s*\{\s*\\ocotscolor\b")
RE_CORPS = re.compile(r"\\begin\s*\{document\}")


def regle_SL8(racines):
    """SL8 — couleur en dur dans une diapositive, réglage de thème dans le corps."""
    v = vocabulaire.charger()
    for chemin, arbre in arbres(racines, v, TRANSPARENTS):
        texte = arbre.texte
        corps = RE_CORPS.search(texte)
        debut_corps = corps.end() if corps else 0
        for n, ancetres in arbre.avec_ancetres(arguments=True):
            if n.genre != "macro":
                continue
            if n.nom in REGLAGES and n.debut >= debut_corps:
                yield chemin, arbre.position(n.debut)[0], (
                    f"\\{n.nom} dans le corps du document — le thème se règle "
                    f"au préambule, une fois")
            elif (n.nom in COULEURS
                  and any(est_diapositive(a, v) for a in ancetres)
                  and not RE_COULEUR_DU_THEME.match(texte, n.debut)):
                yield chemin, arbre.position(n.debut)[0], (
                    f"\\{n.nom} : couleur en dur dans une diapositive — prendre "
                    f"une couleur du thème (\\ocotscolor{{…}}) ou \\slidecolor")
