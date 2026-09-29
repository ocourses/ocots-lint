"""C4 — typographie.

Lu sur l'arbre syntaxique (S4.3) : les contrôles portent sur la prose seule
— commentaires, maths (`\\ensuremath` compris), verbatim (`\\verb`, `\\url`,
`lstlisting`, `minted`…) et figures TikZ blanchis. Pour un fichier que
l'analyse refuse, repli sur les masques par regex (`lecture.py`).
"""

import re

from ocots_lint.arbre import lire_arbre, prose
from ocots_lint.lecture import hors_math, ligne_de, sans_commentaires, sources

RE_TILDE_DEUX_POINTS = re.compile(r"~:")
RE_GUILLEMETS = re.compile(r"``|\\og\b")
RE_APOSTROPHE = re.compile("\u2019")
RE_RENVOI_BAS_DE_CASSE = re.compile(
    r"\b(théorème|définition|proposition|corollaire|lemme|figure|tableau"
    r"|exemple|section|exercice)[ ~]*\\ref\{")
RE_SOUS = re.compile(r"\bsous (section|espace|ensemble|groupe|suite)\b")

CONTROLES = (
    (RE_TILDE_DEUX_POINTS, "`~:` inutile — babel-french pose l'espace seul"),
    (RE_GUILLEMETS, "guillemets : utiliser \\enquote{…}"),
    (RE_APOSTROPHE, "apostrophe U+2019 — utiliser U+0027"),
    (RE_RENVOI_BAS_DE_CASSE, "renvoi en bas de casse — « Théorème~\\ref{…} »"),
    (RE_SOUS, "mot composé — trait d'union"),
)


def regle_C4(racines):
    """C4 — typographie : ~:, guillemets, apostrophes, renvois, mots composés."""
    for chemin in sources(racines):
        arbre = lire_arbre(chemin)
        if arbre.erreur is None:
            texte = prose(arbre)
        else:
            # Repli. Commentaires retirés avant le masque maths : un `$` seul
            # dans un commentaire (ex. « % coût : $5 ») déparierait sinon
            # tout le masquage des vraies formules qui suivent.
            texte = hors_math(sans_commentaires(arbre.texte))
        for motif, message in CONTROLES:
            for m in motif.finditer(texte):
                yield chemin, ligne_de(texte, m.start()), message
