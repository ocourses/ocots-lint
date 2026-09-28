"""Exemptions `% ocots-lint: ignore <règles> — raison` (S2.4)."""

import textwrap

from ocots_lint import verifier
from ocots_lint.exemptions import lire_directives

CHAINE = r"""
\begin{theorem}
  Énoncé.
\end{theorem}{fin}

\begin{proposition}
  Énoncé.
\end{proposition}
"""


def ecrire(tmp_path, texte, nom="a.tex"):
    chemin = tmp_path / nom
    chemin.write_text(textwrap.dedent(texte).lstrip("\n"), encoding="utf-8")
    return str(chemin)


def lancer(capsys, *argv):
    code = verifier.main(list(argv))
    sortie = capsys.readouterr()
    return code, sortie.out, sortie.err


def test_directive_en_fin_de_ligne(tmp_path, capsys):
    f = ecrire(tmp_path, CHAINE.replace(
        "{fin}", " % ocots-lint: ignore P2 — corollaire immédiat"))
    code, out, err = lancer(capsys, "P2", f)
    assert (code, out) == (0, "")
    assert "P2 : 0 infraction(s) (+ 1 exemptée(s))" in err


def test_directive_seule_couvre_la_ligne_suivante(tmp_path, capsys):
    f = ecrire(tmp_path, CHAINE.replace("{fin}", "").replace(
        "\\end{theorem}", "% ocots-lint: ignore P2 -- voulu\n\\end{theorem}"))
    assert lancer(capsys, "P2", f)[0] == 0


def test_directive_seule_ne_couvre_pas_sa_propre_ligne_ni_au_dela(tmp_path, capsys):
    f = ecrire(tmp_path, CHAINE.replace("{fin}", "").replace(
        "  Énoncé.\n\\end{theorem}",
        "  % ocots-lint: ignore P2 — trop tôt\n  Énoncé.\n\\end{theorem}"))
    code, out, err = lancer(capsys, "P2", f)
    assert code == 1
    assert "[ocots-lint] exemption P2 inutile" in err


def test_raison_obligatoire(tmp_path, capsys):
    f = ecrire(tmp_path, CHAINE.replace("{fin}", " % ocots-lint: ignore P2"))
    code, out, err = lancer(capsys, "P2", f)
    assert code == 1
    assert "exemption sans règle ou sans raison, ignorée" in err


def test_autre_regle_non_exemptee(tmp_path, capsys):
    f = ecrire(tmp_path, CHAINE.replace(
        "{fin}", " % ocots-lint: ignore P5 — mauvaise règle"))
    code, _, err = lancer(capsys, "P2", "P5", f)
    assert code == 1
    assert "exemption P5 inutile" in err


def test_regle_non_lancee_ne_rend_pas_l_exemption_inutile(tmp_path, capsys):
    f = ecrire(tmp_path, CHAINE.replace(
        "{fin}", " % ocots-lint: ignore P2 — voulu"))
    _, _, err = lancer(capsys, "C4", f)
    assert "inutile" not in err


def test_sans_exemptions_montre_tout(tmp_path, capsys):
    f = ecrire(tmp_path, CHAINE.replace(
        "{fin}", " % ocots-lint: ignore P2 — voulu"))
    code, out, err = lancer(capsys, "P2", "--sans-exemptions", f)
    assert code == 1
    assert "[P2] theorem -> proposition" in out
    assert "exemptée" not in err


def test_plusieurs_regles_une_directive(tmp_path, capsys):
    f = ecrire(tmp_path, r"""
        % ocots-lint: ignore P5, P2 — quatre vrais apartés
        \begin{remark} Un. \end{remark}
        \begin{remark} Deux. \end{remark}
        \begin{remark} Trois. \end{remark}
        \begin{remark} Quatre. \end{remark}
        """)
    code, _, err = lancer(capsys, "P5", f)
    assert code == 0
    assert "inutile" not in err     # P2 n'a pas été lancée


def test_lecture_des_directives():
    valides, invalides = lire_directives(
        "a % ocots-lint: ignore C4, P2 — raison\n"
        "  % ocots-lint: ignore P3: autre raison\n"
        "\\% ocots-lint: ignore P2 — pourcentage échappé, pas un commentaire\n"
        "% ocots-lint: ignore — sans règle\n")
    assert [(d.ligne, d.couverte, sorted(d.regles), d.raison) for d in valides] == [
        (1, 1, ["C4", "P2"], "raison"),
        (2, 3, ["P3"], "autre raison"),
    ]
    assert [no for no, _ in invalides] == [4]
