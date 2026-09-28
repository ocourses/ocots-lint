"""Cohérence du registre, et avec la version épinglée des conventions (S2.2).

Si les conventions renumérotent ou retirent une règle outillée, ces tests
échouent au moment où l'on monte le sous-module : c'est voulu.
"""

from pathlib import Path

import pytest

from ocots_lint import conventions
from ocots_lint.couverture import inconnues, outillage
from ocots_lint.mesures import MESURES
from ocots_lint.regles import GARANTIES, REGISTRE, REGLES

EPINGLEES = Path(__file__).parent.parent / "conventions"


def test_chaque_verificateur_a_une_garantie_du_vocabulaire():
    for v in REGISTRE:
        assert v.garantie in GARANTIES, v
        assert v.garantie != "mesure", "une mesure passe par MESURES, pas REGISTRE"


def test_un_verificateur_par_regle():
    assert len(REGLES) == len(REGISTRE)


def test_chaque_verificateur_a_un_resume():
    for v in REGISTRE:
        assert v.resume.startswith(f"{v.regle} — "), v.resume


def test_ancre_comme_github():
    assert conventions.ancre("P7 — Ouverture de chapitre et de section") == (
        "p7--ouverture-de-chapitre-et-de-section")
    assert conventions.ancre("P5 — Ce qu'est une `remark`") == (
        "p5--ce-quest-une-remark")


@pytest.fixture
def epinglees():
    try:
        return conventions.trouver(str(EPINGLEES))
    except conventions.ConventionsIntrouvables:
        pytest.skip("sous-module conventions absent")


def test_regles_outillees_presentes_dans_les_conventions_epinglees(epinglees):
    assert inconnues(conventions.regles(epinglees)) == []


def test_identifiants_uniques_dans_les_conventions_epinglees(epinglees):
    idents = [r.ident for r in conventions.regles(epinglees)]
    assert len(idents) == len(set(idents))


def test_mesures_et_verificateurs_couverts(epinglees):
    idents = {r.ident for r in conventions.regles(epinglees)}
    assert {regle for regle, *_ in MESURES} <= idents
    assert set(outillage()) <= idents
