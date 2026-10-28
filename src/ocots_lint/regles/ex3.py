"""EX3 — barème par les clés, pas à la main.

Le barème d'un sujet se porte par `points=` sur l'exercice : le template
l'affiche et en fait le total (exam.md#ex3). Écrit dans le texte —
`\\begin{exercise}(7 points)`, « barème prévisionnel : 8 points »,
« Intégrale de Dirichlet - 7 points », « (1 point) » devant une question —,
il se désynchronise à la première retouche.

Lu dans la prose du corps du document (`arbre.prose` : ni commentaires, ni
formules, ni préambule). Une `correction` n'est pas lue : la répartition des
points par question y a sa place (EX6).

Garantie `heuristique` : « 3 points d'intersection » est de la géométrie.
Les tournures connues (`NON_BAREME`) sont écartées, pas toutes.
"""

import re

from ocots_lint import vocabulaire
from ocots_lint.arbre import prose
from ocots_lint.regles.supports import EXAMENS, arbres

# Ce qui suit « N points » quand ce sont des points d'une figure ou d'une
# fonction, pas un barème : points d'équilibre, de fonctionnement, fixes…
NON_BAREME = r"\s*(?:d['’]|de\b|du\b|des\b|fixes?\b|critiques?\b|singuliers?\b)"

RE_BAREME = re.compile(
    r"(?<![\w=.,])\d+(?:[.,]\d+)?\s*(?:points?|pts?)\b(?!" + NON_BAREME + r")",
    re.I)
RE_CORPS = re.compile(r"\\begin\s*\{document\}")


def _corriges(arbre, v):
    """Intervalles (début, fin) des corrigés."""
    return [(n.debut, n.fin) for n, _ in arbre.avec_ancetres()
            if n.genre == "environnement" and v.est_corrige(n.nom)]


def regle_EX3(racines):
    """EX3 — barème écrit dans le texte du sujet au lieu de la clé points=."""
    v = vocabulaire.charger()
    for chemin, arbre in arbres(racines, v, EXAMENS):
        texte = prose(arbre)
        corps = RE_CORPS.search(arbre.texte)
        debut = corps.end() if corps else 0
        corriges = _corriges(arbre, v)
        for m in RE_BAREME.finditer(texte, debut):
            if any(d <= m.start() < f for d, f in corriges):
                continue
            yield chemin, arbre.position(m.start())[0], (
                f"barème écrit dans le texte (« {m.group(0)} ») — le porter "
                f"par la clé points= de l'exercice ; la répartition par "
                f"question va dans la correction (EX6)")
