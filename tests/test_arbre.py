"""Lecture par arbre (S4.2) : genres, positions, verbatim, maths, refus."""

import pathlib

import pytest

from ocots_lint import arbre
from ocots_lint.arbre import analyser

FIXTURES = pathlib.Path(__file__).parent / "fixtures"

# Fixtures que l'analyse stricte refuse, en connaissance de cause : elles
# sont lues par le repli (décision 0004). Toute nouvelle entrée est un choix.
REFUSEES = {
    "P2/limites/boite_par_macro.tex",       # \begin sans \end dans une macro
    "C4/signale/colonnes_longtable.tex",    # >{$}l<{$} (cas réel du corpus)
}


def genres(texte):
    a = analyser(texte)
    assert a.erreur is None, a.erreur
    return [(n.genre, n.nom, a.texte[n.debut:n.fin]) for n in a.parcourir()]


def premier(texte, genre):
    return next(g for g in genres(texte) if g[0] == genre)


# ------------------------------------------------------------ genres

def test_prose_commentaire_et_pourcent_echappe():
    g = genres("50\\% des cas % un commentaire\nsuite")
    assert ("macro", "%", "\\%") in g
    assert ("commentaire", None, "% un commentaire\n") in g
    assert ("texte", None, "suite") in g


def test_environnement_et_ses_arguments():
    a = analyser("\\begin{theorem}[title=T]\n  Énoncé.\n\\end{theorem}")
    (env,) = a.noeuds
    assert (env.genre, env.nom) == ("environnement", "theorem")
    assert [a.texte[n.debut:n.fin] for n in env.arguments] == ["[title=T]"]
    assert "Énoncé." in [a.texte[n.debut:n.fin].strip() for n in env.enfants]


@pytest.mark.parametrize("source, nom", [
    ("$x ~:~ y$", "inline"),
    ("\\(x ~:~ y\\)", "inline"),
    ("\\[x ~:~ y\\]", "display"),
    ("\\begin{equation}x ~:~ y\\end{equation}", "equation"),
    ("\\begin{align*}x &= y\\end{align*}", "align*"),
    ("\\begin{alignat}{2}x &= y\\end{alignat}", "alignat"),
    ("\\begin{displaymath}x\\end{displaymath}", "displaymath"),
    ("\\ensuremath{\\forall h ~:~ h = 0}", "ensuremath"),
])
def test_maths(source, nom):
    assert premier(source, "maths")[:2] == ("maths", nom)


@pytest.mark.parametrize("source, nom", [
    ("\\verb|a~:b| fin", "verb"),
    ("\\url{https://exemple.org/a~:b} fin", "url"),
    ("\\begin{verbatim}\na~:b \\end{x} {\n\\end{verbatim}\nfin", "verbatim"),
    ("\\begin{verbatim*}\na~:b {\n\\end{verbatim*}\nfin", "verbatim*"),
    ("\\begin{lstlisting}[language=Python]\na~:b \\end{x} {\n\\end{lstlisting}\nfin",
     "lstlisting"),
    ("\\begin{minted}{python}\na~:b {\n\\end{minted}\nfin", "minted"),
    ("\\begin{Verbatim}[frame=single]\na~:b {\n\\end{Verbatim}\nfin", "Verbatim"),
])
def test_verbatim_lu_tel_quel(source, nom):
    a = analyser(source)
    assert a.erreur is None, a.erreur
    verbatims = [n for n in a.parcourir() if n.genre == "verbatim"]
    assert [(n.nom, n.enfants, n.arguments) for n in verbatims] == [(nom, (), ())]
    assert not any(n.genre == "special" for n in a.parcourir())   # pas de ~ vu
    assert a.texte[verbatims[0].fin:].strip() == "fin"


# ------------------------------------------------------------ positions

def test_position_ligne_colonne():
    a = analyser("ab\n\ncd $x$\n")
    (m,) = [n for n in a.parcourir() if n.genre == "maths"]
    assert (a.position(m.debut), a.position(m.fin)) == ((3, 4), (3, 7))
    assert a.position(0) == (1, 1)


def couvre_tout(a):
    """Les nœuds de premier niveau pavent le texte, sans trou."""
    bornes = [(n.debut, n.fin) for n in a.noeuds]
    return (bornes[0][0] == 0 and bornes[-1][1] == len(a.texte)
            and all(f == d for (_, f), (d, _) in zip(bornes, bornes[1:], strict=False)))


FICHIERS = sorted(p.relative_to(FIXTURES).as_posix()
                  for p in FIXTURES.rglob("*.tex"))


@pytest.mark.parametrize("fixture", FICHIERS)
def test_fixtures_analysees_ou_refusees_en_connaissance_de_cause(fixture):
    a = arbre.lire_arbre(FIXTURES / fixture)
    if fixture in REFUSEES:
        assert a.erreur is not None and a.noeuds is None
    else:
        assert a.erreur is None, a.erreur
        assert couvre_tout(a)


# ------------------------------------------------------------ refus

def test_refus_porte_la_position_de_l_erreur():
    a = arbre.lire_arbre(FIXTURES / "C4/signale/colonnes_longtable.tex")
    assert a.erreur.message
    assert a.position(a.erreur.debut)[0] == 4       # la ligne du longtable
    assert list(a.parcourir()) == []


def test_url_sans_accolade_refusee():
    assert analyser("\\url x").erreur.message == "argument {…} attendu"


def test_verbatim_non_ferme_refuse():
    assert "\\end{lstlisting}" in analyser("\\begin{lstlisting}\nx").erreur.message


def test_defaut_de_l_analyseur_devient_une_erreur(monkeypatch):
    class Casse:
        def __init__(self, *a, **k):
            pass

        def get_latex_nodes(self):
            raise IndexError("boum")
    monkeypatch.setattr(arbre.lw, "LatexWalker", Casse)
    arbre.analyser.cache_clear()
    try:
        assert arbre.analyser("x").erreur.message == "IndexError : boum"
    finally:
        arbre.analyser.cache_clear()


def test_cache_par_contenu():
    assert analyser("texte identique") is analyser("texte identique")
