"""`ocots-lint synchroniser` (S3.5) : le plan, puis son application par gh."""

import json
import os
import stat
import textwrap

import pytest

from ocots_lint import synchroniser as sync
from ocots_lint.sorties import Avertissement
from ocots_lint.synchroniser import Constat, Issue, planifier


def constat(fichier="a.tex", ligne=3, empreinte="aaaaaaaaaaaaaaaa:0", regle="P2"):
    return Constat(fichier, ligne, regle, "heuristique", "tri",
                   "theorem -> lemma", empreinte)


def issue(numero, fichier="a.tex", ouverte=True, label=sync.LABEL_CANDIDAT,
          corps="", raison=""):
    return Issue(numero, sync.titre(fichier), ouverte, frozenset({label}),
                 corps, raison)


def genres(plan):
    return [(a.genre, a.fichier, a.numero) for a in plan.actions]


# ------------------------------------------------------------------ plan

def test_creer():
    assert genres(planifier([constat()], [], [])) == [("creer", "a.tex", 0)]


def test_mettre_a_jour_ou_inchangee():
    plan = planifier([constat()], [], [issue(7, corps="ancien")])
    assert genres(plan) == [("mettre_a_jour", "a.tex", 7)]
    corps = plan.actions[0].corps
    assert genres(planifier([constat()], [], [issue(7, corps=corps)])) == [
        ("inchangee", "a.tex", 7)]


def test_promue_jamais_touchee():
    plan = planifier([constat()], [], [issue(7, label=sync.LABEL_PROMU)])
    assert genres(plan) == [("promue", "a.tex", 0)]


def test_fermer_quand_plus_rien():
    plan = planifier([], [], [issue(7)])
    assert genres(plan) == [("fermer", "a.tex", 7)]
    assert plan.actions[0].raison == "completed"


def test_fichier_ignore():
    plan = planifier([constat("poly/solutions/x.tex")], [],
                     [issue(7, "poly/solutions/y.tex")], ignores=["poly/solutions/"])
    assert genres(plan) == [("fermer", "poly/solutions/y.tex", 7)]
    assert plan.actions[0].raison == "not planned"


def corps_avec(*empreintes):
    return sync.corps_issue("a.tex", [constat(empreinte=e) for e in empreintes],
                            [], "")


def test_rejet_non_redemande():
    rejetee = issue(5, ouverte=False, raison="NOT_PLANNED",
                    corps=corps_avec("aaaaaaaaaaaaaaaa:0", "bbbbbbbbbbbbbbbb:0"))
    plan = planifier([constat()], [], [rejetee])
    assert genres(plan) == [("rejet", "a.tex", 5)]
    assert "ocots-lint exempter" in plan.actions[0].commentaire


def test_nouvelle_trouvaille_apres_un_rejet():
    rejetee = issue(5, ouverte=False, raison="NOT_PLANNED",
                    corps=corps_avec("bbbbbbbbbbbbbbbb:0"))
    assert genres(planifier([constat()], [], [rejetee])) == [("creer", "a.tex", 0)]


def test_ancienne_issue_sans_bloc_ne_bloque_pas():
    """Les issues ouvertes par conventions.sh n'ont pas d'empreintes."""
    rejetee = issue(5, ouverte=False, raison="NOT_PLANNED", corps="| 3 | P2 |")
    assert genres(planifier([constat()], [], [rejetee])) == [("creer", "a.tex", 0)]


def test_fermee_car_corrigee_n_est_pas_un_rejet():
    fermee = issue(5, ouverte=False, raison="COMPLETED",
                   corps=corps_avec("aaaaaaaaaaaaaaaa:0"))
    assert genres(planifier([constat()], [], [fermee])) == [("creer", "a.tex", 0)]


