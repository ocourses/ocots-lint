"""C5 : les renvois se lisent dans tout le cours, les labels signalés se
limitent au périmètre vérifié."""

from ocots_lint.regles.c5 import regle_C5


def test_perimetre(tmp_path, monkeypatch):
    (tmp_path / "poly").mkdir()
    (tmp_path / "td").mkdir()
    (tmp_path / "poly" / "ch1.tex").write_text(
        "\\begin{theorem}[label=thm:cite]\nA.\n\\end{theorem}\n"
        "\\begin{theorem}[label=thm:orphelin]\nB.\n\\end{theorem}\n",
        encoding="utf-8")
    (tmp_path / "td" / "td1.tex").write_text(
        "Par le Théorème~\\ref{thm:cite}.\n\\section{TD}\\label{sec:td}\n",
        encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    assert [(f, l) for f, l, _ in regle_C5(["poly"])] == [("poly/ch1.tex", 4)]
    assert [(f, l) for f, l, _ in regle_C5(["td/td1.tex"])] == [("td/td1.tex", 2)]
    assert len(list(regle_C5(["."]))) == 2
