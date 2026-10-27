from pathlib import Path

from ocots_lint.verifier import analyser

FIXTURES = Path(__file__).parent / "fixtures/P2"


def trouvees(fichier):
    return analyser([str(fichier)], ["P2"])[0]


def test_p2_nes_signale_pas_deux_boites_sous_un_slide_titre():
    assert trouvees(FIXTURES / "accepte/slides/titre.tex") == []


def test_p2_signale_deux_boites_sous_une_frame_nue():
    trouvailles = trouvees(FIXTURES / "signale/slides/frame_nue.tex")
    assert len(trouvailles) == 1
    assert trouvailles[0].regle == "P2"