def test_corps_porte_trouvailles_bloc_et_avertissements():
    corps = sync.corps_issue(
        "a.tex", [constat()], [Avertissement("a.tex", 9, "exemption P5 inutile")],
        "ocots-lint 0.3.0")
    assert "| 3 | P2 | heuristique | tri | theorem -> lemma |" in corps
    assert "- ligne 9 : exemption P5 inutile" in corps
    assert "ocots-lint 0.3.0" in corps
    assert Issue(1, "", True, frozenset(), corps).empreintes == {"aaaaaaaaaaaaaaaa:0"}


def test_lire_ignores(tmp_path):
    f = tmp_path / ".agents-ignore"
    f.write_text("# commentaire\n\npoly/solutions/\n  td/old/  \n", encoding="utf-8")
    assert sync.lire_ignores(str(f)) == ["poly/solutions/", "td/old/"]
    assert sync.lire_ignores(str(tmp_path / "absent")) == []


# ------------------------------------------------- commande, avec un faux gh

FAUX_GH = """#!/usr/bin/env python3
import json, os, sys
journal = os.environ["GH_JOURNAL"]
entree = sys.stdin.read() if "-" in sys.argv else ""
with open(journal, "a", encoding="utf-8") as fh:
    fh.write(json.dumps({"args": sys.argv[1:], "entree": entree}) + "\\n")
if sys.argv[1:3] == ["issue", "list"]:
    label = sys.argv[sys.argv.index("--label") + 1]
    print(json.dumps(json.loads(os.environ.get("GH_ISSUES", "{}")).get(label, [])))
if os.environ.get("GH_ECHEC") and sys.argv[1:3] == ["issue", "create"]:
    sys.exit(1)
"""


@pytest.fixture
def cours(tmp_path, monkeypatch):
    bin_ = tmp_path / "bin"
    bin_.mkdir()
    gh = bin_ / "gh"
    gh.write_text(FAUX_GH, encoding="utf-8")
    gh.chmod(gh.stat().st_mode | stat.S_IEXEC)
    racine = tmp_path / "cours"
    racine.mkdir()
    (racine / "a.tex").write_text(textwrap.dedent("""\
        \\begin{theorem}
        \\end{theorem}

        \\begin{lemma}
        \\end{lemma}
        """), encoding="utf-8")
    monkeypatch.chdir(racine)
    monkeypatch.setenv("PATH", f"{bin_}{os.pathsep}{os.environ['PATH']}")
    monkeypatch.setenv("GH_JOURNAL", str(tmp_path / "journal"))
    monkeypatch.setenv("GITHUB_REPOSITORY", "ocourses/essai")
    return tmp_path


def appels(cours):
    f = cours / "journal"
    if not f.exists():
        return []
    return [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines()]


def ecritures(cours):
    return [a for a in appels(cours)
            if a["args"][:2] in (["issue", "create"], ["issue", "edit"],
                                 ["issue", "close"], ["issue", "comment"])]


def test_dry_run_ne_touche_rien(cours, capsys):
    assert sync.main(["--dry-run"]) == 0
    assert "+ créer : [conventions] a.tex" in capsys.readouterr().out
    assert ecritures(cours) == []


def test_applique_le_plan(cours, capsys):
    assert sync.main([]) == 0
    (creation,) = ecritures(cours)
    assert creation["args"][:2] == ["issue", "create"]
    assert "[conventions] a.tex" in creation["args"]
    assert sync.LABEL_CANDIDAT in creation["args"]
    assert "<!-- ocots-lint " in creation["entree"]


def test_ferme_une_candidate_corrigee(cours, capsys, monkeypatch):
    (cours / "cours" / "a.tex").write_text("Rien à signaler.\n", encoding="utf-8")
    monkeypatch.setenv("GH_ISSUES", json.dumps({sync.LABEL_CANDIDAT: [{
        "number": 4, "title": "[conventions] a.tex", "body": "", "state": "OPEN",
        "labels": [{"name": sync.LABEL_CANDIDAT}], "stateReason": ""}]}))
    assert sync.main([]) == 0
    genres = [a["args"][:2] for a in ecritures(cours)]
    assert genres == [["issue", "comment"], ["issue", "close"]]


