"""`ocots-lint extraire` : l'inventaire des boîtes du polycopié (S7.1)."""

import json

import pytest

from ocots_lint import extraire

MAIN = """\
\\documentclass{ocots-book}
\\begin{document}
{\\pagestyle{empty}
\\chapter*{Avant-propos}
Un avant-propos dans un groupe.
}
\\chapter{Suites}
\\minitoc

\\begin{chapterintro}
  Ce chapitre étudie les suites.
\\end{chapterintro}
\\input{chapitres/suites}
\\begin{appendix}
\\chapter{Annexe}
\\end{appendix}
\\end{document}
"""

SUITES = """\
\\def\\subsectionname{Convergence}
\\subsection{\\subsectionname}

Une suite bornée n'est pas forcément convergente.
% un commentaire seul ne coupe pas le paragraphe
Mais elle a une sous-suite qui l'est : c'est le résultat central.

\\begin{theorem}[title={Bolzano-Weierstrass}, label=thm:bw]
  Toute suite réelle bornée a une sous-suite convergente.
\\end{theorem}%
\\footnotetext{Une note de l'énoncé.}%
\\begin{proof}
  Par dichotomie.
\\end{proof}

On en tire la compacité des segments.

\\begin{remark}
  Une remarque, avec un exemple dedans :
  \\begin{example}
    $u_n = (-1)^n$.
  \\end{example}
\\end{remark}
\\begin{itemize}
  \\item une liste fait partie du texte ;
\\end{itemize}
Voici l'exercice.

\\begin{exercise}
  Montrer que $(-1)^n$ a deux valeurs d'adhérence.
\\end{exercise}

\\section{Suite}
Le cadre de la section.

\\begin{assumption}[label=hyp:h]
  $u$ est bornée.
\\end{assumption}
"""

TD = "Par le Théorème~\\ref{thm:bw}.\n"


