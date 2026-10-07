"""`.agents-ignore` (préfixes de chemins, à la racine du cours) exclut des
fichiers du parcours des racines : un document rangé (`attic/`, `archived/`)
ne produit plus de trouvailles. Un fichier, ou un dossier, désigné
explicitement reste vérifié (issue #75)."""

import shutil

from ocots_lint import cli
from ocots_lint.lecture import sources

from outils import FIXTURES

SIGNALE = FIXTURES / "P2" / "signale" / "ligne_blanche.tex"


def _cours(tmp_path, monkeypatch, ignore="attic/\n"):
    (tmp_path / "poly").mkdir()
    (tmp_path / "attic" / "slides").mkdir(parents=True)
    shutil.copy(SIGNALE, tmp_path / "poly" / "a.tex")
    shutil.copy(SIGNALE, tmp_path / "attic" / "slides" / "b.tex")
    if ignore is not None:
        (tmp_path / ".agents-ignore").write_text(
            "# rangé\n" + ignore, encoding="utf-8")
    monkeypatch.chdir(tmp_path)


def test_parcours_saute_les_prefixes_ignores(tmp_path, monkeypatch):
    _cours(tmp_path, monkeypatch)
    assert sorted(sources(["."])) == ["./poly/a.tex"]


def test_sans_agents_ignore_tout_est_parcouru(tmp_path, monkeypatch):
    _cours(tmp_path, monkeypatch, ignore=None)
    assert sorted(sources(["."])) == ["./attic/slides/b.tex", "./poly/a.tex"]


def test_fichier_explicite_reste_verifie(tmp_path, monkeypatch):
    _cours(tmp_path, monkeypatch)
    assert list(sources(["attic/slides/b.tex"])) == ["attic/slides/b.tex"]


def test_dossier_explicite_ignore_reste_verifie(tmp_path, monkeypatch):
    _cours(tmp_path, monkeypatch)
    assert list(sources(["attic"])) == ["attic/slides/b.tex"]


def test_verifier_sans_argument(tmp_path, monkeypatch, capsys):
    _cours(tmp_path, monkeypatch)
    assert cli.main(["verifier", "P2"]) == 1
    sortie = capsys.readouterr().out
    assert "poly/a.tex" in sortie
    assert "attic/" not in sortie
