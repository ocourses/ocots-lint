"""Parité avec `ocots-conventions/bin/verifier` (sprint S1), sur les fixtures.

Les deux outils doivent produire la même sortie standard, la même sortie
d'erreur et le même code de sortie.

Depuis S4, seulement pour les règles encore lues par les masques : une règle
qui passe sur l'arbre syntaxique (`SUR_ARBRE`) s'écarte volontairement de
l'ancien outil. Une règle encore sur les masques peut aussi s'écarter de
l'ancien outil pour un défaut corrigé : chaque fixture en écart est déclarée
dans `ECARTS_VOULUS`, avec sa raison, et un test vérifie que l'écart existe
bien.

Sur un cours réel, la référence n'est plus l'ancien outil mais le corpus
figé (S4.7) : `python -m ocots_lint.instantane verifier` (tests/README.md).
"""

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

# Fixtures où l'outil s'écarte volontairement de l'ancien : défaut corrigé.
ECARTS_VOULUS = {
    "C6/accepte/qedhere_avant_un_saut_espace.tex":
        "S4.6 : `\\\\[1em]` n'est pas l'ouverture de la formule",
    "P5/signale/remarques_etoilees.tex":
        "S5.2 : `remark*` est une remarque (famille du vocabulaire du template)",
}

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
def test_parite_sur_les_fixtures(tmp_path, arguments):
    copie = tmp_path / "fixtures"
    shutil.copytree(FIXTURES, copie)
    for fixture in ECARTS_VOULUS:
        (copie / fixture).unlink()
    comparer(copie, arguments)


@pytest.mark.parametrize("fixture", sorted(ECARTS_VOULUS))
def test_ecart_voulu_bien_reel(fixture):
    regle = fixture.split("/")[0]
    ancien = executer([sys.executable, str(ANCIEN), regle, fixture], FIXTURES)
    nouveau = executer([sys.executable, "-m", "ocots_lint", "verifier", regle,
                        fixture], FIXTURES)
    assert nouveau != ancien



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

