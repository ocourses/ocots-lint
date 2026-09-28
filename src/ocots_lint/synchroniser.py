"""`ocots-lint synchroniser` — une issue par fichier en infraction (S3.5).

    ocots-lint synchroniser --dry-run            le plan, sans rien toucher
    ocots-lint synchroniser                      applique le plan (gh)
    ocots-lint synchroniser --depot ocourses/x   dépôt (défaut : GITHUB_REPOSITORY)

Remplace `ocourses/agents/scripts/checkers/conventions.sh`, avec les mêmes
titres (`[conventions] <fichier>`) et les mêmes labels, pour que la file
d'attente et les rôles des agents continuent de fonctionner. Ce qui change :

- **le plan est une fonction pure** (`planifier`), testée ; `--dry-run`
  l'affiche sans rien toucher ;
- chaque issue porte, dans un commentaire HTML, les trouvailles au format du
  contrat JSON (empreinte, règle, ligne, garantie, voie) : les agents lisent
  ce bloc, pas le tableau ;
- **un rejet n'est pas redemandé** : si une issue fermée « not planned »
  portait déjà toutes les empreintes actuelles d'un fichier, elle n'est pas
  recréée — le plan le signale, et il faut poser les exemptions
  (`ocots-lint exempter`) ;
- les avertissements sur les exemptions figurent dans l'issue du fichier ;
- si l'analyse échoue, rien n'est touché (sortie 2).

Les issues promues `conventions-style` ne sont jamais touchées ; un fichier
exclu par `.agents-ignore` (préfixes de chemins, `#` commente) voit sa
candidate fermée.
"""

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import PurePath

from ocots_lint import __version__, conventions
from ocots_lint.regles import REGISTRE, REGLES
from ocots_lint.sorties import SCHEMA_JSON
from ocots_lint.verifier import analyser

LABEL_CANDIDAT = "conventions-candidate"
LABEL_PROMU = "conventions-style"
PREFIXE_TITRE = "[conventions] "
RE_BLOC = re.compile(r"<!-- ocots-lint (\{.*?\}) -->", re.S)
DOC_LIMITES = "https://github.com/ocourses/ocots-lint#ce-que-loutil-garantit--et-ce-quil-ne-garantit-pas"


# ------------------------------------------------------------------ modèle

@dataclass(frozen=True)
class Issue:
    numero: int
    titre: str
    ouverte: bool
    labels: frozenset
    corps: str = ""
    raison_fermeture: str = ""       # "NOT_PLANNED", "COMPLETED"…

    @property
    def empreintes(self):
        m = RE_BLOC.search(self.corps)
        if not m:
            return frozenset()
        try:
            bloc = json.loads(m.group(1))
            return frozenset(t["empreinte"] for t in bloc["trouvailles"])
        except (ValueError, KeyError, TypeError):
            return frozenset()


@dataclass(frozen=True)
class Action:
    genre: str          # creer, mettre_a_jour, fermer, inchangee, promue, rejet
    fichier: str
    numero: int = 0
    corps: str = ""
    commentaire: str = ""
    raison: str = ""    # pour fermer : completed, not planned


@dataclass
class Plan:
    actions: list = field(default_factory=list)

    def compte(self, genre):
        return sum(1 for a in self.actions if a.genre == genre)


# ------------------------------------------------------------------ plan

def titre(fichier):
    return PREFIXE_TITRE + fichier


def lire_ignores(chemin):
    """Préfixes de `.agents-ignore` (lignes non vides, `#` commente)."""
    if not chemin or not os.path.isfile(chemin):
        return []
    with open(chemin, encoding="utf-8") as fh:
        return [ligne.strip() for ligne in fh
                if ligne.strip() and not ligne.strip().startswith("#")]


def est_ignore(fichier, ignores):
    return any(fichier.startswith(p) for p in ignores)


def corps_issue(fichier, trouvailles, avertissements, contexte_versions):
    """Corps d'une issue candidate : lisible par un humain, et un bloc JSON
    pour les agents."""
    lignes = [
        f"**⚠️ Candidat brut, pas relu.** Sortie de `ocots-lint verifier` "
        f"({contexte_versions}) — *un signal, pas un verdict*. L'outil rate des "
        f"choses et signale parfois du correct ; zéro trouvaille ne veut pas "
        f"dire règle respectée ([garanties]({DOC_LIMITES})).",
        "",
        "**Ne pas agir sans relecture.** Voie `mecanique` : `ocots-lint "
        "nettoyer` sait corriger. Voie `tri` : un agent (`conventions-reviewer`) "
        "tranche — confirmée → `conventions-style` ; rejetée → exemption posée "
        "par `ocots-lint exempter`, pour qu'elle ne revienne pas.",
        "",
        "| Ligne | Règle | Garantie | Voie | Message |",
        "|---|---|---|---|---|",
    ]
    for t in sorted(trouvailles, key=lambda t: (t.ligne, t.regle)):
        message = t.message.replace("|", "\\|")
        lignes.append(f"| {t.ligne} | {t.regle} | {t.garantie} | {t.voie} "
                      f"| {message} |")
    if avertissements:
        lignes += ["", "**Exemptions à revoir :**", ""]
        lignes += [f"- ligne {a.ligne} : {a.message}"
                   for a in sorted(avertissements, key=lambda a: a.ligne)]
    bloc = {"schema": SCHEMA_JSON, "fichier": fichier, "trouvailles": [
        {"empreinte": t.empreinte, "regle": t.regle, "ligne": t.ligne,
         "garantie": t.garantie, "voie": t.voie}
        for t in sorted(trouvailles, key=lambda t: (t.ligne, t.regle))]}
    lignes += ["", "---",
               "_Détecté par `ocots-lint synchroniser`._",
               f"<!-- ocots-lint {json.dumps(bloc, ensure_ascii=False)} -->"]
    return "\n".join(lignes)


