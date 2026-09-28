"""`ocots-lint exempter` (S3.4) : n'ajouter qu'une directive, et le prouver."""

import json
import subprocess
import textwrap

import pytest

from ocots_lint import exempter, verifier
from ocots_lint.exemptions import lire_directives

SOURCE = r"""
\begin{theorem}
  Énoncé.
  ``ici'' \end{theorem}

\begin{proposition}
  Énoncé.
\end{proposition}
"""


@pytest.fixture
def depot(tmp_path, monkeypatch):
    """Un dépôt git avec a.tex commité ; on travaille depuis sa racine."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "a.tex").write_text(textwrap.dedent(SOURCE).lstrip("\n"),
                                    encoding="utf-8")
    for commande in (["git", "init", "-q"], ["git", "add", "a.tex"],
                     ["git", "-c", "user.email=x@y", "-c", "user.name=x",
                      "commit", "-qm", "init"]):
        subprocess.run(commande, check=True)
    return tmp_path


def diff():
    return subprocess.run(["git", "diff"], capture_output=True, text=True).stdout


def actives(capsys, regle):
    capsys.readouterr()          # vide ce qu'exempter a pu afficher avant
    verifier.main(["--format", "json", regle, "a.tex"])
    doc = json.loads(capsys.readouterr().out)
    return [t for t in doc["trouvailles"] if not t["exemption"]]


def test_une_seule_ligne_ajoutee_a_la_bonne_indentation(depot, capsys):
    assert exempter.main(["a.tex:3", "P2", "la proposition en découle"]) == 0
    lignes = (depot / "a.tex").read_text(encoding="utf-8").split("\n")
    assert lignes[2] == "  % ocots-lint: ignore P2 — la proposition en découle"
    ajouts = [l for l in diff().split("\n")
              if l.startswith("+") and not l.startswith("+++")]
    assert ajouts == ["+  % ocots-lint: ignore P2 — la proposition en découle"]
    assert actives(capsys, "P2") == []


def test_par_empreinte(depot, capsys):
    empreinte = actives(capsys, "P2")[0]["empreinte"]
    assert exempter.main([f"a.tex@{empreinte}", "P2", "voulu"]) == 0
    assert actives(capsys, "P2") == []


def test_empiler_deux_exemptions(depot, capsys):
    assert exempter.main(["a.tex:3", "P2", "voulu"]) == 0
    assert exempter.main(["a.tex:4", "C4", "citation d'une source anglaise"]) == 0
    assert actives(capsys, "P2") == [] and actives(capsys, "C4") == []
    assert exempter.controler(diff()) == []


def test_plusieurs_regles_d_un_coup(depot, capsys):
    assert exempter.main(["a.tex:3", "P2,C4", "voulu"]) == 0
    assert actives(capsys, "P2") == [] and actives(capsys, "C4") == []


@pytest.mark.parametrize("argv,message", [
    (["a.tex:2", "P2", "voulu"], "aucune trouvaille P2 active en a.tex:2"),
    (["a.tex:3", "P9", "voulu"], "règle sans vérificateur : P9"),
    (["a.tex:3", "P2", "   "], "la raison est obligatoire"),
    (["b.tex:3", "P2", "voulu"], "fichier introuvable : b.tex"),
    (["a.tex", "P2", "voulu"], "cible illisible"),
    (["a.tex@0123456789abcdef:0", "P2", "voulu"], "aucune trouvaille P2 active"),
])
def test_refus(depot, capsys, argv, message):
    avant = (depot / "a.tex").read_text(encoding="utf-8")
    assert exempter.main(argv) == 2
    assert message in capsys.readouterr().err
    assert (depot / "a.tex").read_text(encoding="utf-8") == avant


def test_deja_exemptee_est_refusee(depot, capsys):
    assert exempter.main(["a.tex:3", "P2", "voulu"]) == 0
    assert exempter.main(["a.tex:4", "P2", "encore"]) == 2


def test_refus_dans_un_verbatim(depot, capsys):
    (depot / "a.tex").write_text(
        "\\begin{verbatim}\n\\end{theorem}\n\n\\begin{lemma}\n\\end{verbatim}\n",
        encoding="utf-8")
    assert exempter.main(["a.tex:2", "P2", "voulu"]) == 2
    assert "verbatim" in capsys.readouterr().err


# ------------------------------------------------------------ --controler

def test_controler_refuse_toute_autre_modification(depot):
    f = depot / "a.tex"
    f.write_text(f.read_text(encoding="utf-8").replace("Énoncé.", "Autre."),
                 encoding="utf-8")
    problemes = exempter.controler(diff())
    assert any("ligne retirée" in m for _, m in problemes)
    assert any("pas une directive" in m for _, m in problemes)


def test_controler_refuse_une_directive_sans_raison(depot):
    f = depot / "a.tex"
    f.write_text("% ocots-lint: ignore P2\n" + f.read_text(encoding="utf-8"),
                 encoding="utf-8")
    assert "sans règle ou sans raison" in exempter.controler(diff())[0][1]


def test_controler_refuse_une_directive_en_fin_de_ligne(depot):
    """En fin de ligne, la directive modifierait une ligne existante."""
    f = depot / "a.tex"
    f.write_text(f.read_text(encoding="utf-8").replace(
        "\\end{proposition}", "\\end{proposition} % ocots-lint: ignore P2 — x"),
        encoding="utf-8")
    assert exempter.controler(diff())


def test_controler_refuse_un_nouveau_fichier_ou_un_autre_format():
    nouveau = ("diff --git a/b.tex b/b.tex\nnew file mode 100644\n--- /dev/null\n"
               "+++ b/b.tex\n@@ -0,0 +1 @@\n+% ocots-lint: ignore P2 — x\n")
    assert any("changement de fichier" in m for _, m in exempter.controler(nouveau))
    autre = ("diff --git a/x.md b/x.md\n--- a/x.md\n+++ b/x.md\n@@ -1 +1,2 @@\n"
             " a\n+% ocots-lint: ignore P2 — x\n")
    assert exempter.controler(autre) == [("x.md", "fichier autre qu'un .tex")]


def test_controler_diff_vide():
    assert exempter.controler("") == []


def test_controler_cli(depot, capsys, monkeypatch):
    exempter.main(["a.tex:3", "P2", "voulu"])
    (depot / "d.diff").write_text(diff(), encoding="utf-8")
    assert exempter.main(["--controler", "d.diff"]) == 0


# ----------------------------------------------- empilement des directives

def test_directive_seule_saute_les_commentaires_seuls():
    valides, _ = lire_directives(
        "% ocots-lint: ignore P2 — a\n% ocots-lint: ignore C4 — b\n% note\nx\n")
    assert [d.couverte for d in valides] == [4, 4]
