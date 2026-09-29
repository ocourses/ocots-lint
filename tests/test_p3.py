"""P3 sur l'arbre (S4.5) : la ponctuation finale d'une formule hors texte."""

import pytest

from ocots_lint.arbre import analyser
from ocots_lint.regles.p3 import ponctuation_finale, texte_p3


@pytest.mark.parametrize("source, attendue", [
    ("\\[ x = 1. \\]", "."),
    ("\\[\n  x = 1,\n\\]", ","),
    ("\\[ x = 1 \\]", None),
    ("$$ x = 1 ; $$", ";"),
    ("\\begin{equation}\n  x = 1.\n\\end{equation}", "."),
    ("\\begin{equation*} x = 1. \\label{eq:x} \\end{equation*}", "."),
    ("\\begin{align}\n  a &= b, \\\\\n  c &= d. \\\\[2pt]\n\\end{align}", "."),
    ("\\begin{align} a &= b. \\nonumber \\end{align}", "."),
    ("\\[ x = 1 \\quad \\text{.} \\]", "."),
    ("\\[ x = 1 \\, . \\]", "."),
    ("\\[ x = 1 \\, \\]", None),
    ("\\[ \\{ 1 \\} \\]", None),
])
def test_ponctuation_finale(source, attendue):
    assert ponctuation_finale(source) == attendue


def test_ponctuation_a_l_ouverture_de_la_formule():
    source = "par\n\\[\n  x = 1.\n\\]\n"
    lignes = [l.rstrip() for l in texte_p3(analyser(source)).split("\n")]
    assert lignes == ["par", ".", "", "", ""]


def test_formule_dans_une_formule_ignoree():
    source = "\\[ \\begin{cases} 1, \\\\ 2. \\end{cases} \\]"
    assert texte_p3(analyser(source)).strip() == ""


def test_repli_sur_le_masque_des_maths():
    source = "}\n\\[ x = 1. \\]\n"
    assert analyser(source).erreur is not None
    assert texte_p3(analyser(source)).strip() == "}"