@dataclass(frozen=True)
class Constat:
    """Une trouvaille non exemptée, prête pour une issue."""
    fichier: str
    ligne: int
    regle: str
    garantie: str
    voie: str
    message: str
    empreinte: str


def planifier(constats, avertissements, issues, ignores=(), versions=""):
    """Le plan : fonction pure, sans accès à GitHub ni au disque.

    constats       : trouvailles non exemptées (Constat)
    avertissements : sorties.Avertissement, rattachés à leur fichier
    issues         : Issue existantes portant l'un des deux labels
    """
    par_fichier = {}
    for c in constats:
        if not est_ignore(c.fichier, ignores):
            par_fichier.setdefault(c.fichier, []).append(c)
    avert_par_fichier = {}
    for a in avertissements:
        avert_par_fichier.setdefault(PurePath(a.fichier).as_posix(), []).append(a)

    ouvertes = {i.titre: i for i in issues if i.ouverte and LABEL_CANDIDAT in i.labels}
    promues = {i.titre for i in issues if i.ouverte and LABEL_PROMU in i.labels}
    rejetees = {}
    for i in issues:
        if (not i.ouverte and i.raison_fermeture == "NOT_PLANNED"
                and LABEL_CANDIDAT in i.labels):
            rejetees.setdefault(i.titre, []).append(i)

    plan = Plan()
    for fichier in sorted(par_fichier):
        t = titre(fichier)
        if t in promues:
            plan.actions.append(Action("promue", fichier))
            continue
        corps = corps_issue(fichier, par_fichier[fichier],
                            avert_par_fichier.get(fichier, []), versions)
        if t in ouvertes:
            issue = ouvertes[t]
            genre = "inchangee" if issue.corps == corps else "mettre_a_jour"
            plan.actions.append(Action(genre, fichier, issue.numero, corps))
            continue
        actuelles = {c.empreinte for c in par_fichier[fichier]}
        deja = [i for i in rejetees.get(t, []) if actuelles <= i.empreintes]
        if deja:
            plan.actions.append(Action(
                "rejet", fichier, deja[0].numero,
                commentaire=f"déjà rejeté en #{deja[0].numero}, sans exemption "
                            f"posée : `ocots-lint exempter` pour clore"))
            continue
        plan.actions.append(Action("creer", fichier, corps=corps))

    for t, issue in sorted(ouvertes.items()):
        fichier = t[len(PREFIXE_TITRE):] if t.startswith(PREFIXE_TITRE) else t
        if fichier in par_fichier:
            continue
        if est_ignore(fichier, ignores):
            plan.actions.append(Action(
                "fermer", fichier, issue.numero, raison="not planned",
                commentaire=f"Cible désormais exclue par `.agents-ignore` "
                            f"(`{fichier}`). Fermeture automatique : hors "
                            f"périmètre des détecteurs."))
        else:
            plan.actions.append(Action(
                "fermer", fichier, issue.numero, raison="completed",
                commentaire="Plus aucune trouvaille active de `ocots-lint` sur "
                            "ce fichier (corrigée ou exemptée). Fermeture "
                            "automatique — zéro trouvaille ne certifie pas la "
                            "conformité."))
    return plan


def constats_depuis(trouvailles):
    """Constat pour chaque trouvaille non exemptée."""
    garanties = {v.regle: v.garantie for v in REGISTRE}
    return [Constat(PurePath(t.fichier).as_posix(), t.ligne, t.regle,
                    garanties[t.regle], t.voie, t.message, t.empreinte)
            for t in trouvailles if not t.exemption]


