"""Parité avec `ocots-conventions/bin/verifier` (sprint S1).

Les deux outils doivent produire la même sortie standard, la même sortie
d'erreur et le même code de sortie. Comparé sur les fixtures, et sur un
corpus réel si la variable `OCOTS_LINT_CORPUS` le désigne :

    OCOTS_LINT_CORPUS=~/cours/mesure-integration-enseignants \
        uv run pytest tests/test_parite.py

Depuis S4, seulement pour les règles encore lues par les masques : une règle
qui passe sur l'arbre syntaxique (`SUR_ARBRE`) s'écarte volontairement de
l'ancien outil, et sa référence devient le corpus figé
(`python -m ocots_lint.instantane`).
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from ocots_lint.regles import REGLES, SUR_ARBRE

from outils import FIXTURES

RACINE = Path(__file__).parent.parent
ANCIEN = RACINE / "conventions" / "bin" / "verifier"

pytestmark = pytest.mark.skipif(
    not ANCIEN.exists(),
    reason="sous-module conventions absent (git submodule update --init)")

MASQUES = sorted(set(REGLES) - SUR_ARBRE)

ARGUMENTS = (
    MASQUES,
    *([r] for r in MASQUES),
    MASQUES[:2],
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


# --------------------------------------------------------------- nettoyer

ANCIEN_NETTOYER = RACINE / "conventions" / "bin" / "nettoyer"

CAS_NETTOYER = ("sans-csquotes", "avec-csquotes")


@pytest.mark.parametrize("cas", CAS_NETTOYER)
@pytest.mark.parametrize("appliquer", [False, True], ids=["apercu", "appliquer"])
def test_parite_nettoyer(tmp_path, cas, appliquer):
    """Chaque outil travaille sur sa propre copie ; sorties et fichiers
    produits doivent être identiques."""
    argv = ["C4", "."] + (["--appliquer"] if appliquer else [])
    copies = {}
    for nom, commande in (
            ("ancien", [sys.executable, str(ANCIEN_NETTOYER)]),
            ("nouveau", [sys.executable, "-m", "ocots_lint", "nettoyer"])):
        copie = tmp_path / nom
        shutil.copytree(FIXTURES / "nettoyer" / cas, copie)
        copies[nom] = (executer([*commande, *argv], copie), copie)
    (sortie_a, dossier_a), (sortie_n, dossier_n) = copies["ancien"], copies["nouveau"]
    assert sortie_n == sortie_a
    for f in sorted(dossier_a.rglob("*.tex")):
        assert (dossier_n / f.relative_to(dossier_a)).read_text() == f.read_text()


@pytest.mark.skipif(not CORPUS, reason="OCOTS_LINT_CORPUS non défini")
def test_parite_nettoyer_apercu_sur_le_corpus():
    corpus = Path(CORPUS).expanduser()
    ancien = executer([sys.executable, str(ANCIEN_NETTOYER), "C4"], corpus)
    nouveau = executer([sys.executable, "-m", "ocots_lint", "nettoyer", "C4"], corpus)
    assert nouveau == ancien
