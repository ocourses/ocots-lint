import re
from collections import Counter

from ocots_lint.mesures import MESURES, mesurer

from outils import FIXTURES, RE_ATTENDU, RE_IDENTIFIANT

RE_SORTIE = re.compile(r"^(.*):(\d+): \[mesure (\w+)\] ")


def comptes_marques(chemin):
    compte = Counter()
    for no, ligne in enumerate(chemin.read_text(encoding="utf-8").split("\n"), 1):
        m = RE_ATTENDU.search(ligne)
        if m:
            for ident in RE_IDENTIFIANT.findall(m.group(1)):
                compte[(no, ident)] += 1
    return compte


def test_une_mesure_de_chaque(capsys):
    chemin = FIXTURES / "mesures" / "une_de_chaque.tex"
    assert mesurer([str(chemin)]) == 0
    sortie = capsys.readouterr()
    trouvees = Counter()
    for ligne in sortie.out.splitlines():
        m = RE_SORTIE.match(ligne)
        assert m, ligne
        trouvees[(int(m.group(2)), m.group(3))] += 1
    assert trouvees == comptes_marques(chemin)


def test_bilan_liste_toutes_les_mesures_meme_a_zero(capsys):
    assert mesurer([str(FIXTURES / "mesures" / "rien.tex")]) == 0
    sortie = capsys.readouterr()
    assert sortie.out == ""
    bilan = sortie.err.splitlines()
    assert len(bilan) == len(MESURES)
    assert all(re.match(r"mesure \w+ :\s+0  ", ligne) for ligne in bilan)


def test_p7_signale_un_chapitre_etoile_ajoute_sans_adjustmtc(capsys):
    chemin = FIXTURES / "mesures" / "minitoc_sans_adjustmtc.tex"
    assert mesurer([str(chemin)]) == 0
    sortie = capsys.readouterr()
    assert "[mesure P7]" in sortie.out
    assert r"sans \adjustmtc — \adjustmtc juste après \addcontentsline" in sortie.out


def test_p7_accepte_adjustmtc_juste_apres_l_ajout(capsys):
    chemin = FIXTURES / "mesures" / "minitoc_avec_adjustmtc.tex"
    assert mesurer([str(chemin)]) == 0
    sortie = capsys.readouterr()
    assert "[mesure P7]" not in sortie.out
