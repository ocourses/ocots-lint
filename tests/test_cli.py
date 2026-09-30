import os

from ocots_lint import cli
from ocots_lint.regles import REGLES

from outils import FIXTURES

SIGNALE = FIXTURES / "P2" / "signale" / "ligne_blanche.tex"
ACCEPTE = FIXTURES / "P2" / "accepte" / "texte_entre.tex"


def test_sans_argument_affiche_l_aide(capsys):
    assert cli.main([]) == 0
    assert "verifier" in capsys.readouterr().out


def test_version(capsys):
    assert cli.main(["--version"]) == 0
    assert capsys.readouterr().out.startswith("ocots-lint ")


def test_commande_inconnue(capsys):
    assert cli.main(["inconnue"]) == 2
    assert "commande inconnue" in capsys.readouterr().err


def test_list_nomme_chaque_regle(capsys):
    assert cli.main(["verifier", "--list"]) == 0
    sortie = capsys.readouterr().out
    for regle in REGLES:
        assert f"  {regle}  " in sortie


def test_sortie_1_si_infraction(capsys):
    assert cli.main(["verifier", "P2", str(SIGNALE)]) == 1
    sortie = capsys.readouterr()
    assert sortie.out == f"{os.path.relpath(SIGNALE)}:3: [P2] theorem -> proposition\n"
    assert sortie.err == "P2 : 1 infraction(s)\n"


def test_sortie_0_sans_infraction(capsys):
    assert cli.main(["verifier", "P2", str(ACCEPTE)]) == 0
    assert capsys.readouterr().out == ""


def test_toutes_les_regles_par_defaut(capsys, monkeypatch):
    monkeypatch.chdir(ACCEPTE.parent)    # comme depuis la racine d'un cours
    cli.main(["verifier", str(ACCEPTE)])
    bilan = capsys.readouterr().err.splitlines()
    assert [ligne.split(" : ")[0] for ligne in bilan] == sorted(REGLES)


def test_chemin_inconnu(capsys):
    assert cli.main(["verifier", "P2", "n-existe-pas/"]) == 2
    assert "chemin ou règle inconnu : n-existe-pas/" in capsys.readouterr().err
