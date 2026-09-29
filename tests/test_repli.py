"""Repli sur les masques pour un fichier que l'analyse syntaxique refuse
(décision 0004) : les trouvailles restent, et un avertissement le dit."""

import json

from ocots_lint import verifier

from outils import FIXTURES

REFUSE = str(FIXTURES / "C4" / "signale" / "colonnes_longtable.tex")


def lancer(capsys, *argv):
    code = verifier.main(list(argv))
    sortie = capsys.readouterr()
    return code, sortie.out, sortie.err


def test_trouvaille_conservee_et_avertissement(capsys):
    code, out, err = lancer(capsys, "C4", REFUSE)
    assert code == 1
    assert out.endswith("colonnes_longtable.tex:8: [C4] mot composé — trait d'union\n")
    (avert,) = [l for l in err.splitlines() if "[ocots-lint]" in l]
    assert "colonnes_longtable.tex:4: [ocots-lint] analyse syntaxique refusée" in avert
    assert "C4 lu par les masques de secours" in avert


def test_avertissement_dans_le_json(capsys):
    _, out, _ = lancer(capsys, "C4", REFUSE, "--format", "json")
    (avert,) = json.loads(out)["avertissements"]
    assert avert["ligne"] == 4
    assert "analyse syntaxique refusée" in avert["message"]


def test_pas_d_avertissement_si_aucune_regle_ne_lit_l_arbre(capsys):
    _, _, err = lancer(capsys, "P2", REFUSE)
    assert "[ocots-lint]" not in err


def test_pas_d_avertissement_pour_un_fichier_analyse(capsys):
    _, _, err = lancer(capsys, "C4", str(FIXTURES / "C4" / "signale"
                                         / "tilde_deux_points.tex"))
    assert "[ocots-lint]" not in err
