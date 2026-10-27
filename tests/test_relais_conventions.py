"""Tests de scripts/relais-conventions : la montée d'ocots-lint (#27)."""

import importlib.machinery
import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/relais-conventions"
chargeur = importlib.machinery.SourceFileLoader("relais_conventions", str(SCRIPT))
spec = importlib.util.spec_from_loader("relais_conventions", chargeur)
relais = importlib.util.module_from_spec(spec)
chargeur.exec_module(relais)

BIN = """#!/bin/sh
# Relais vers ocots-lint.

OCOTS_LINT_VERSION=v0.9.0

if [ -n "${OCOTS_LINT:-}" ]; then
  exec $OCOTS_LINT "$@"
fi
"""

CHANGELOG = """# Journal des versions

---

## Non publié

- une entrée déjà là.

---

## v2.9.0 — 2026-10-07

Version mineure.
"""

NOTES = """Deux règles des conventions sont outillées et `couverture` lit `site.md`.
Une montée peut faire disparaître des trouvailles.

- `couverture` lit `site.md`.
"""


def depot(tmp_path, changelog=CHANGELOG, bin_=BIN):
    (tmp_path / "bin").mkdir()
    (tmp_path / "bin/ocots-lint").write_text(bin_, encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text(changelog, encoding="utf-8")
    notes = tmp_path / "notes.md"
    notes.write_text(NOTES, encoding="utf-8")
    return notes


def test_la_version_epinglee_est_lue():
    assert relais.version_epinglee(BIN) == "v0.9.0"
    assert relais.version_epinglee("rien ici") is None


def test_monter_ne_change_que_la_ligne_de_version():
    assert relais.monte_relais(BIN, "v0.10.0") == BIN.replace("v0.9.0", "v0.10.0")


def test_le_resume_est_le_premier_paragraphe_sur_une_ligne():
    assert relais.resume(NOTES) == (
        "Deux règles des conventions sont outillées et `couverture` lit `site.md`. "
        "Une montée peut faire disparaître des trouvailles.")


def plat(texte):
    return " ".join(texte.split())


def test_l_entree_a_le_lien_de_la_release_et_son_resume():
    ligne = relais.entree("v0.10.0", NOTES)
    assert plat(ligne).startswith(
        "- `ocots-lint` passe à [`v0.10.0`]"
        "(https://github.com/ocourses/ocots-lint/releases/tag/v0.10.0) : Deux règles")
    assert plat(ligne).endswith("trouvailles.")


def test_l_entree_est_une_puce_a_retrait_et_tient_en_78_colonnes():
    lignes = relais.entree("v0.10.0", NOTES).splitlines()
    assert lignes[0].startswith("- ")
    assert all(l.startswith("  ") for l in lignes[1:])
    assert all(len(l) <= 78 for l in lignes)


def test_l_entree_ouvre_la_section_non_publie():
    nouveau = relais.ajoute_entree(CHANGELOG, "- neuf.\n")
    assert "## Non publié\n\n- neuf.\n- une entrée déjà là." in nouveau
    assert nouveau.count("## Non publié") == 1


def test_sans_section_non_publie_rien_n_est_ajoute():
    assert relais.ajoute_entree("# Journal\n", "- x\n") is None


def test_main_monte_la_version_et_le_journal(tmp_path, capsys):
    notes = depot(tmp_path)
    assert relais.main([str(tmp_path), "v0.10.0", str(notes)]) == 0
    assert capsys.readouterr().out.strip() == "v0.9.0 -> v0.10.0"
    assert "OCOTS_LINT_VERSION=v0.10.0" in (tmp_path / "bin/ocots-lint").read_text()
    journal = (tmp_path / "CHANGELOG.md").read_text()
    assert plat(journal).count("## Non publié - `ocots-lint` passe à [`v0.10.0`]") == 1
    assert "- une entrée déjà là." in journal


def test_main_est_sans_effet_si_deja_a_la_version(tmp_path, capsys):
    notes = depot(tmp_path)
    assert relais.main([str(tmp_path), "v0.9.0", str(notes)]) == 0
    assert "déjà à v0.9.0" in capsys.readouterr().out
    assert (tmp_path / "CHANGELOG.md").read_text() == CHANGELOG
    assert (tmp_path / "bin/ocots-lint").read_text() == BIN


def test_main_refuse_un_relais_sans_ligne_de_version(tmp_path, capsys):
    notes = depot(tmp_path, bin_="#!/bin/sh\n")
    assert relais.main([str(tmp_path), "v0.10.0", str(notes)]) == 1
    assert "OCOTS_LINT_VERSION" in capsys.readouterr().err


def test_main_n_ecrit_rien_si_le_journal_n_a_pas_de_section(tmp_path, capsys):
    notes = depot(tmp_path, changelog="# Journal\n")
    assert relais.main([str(tmp_path), "v0.10.0", str(notes)]) == 1
    assert "Non publié" in capsys.readouterr().err
    assert "v0.9.0" in (tmp_path / "bin/ocots-lint").read_text()


REEL = Path(__file__).resolve().parents[1] / "conventions"


@pytest.mark.skipif(not (REEL / "bin/ocots-lint").exists(),
                    reason="le sous-module conventions n'a pas bin/ocots-lint")
def test_sur_les_vraies_conventions(tmp_path):
    reel = REEL
    (tmp_path / "bin").mkdir()
    (tmp_path / "bin/ocots-lint").write_text((reel / "bin/ocots-lint").read_text())
    (tmp_path / "CHANGELOG.md").write_text((reel / "CHANGELOG.md").read_text())
    notes = tmp_path / "notes.md"
    notes.write_text(NOTES)
    assert relais.main([str(tmp_path), "v99.0.0", str(notes)]) == 0
    assert "OCOTS_LINT_VERSION=v99.0.0" in (tmp_path / "bin/ocots-lint").read_text()
