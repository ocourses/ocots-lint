"""Registre des vérificateurs, un module par règle de ocots-conventions.

Un vérificateur est un générateur `regle_X(racines)` qui produit des
trouvailles `(chemin, ligne, message)`. La première ligne de sa docstring
est son résumé dans `--list`.

Ajouter un vérificateur : écrire le module, l'inscrire dans `REGISTRE` avec
sa garantie et sa lecture, et ses fixtures dans `tests/fixtures/<règle>/`.

Lecture (S4) : `masques` — le texte par expressions régulières
(`lecture.py`) ; `arbre` — l'arbre syntaxique (`arbre.py`), avec repli sur
les masques pour un fichier que l'analyse refuse (décision 0004).
"""

from dataclasses import dataclass
from typing import Callable

from ocots_lint.regles.c4 import regle_C4
from ocots_lint.regles.c6 import regle_C6
from ocots_lint.regles.p2 import regle_P2
from ocots_lint.regles.p3 import regle_P3
from ocots_lint.regles.p5 import regle_P5

# Ce qu'une trouvaille — ou son absence — permet de conclure.
GARANTIES = {
    "exact": "aucun faux négatif ni faux positif connu dans le périmètre déclaré",
    "heuristique": "une trouvaille est presque toujours une infraction, "
                   "mais l'outil en rate (limites connues)",
    "signal": "une trouvaille dit où regarder ; elle n'est pas forcément une faute",
    "mesure": "compte, ne bloque jamais",
}


@dataclass(frozen=True)
class Verificateur:
    regle: str
    fonction: Callable
    garantie: str
    lecture: str = "masques"

    @property
    def resume(self):
        return self.fonction.__doc__.splitlines()[0]


REGISTRE = (
    Verificateur("P2", regle_P2, "heuristique", lecture="arbre"),
    Verificateur("P3", regle_P3, "signal", lecture="arbre"),
    Verificateur("P5", regle_P5, "signal"),
    Verificateur("C4", regle_C4, "heuristique", lecture="arbre"),
    Verificateur("C6", regle_C6, "heuristique"),
)

REGLES = {v.regle: v.fonction for v in REGISTRE}
SUR_ARBRE = frozenset(v.regle for v in REGISTRE if v.lecture == "arbre")