def test_echec_gh(cours, capsys, monkeypatch):
    monkeypatch.setenv("GH_ECHEC", "1")
    assert sync.main([]) == 2
    assert "GitHub" in capsys.readouterr().err


def test_echec_de_l_analyse_ne_touche_rien(cours, capsys, monkeypatch):
    def plante(*_):
        raise RuntimeError("boum")
    monkeypatch.setattr(sync, "analyser", plante)
    assert sync.main([]) == 2
    assert "aucune issue touchée" in capsys.readouterr().err
    assert appels(cours) == []


def test_option_inconnue(capsys):
    assert sync.main(["--rien"]) == 2


# ------------------------------------------------- deux familles (S3.7, étape 2)

def mecanique(fichier="a.tex", ligne=5, empreinte="cccccccccccccccc:0"):
    return Constat(fichier, ligne, "C4", "heuristique", "mecanique",
                   "`~:` inutile", empreinte)


def titres(plan):
    return [(a.genre, sync.titre(a.fichier, a.famille)) for a in plan.actions]


def test_mecanique_a_sa_propre_issue():
    plan = planifier([constat(), mecanique()], [], [])
    assert titres(plan) == [("creer", "[conventions] a.tex"),
                            ("creer", "[nettoyer] a.tex")]
    nettoyer = plan.actions[1]
    assert nettoyer.famille.label == sync.LABEL_MECANIQUE
    assert "ocots-lint/nettoyer/a.tex" in nettoyer.corps
    assert "| 5 | C4 | heuristique | mecanique |" in nettoyer.corps
    assert "| 5 |" not in plan.actions[0].corps


def test_pr_en_cours_bloque_la_recreation():
    plan = planifier([mecanique()], [], [],
                     branches_ouvertes=frozenset({"ocots-lint/nettoyer/a.tex"}))
    assert titres(plan) == [("pr_en_cours", "[nettoyer] a.tex")]


def test_candidate_fermee_quand_il_ne_reste_que_du_mecanique():
    plan = planifier([mecanique()], [], [issue(7)])
    assert titres(plan) == [("fermer", "[conventions] a.tex"),
                            ("creer", "[nettoyer] a.tex")]


def test_issue_nettoyer_fermee_quand_corrige():
    ouverte = Issue(9, "[nettoyer] a.tex", True, frozenset({sync.LABEL_MECANIQUE}))
    assert titres(planifier([constat()], [], [ouverte])) == [
        ("creer", "[conventions] a.tex"), ("fermer", "[nettoyer] a.tex")]


def test_avertissements_dans_l_issue_conventions_sinon_nettoyer():
    avert = [Avertissement("a.tex", 2, "exemption P5 inutile")]
    mixte = planifier([constat(), mecanique()], avert, [])
    assert "exemption P5 inutile" in mixte.actions[0].corps
    assert "exemption P5 inutile" not in mixte.actions[1].corps
    seul = planifier([mecanique()], avert, [])
    assert "exemption P5 inutile" in seul.actions[0].corps


def test_rejet_ne_concerne_que_les_candidates():
    """Une issue [nettoyer] fermée n'empêche pas d'en recréer une."""
    fermee = Issue(5, "[nettoyer] a.tex", False, frozenset({sync.LABEL_MECANIQUE}),
                   sync.corps_issue("a.tex", [mecanique()], [], "", sync.NETTOYER),
                   "NOT_PLANNED")
    assert titres(planifier([mecanique()], [], [fermee])) == [
        ("creer", "[nettoyer] a.tex")]


def test_branche_nettoyer():
    assert sync.branche_nettoyer("poly/ch 1/a+b.tex") == (
        "ocots-lint/nettoyer/poly/ch-1/a-b.tex")


def test_applique_avec_le_label_mecanique(cours, capsys):
    (cours / "cours" / "a.tex").write_text("Question~: ici.\n", encoding="utf-8")
    assert sync.main([]) == 0
    (creation,) = ecritures(cours)
    assert "[nettoyer] a.tex" in creation["args"]
    assert sync.LABEL_MECANIQUE in creation["args"]
