"""`ocots-lint nettoyer` (S2.6) : corrections, et garde-fous."""

import shutil

from ocots_lint import nettoyer

from outils import FIXTURES

NETTOYER = FIXTURES / "nettoyer"


def corriger(texte, guillemets=True):
    return nettoyer.appliquer_corrections(
        texte, nettoyer.corrections_C4(texte, guillemets=guillemets))


def test_tilde_retire_hors_maths_seulement():
    assert corriger("question~: $a ~:~ b$ \\[ x ~: y \\]") == (
        "question: $a ~:~ b$ \\[ x ~: y \\]")


def test_guillemets_en_enquote():
    assert corriger("dit ``presque partout''.") == "dit \\enquote{presque partout}."


def test_guillemets_laisses_sans_csquotes():
    assert corriger("dit ``ici''~:", guillemets=False) == "dit ``ici'':"


def test_paire_qui_enjambe_un_paragraphe_intacte():
    texte = "``un\n\ndeux''"
    assert corriger(texte) == texte


def test_apercu_n_ecrit_rien(tmp_path, capsys):
    copie = tmp_path / "cas"
    shutil.copytree(NETTOYER / "avec-csquotes", copie)
    avant = (copie / "b.tex").read_text(encoding="utf-8")
    assert nettoyer.main(["C4", str(copie)]) == 0
    assert (copie / "b.tex").read_text(encoding="utf-8") == avant
    assert "Rien n'a été écrit" in capsys.readouterr().err


def test_appliquer_ecrit(tmp_path, capsys):
    copie = tmp_path / "cas"
    shutil.copytree(NETTOYER / "avec-csquotes", copie)
    assert nettoyer.main(["C4", str(copie), "--appliquer"]) == 0
    b = (copie / "b.tex").read_text(encoding="utf-8")
    assert "\\enquote{presque partout}" in b and "~:" not in b
    assert "$``x''$" in b


def test_sans_csquotes_le_dit(tmp_path, capsys):
    copie = tmp_path / "cas"
    shutil.copytree(NETTOYER / "sans-csquotes", copie)
    nettoyer.main(["C4", str(copie), "--appliquer"])
    assert "csquotes introuvable" in capsys.readouterr().err
    assert "``presque partout''" in (copie / "a.tex").read_text(encoding="utf-8")


def test_chemin_inconnu(capsys):
    assert nettoyer.main(["C4", "n-existe-pas/"]) == 2


def test_ligne_exemptee_non_corrigee(tmp_path, capsys):
    f = tmp_path / "a.tex"
    f.write_text("voulu~: ici % ocots-lint: ignore C4 — forme voulue\n"
                 "corrigé~: là\n", encoding="utf-8")
    assert nettoyer.main(["C4", str(tmp_path), "--appliquer"]) == 0
    assert f.read_text(encoding="utf-8") == (
        "voulu~: ici % ocots-lint: ignore C4 — forme voulue\ncorrigé: là\n")


# ------------------------------------------- lecture par l'arbre (S4.3)

def test_ne_touche_que_la_prose():
    """URL, \\verb, verbatim, commentaire : jamais corrigés — une URL
    « nettoyée » ne mène plus nulle part."""
    texte = ("Voir \\url{https://exemple.org/a~:b} et \\verb|x~:y|.\n"
             "% note~: ``commentée''\n"
             "\\begin{lstlisting}\nprint(\"a~:b\")\n\\end{lstlisting}\n"
             "Enfin~: ``ici''.\n")
    assert corriger(texte) == texte.replace("Enfin~: ``ici''",
                                            "Enfin: \\enquote{ici}")


def test_saut_de_ligne_espace_n_est_pas_une_formule():
    texte = "Ligne\\\\[0.2em]\nles inclusions suivantes~:\n\\[ a ~: b \\]\n"
    assert corriger(texte) == texte.replace("suivantes~:", "suivantes:")


def test_fichier_refuse_lu_par_le_repli(tmp_path, capsys):
    f = tmp_path / "notations.tex"
    f.write_text("\\begin{longtable}{>{$}l<{$}l}\n\\R & réels \\\\\n"
                 "\\end{longtable}\nQuestion~: oui.\n", encoding="utf-8")
    assert nettoyer.main(["C4", str(f), "--appliquer"]) == 0
    assert f.read_text(encoding="utf-8").endswith("Question: oui.\n")
    err = capsys.readouterr().err
    assert "notations.tex:1: analyse syntaxique refusée" in err


def lignes_de(texte, positions):
    return sorted(texte.count("\n", 0, p) + 1 for p in positions)


def debuts(corrections, etiquette):
    return [d for d, _, _, e in corrections if e == etiquette]


def test_la_voie_mecanique_suit_c4():
    """Sur toutes les fixtures : `nettoyer` corrige un `~:` exactement là où
    C4 le signale, et ne réécrit des guillemets que là où C4 en signale.
    C'est ce qui rend la voie `mecanique` de `verifier` juste."""
    from ocots_lint.regles.c4 import regle_C4
    for chemin in sorted(FIXTURES.rglob("*.tex")):
        texte = chemin.read_text(encoding="utf-8")
        c4 = list(regle_C4([str(chemin)]))
        tildes_c4 = sorted(l for _, l, m in c4 if m.startswith("`~:`"))
        guillemets_c4 = {l for _, l, m in c4 if m.startswith("guillemets")}
        corrections = nettoyer.corrections_C4(texte)
        tildes = lignes_de(texte, debuts(corrections, "~: inutile"))
        guillemets = lignes_de(texte, debuts(corrections, "guillemets"))
        assert tildes == tildes_c4, chemin
        assert set(guillemets) <= guillemets_c4, chemin