def afficher(plan, depot):
    symboles = {"creer": "+", "mettre_a_jour": "~", "fermer": "x",
                "inchangee": "=", "promue": "=", "rejet": "!"}
    textes = {"creer": "créer", "mettre_a_jour": "mettre à jour",
              "fermer": "fermer", "inchangee": "inchangée",
              "promue": "déjà promue conventions-style, ignorée",
              "rejet": "non recréée"}
    for a in plan.actions:
        numero = f" #{a.numero}" if a.numero else ""
        detail = f" — {a.commentaire}" if a.genre == "rejet" else ""
        print(f"  {symboles[a.genre]} {textes[a.genre]}{numero} : {a.fichier}{detail}")
    print(f"\n{depot} : {plan.compte('creer')} à créer, "
          f"{plan.compte('mettre_a_jour')} à mettre à jour, "
          f"{plan.compte('fermer')} à fermer, {plan.compte('inchangee')} "
          f"inchangée(s), {plan.compte('promue')} promue(s), "
          f"{plan.compte('rejet')} rejet(s) sans exemption.", file=sys.stderr)


# ------------------------------------------------------------ GitHub (gh)

class ErreurGitHub(Exception):
    pass


def _gh(*args, entree=None):
    try:
        r = subprocess.run(["gh", *args], input=entree, capture_output=True,
                           text=True)
    except OSError as e:
        raise ErreurGitHub(f"gh introuvable : {e}") from e
    if r.returncode != 0:
        raise ErreurGitHub(f"gh {' '.join(args[:3])} : {r.stderr.strip()}")
    return r.stdout


def lire_issues(depot):
    issues = []
    for label in (LABEL_CANDIDAT, LABEL_PROMU):
        brut = _gh("issue", "list", "--repo", depot, "--label", label,
                   "--state", "all", "--limit", "1000", "--json",
                   "number,title,body,state,labels,stateReason")
        for i in json.loads(brut or "[]"):
            issues.append(Issue(
                i["number"], i["title"], i["state"] == "OPEN",
                frozenset(lab["name"] for lab in i.get("labels", [])),
                i.get("body") or "", i.get("stateReason") or ""))
    return issues


def appliquer(plan, depot):
    for label, couleur, description in (
            (LABEL_CANDIDAT, "fbca04", "Candidat brut (ocots-lint) à trier — "
                                       "pas encore un verdict"),
            (LABEL_PROMU, "d93f0b", "Infraction confirmée par un agent "
                                    "après relecture")):
        try:
            _gh("label", "create", label, "--repo", depot, "--color", couleur,
                "--description", description)
        except ErreurGitHub:
            pass    # existe déjà
    for a in plan.actions:
        if a.genre == "creer":
            _gh("issue", "create", "--repo", depot, "--title", titre(a.fichier),
                "--label", LABEL_CANDIDAT, "--body-file", "-", entree=a.corps)
        elif a.genre == "mettre_a_jour":
            _gh("issue", "edit", str(a.numero), "--repo", depot,
                "--body-file", "-", entree=a.corps)
        elif a.genre == "fermer":
            _gh("issue", "comment", str(a.numero), "--repo", depot,
                "--body-file", "-", entree=a.commentaire)
            _gh("issue", "close", str(a.numero), "--repo", depot,
                "--reason", a.raison)


def depot_courant():
    if os.environ.get("GITHUB_REPOSITORY"):
        return os.environ["GITHUB_REPOSITORY"]
    return _gh("repo", "view", "--json", "nameWithOwner",
               "-q", ".nameWithOwner").strip()


# ------------------------------------------------------------------ main

def _options(argv):
    options = {"dry_run": False, "depot": None, "ignore": ".agents-ignore",
               "racines": []}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--dry-run":
            options["dry_run"] = True
        elif a in ("--depot", "--ignore"):
            if i + 1 >= len(argv):
                raise ValueError(f"{a} attend une valeur")
            options[a[2:]] = argv[i + 1]
            i += 1
        elif a.startswith("-"):
            raise ValueError(f"option inconnue : {a}")
        else:
            options["racines"].append(a)
        i += 1
    for r in options["racines"]:
        if not os.path.exists(r):
            raise ValueError(f"chemin inconnu : {r}")
    return options


def main(argv):
    try:
        options = _options(argv)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2

    try:
        trouvailles, avertissements = analyser(options["racines"] or ["."],
                                               sorted(REGLES))
    except Exception as e:  # l'analyse a échoué : ne rien toucher
        print(f"analyse impossible, aucune issue touchée : {e}", file=sys.stderr)
        return 2

    version_conv = (conventions.version("conventions")
                    if os.path.isdir("conventions") else None)
    versions = f"ocots-lint {__version__}" + (
        f", conventions {version_conv}" if version_conv else "")

    try:
        depot = options["depot"] or depot_courant()
        issues = lire_issues(depot)
        plan = planifier(constats_depuis(trouvailles), avertissements, issues,
                         lire_ignores(options["ignore"]), versions)
        afficher(plan, depot)
        for a in avertissements:
            print(f"{a.fichier}:{a.ligne}: [ocots-lint] {a.message}", file=sys.stderr)
        if not options["dry_run"]:
            appliquer(plan, depot)
    except ErreurGitHub as e:
        print(f"GitHub : {e}", file=sys.stderr)
        return 2
    return 0
