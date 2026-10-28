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
    _, _, err = lancer(capsys, "P5", REFUSE)
    assert "[ocots-lint]" not in err


def test_pas_d_avertissement_pour_un_fichier_analyse(capsys):
    _, _, err = lancer(capsys, "C4", str(FIXTURES / "C4" / "signale"
                                         / "tilde_deux_points.tex"))
    assert "[ocots-lint]" not in err


# ------------------------------------------------------------ règles sans repli (S8)

def refuse_dans(tmp_path, monkeypatch, dossier):
    """Un fichier que l'analyse refuse (accolade orpheline), rangé sous
    `dossier` dans un cours vide."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / dossier).mkdir(parents=True)
    chemin = tmp_path / dossier / "contenu.tex"
    chemin.write_text("Texte.\n}\n", encoding="utf-8")
    return str(chemin.relative_to(tmp_path))


def test_regle_sans_repli_dite_non_verifiee(tmp_path, monkeypatch, capsys):
    chemin = refuse_dans(tmp_path, monkeypatch, "td/td1")
    _, _, err = lancer(capsys, "TD8", "C4", chemin)
    (avert,) = [l for l in err.splitlines() if "[ocots-lint]" in l]
    assert "C4 lu par les masques de secours" in avert
    assert "TD8 non vérifié sur ce fichier" in avert


def test_regle_hors_de_son_support_pas_citee(tmp_path, monkeypatch, capsys):
    """Un fichier du polycopié refusé : TD8 ne l'aurait pas lu, l'avertissement
    ne la cite pas."""
    chemin = refuse_dans(tmp_path, monkeypatch, "poly")
    _, _, err = lancer(capsys, "TD8", chemin)
    assert "[ocots-lint]" not in err
    _, _, err = lancer(capsys, "TD8", "C4", chemin)
    assert "TD8" not in "".join(l for l in err.splitlines() if "[ocots-lint]" in l)
