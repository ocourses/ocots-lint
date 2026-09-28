"""Les vérificateurs, un module par règle de ocots-conventions.

Un vérificateur est un générateur `regle_X(racines)` qui produit des
trouvailles `(chemin, ligne, message)`. La première ligne de sa docstring
est son résumé dans `--list`.
"""

from ocots_lint.regles.c4 import regle_C4
from ocots_lint.regles.c6 import regle_C6
from ocots_lint.regles.p2 import regle_P2
from ocots_lint.regles.p3 import regle_P3
from ocots_lint.regles.p5 import regle_P5

REGLES = {"P2": regle_P2, "P3": regle_P3, "P5": regle_P5, "C4": regle_C4,
          "C6": regle_C6}
