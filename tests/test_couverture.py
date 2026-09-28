from ocots_lint import couverture
from ocots_lint.conventions import FICHIERS

CONTENU = {
    "communes.md": "## C1 — Langue\n\n## C3 — Macros\n\n## C4 — Typographie\n"
                   "\n## C6 — Listes\n",
    "poly.md": "## P1 — Hypothèses\n\n## P2 — Boîtes\n\n## P3 — Amorce\n"
               "\n## P5 — Remarques | apartés\n",
    "slides.md": "## SL1 — Référence\n",
    "td.md": "# TD\n",
    "exam.md": "# Examens\n",
}


def conventions_fictives(tmp_path, sans=()):
    for fichier in FICHIERS:
        texte = CONTENU[fichier]
        for ident in sans:
            texte = "\n".join(l for l in texte.split("\n")
                              if not l.startswith(f"## {ident} "))
        (tmp_path / fichier).write_text(texte, encoding="utf-8")
    return str(tmp_path)


def test_une_ligne_par_regle_avec_son_outillage(tmp_path, capsys):
    assert couverture.main(["--conventions", conventions_fictives(tmp_path)]) == 0
    sortie = capsys.readouterr()
    lignes = {l.split()[0]: l for l in sortie.out.splitlines()[2:]}
    assert list(lignes) == ["C1", "C3", "C4", "C6", "P1", "P2", "P3", "P5", "SL1"]
    assert lignes["C1"].endswith("mesure")
    assert lignes["C4"].endswith("heuristique + mesure")
    assert lignes["P1"].endswith("non outillée")
    assert lignes["P3"].endswith("signal")
    assert "9 règles : 5 vérifiées, 2 mesurées seulement, 2 non outillées" in (
        sortie.err)


def test_markdown(tmp_path, capsys):
    dossier = conventions_fictives(tmp_path)
    assert couverture.main(["--conventions", dossier, "--markdown"]) == 0
    out = capsys.readouterr().out
    assert "| Règle | Titre | Outillage |" in out
    assert "/poly.md#p2--boîtes) | Boîtes | heuristique |" in out
    assert "| Remarques \\| apartés | signal |" in out


def test_regle_outillee_absente_des_conventions(tmp_path, capsys):
    dossier = conventions_fictives(tmp_path, sans=("P5",))
    assert couverture.main(["--conventions", dossier]) == 2
    assert "absentes de ces conventions : P5" in capsys.readouterr().err


def test_conventions_introuvables(tmp_path, capsys):
    assert couverture.main(["--conventions", str(tmp_path)]) == 2
    assert "conventions introuvables" in capsys.readouterr().err


def test_argument_inconnu(capsys):
    assert couverture.main(["--inconnu"]) == 2
    assert "argument inconnu" in capsys.readouterr().err
