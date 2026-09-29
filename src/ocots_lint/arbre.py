"""Lecture par arbre syntaxique (S4.2) — décision 0004.

    arbre = lire_arbre(chemin)
    if arbre.erreur:            # analyse refusée : la règle se replie sur
        ...                     # la lecture par masques (lecture.py)
    for noeud in arbre.parcourir():
        ligne, colonne = arbre.position(noeud.debut)

Les règles ne voient que des `Noeud` d'ocots-lint, jamais les classes de
`pylatexenc` : changer d'analyseur ne touche que ce module.

Genres de nœud :

    texte          caractères de prose
    commentaire    `% …` jusqu'à la fin de ligne (sans le `\\%` échappé)
    macro          `\\nom` et ses arguments (`arguments`)
    environnement  `\\begin{nom}…\\end{nom}` (`enfants`, `arguments`)
    maths          `$…$`, `\\[…\\]`, `\\(…\\)`, environnements de ENV_MATHS,
                   `\\ensuremath{…}`
    verbatim       contenu lu tel quel, jamais analysé : environnements de
                   ENV_VERBATIM, `\\verb`, `\\url`
    groupe         `{…}`
    special        `~`, `--`, ``` `` ```…

L'analyse est **stricte** : sur du LaTeX qu'elle ne sait pas lire (accolade
orpheline, `>{$}l<{$}` dans une spécification de colonnes…), l'arbre n'a pas
de nœuds et porte une `erreur` avec sa position. Jamais d'arbre partiel : le
mode tolérant de `pylatexenc` produit alors des erreurs en cascade, sans le
dire (décision 0004).

Positions : décalages dans le texte source (`debut` inclus, `fin` exclu) ;
`position()` les traduit en (ligne, colonne), à partir de 1.
"""

import bisect
import functools
from dataclasses import dataclass

from pylatexenc import latexwalker as lw
from pylatexenc.macrospec import (
    EnvironmentSpec,
    MacroSpec,
    MacroStandardArgsParser,
    ParsedVerbatimArgs,
)

from ocots_lint.lecture import lire

ENV_MATHS = ("equation", "align", "alignat", "flalign", "gather", "multline",
             "eqnarray", "displaymath", "math", "aligned", "array", "cases",
             "split", "pmatrix", "bmatrix", "vmatrix")
ENV_VERBATIM = ("verbatim", "lstlisting", "minted", "Verbatim")
MACROS_VERBATIM = ("verb", "url")
MACROS_MATHS = ("ensuremath",)
# Environnements qui ne sont pas de la prose sans être des maths : leur
# texte est du code de dessin (`prose()` les blanchit).
ENV_HORS_PROSE = ("tikzpicture",)


def _etoilees(noms):
    return frozenset(noms) | {f"{n}*" for n in noms}


_MATHS = _etoilees(ENV_MATHS)
_VERBATIM = _etoilees(ENV_VERBATIM)
_HORS_PROSE = _etoilees(ENV_HORS_PROSE)


# ------------------------------------------------------------ analyseur

class _Verbatim(MacroStandardArgsParser):
    """Contenu lu tel quel : jusqu'à `\\end{nom}` pour un environnement,
    jusqu'à l'accolade fermante pour `\\url{…}`.

    `pylatexenc` 2 ne sait lire ainsi que `verbatim` et `\\verb` (son
    `VerbatimArgsParser` cherche toujours `\\end{verbatim}`). Pour un
    environnement, les options (`[language=…]`, `{python}`) font partie du
    contenu verbatim."""

    def __init__(self, fin=None):
        super().__init__(argspec="{")
        self.fin = fin

    def parse_args(self, w, pos, parsing_state=None):
        if self.fin is not None:
            fin = w.s.find(self.fin, pos)
            if fin == -1:
                raise lw.LatexWalkerParseError(s=w.s, pos=pos,
                                               msg=f"{self.fin} introuvable")
        else:
            debut = pos
            while debut < len(w.s) and w.s[debut].isspace():
                debut += 1
            fin = w.s.find("}", debut) + 1 if w.s[debut:debut + 1] == "{" else 0
            if fin == 0:
                raise lw.LatexWalkerParseError(s=w.s, pos=pos,
                                               msg="argument {…} attendu")
        contenu = w.make_node(lw.LatexCharsNode, parsing_state=parsing_state,
                              chars=w.s[pos:fin], pos=pos, len=fin - pos)
        return ParsedVerbatimArgs(verbatim_chars_node=contenu), pos, fin - pos


def _contexte():
    ctx = lw.get_default_latex_context_db().filter_context()
    ctx.add_context_category(
        "ocots-lint", prepend=True,
        environments=[EnvironmentSpec(n, args_parser=_Verbatim(f"\\end{{{n}}}"))
                      for n in sorted(_VERBATIM - {"verbatim"})],
        macros=[MacroSpec("url", args_parser=_Verbatim())])
    return ctx


_CONTEXTE = _contexte()


# ------------------------------------------------------------ modèle

@dataclass(frozen=True)
class Noeud:
    genre: str
    nom: str | None
    debut: int
    fin: int
    enfants: tuple = ()
    arguments: tuple = ()


