"""Instantanés du corpus (S4.0) : figer, puis vérifier que rien n'a bougé."""

import json
import os
import subprocess

import pytest

from ocots_lint import instantane

CHAINE = "\\begin{theorem}\nx\n\\end{theorem}\n\n\\begin{lemma}\ny\n\\end{lemma}\n"


def git(depot, *args):
    return subprocess.run(["git", "-C", str(depot), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


@pytest.fixture
def depot(tmp_path, monkeypatch):
    for variable in ("GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME"):
        monkeypatch.setenv(variable, "essai")
    for variable in ("GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL"):
        monkeypatch.setenv(variable, "essai@exemple.org")
    d = tmp_path / "cours"
    (d / "poly").mkdir(parents=True)
    (d / "poly" / "a.tex").write_text("Texte.\n\n" + CHAINE, encoding="utf-8")
    git(d, "init", "-q")
    git(d, "add", "-A")
    git(d, "commit", "-qm", "init")
    monkeypatch.chdir(tmp_path)     # l'outil tourne hors du dépôt du cours
    return d


def lire(chemin):
    return json.loads(chemin.read_text(encoding="utf-8"))


def ecrire(chemin, doc):
    chemin.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")


def test_figer_enregistre_commit_et_trouvailles(depot):
    chemin, doc = instantane.figer("essai", str(depot))
    assert chemin == instantane.Path("corpus/essai.json")
    fige = lire(chemin)
    assert fige["corpus"]["commit"] == git(depot, "rev-parse", "HEAD")
    assert fige["corpus"]["depot"] == str(depot)
    assert [(t["regle"], t["fichier"], t["ligne"]) for t in fige["trouvailles"]] == [
        ("P2", "poly/a.tex", 5)]


def test_figer_ne_lit_pas_la_copie_de_travail(depot):
    (depot / "poly" / "a.tex").write_text("Un sous espace.\n", encoding="utf-8")
    _, doc = instantane.figer("essai", str(depot))
    assert [t["regle"] for t in doc["trouvailles"]] == ["P2"]
    assert os.getcwd() == str(depot.parent)


def test_figer_a_une_revision_anterieure(depot):
    premier = git(depot, "rev-parse", "HEAD")
    (depot / "poly" / "a.tex").write_text("Rien.\n", encoding="utf-8")
    git(depot, "commit", "-qam", "corrige")
    _, doc = instantane.figer("essai", str(depot), premier)
    assert doc["corpus"]["commit"] == premier
    assert len(doc["trouvailles"]) == 1


def test_verifier_rien_n_a_bouge(depot, capsys):
    instantane.figer("essai", str(depot))
    assert instantane.main(["verifier"]) == 0
    assert "essai (" in capsys.readouterr().out


def test_verifier_voit_une_trouvaille_modifiee(depot, capsys):
    chemin, _ = instantane.figer("essai", str(depot))
    doc = lire(chemin)
    doc["trouvailles"][0]["message"] = "ancien message"
    ecrire(chemin, doc)
    code, [(_, _, e)] = instantane.verifier()
    assert code == 1
    assert (e["apparues"], e["disparues"], e["inchangees"]) == ([], [], 0)
    (m,) = e["modifiees"]
    assert (m["avant"]["message"], m["apres"]["message"]) == (
        "ancien message", "theorem -> lemma")
    instantane.main(["verifier"])
    assert "('ancien message', None) → ('theorem -> lemma', None)" in (
        capsys.readouterr().out)


def test_verifier_voit_une_trouvaille_apparue(depot):
    chemin, _ = instantane.figer("essai", str(depot))
    doc = lire(chemin)
    doc["trouvailles"] = []
    ecrire(chemin, doc)
    code, [(_, _, e)] = instantane.verifier()
    assert code == 1
    assert [t["regle"] for t in e["apparues"]] == ["P2"]


def test_une_empreinte_changee_compte_apparue_et_disparue(depot):
    """Critère de S4 : une trouvaille inchangée garde son empreinte."""
    chemin, _ = instantane.figer("essai", str(depot))
    doc = lire(chemin)
    doc["trouvailles"][0]["empreinte"] = "0000000000000000:0"
    ecrire(chemin, doc)
    _, [(_, _, e)] = instantane.verifier()
    assert (len(e["apparues"]), len(e["disparues"])) == (1, 1)


def test_dossier_vide(tmp_path, capsys):
    assert instantane.main(["verifier", "--dossier", str(tmp_path / "rien")]) == 2
    assert "aucun instantané" in capsys.readouterr().err


def test_depot_introuvable(tmp_path, capsys):
    assert instantane.main(["figer", "x", str(tmp_path)]) == 2


@pytest.mark.parametrize("argv", [[], ["figer"], ["verifier", "trop"],
                                  ["verifier", "--dossier"]])
def test_usage(argv, capsys):
    assert instantane.main(argv) == 2
    assert "usage" in capsys.readouterr().err


EXEMPTEE = ("Texte.\n\n\\begin{theorem}\nx\n"
            "% ocots-lint: ignore P2 — série voulue\n"
            "\\end{theorem}\n\n\\begin{lemma}\ny\n\\end{lemma}\n")


def test_trouvaille_exemptee_comparee_aussi(depot):
    (depot / "poly" / "a.tex").write_text(EXEMPTEE, encoding="utf-8")
    git(depot, "commit", "-qam", "exempte")
    chemin, doc = instantane.figer("essai", str(depot))
    assert doc["trouvailles"][0]["exemption"] == "série voulue"
    code, [(_, _, e)] = instantane.verifier()
    assert (code, e["inchangees"]) == (0, 1)
    doc = lire(chemin)
    doc["trouvailles"][0]["exemption"] = None
    ecrire(chemin, doc)
    code, [(_, _, e)] = instantane.verifier()
    assert (code, len(e["modifiees"])) == (1, 1)


def test_avertissement_apparu(depot):
    chemin, _ = instantane.figer("essai", str(depot))
    doc = lire(chemin)
    doc["avertissements"] = [{"fichier": "poly/a.tex", "ligne": 1,
                              "message": "ancien"}]
    ecrire(chemin, doc)
    code, [(_, _, e)] = instantane.verifier()
    assert code == 1
    assert e["avertissements"]["disparus"] == [("poly/a.tex", 1, "ancien")]