@pytest.fixture
def cours(tmp_path, monkeypatch):
    (tmp_path / "poly" / "chapitres").mkdir(parents=True)
    (tmp_path / "td").mkdir()
    (tmp_path / "poly" / "main.tex").write_text(MAIN, encoding="utf-8")
    chapitre = tmp_path / "poly" / "chapitres" / "suites.tex"
    chapitre.write_text(SUITES, encoding="utf-8")
    (tmp_path / "td" / "td1.tex").write_text(TD, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def boites(racines=("poly",)):
    return {b["environnement"]: b for b in extraire.extraire(list(racines))["boites"]}


def test_toutes_les_boites_imbriquees_comprises(cours):
    assert [b["environnement"] for b in
            extraire.extraire(["poly"])["boites"]] == [
        "theorem", "remark", "example", "exercise", "assumption"]


def test_section_suit_l_inclusion_et_les_macros_de_titre(cours):
    assert boites()["theorem"]["section"] == {
        "chapter": "Suites", "subsection": "Convergence"}


def test_amorce_paragraphe_entier(cours):
    assert boites()["theorem"]["amorce"] == (
        "Une suite bornée n'est pas forcément convergente. Mais elle a une "
        "sous-suite qui l'est : c'est le résultat central.")
    assert boites()["theorem"]["precede_par"] == "subsection"


def test_preuve_par_dessus_une_note_et_reprise(cours):
    t = boites()["theorem"]
    assert t["preuve"] == {"environnement": "proof", "ligne": 12, "fin": 14}
    assert t["reprise"] == "On en tire la compacité des segments."
    assert t["suivi_par"] == "remark"


def test_citations_de_tout_le_cours(cours):
    t = boites()["theorem"]
    assert t["label"] == "thm:bw"
    assert t["citations"] == {"total": 1, "fichiers": ["td/td1.tex"],
                              "ailleurs": True}


def test_une_liste_fait_partie_du_texte(cours):
    e = boites()["exercise"]
    assert e["precede_par"] == "remark"
    assert e["amorce"] == ("\\begin{itemize} \\item une liste fait partie du "
                           "texte ; \\end{itemize} Voici l'exercice.")
    assert e["reprise"] == "" and e["suivi_par"] == "section"
    assert boites()["remark"]["preuve"] is None


def test_empreinte_stable_quand_on_insere_au_dessus(cours):
    avant = boites()["exercise"]
    f = cours / "poly" / "chapitres" / "suites.tex"
    f.write_text("% en tête\n\n" + f.read_text(encoding="utf-8"), encoding="utf-8")
    apres = boites()["exercise"]
    assert apres["empreinte"] == avant["empreinte"]
    assert apres["ligne"] == avant["ligne"] + 2


def test_fichier_refuse_signale(cours):
    (cours / "poly" / "casse.tex").write_text(
        "\\begin{theorem}\nx}\n\\end{theorem}\n", encoding="utf-8")
    doc = extraire.extraire(["poly"])
    assert [a["fichier"] for a in doc["avertissements"]] == ["poly/casse.tex"]
    assert "1 boîte(s) non extraite(s)" in doc["avertissements"][0]["message"]


def test_aucun_verdict(cours):
    """L'extraction décrit : aucun champ ne juge."""
    for b in extraire.extraire(["poly"])["boites"]:
        assert not {"verdict", "infraction", "regle"} & set(b)


def test_main(cours, capsys):
    assert extraire.main([]) == 0
    sortie = capsys.readouterr()
    doc = json.loads(sortie.out)
    assert doc["schema"] == 1 and doc["racines"] == ["poly"]
    assert "5 boîte(s), 5 section(s) extraite(s)" in sortie.err
    assert extraire.main(["n-existe-pas/"]) == 2
    assert extraire.main(["--inconnu"]) == 2


@pytest.mark.parametrize("texte,attendu", [
    ("a\n\nb\n\nc", ["a", "b", "c"]),
    ("a\n% note\nb", ["a b"]),
    ("a \\label{x} b \\index{y} c", ["a b c"]),
    ("\\def\\t{T}\nx", ["x"]),
])
def test_paragraphes(texte, attendu):
    assert extraire.paragraphes(texte) == attendu


# ------------------------------------------------------------ carte (S7.2)

def sections():
    return {s["titre"]: s for s in extraire.extraire(["poly"])["sections"]}


def test_carte_dans_l_ordre_de_lecture(cours):
    assert [(s["niveau"], s["titre"]) for s in
            extraire.extraire(["poly"])["sections"]] == [
        ("chapter", "Avant-propos"), ("chapter", "Suites"),
        ("subsection", "Convergence"), ("section", "Suite"),
        ("chapter", "Annexe")]


def test_ouverture_de_chapitre(cours):
    o = sections()["Suites"]["ouverture"]
    assert o["minitoc"] is True and o["texte"] == []
    assert o["structure"] == [{"environnement": "chapterintro", "ligne": 10,
                               "debut": "Ce chapitre étudie les suites."}]
    assert sections()["Avant-propos"]["ouverture"]["texte"] == [
        "Un avant-propos dans un groupe."]


def test_contenu_et_fin_de_section(cours):
    s = sections()["Convergence"]
    assert [(c["type"], c.get("environnement")) for c in s["contenu"]] == [
        ("boite", "theorem"), ("preuve", "proof"), ("texte", None),
        ("boite", "remark"), ("texte", None), ("boite", "exercise")]
    assert s["termine_par"] == "exercise"
    assert s["parents"] == {"chapter": "Suites"}
    assert s["contenu"][0]["empreinte"] == boites()["theorem"]["empreinte"]


def test_hypotheses_de_la_section_et_des_parents(cours):
    hyp = boites()["assumption"]["empreinte"]
    assert sections()["Suite"]["hypotheses"] == [hyp]
    assert sections()["Suites"]["hypotheses"] == [hyp]
    assert sections()["Suite"]["ouverture"]["texte"] == ["Le cadre de la section."]


def test_titre_d_un_fichier_refuse_signale(cours):
    (cours / "poly" / "casse.tex").write_text(
        "\\section{Cassée}\nx}\n", encoding="utf-8")
    doc = extraire.extraire(["poly"])
    assert [a["message"].split(" — ")[-1] for a in doc["avertissements"]] == [
        "1 titre(s) absent(s) de la carte des sections"]
