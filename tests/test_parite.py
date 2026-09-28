"""Parité avec `ocots-conventions/bin/verifier` (sprint S1).

Les deux outils doivent produire la même sortie standard, la même sortie
d'erreur et le même code de sortie. Comparé sur les fixtures, et sur un
corpus réel si la variable `OCOTS_LINT_CORPUS` le désigne :

    OCOTS_LINT_CORPUS=~/cours/mesure-integration-enseignants \
        uv run pytest tests/test_parite.py
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from outils import FIXTURES

RACINE = Path(__file__).parent.parent
ANCIEN = RACINE / "conventions" / "bin" / "verifier"

pytestmark = pytest.mark.skipif(
    not ANCIEN.exists(),
    reason="sous-module conventions absent (git submodule update --init)")

ARGUMENTS = (
    [],
    ["P2"], ["P3"], ["P5"], ["C4"], ["C6"],
    ["P2", "C4"],
    ["--mesure"],
    ["--list"],
    ["X"],
)


def executer(commande, cwd):
    r = subprocess.run(commande, cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def comparer(cwd, arguments):
    ancien = executer([sys.executable, str(ANCIEN), *arguments], cwd)
    nouveau = executer([sys.executable, "-m", "ocots_lint", "verifier", *arguments],
                       cwd)
    assert nouveau == ancien


@pytest.mark.parametrize("arguments", ARGUMENTS, ids=lambda a: " ".join(a) or "(rien)")
def test_parite_sur_les_fixtures(arguments):
    comparer(FIXTURES, arguments)


CORPUS = os.environ.get("OCOTS_LINT_CORPUS")


@pytest.mark.skipif(not CORPUS, reason="OCOTS_LINT_CORPUS non défini")
@pytest.mark.parametrize("arguments", ARGUMENTS, ids=lambda a: " ".join(a) or "(rien)")
def test_parite_sur_le_corpus(arguments):
    comparer(Path(CORPUS).expanduser(), arguments)
