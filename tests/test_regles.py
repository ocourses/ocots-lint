"""Chaque fixture fixe le comportement d'une règle : les lignes signalées
doivent être exactement celles marquées `% attendu: <règle>`.

- `signale/` : au moins une trouvaille attendue ;
- `accepte/` : aucune ;
- `limites/` : ce que l'outil *devrait* faire et ne fait pas encore. Le test
  est attendu en échec (xfail strict) : le jour où l'outil y parvient, le test
  passe, pytest le signale, et la fixture migre vers `signale/` ou `accepte/`.

Une fixture est vérifiée depuis son dossier, comme un cours depuis sa racine :
une règle qui croise tout le cours (C5) y lit aussi les fixtures voisines —
leurs clés doivent donc être distinctes.
"""

from collections import Counter

import pytest

from ocots_lint.regles import REGLES

from outils import FIXTURES, attendus, marques

GENRES = ("signale", "accepte", "limites")


def fixtures():
    return list(_fixtures())


def _fixtures():
    for regle in sorted(REGLES):
        for genre in GENRES:
            for chemin in sorted((FIXTURES / regle / genre).rglob("*.tex")):
                nom = f"{regle}/{chemin.relative_to(FIXTURES / regle)}"
                marks = [pytest.mark.xfail(reason="limite connue", strict=True)
                         ] if genre == "limites" else []
                yield pytest.param(regle, genre, chemin, id=nom, marks=marks)


@pytest.mark.parametrize("regle,genre,chemin", fixtures())
def test_trouvailles_conformes_aux_marques(regle, genre, chemin, monkeypatch):
    monkeypatch.chdir(chemin.parent)
    trouvees = Counter(ligne for _, ligne, _ in REGLES[regle]([str(chemin)]))
    assert trouvees == attendus(chemin, regle)


@pytest.mark.parametrize("regle,genre,chemin",
                         [p for p in fixtures() if p.values[1] != "limites"])
def test_genre_coherent_avec_les_marques(regle, genre, chemin):
    """Une fixture `signale/` marque au moins une trouvaille, une `accepte/`
    aucune : sinon le rangement ment sur ce que la fixture teste."""
    if genre == "signale":
        assert attendus(chemin, regle), "fixture signale/ sans marque attendue"
    else:
        assert not marques(chemin), "fixture accepte/ avec une marque attendue"


@pytest.mark.parametrize("regle", sorted(REGLES))
def test_chaque_regle_a_ses_fixtures(regle):
    for genre in ("signale", "accepte"):
        assert list((FIXTURES / regle / genre).rglob("*.tex")), (
            f"{regle} n'a aucune fixture {genre}/")


def test_pas_de_dossier_de_fixtures_orphelin():
    """Un dossier de fixtures doit correspondre à une règle implémentée."""
    dossiers = {d.name for d in FIXTURES.iterdir() if d.is_dir()}
    assert dossiers - {"mesures", "nettoyer"} <= set(REGLES)
