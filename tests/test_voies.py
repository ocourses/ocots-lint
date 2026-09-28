"""Voie d'une trouvaille (S3.6)."""

from ocots_lint import voies
from ocots_lint.regles import Verificateur, regle_P2
from ocots_lint.verifier import analyser


def voies_de(tmp_path, texte, regles=("C4",), csquotes=False):
    (tmp_path / "a.tex").write_text(texte, encoding="utf-8")
    if csquotes:
        (tmp_path / "preambule.tex").write_text("\\usepackage{csquotes}\n",
                                                encoding="utf-8")
    trouvailles, _ = analyser([str(tmp_path)], list(regles))
    return {(t.ligne, t.message.split(" ")[0]): t.voie for t in trouvailles}


def test_tilde_est_mecanique(tmp_path):
    assert voies_de(tmp_path, "question~: ici\n") == {(1, "`~:`"): "mecanique"}


def test_tilde_en_maths_n_est_pas_signale(tmp_path):
    assert voies_de(tmp_path, "$a ~: b$\n") == {}


def test_guillemets_mecaniques_seulement_avec_csquotes(tmp_path):
    assert voies_de(tmp_path, "``ici''\n") == {(1, "guillemets"): "tri"}
    assert voies_de(tmp_path, "``ici''\n", csquotes=True) == {
        (1, "guillemets"): "mecanique"}


def test_guillemets_hors_de_portee_de_nettoyer(tmp_path):
    """nettoyer ne touche pas une paire qui enjambe un paragraphe."""
    assert voies_de(tmp_path, "``un\n\ndeux''\n", csquotes=True) == {
        (1, "guillemets"): "tri"}


def test_autres_c4_au_tri(tmp_path):
    assert voies_de(tmp_path, "le théorème~\\ref{x}\n") == {(1, "renvoi"): "tri"}


def test_heuristique_au_tri(tmp_path):
    texte = "\\begin{theorem}\n\\end{theorem}\n\n\\begin{lemma}\n\\end{lemma}\n"
    assert voies_de(tmp_path, texte, regles=("P2",)) == {(2, "theorem"): "tri"}


def test_exact_va_a_la_correction(tmp_path, monkeypatch):
    monkeypatch.setattr(voies, "REGISTRE", (Verificateur("P2", regle_P2, "exact"),))
    texte = "\\begin{theorem}\n\\end{theorem}\n\n\\begin{lemma}\n\\end{lemma}\n"
    assert voies_de(tmp_path, texte, regles=("P2",)) == {
        (2, "theorem"): "correction"}
