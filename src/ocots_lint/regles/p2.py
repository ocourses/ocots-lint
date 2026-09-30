"""P2 — enchaînements de boîtes sans texte entre elles.

Lu sur l'arbre syntaxique (S4.4) : deux boîtes sœures s'enchaînent si rien
ne les sépare que de la **mise en page** — blancs, commentaires, commandes
d'espacement (`MISE_EN_PAGE`), figures (`FIGURES`). Tout le reste rompt la
chaîne : de la prose, mais aussi `\\pause` (idiome des transparents, SL6),
un titre de section, une formule hors texte, une commande inconnue. Seule
une mise en page reconnue peut donc cacher une infraction : la règle
n'invente pas de chaîne. Pour un fichier que l'analyse refuse, repli sur la
lecture par masques.
"""

import re

from ocots_lint import vocabulaire
from ocots_lint.arbre import lire_arbre
from ocots_lint.lecture import ligne_de, motif, sans_commentaires, sources

# Familles du vocabulaire du template (template/vocabulaire.json) : un alias
# (`myexercisecb`) ou une variante étoilée (`remark*`) a la famille de sa
# cible.

# Une série d'exercices est une liste, pas une narration (P2).
SERIE_TOLEREE = "exercice"

# Entrer dans une remarque ne demande pas de phrase de liaison : elle se
# rattache à ce qui précède (P5). Ce qui en *sort* reste soumis à P2 — une
# boîte collée après une remarque perd son amorce dès qu'on saute la remarque.
ENTREE_TOLEREE = "remarque"

# Ni prose ni contenu : ce qui ne sépare pas deux boîtes.
MISE_EN_PAGE = frozenset({
    "smallskip", "medskip", "bigskip", "vspace", "vfill", "par", "noindent",
    "newpage", "clearpage", "cleardoublepage", "pagebreak", "nopagebreak",
    "smallbreak", "medbreak", "bigbreak", "label", "index"})
FIGURES = frozenset({"figure", "figure*", "center", "wrapfigure", "tikzpicture"})



def re_chaine(v):
    """Le repli par masques : `\\end{boîte}` suivi, à des blancs et
    commentaires près, de `\\begin{boîte}`."""
    boite = motif(v.boites)
    return re.compile(
        r"\\end\{(" + boite + r")\}"
        r"((?:[^\S\n]*\n|[^\S\n]*%[^\n]*\n)*)"
        r"[^\S\n]*\\begin\{(" + boite + r")\}")


def tolere(v, avant, apres):
    fa, fb = v.famille(avant), v.famille(apres)
    return fa == fb == SERIE_TOLEREE or fb == ENTREE_TOLEREE


def _est_boite(n, v):
    return n.genre == "environnement" and n.nom in v.boites


def _transparent(n, texte):
    if n.genre == "commentaire":
        return True
    if n.genre == "texte":
        return not texte[n.debut:n.fin].strip()
    if n.genre == "macro":
        return n.nom in MISE_EN_PAGE
    if n.genre == "environnement":
        return n.nom in FIGURES
    return False


def _freres(arbre):
    """Chaque liste de nœuds frères de l'arbre, à tous les niveaux."""
    yield arbre.noeuds
    for n in arbre.parcourir():
        if n.enfants:
            yield n.enfants


def chaines_arbre(arbre, v):
    """(boîte, boîte suivante) séparées seulement par de la mise en page,
    dans l'ordre du texte."""
    paires = []
    for freres in _freres(arbre):
        precedente = None
        for n in freres:
            if _est_boite(n, v):
                if precedente is not None:
                    paires.append((precedente, n))
                precedente = n
            elif not _transparent(n, arbre.texte):
                precedente = None
    return sorted(paires, key=lambda p: p[0].fin)


def regle_P2(racines):
    """P2 — enchaînements de boîtes sans texte entre elles."""
    v = vocabulaire.charger()
    chaine = re_chaine(v)
    for chemin in sources(racines):
        arbre = lire_arbre(chemin)
        if arbre.erreur is None:
            for avant, apres in chaines_arbre(arbre, v):
                if not tolere(v, avant.nom, apres.nom):
                    # la ligne du \end{…} de la première boîte
                    ligne = arbre.position(avant.fin - 1)[0]
                    yield chemin, ligne, f"{avant.nom} -> {apres.nom}"
            continue
        texte = sans_commentaires(arbre.texte)            # repli
        for m in chaine.finditer(texte):
            if not tolere(v, m.group(1), m.group(3)):
                yield (chemin, ligne_de(texte, m.start()),
                       f"{m.group(1)} -> {m.group(3)}")
