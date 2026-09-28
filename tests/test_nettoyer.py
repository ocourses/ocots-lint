"""`ocots-lint nettoyer` (S2.6) : corrections, et garde-fous."""

import shutil

from ocots_lint import nettoyer

from outils import FIXTURES

NETTOYER = FIXTURES / "nettoyer"


def corriger(texte, guillemets=True):
    return nettoyer.appliquer_corrections(
        texte, nettoyer.corrections_C4(texte, guillemets=guillemets))


def test_tilde_retire_hors_maths_seulement():
    assert corriger("question~: $a ~:~ b$ \\[ x ~: y \\]") == (
        "question: $a ~:~ b$ \\[ x ~: y \\]")


def test_guillemets_en_enquote():
    assert corriger("dit ``presque partout''.") == "dit \\enquote{presque partout}."


def test_guillemets_laisses_sans_csquotes():
    assert corriger("dit ``ici''~:", guillemets=False) == "dit ``ici'':"


def test_paire_qui_enjambe_un_paragraphe_intacte():
    texte = "``un\n\ndeux''"
    assert corriger(texte) == texte


def test_apercu_n_ecrit_rien(tmp_path, capsys):
    copie = tmp_path / "cas"
    shutil.copytree(NETTOYER / "avec-csquotes", copie)
    avant = (copie / "b.tex").read_text(encoding="utf-8")
    assert nettoyer.main(["C4", str(copie)]) == 0
    assert (copie / "b.tex").read_text(encoding="utf-8") == avant
    assert "Rien n'a été écrit" in capsys.readouterr().err


def test_appliquer_ecrit(tmp_path, capsys):
    copie = tmp_path / "cas"
    shutil.copytree(NETTOYER / "avec-csquotes", copie)
    assert nettoyer.main(["C4", str(copie), "--appliquer"]) == 0
    b = (copie / "b.tex").read_text(encoding="utf-8")
    assert "\\enquote{presque partout}" in b and "~:" not in b
    assert "$``x''$" in b


def test_sans_csquotes_le_dit(tmp_path, capsys):
    copie = tmp_path / "cas"
    shutil.copytree(NETTOYER / "sans-csquotes", copie)
    nettoyer.main(["C4", str(copie), "--appliquer"])
    assert "csquotes introuvable" in capsys.readouterr().err
    assert "``presque partout''" in (copie / "a.tex").read_text(encoding="utf-8")


def test_chemin_inconnu(capsys):
    assert nettoyer.main(["C4", "n-existe-pas/"]) == 2


def test_ligne_exemptee_non_corrigee(tmp_path, capsys):
    f = tmp_path / "a.tex"
    f.write_text("voulu~: ici % ocots-lint: ignore C4 — forme voulue\n"
                 "corrigé~: là\n", encoding="utf-8")
    assert nettoyer.main(["C4", str(tmp_path), "--appliquer"]) == 0
    assert f.read_text(encoding="utf-8") == (
        "voulu~: ici % ocots-lint: ignore C4 — forme voulue\ncorrigé: là\n")
