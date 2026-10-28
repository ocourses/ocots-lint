from ocots_lint import couverture
from ocots_lint.conventions import FACULTATIFS, FICHIERS

CONTENU = {
    "communes.md": "## C1 — Langue\n\n## C3 — Macros\n\n## C4 — Typographie\n"
                   "\n## C5 — Labels\n\n## C6 — Listes\n",
    "poly.md": "## P1 — Hypothèses\n\n## P2 — Boîtes\n\n## P3 — Amorce\n"
               "\n## P5 — Remarques | apartés\n\n## P7 — Ouverture\n",
    "slides.md": "## SL1 — Référence\n\n## SL8 — Thème global\n",
    "td.md": "# TD\n\n## TD3 — Questions\n\n## TD8 — Corrigé au fil des questions\n",
    "exam.md": "# Examens\n\n## EX3 — Barème par les clés\n",
    "site.md": "## WEB1 — Modèles\n\n## WEB2 — Une page tient\n",
}


def conventions_fictives(tmp_path, sans=(), fichiers=FICHIERS):
    tmp_path.mkdir(parents=True, exist_ok=True)
    for fichier in fichiers:
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
    assert list(lignes) == [
        "C1", "C3", "C4", "C5", "C6", "P1", "P2", "P3", "P5", "P7", "SL1",
        "SL8", "TD3", "TD8", "EX3",
    ]
    assert lignes["C1"].endswith("mesure")
    assert lignes["C4"].endswith("heuristique + mesure")
    assert lignes["P1"].endswith("non outillée")
    assert lignes["P3"].endswith("signal")
    assert lignes["TD8"].endswith("exact")
    assert lignes["TD3"].endswith("heuristique")
    assert lignes["EX3"].endswith("heuristique")
    assert "15 règles : 9 vérifiées, 3 mesurées seulement, 3 non outillées" in (
        sortie.err)


def test_markdown(tmp_path, capsys):
    dossier = conventions_fictives(tmp_path)
    assert couverture.main(["--conventions", dossier, "--markdown"]) == 0
    out = capsys.readouterr().out
    assert "| Règle | Titre | Outillage |" in out
    assert "/poly.md#p2--boîtes) | Boîtes | heuristique |" in out
    assert "| Remarques \\| apartés | signal |" in out


def test_support_td_ne_compte_que_commun_et_td(tmp_path, capsys):
    assert couverture.main(["--conventions", conventions_fictives(tmp_path),
                            "--support", "td"]) == 0
    sortie = capsys.readouterr()
    lignes = [l for l in sortie.out.splitlines()
              if l and not l.startswith("Conventions") and not l.startswith("|")]
    assert [l.split()[0] for l in lignes] == [
        "C1", "C3", "C4", "C5", "C6", "TD3", "TD8"]
    assert "7 règles applicables au support « td »" in sortie.err
    assert "5 vérifiées" in sortie.err


def test_les_regles_web_sont_hors_ocots_lint_et_comptees_a_part(tmp_path, capsys):
    # Le résumé avec site.md : celui sans, plus deux règles « hors ocots-lint ».
    sans_web = conventions_fictives(tmp_path / "sans")
    assert couverture.main(["--conventions", sans_web]) == 0
    sans = capsys.readouterr().err.strip().rstrip(".")
    dossier = conventions_fictives(tmp_path / "avec", fichiers=FICHIERS + FACULTATIFS)
    assert couverture.main(["--conventions", dossier]) == 0
    sortie = capsys.readouterr()
    lignes = {l.split()[0]: l for l in sortie.out.splitlines()[2:]}
    assert lignes["WEB1"].endswith("hors ocots-lint")
    total, reste = sans.split(" règles : ", 1)
    assert sortie.err.strip() == (f"{int(total) + 2} règles : {reste}, "
                                  "2 hors ocots-lint (site.md, « Vérifié par »).")


def test_support_site_ne_liste_que_les_regles_web(tmp_path, capsys):
    dossier = conventions_fictives(tmp_path, fichiers=FICHIERS + FACULTATIFS)
    assert couverture.main(["--conventions", dossier, "--support", "site"]) == 0
    sortie = capsys.readouterr()
    lignes = [l for l in sortie.out.splitlines()[2:] if l]
    assert [l.split()[0] for l in lignes] == ["WEB1", "WEB2"]
    assert "0 non outillées, 2 hors ocots-lint" in sortie.err


def test_support_inconnu(tmp_path, capsys):
    assert couverture.main(["--conventions", conventions_fictives(tmp_path),
                            "--support", "tds"]) == 2
    assert "support inconnu" in capsys.readouterr().err


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
