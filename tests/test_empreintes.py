"""Empreintes stables (S3.2) : l'identité d'une trouvaille ne dépend pas de
son numéro de ligne."""

import json
import textwrap

from ocots_lint import verifier
from ocots_lint.empreintes import contexte, normaliser

SOURCE = r"""
Introduction.

\begin{theorem}
  Premier énoncé.
\end{theorem}

\begin{proposition}
  Le sous espace~: voir ``ici''.
\end{proposition}
"""


def empreintes(tmp_path, capsys, texte, *regles):
    f = tmp_path / "cours.tex"
    f.write_text(textwrap.dedent(texte).lstrip("\n"), encoding="utf-8")
    verifier.main(["--format", "json", *regles, str(f)])
    doc = json.loads(capsys.readouterr().out)
    return {(t["regle"], t["message"], t["empreinte"]): t["ligne"]
            for t in doc["trouvailles"]}


def cles(trouvees):
    return set(trouvees)


def test_lignes_inserees_au_dessus(tmp_path, capsys):
    avant = empreintes(tmp_path, capsys, SOURCE)
    apres = empreintes(tmp_path, capsys, "Une.\n\nDeux.\n\nTrois.\n" + SOURCE)
    assert cles(avant) == cles(apres)
    assert all(apres[k] == avant[k] + 6 for k in avant)


def test_exemption_posee_au_dessus(tmp_path, capsys):
    avant = empreintes(tmp_path, capsys, SOURCE, "P2")
    apres = empreintes(tmp_path, capsys, SOURCE.replace(
        "\\end{theorem}",
        "  % ocots-lint: ignore P2 — voulu\n\\end{theorem}"), "P2")
    assert cles(avant) == cles(apres)


def test_commentaire_en_fin_de_ligne(tmp_path, capsys):
    avant = empreintes(tmp_path, capsys, SOURCE, "P2")
    apres = empreintes(tmp_path, capsys, SOURCE.replace(
        "\\end{theorem}", "\\end{theorem} % ocots-lint: ignore P2 — voulu"), "P2")
    assert cles(avant) == cles(apres)


def test_ligne_signalee_modifiee(tmp_path, capsys):
    avant = empreintes(tmp_path, capsys, SOURCE, "P2")
    apres = empreintes(tmp_path, capsys,
                       SOURCE.replace("Premier énoncé.", "Autre énoncé."), "P2")
    assert cles(avant) != cles(apres)


def test_plusieurs_trouvailles_sur_une_ligne(tmp_path, capsys):
    trouvees = empreintes(tmp_path, capsys, SOURCE, "C4")
    rangs = sorted(e.split(":")[1] for _, _, e in trouvees)
    assert rangs == ["0", "1", "2"]
    assert len({e.split(":")[0] for _, _, e in trouvees}) == 1


def test_blocs_identiques(tmp_path, capsys):
    bloc = ("\\begin{theorem}\n  x\n\\end{theorem}\n\n"
            "\\begin{lemma}\n  y\n\\end{lemma}\n")
    trouvees = empreintes(tmp_path, capsys, bloc + "\nTexte.\n\n" + bloc, "P2")
    assert sorted(e[-2:] for _, _, e in trouvees) == [":0", ":1"]


def test_ordre_des_regles_sans_effet(tmp_path, capsys):
    assert empreintes(tmp_path, capsys, SOURCE, "P2", "C4") == (
        empreintes(tmp_path, capsys, SOURCE, "C4", "P2"))


def test_normaliser():
    assert normaliser("  a   b  % commentaire") == "a b"
    assert normaliser("100\\% sûr % note") == "100\\% sûr"
    assert normaliser("% seul") == ""


def test_contexte_saute_les_lignes_vides_et_commentees():
    lignes = ["a", "", "% note", "b", "   ", "c"]
    assert contexte(lignes, 4) == ("a", "b", "c")
    assert contexte(lignes, 1) == ("", "a", "b")
