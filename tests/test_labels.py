"""Labels et renvois lus dans la source (S6.1, décision 0006)."""

import json

import pytest

from ocots_lint import labels, vocabulaire

ANCIENNE = {
    "theorem": {"forme": "{titre}{clé}", "prefixe": "thm:", "sans_doublon": True},
    "mytheorem": {"forme": "{titre}{clé}", "prefixe": "thm:", "sans_doublon": True},
    "myexercisecb": {"forme": "<clé>", "prefixe": "ex:", "sans_doublon": False},
}


@pytest.fixture
def cours(tmp_path, monkeypatch):
    """Un cours dont le template publie `ancienne_syntaxe`."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(vocabulaire, "_averti", set())
    vocabulaire._lire.cache_clear()
    doc = json.loads(vocabulaire.EMBARQUE.read_text(encoding="utf-8"))
    for nom, syntaxe in ANCIENNE.items():
        doc["environnements"][nom]["ancienne_syntaxe"] = syntaxe
    (tmp_path / "template").mkdir()
    (tmp_path / "template" / "vocabulaire.json").write_text(json.dumps(doc))
    return tmp_path


def lire(cours, texte, nom="a.tex"):
    (cours / nom).write_text(texte, encoding="utf-8")
    return labels.lire(nom, vocabulaire.charger())


def cles(liste):
    return [(x.cle, x.ligne, getattr(x, "objet", None) or getattr(x, "commande", None))
            for x in liste]


def test_label_de_boite_par_option(cours):
    lus, _ = lire(cours,
                  "\\begin{theorem}[title=T, label={thm:a}]\nx\n\\end{theorem}\n")
    assert cles(lus) == [("thm:a", 1, "theorem")]


def test_objet_du_label(cours):
    lus, _ = lire(cours, (
        "\\section{S}\\label{sec:s}\n"
        "\\begin{figure}\\caption{c}\\label{fig:f}\\end{figure}\n"
        "\\begin{equation}\\label{eq:e} x \\end{equation}\n"
        "\\[ y \\label{eq:d} \\]\n"
        "\\begin{proof}\\label{prf:p}\\end{proof}\n"))
    assert cles(lus) == [("sec:s", 1, "section"), ("fig:f", 2, "figure"),
                         ("eq:e", 3, "equation"), ("eq:d", 4, "equation"),
                         ("prf:p", 5, "proof")]


@pytest.mark.parametrize("source, attendu", [
    ("\\begin{theorem}{Titre $\\{x\\}$}{cauchy}\nx\n\\end{theorem}", "thm:cauchy"),
    ("\\begin{theorem}{Titre}{thm:cauchy}\nx\n\\end{theorem}", "thm:cauchy"),
    ("\\begin{mytheorem}{Titre}{cauchy}\nx\n\\end{mytheorem}", "thm:cauchy"),
    ("\\begin{myexercisecb}<un>\nx\n\\end{myexercisecb}", "ex:un"),
    ("\\begin{myexercisecb}<ex:un>\nx\n\\end{myexercisecb}", "ex:ex:un"),
], ids=["prefixe", "deja_prefixe", "alias", "chevrons", "chevrons_sans_doublon"])
def test_ancienne_syntaxe(cours, source, attendu):
    lus, _ = lire(cours, source)
    assert [x.cle for x in lus] == [attendu]


def test_ancienne_syntaxe_ignoree_sans_le_vocabulaire(tmp_path, monkeypatch):
    """Sans `ancienne_syntaxe` dans le vocabulaire (template v1.2.0 à
    v1.4.0), aucun label deviné."""
    monkeypatch.chdir(tmp_path)
    vocabulaire._lire.cache_clear()
    doc = json.loads(vocabulaire.EMBARQUE.read_text(encoding="utf-8"))
    for e in doc["environnements"].values():
        e.pop("ancienne_syntaxe", None)
    (tmp_path / "template").mkdir()
    (tmp_path / "template" / "vocabulaire.json").write_text(json.dumps(doc))
    (tmp_path / "a.tex").write_text("\\begin{theorem}{T}{cauchy}\nx\n\\end{theorem}\n")
    assert labels.lire("a.tex", vocabulaire.charger())[0] == []


def test_renvois(cours):
    _, cites = lire(cours, (
        "voir \\ref{thm:a}, \\eqref{eq:1}, \\cref{thm:a, sec:b}\n"
        "et \\Cref*{fig:x}, \\hyperref[thm:a]{là}, \\autoref{lem:c}.\n"))
    assert cles(cites) == [("thm:a", 1, "ref"), ("eq:1", 1, "eqref"),
                           ("thm:a", 1, "cref"), ("sec:b", 1, "cref"),
                           ("fig:x", 2, "Cref"), ("thm:a", 2, "hyperref"),
                           ("lem:c", 2, "autoref")]


def test_rien_dans_un_commentaire_ni_un_verbatim(cours):
    lus, cites = lire(cours, (
        "% \\label{sec:mort} \\ref{thm:mort}\n"
        "\\begin{verbatim}\\label{v} \\ref{w}\\end{verbatim}\n"
        "\\verb|\\ref{x}|\n"
        "\\begin{enumerate}[label=\\alph*)]\\item a\\end{enumerate}\n"))
    assert (lus, cites) == ([], [])


def test_repli_pour_un_fichier_refuse(cours):
    lus, cites = lire(cours, "}\n\\label{sec:a} % \\label{sec:b}\n\\ref{sec:a}\n")
    assert cles(lus) == [("sec:a", 2, None)]
    assert cles(cites) == [("sec:a", 3, "ref")]


def test_index_du_cours_couvre_tous_les_fichiers(cours):
    (cours / "poly").mkdir()
    (cours / "td").mkdir()
    (cours / "poly" / "a.tex").write_text("\\section{A}\\label{sec:a}\n")
    (cours / "td" / "b.tex").write_text("voir \\ref{sec:a}\n")
    lus, cites = labels.index_du_cours(vocabulaire.charger())
    assert [(x.cle, x.fichier) for x in lus] == [("sec:a", "poly/a.tex")]
    assert [(x.cle, x.fichier) for x in cites] == [("sec:a", "td/b.tex")]
