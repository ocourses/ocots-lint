"""Vocabulaire du template (S5.2, S5.3) : lecture, repli, refus."""

import ast
import json
import re
from pathlib import Path

import pytest

from ocots_lint import cli, vocabulaire

RACINE = Path(__file__).parent.parent
DU_TEMPLATE = RACINE / "tests" / "amont" / "ocots-latex-template" / "vocabulaire.json"


@pytest.fixture
def cours(tmp_path, monkeypatch):
    """Un cours vide, dossier courant ; le cache de lecture est vidé."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(vocabulaire, "_averti", set())
    vocabulaire._lire.cache_clear()
    (tmp_path / "a.tex").write_text("Texte.\n", encoding="utf-8")
    return tmp_path


def embarque():
    return json.loads(vocabulaire.EMBARQUE.read_text(encoding="utf-8"))


def poser(cours, doc):
    (cours / "template").mkdir(exist_ok=True)
    texte = doc if isinstance(doc, str) else json.dumps(doc)
    (cours / "template" / "vocabulaire.json").write_text(texte, encoding="utf-8")


# ------------------------------------------------------------ contenu

@pytest.mark.skipif(not DU_TEMPLATE.exists(),
                    reason="sous-module template absent (git submodule update --init)")
def test_copie_embarquee_egale_au_template_epingle():
    assert json.loads(DU_TEMPLATE.read_text(encoding="utf-8")) == embarque()


def test_familles_boites_et_alias(cours):
    v = vocabulaire.charger()
    assert v.famille("myremark*") == "remarque"
    assert {"theorem", "mytheorem", "openquestion", "difficulty*",
            "assumption", "exercise"} <= v.boites
    assert not {"proof", "question", "slide", "web", "myframe"} & v.boites
    assert v.noms("remarque") == {"remark", "remark*", "myremark", "myremark*"}
    assert v.symbole_de_fin == {"proof", "proofend", "prooffin", "example",
                                "example*", "myexample", "myexample*"}
    assert (v.support("beamer"), v.support("ocots-td"), v.support("article")) == (
        "slides", "td", "book")


# ------------------------------------------------------------ source et repli

def test_sans_template_copie_embarquee_en_silence(cours, capsys):
    v = vocabulaire.charger()
    assert v.source == str(vocabulaire.EMBARQUE)
    assert capsys.readouterr().err == ""


def test_template_sans_vocabulaire_averti_une_fois(cours, capsys):
    (cours / "template").mkdir()
    vocabulaire.charger()
    vocabulaire.charger()
    err = capsys.readouterr().err
    assert err.count("template/vocabulaire.json absent") == 1
    assert "vocabulaire embarqué utilisé" in err


def test_le_vocabulaire_du_cours_l_emporte(cours):
    doc = embarque()
    doc["environnements"]["nouvelle"] = {"famille": "resultat"}
    poser(cours, doc)
    v = vocabulaire.charger()
    assert v.source.endswith("template/vocabulaire.json")
    assert "nouvelle" in v.boites


def test_verifier_passe_sans_bruit_avec_le_vocabulaire_du_cours(cours, capsys):
    poser(cours, embarque())
    assert cli.main(["verifier", "a.tex"]) == 0
    assert "vocabulaire" not in capsys.readouterr().err


# ------------------------------------------------------------ refus (S5.3)

def schema_2():
    doc = embarque()
    doc["schema"] = 2
    return doc


def famille_inconnue():
    doc = embarque()
    doc["environnements"]["remark"]["famille"] = "aparte"
    return doc


def alias_vers_rien():
    doc = embarque()
    doc["environnements"]["mytheorem"]["alias_de"] = "theoreme"
    return doc


def sans_boite():
    doc = embarque()
    del doc["familles"]["remarque"]["boite"]
    return doc


@pytest.mark.parametrize("doc, attendu", [
    ("{ pas du JSON", "vocabulaire illisible"),
    ("[]", "un objet JSON est attendu"),
    (schema_2(), "schéma 2, alors que cette version d'ocots-lint lit le schéma 1"),
    (famille_inconnue(), "« remark » : famille 'aparte' inconnue"),
    (alias_vers_rien(), "« mytheorem » est l'alias de « theoreme »"),
    (sans_boite(), "famille « remarque » sans « boite »"),
], ids=["json", "objet", "schema", "famille", "alias", "boite"])
def test_vocabulaire_illisible_arrete_verifier(cours, capsys, doc, attendu):
    poser(cours, doc)
    assert cli.main(["verifier", "a.tex"]) == 2
    err = capsys.readouterr().err
    assert attendu in err
    assert err.startswith("ocots-lint : vocabulaire illisible")


# ------------------------------------------------------------ règles (S5.2)

def test_une_boite_ajoutee_au_template_du_cours_est_vue(cours, capsys):
    """Le but de S5 : un environnement ajouté au template est vu par les
    règles sans toucher à l'outil."""
    doc = embarque()
    doc["environnements"]["lemmeinedit"] = {"famille": "resultat"}
    poser(cours, doc)
    (cours / "a.tex").write_text(
        "\\begin{theorem}\nx\n\\end{theorem}\n\n"
        "\\begin{lemmeinedit}\ny\n\\end{lemmeinedit}\n", encoding="utf-8")
    assert cli.main(["verifier", "P2", "a.tex"]) == 1
    assert "[P2] theorem -> lemmeinedit" in capsys.readouterr().out


# Règles pas encore passées au vocabulaire (S5.2, étape suivante).
EN_ATTENTE = {"regles/c6.py"}

# Mots français homographes d'un environnement : « proposition » dans les
# motifs de P3 et C4 (prose française), « correction » (voie de correction,
# messages de `nettoyer`). Ce ne sont pas des noms d'environnement.
FRANCAIS = {"proposition", "correction"}


def chaines_du_code(chemin):
    """Les chaînes littérales d'un module, sans ses docstrings."""
    arbre = ast.parse(chemin.read_text(encoding="utf-8"))
    docstrings = {id(n.body[0].value) for n in ast.walk(arbre)
                  if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef))
                  and n.body and isinstance(n.body[0], ast.Expr)
                  and isinstance(n.body[0].value, ast.Constant)}
    for n in ast.walk(arbre):
        if (isinstance(n, ast.Constant) and isinstance(n.value, str)
                and id(n) not in docstrings):
            yield n.lineno, n.value


def test_aucun_nom_du_template_en_dur_dans_le_code():
    """Critère 2 de S5 : les noms d'environnements du template viennent du
    vocabulaire, jamais d'une chaîne du code."""
    # Un nom de famille (« definition ») est le contrat du schéma, pas un nom
    # d'environnement : les règles le citent à dessein.
    noms = set(embarque()["environnements"]) - FRANCAIS - set(embarque()["familles"])
    motif = re.compile(r"(?<![\w@])(" + "|".join(
        re.escape(n) for n in sorted(noms, key=len, reverse=True)) + r")(?![\w*])")
    src = RACINE / "src" / "ocots_lint"
    trouves = [f"{p.relative_to(src)}:{ligne}: {m.group(1)!r}"
               for p in sorted(src.rglob("*.py"))
               if p.relative_to(src).as_posix() not in EN_ATTENTE
               for ligne, chaine in chaines_du_code(p)
               for m in motif.finditer(chaine)]
    assert trouves == []