@dataclass(frozen=True)
class Erreur:
    debut: int
    message: str


@dataclass(frozen=True)
class Arbre:
    texte: str
    noeuds: tuple | None
    erreur: Erreur | None = None

    @functools.cached_property
    def _debuts_de_ligne(self):
        return [0] + [i + 1 for i, c in enumerate(self.texte) if c == "\n"]

    def position(self, decalage):
        """(ligne, colonne) du décalage, à partir de 1."""
        i = bisect.bisect_right(self._debuts_de_ligne, decalage) - 1
        return i + 1, decalage - self._debuts_de_ligne[i] + 1

    def parcourir(self, noeuds=None):
        """Tous les nœuds, en profondeur, dans l'ordre du texte : arguments
        d'un nœud avant ses enfants. Rien si l'analyse a été refusée."""
        for n in (self.noeuds or ()) if noeuds is None else noeuds:
            yield n
            yield from self.parcourir(n.arguments)
            yield from self.parcourir(n.enfants)


# ------------------------------------------------------------ conversion

def _liste(noeuds):
    return tuple(_convertir(n) for n in noeuds or () if n is not None)


def _arguments(n):
    argd = getattr(n, "nodeargd", None)
    return _liste(getattr(argd, "argnlist", None))


def _convertir(n):
    debut, fin = n.pos, n.pos + n.len
    verbatim = isinstance(getattr(n, "nodeargd", None), ParsedVerbatimArgs)
    if isinstance(n, lw.LatexCharsNode):
        return Noeud("texte", None, debut, fin)
    if isinstance(n, lw.LatexCommentNode):
        return Noeud("commentaire", None, debut, fin)
    if isinstance(n, lw.LatexGroupNode):
        return Noeud("groupe", None, debut, fin, _liste(n.nodelist))
    if isinstance(n, lw.LatexMathNode):
        return Noeud("maths", n.displaytype, debut, fin, _liste(n.nodelist))
    if isinstance(n, lw.LatexSpecialsNode):
        return Noeud("special", n.specials_chars, debut, fin, (), _arguments(n))
    if isinstance(n, lw.LatexMacroNode):
        if verbatim or n.macroname in MACROS_VERBATIM:
            return Noeud("verbatim", n.macroname, debut, fin)
        genre = "maths" if n.macroname in MACROS_MATHS else "macro"
        return Noeud(genre, n.macroname, debut, fin, (), _arguments(n))
    if isinstance(n, lw.LatexEnvironmentNode):
        nom = n.environmentname
        if verbatim or nom in _VERBATIM:
            return Noeud("verbatim", nom, debut, fin)
        genre = "maths" if nom in _MATHS else "environnement"
        return Noeud(genre, nom, debut, fin, _liste(n.nodelist), _arguments(n))
    raise TypeError(f"nœud pylatexenc inattendu : {type(n).__name__}")


# ------------------------------------------------------------ prose

def _hors_prose(noeuds):
    """Intervalles (début, fin) des nœuds qui ne sont pas de la prose, sans
    descendre dans ceux qu'on écarte déjà."""
    for n in noeuds:
        if n.genre in ("commentaire", "maths", "verbatim") or (
                n.genre == "environnement" and n.nom in _HORS_PROSE):
            yield n.debut, n.fin
        else:
            yield from _hors_prose(n.arguments)
            yield from _hors_prose(n.enfants)


def prose(arbre):
    """Le texte source où ce qui n'est pas de la prose est blanchi —
    commentaires, maths, verbatim, figures (ENV_HORS_PROSE) —, longueur et
    retours à la ligne conservés : une position trouvée dans le résultat
    désigne le même caractère dans la source, à la même ligne."""
    morceaux, fin = [], 0
    for debut, f in sorted(_hors_prose(arbre.noeuds or ())):
        if debut < fin:          # imbriqué dans une zone déjà blanchie
            continue
        morceaux.append(arbre.texte[fin:debut])
        morceaux.append("".join(c if c == "\n" else " "
                                for c in arbre.texte[debut:f]))
        fin = f
    morceaux.append(arbre.texte[fin:])
    return "".join(morceaux)


# ------------------------------------------------------------ entrée

@functools.lru_cache(maxsize=256)
def analyser(texte):
    """L'arbre de `texte` ; en cas de refus, un arbre sans nœuds et l'erreur.
    Mis en cache par contenu : plusieurs règles lisent le même fichier."""
    try:
        noeuds, _, _ = lw.LatexWalker(texte, latex_context=_CONTEXTE,
                                      tolerant_parsing=False).get_latex_nodes()
    except lw.LatexWalkerError as e:
        pos = getattr(e, "pos", None)
        message = getattr(e, "msg", None) or str(e).splitlines()[0]
        return Arbre(texte, None, Erreur(pos if pos is not None else 0, message))
    except Exception as e:  # défaut de pylatexenc : une erreur, pas un plantage
        return Arbre(texte, None, Erreur(0, f"{type(e).__name__} : {e}"))
    return Arbre(texte, _liste(noeuds))


def lire_arbre(chemin):
    return analyser(lire(chemin))
