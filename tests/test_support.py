"""Le support d'un fichier (S8.0, décision 0009) : sa classe, sinon son
dossier, sinon le polycopié."""

import pytest

from ocots_lint import vocabulaire
from ocots_lint.lecture import est_transparent, support_de


@pytest.fixture
def v(tmp_path, monkeypatch):
    """Le vocabulaire embarqué : aucun `template/` dans le dossier courant."""
    monkeypatch.chdir(tmp_path)
    return vocabulaire.charger()


@pytest.mark.parametrize("classe,support", [
    ("ocots-td", "td"),
    ("ocots-exam", "exam"),
    ("beamer", "slides"),
    ("ocots-book", "book"),
    ("article", "book"),            # classe inconnue : support par défaut
])
def test_la_classe_declaree_decide(v, classe, support):
    texte = f"\\documentclass[11pt]{{{classe}}}\n\\begin{{document}}\n"
    assert support_de("poly/ailleurs.tex", texte, v) == support


@pytest.mark.parametrize("chemin,support", [
    ("td/td1/contenu.tex", "td"),
    ("exams/2024-2025/session1/contenu.tex", "exam"),
    ("slides/chapitre1/ch1.tex", "slides"),
    ("poly/mainmatter/ch1.tex", "book"),
    ("contenu.tex", "book"),
    # le dossier le plus proche l'emporte : un TD rangé sous les transparents
    ("slides/td/contenu.tex", "td"),
])
def test_sans_classe_le_dossier_decide(v, chemin, support):
    assert support_de(chemin, "Texte.\n", v) == support


def test_la_classe_l_emporte_sur_le_dossier(v):
    """`td/td4/slides-td4-rk.tex` d'automatique : des transparents rangés
    dans un TD."""
    texte = "\\documentclass{beamer}\n"
    assert support_de("td/td4/slides.tex", texte, v) == "slides"


def test_une_classe_commentee_ne_compte_pas(v):
    texte = "% \\documentclass{beamer}\nTexte.\n"
    assert support_de("td/td1/contenu.tex", texte, v) == "td"


def test_est_transparent_est_un_cas_du_support(v):
    assert est_transparent("slides/ch1.tex", "", v)
    assert not est_transparent("td/td1/contenu.tex", "", v)
