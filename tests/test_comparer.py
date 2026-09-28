"""`ocots-lint comparer` (S3.9)."""

import json

from ocots_lint import comparer


def trouvaille(fichier="a.tex", ligne=3, regle="P2", empreinte="aaaaaaaaaaaaaaaa:0",
               exemption=None):
    return {"regle": regle, "garantie": "heuristique", "fichier": fichier,
            "ligne": ligne, "message": "theorem -> lemma", "empreinte": empreinte,
            "voie": "tri", "exemption": exemption}


def ecrire(tmp_path, nom, trouvailles, empreintes=True):
    if not empreintes:
        trouvailles = [{k: v for k, v in t.items() if k != "empreinte"}
                       for t in trouvailles]
    f = tmp_path / nom
    f.write_text(json.dumps({"schema": 1, "trouvailles": trouvailles}),
                 encoding="utf-8")
    return str(f)


def test_identiques(tmp_path, capsys):
    a = ecrire(tmp_path, "a.json", [trouvaille()])
    assert comparer.main([a, a]) == 0
    assert "= inchangées : 1" in capsys.readouterr().out


def test_decalage_de_lignes_sans_changement(tmp_path, capsys):
    a = ecrire(tmp_path, "a.json", [trouvaille(ligne=3)])
    b = ecrire(tmp_path, "b.json", [trouvaille(ligne=9)])
    assert comparer.main([a, b]) == 0


def test_apparues_disparues_et_issues(tmp_path, capsys):
    b_tex = trouvaille("b.tex", empreinte="b" * 16 + ":0")
    c_tex = trouvaille("c.tex", regle="C4", empreinte="c" * 16 + ":0")
    a = ecrire(tmp_path, "a.json", [trouvaille(), b_tex])
    b = ecrire(tmp_path, "b.json", [trouvaille(), c_tex])
    assert comparer.main([a, b]) == 1
    out = capsys.readouterr().out
    assert "+ apparues (1)\n  c.tex:3: [C4]" in out
    assert "- disparues (1)\n  b.tex:3: [P2]" in out
    assert "Par règle : C4 +1 −0 ; P2 +0 −1" in out
    assert "Issues à créer : c.tex" in out
    assert "Issues à fermer : b.tex" in out


def test_exemptees_ignorees(tmp_path, capsys):
    a = ecrire(tmp_path, "a.json", [trouvaille()])
    b = ecrire(tmp_path, "b.json", [trouvaille(exemption="voulu")])
    assert comparer.main([a, b]) == 1
    assert "- disparues (1)" in capsys.readouterr().out


def test_sortie_sans_empreintes(tmp_path, capsys):
    a = ecrire(tmp_path, "a.json", [trouvaille()], empreintes=False)
    b = ecrire(tmp_path, "b.json", [trouvaille()])
    assert comparer.main([a, b]) == 0
    assert "sans empreintes" in capsys.readouterr().err


def test_format_json(tmp_path, capsys):
    a = ecrire(tmp_path, "a.json", [])
    b = ecrire(tmp_path, "b.json", [trouvaille()])
    assert comparer.main([a, b, "--format", "json"]) == 1
    ecart = json.loads(capsys.readouterr().out)
    assert len(ecart["apparues"]) == 1
    assert ecart["fichiers"]["nouvelle_issue"] == ["a.tex"]


def test_entree_illisible(tmp_path, capsys):
    f = tmp_path / "x.json"
    f.write_text("pas du json", encoding="utf-8")
    assert comparer.main([str(f), str(f)]) == 2
    assert comparer.main(["seul.json"]) == 2
