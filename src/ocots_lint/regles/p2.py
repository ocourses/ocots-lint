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

from ocots_lint.arbre import lire_arbre
from ocots_lint.lecture import BOX, ligne_de, sans_commentaires, sources

# Une série d'exercices est une liste, pas une narration (P2).
CHAINE_TOLEREE = {("exercise", "exercise"), ("exercisecb", "exercisecb")}

# Entrer dans une remarque ne demande pas de phrase de liaison : elle se
# rattache à ce qui précède (P5). Ce qui en *sort* reste soumis à P2 — une
# boîte collée après une remarque perd son amorce dès qu'on saute la remarque.
ENTREE_TOLEREE = "remark"

# Ni prose ni contenu : ce qui ne sépare pas deux boîtes.
MISE_EN_PAGE = frozenset({
    "smallskip", "medskip", "bigskip", "vspace", "vfill", "par", "noindent",
    "newpage", "clearpage", "cleardoublepage", "pagebreak", "nopagebreak",
    "smallbreak", "medbreak", "bigbreak", "label", "index"})
FIGURES = frozenset({"figure", "figure*", "center", "wrapfigure", "tikzpicture"})

RE_BOITE = re.compile(BOX)

RE_CHAINE = re.compile(
    r"\\end\{(" + BOX + r")\}"
    r"((?:[^\S\n]*\n|[^\S\n]*%[^\n]*\n)*)"
    r"[^\S\n]*\\begin\{(" + BOX + r")\}")


def _nu(nom):
    """Le type de boîte, sans préfixe `my` ni étoile : `myremark*` est une
    remarque (non numérotée), la tolérance s'y applique pareil."""
    return nom.replace("my", "").rstrip("*")


def tolere(avant, apres):
    nus = (_nu(avant), _nu(apres))
    return nus in CHAINE_TOLEREE or nus[1] == ENTREE_TOLEREE


def _est_boite(n):
    return n.genre == "environnement" and RE_BOITE.fullmatch(n.nom)


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


def chaines_arbre(arbre):
    """(boîte, boîte suivante) séparées seulement par de la mise en page,
    dans l'ordre du texte."""
    paires = []
    for freres in _freres(arbre):
        precedente = None
        for n in freres:
            if _est_boite(n):
                if precedente is not None:
                    paires.append((precedente, n))
                precedente = n
            elif not _transparent(n, arbre.texte):
                precedente = None
    return sorted(paires, key=lambda p: p[0].fin)


def regle_P2(racines):
    """P2 — enchaînements de boîtes sans texte entre elles."""
    for chemin in sources(racines):
        arbre = lire_arbre(chemin)
        if arbre.erreur is None:
            for avant, apres in chaines_arbre(arbre):
                if not tolere(avant.nom, apres.nom):
                    # la ligne du \end{…} de la première boîte
                    ligne = arbre.position(avant.fin - 1)[0]
                    yield chemin, ligne, f"{avant.nom} -> {apres.nom}"
            continue
        texte = sans_commentaires(arbre.texte)            # repli
        for m in RE_CHAINE.finditer(texte):
            if not tolere(m.group(1), m.group(3)):
                yield (chemin, ligne_de(texte, m.start()),
                       f"{m.group(1)} -> {m.group(3)}")
