"""Formats `--format json` et `--format sarif` (S2.5)."""

import json
import textwrap

from ocots_lint import verifier

TEXTE = r"""
\begin{theorem}
  Énoncé.
\end{theorem} % ocots-lint: ignore P2 — la proposition en découle

\begin{proposition}
  Énoncé.
\end{proposition}

\begin{lemma}
  Énoncé.
\end{lemma}

\begin{definition}
  Énoncé.
\end{definition}
"""


def lancer(tmp_path, capsys, *argv):
    f = tmp_path / "a.tex"
    f.write_text(textwrap.dedent(TEXTE).lstrip("\n"), encoding="utf-8")
    code = verifier.main([*argv, "P2", str(f)])
    return code, capsys.readouterr()


def test_json(tmp_path, capsys):
    code, sortie = lancer(tmp_path, capsys, "--format", "json")
    assert code == 1
    doc = json.loads(sortie.out)
    assert doc["outil"] == "ocots-lint"
    assert doc["regles"]["P2"]["garantie"] == "heuristique"
    assert [(t["ligne"], t["exemption"]) for t in doc["trouvailles"]] == [
        (3, "la proposition en découle"), (7, None), (11, None)]


def test_sarif(tmp_path, capsys):
    code, sortie = lancer(tmp_path, capsys, "--format=sarif")
    assert code == 1
    doc = json.loads(sortie.out)
    assert doc["version"] == "2.1.0"
    run = doc["runs"][0]
    assert [r["id"] for r in run["tool"]["driver"]["rules"]] == ["P2"]
    exemptee, _, retenue = run["results"]
    assert exemptee["suppressions"] == [
        {"kind": "inSource", "justification": "la proposition en découle"}]
    assert "suppressions" not in retenue
    assert retenue["level"] == "error"
    lieu = retenue["locations"][0]["physicalLocation"]
    assert lieu["region"] == {"startLine": 11}
    assert lieu["artifactLocation"]["uri"].endswith("a.tex")


def test_signal_est_un_avertissement(tmp_path, capsys):
    f = tmp_path / "b.tex"
    f.write_text("Nous avons le théorème suivant.\n\\begin{theorem}\n"
                 "\\end{theorem}\n", encoding="utf-8")
    verifier.main(["--format", "sarif", "P3", str(f)])
    doc = json.loads(capsys.readouterr().out)
    assert doc["runs"][0]["results"][0]["level"] == "warning"


def test_le_texte_reste_le_defaut(tmp_path, capsys):
    _, sortie = lancer(tmp_path, capsys)
    assert sortie.out.endswith(": [P2] lemma -> definition\n")


def test_format_inconnu(capsys):
    assert verifier.main(["--format", "xml"]) == 2
    assert "format inconnu : xml" in capsys.readouterr().err


def test_format_sans_valeur(capsys):
    assert verifier.main(["--format"]) == 2
    assert "--format attend une valeur" in capsys.readouterr().err


def test_github(tmp_path, capsys):
    code, sortie = lancer(tmp_path, capsys, "--format", "github")
    assert code == 1
    lignes = sortie.out.splitlines()
    assert len(lignes) == 2          # la trouvaille exemptée est omise
    assert lignes[0].startswith("::error file=")
    assert lignes[0].endswith(
        ",line=7,title=P2 (heuristique)::proposition -> lemma")


def test_github_echappe():
    from ocots_lint.sorties import _echapper
    assert _echapper("a%b\nc") == "a%25b%0Ac"
    assert _echapper("x:y,z", propriete=True) == "x%3Ay%2Cz"
