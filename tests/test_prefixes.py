"""La table des préfixes de C5, lue dans les conventions (S6.3)."""

import json
import os
from pathlib import Path

import pytest

from ocots_lint import prefixes

TABLE = """\
## C5 — Labels et renvois

| Objet | Préfixe | Objet | Préfixe |
|---|---|---|---|
| théorème (`theorem`) | `thm:` | section (`\\section`) | `sec:` |
| équation (`equation`, `align`) | `eq:` | | |

## C6 — Listes

| exemple (`example`) | `hors:` |
"""


def test_lire():
    assert prefixes.lire(TABLE) == {"theorem": "thm:", "section": "sec:",
                                    "equation": "eq:", "align": "eq:"}


def test_conventions_sans_noms_latex():
    """Avant la table lisible, les objets n'avaient que leur nom français."""
    ancienne = ("## C5 — Labels\n\n| théorème | `thm:` | figure | `fig:` |\n"
                "| exercice | `ex:` | hypothèse (`assumption`) | `hyp:` |\n")
    assert prefixes.lire(ancienne) == {}
    assert prefixes.lire("# rien\n") == {}


def test_charger_lit_les_conventions_du_cours(tmp_path, monkeypatch):
    (tmp_path / "conventions").mkdir()
    (tmp_path / "conventions" / "communes.md").write_text(TABLE, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    assert prefixes.charger()["section"] == "sec:"


def test_repli_sur_la_copie_embarquee(tmp_path, monkeypatch, capsys):
    (tmp_path / "conventions").mkdir()
    (tmp_path / "conventions" / "communes.md").write_text("## C5 — L\n",
                                                           encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    assert prefixes.charger() == prefixes.embarquee()
    assert "table embarquée utilisée" in capsys.readouterr().err
    prefixes.charger()
    assert capsys.readouterr().err == ""            # une seule fois


def test_sans_conventions_silencieux(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert prefixes.charger() == prefixes.embarquee()
    assert capsys.readouterr().err == ""


AMONT = os.environ.get("OCOTS_LINT_AMONT_CONVENTIONS")


@pytest.mark.skipif(not AMONT, reason="OCOTS_LINT_AMONT_CONVENTIONS non défini "
                    "(workflow amont : conventions à main)")
def test_copie_embarquee_a_jour():
    """La copie embarquée est celle des conventions : à recopier sinon
    (`donnees/prefixes.json`) avant la prochaine release."""
    texte = (Path(AMONT) / "communes.md").read_text(encoding="utf-8")
    assert prefixes.lire(texte) == json.loads(
        prefixes.EMBARQUE.read_text(encoding="utf-8"))
