"""`ocots-lint extraire --exercices` : l'inventaire des exercices des TD et
des examens (S8.5). La sortie complète d'un petit cours est figée par le
contrat (`tests/contrat/exercices.json`) ; ici, les cas limites."""

import json

import pytest

from ocots_lint import extraire, extraire_exercices, vocabulaire


@pytest.fixture
def cours(tmp_path, monkeypatch):
    """Un cours vide, dossier courant, vocabulaire embarqué."""
    monkeypatch.chdir(tmp_path)
    vocabulaire._lire.cache_clear()
    (tmp_path / "td" / "td1").mkdir(parents=True)
    return tmp_path


def ecrire(cours, chemin, texte):
    (cours / chemin).parent.mkdir(parents=True, exist_ok=True)
    (cours / chemin).write_text(texte, encoding="utf-8")


def un_exercice(cours, corps):
    ecrire(cours, "td/td1/contenu.tex",
           f"\\begin{{exercise}}\n{corps}\n\\end{{exercise}}\n")
    (exo,) = extraire_exercices.extraire(["td"])["exercices"]
    return exo


def test_alias_deprecies_lus_par_leur_famille(cours):
    exo = un_exercice(cours, "\\begin{myquestion}\nQ.\n\\end{myquestion}\n"
                             "\\begin{mycorr}\nC.\n\\end{mycorr}")
    (q,) = exo["questions"]
    assert (q["numero"], q["environnement"]) == ("1", "myquestion")
    assert [c["environnement"] for c in q["corrections"]] == ["mycorr"]


def test_deux_corriges_de_suite_pour_une_question(cours):
    exo = un_exercice(cours, "\\begin{question}\nQ.\n\\end{question}\n"
                             "\\begin{correction}\nA.\n\\end{correction}\n"
                             "\\begin{correction}\nB.\n\\end{correction}")
    assert [c["place"] for c in exo["questions"][0]["corrections"]] == [
        "apres", "apres"]


def test_corrige_dans_la_question_et_enumerate_d_items(cours):
    """Le corrigé d'un item d'enumerate dans une question (ancien sujet
    d'automatique) : rattaché à la question qui le contient, rien de perdu."""
    exo = un_exercice(cours, "\\begin{question}\n\\begin{enumerate}\n"
                             "\\item a\n\\begin{correction}\nA.\n\\end{correction}\n"
                             "\\item b\n\\begin{correction}\nB.\n\\end{correction}\n"
                             "\\end{enumerate}\n\\end{question}")
    assert [c["place"] for c in exo["questions"][0]["corrections"]] == [
        "dans", "dans"]


def test_lignes_d_un_corrige_sans_blancs_ni_commentaires(cours):
    exo = un_exercice(cours, "\\begin{correction}\nA.\n\n% note\nB.\n"
                             "\\end{correction}")
    assert exo["corrections"][0]["lignes"] == 2


def test_le_polycopie_et_les_transparents_ne_sont_pas_lus(cours):
    ecrire(cours, "poly/ch1.tex", "\\begin{exercise}\nx\n\\end{exercise}\n")
    ecrire(cours, "td/td4/rk.tex", "\\documentclass{beamer}\n"
           "\\begin{exercise}\nx\n\\end{exercise}\n")
    doc = extraire_exercices.extraire(["."])
    assert doc["exercices"] == [] and doc["documents"] == []


def test_fichier_refuse_signale(cours):
    ecrire(cours, "td/td1/contenu.tex", "\\begin{exercise}\nx}\n\\end{exercise}\n")
    doc = extraire_exercices.extraire(["td"])
    assert doc["exercices"] == []
    (a,) = doc["avertissements"]
    assert a["fichier"] == "td/td1/contenu.tex"
    assert "1 exercice(s) non extrait(s)" in a["message"]


def test_aucun_verdict(cours):
    exo = un_exercice(cours, "\\begin{question}\nQ.\n\\end{question}")
    assert not {"verdict", "infraction", "regle"} & set(exo)


def test_main_par_extraire(cours, capsys):
    """`extraire --exercices` : td/ et exams/ par défaut, codes de sortie."""
    ecrire(cours, "td/td1/contenu.tex",
           "\\begin{exercise}\n\\begin{question}\nQ.\n\\end{question}\n"
           "\\end{exercise}\n")
    assert extraire.main(["--exercices"]) == 0
    sortie = capsys.readouterr()
    doc = json.loads(sortie.out)
    assert doc["extraction"] == "exercices" and doc["racines"] == ["td"]
    assert "1 exercice(s), 1 question(s), 0 document(s)" in sortie.err
    assert extraire.main(["--exercices", "n-existe-pas/"]) == 2
    assert extraire.main(["--exercices", "--inconnu"]) == 2
