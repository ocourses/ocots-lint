"""`verifier --nouvelles <réf>` (S3.8) : seulement ce qui est nouveau."""

import subprocess

import pytest

from ocots_lint import verifier

CHAINE = "\\begin{theorem}\nx\n\\end{theorem}\n\n\\begin{lemma}\ny\n\\end{lemma}\n"


def git(*args):
    subprocess.run(["git", *args], check=True, capture_output=True)


@pytest.fixture
def depot(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "cours").mkdir()
    (tmp_path / "cours" / "a.tex").write_text("Texte.\n\n" + CHAINE, encoding="utf-8")
    git("init", "-q")
    git("add", "-A")
    git("-c", "user.email=x@y", "-c", "user.name=x", "commit", "-qm", "init")
    return tmp_path


def lancer(capsys, *argv):
    code = verifier.main(list(argv))
    sortie = capsys.readouterr()
    return code, sortie.out, sortie.err


def test_rien_de_nouveau(depot, capsys):
    code, out, err = lancer(capsys, "--nouvelles", "HEAD")
    assert (code, out) == (0, "")
    assert "P2 : 0 infraction(s) nouvelle(s) depuis HEAD" in err


def test_seulement_la_nouvelle(depot, capsys):
    f = depot / "cours" / "a.tex"
    f.write_text("Ajout.\n\n" + f.read_text(encoding="utf-8")
                 + "\nUn sous espace.\n", encoding="utf-8")
    code, out, _ = lancer(capsys, "--nouvelles", "HEAD")
    assert code == 1
    assert out == "cours/a.tex:13: [C4] mot composé — trait d'union\n"


def test_nouveau_fichier(depot, capsys):
    (depot / "cours" / "b.tex").write_text(CHAINE, encoding="utf-8")
    code, out, _ = lancer(capsys, "--nouvelles", "HEAD", "P2")
    assert (code, out) == (1, "cours/b.tex:3: [P2] theorem -> lemma\n")


def test_retirer_une_exemption_fait_reapparaitre(depot, capsys):
    f = depot / "cours" / "a.tex"
    f.write_text(f.read_text(encoding="utf-8").replace(
        "\\end{theorem}", "% ocots-lint: ignore P2 — voulu\n\\end{theorem}"),
        encoding="utf-8")
    git("commit", "-qam", "exemption")
    assert lancer(capsys, "--nouvelles", "HEAD")[0] == 0
    git("checkout", "-q", "HEAD~1", "--", "cours/a.tex")
    assert lancer(capsys, "--nouvelles", "HEAD", "P2")[0] == 1


def test_depuis_un_sous_dossier(depot, capsys, monkeypatch):
    f = depot / "cours" / "a.tex"
    f.write_text(f.read_text(encoding="utf-8") + "\nUn sous espace.\n",
                 encoding="utf-8")
    monkeypatch.chdir(depot / "cours")
    code, out, _ = lancer(capsys, "--nouvelles", "HEAD", "C4")
    assert (code, out) == (1, "a.tex:11: [C4] mot composé — trait d'union\n")


def test_reference_inconnue(depot, capsys):
    code, _, err = lancer(capsys, "--nouvelles", "n-existe-pas")
    assert code == 2
    assert "git archive" in err


def test_hors_d_un_depot_git(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "a.tex").write_text(CHAINE, encoding="utf-8")
    assert lancer(capsys, "--nouvelles", "HEAD")[0] == 2
