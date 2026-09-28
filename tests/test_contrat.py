"""Contrat avec les consommateurs de `verifier` (S3.3).

- **JSON** : validé contre le schéma publié, et comparé à une sortie de
  référence. Changer la sortie JSON, c'est changer le contrat : on régénère
  la référence en connaissance de cause (voir plus bas), et un changement
  incompatible fait monter `SCHEMA_JSON`.
- **Texte et codes de sortie** : `ocourses/agents/scripts/checkers/
  conventions.sh` lit la sortie texte avec une regex et se fie aux codes 0,
  1 et 2. Figés tant que ce détecteur existe.

Régénérer les références : OCOTS_LINT_REGENERER=1 uv run pytest tests/test_contrat.py
"""

import json
import os
import re
import subprocess
import sys
from importlib import resources
from pathlib import Path

import jsonschema
import pytest

from ocots_lint.sorties import SCHEMA_JSON

CONTRAT = Path(__file__).parent / "contrat"
REGENERER = os.environ.get("OCOTS_LINT_REGENERER") == "1"

# La regex exacte de conventions.sh (ocourses/agents).
RE_DETECTEUR = re.compile(r"^([^:]+):([0-9]+):\ \[([A-Za-z0-9]+)\]\ (.*)$")


def lancer(*argv, cwd=CONTRAT):
    r = subprocess.run([sys.executable, "-m", "ocots_lint", "verifier", *argv],
                       cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def schema():
    nom = f"verifier-{SCHEMA_JSON}.schema.json"
    fichier = resources.files("ocots_lint") / "schemas" / nom
    return json.loads(fichier.read_text(encoding="utf-8"))


def comparer_a_la_reference(nom, contenu):
    reference = CONTRAT / nom
    if REGENERER:
        reference.write_text(contenu, encoding="utf-8")
    assert contenu == reference.read_text(encoding="utf-8"), (
        f"sortie différente de {reference.name} — changement de contrat ? "
        "Régénérer avec OCOTS_LINT_REGENERER=1 si c'est voulu.")


# ------------------------------------------------------------------- JSON

def test_json_valide_contre_le_schema_publie():
    _, out, _ = lancer("--format", "json", "cours.tex")
    jsonschema.validate(json.loads(out), schema())


def test_json_valide_aussi_sur_les_fixtures():
    _, out, _ = lancer("--format", "json", ".", cwd=CONTRAT.parent / "fixtures")
    doc = json.loads(out)
    jsonschema.validate(doc, schema())
    assert len(doc["trouvailles"]) > 20


def test_json_reference():
    code, out, _ = lancer("--format", "json", "cours.tex")
    doc = json.loads(out)
    assert doc["version"]
    doc["version"] = "<version>"
    comparer_a_la_reference("cours.json",
                            json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
    assert code == 1


def test_json_porte_exemptions_et_avertissements():
    _, out, _ = lancer("--format", "json", "cours.tex")
    doc = json.loads(out)
    assert any(t["exemption"] for t in doc["trouvailles"])
    messages = [a["message"] for a in doc["avertissements"]]
    assert any("inutile" in m for m in messages)
    assert any("sans règle ou sans raison" in m for m in messages)


def test_schema_publie_avec_le_paquet():
    assert schema()["properties"]["schema"]["const"] == SCHEMA_JSON


# ---------------------------------------------------- texte, codes de sortie

def test_texte_reference():
    code, out, err = lancer("cours.tex")
    comparer_a_la_reference("cours.txt",
                            f"code : {code}\n--- stdout\n{out}--- stderr\n{err}")


def test_chaque_ligne_lisible_par_le_detecteur():
    _, out, _ = lancer(".", cwd=CONTRAT.parent / "fixtures")
    lignes = out.splitlines()
    assert lignes
    for ligne in lignes:
        assert RE_DETECTEUR.match(ligne), ligne


@pytest.mark.parametrize("argv,code", [
    (["P2", "fixtures/P2/accepte/texte_entre.tex"], 0),
    (["P2", "fixtures/P2/signale/ligne_blanche.tex"], 1),
    (["P2", "n-existe-pas.tex"], 2),
    (["--format", "xml"], 2),
])
def test_codes_de_sortie(argv, code):
    assert lancer(*argv, cwd=CONTRAT.parent)[0] == code
