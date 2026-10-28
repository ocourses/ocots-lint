"""Les fichiers d'un support, pour les règles propres aux TD, aux examens
et aux transparents (S8, décision 0009).

Une règle `TD*`, `EX*` ou `SL*` ne lit que les fichiers de son support
(`lecture.support_de`), sur l'arbre syntaxique : sans arbre, la place d'un
environnement ne se lit pas. Ces règles n'ont pas de repli : un fichier que
l'analyse refuse n'est pas vérifié, et `verifier` le dit.
"""

from ocots_lint.arbre import lire_arbre
from ocots_lint.lecture import DIAPOSITIVES, sources, support_de

# `exam.md` a `td.md` pour prérequis, et EX6 renvoie à TD6–TD8 : les règles
# mécaniques des TD valent pour les examens (décision 0009, point 3).
EXERCICES = frozenset({"td", "exam"})
EXAMENS = frozenset({"exam"})
TRANSPARENTS = frozenset({DIAPOSITIVES})

EXERCICE = "exercice"           # famille du vocabulaire du template


def arbres(racines, v, supports):
    """(chemin, arbre) des fichiers de ces supports que l'analyse accepte."""
    for chemin in sources(racines):
        arbre = lire_arbre(chemin)
        if arbre.erreur is None and support_de(chemin, arbre.texte, v) in supports:
            yield chemin, arbre


def dans_un_exercice(ancetres, v):
    """L'exercice qui contient le nœud, ou None."""
    return next((a for a in ancetres if v.famille(a.nom) == EXERCICE), None)
