"""Instantanés du corpus : figer les trouvailles d'un cours, puis vérifier
qu'elles n'ont pas bougé (S4.0). Outil de mainteneur, hors de la CLI.

    python -m ocots_lint.instantane figer mesure ~/cours/mesure [RÉF]
    python -m ocots_lint.instantane verifier
    python -m ocots_lint.instantane verifier --dossier autre/

`figer` extrait la révision RÉF (défaut : HEAD) du dépôt par `git archive` —
la copie de travail n'est jamais lue ni touchée —, l'analyse avec le code
courant, et écrit `corpus/<nom>.json` : la sortie `verifier --format json`,
plus le dépôt, le commit exact et la version de l'outil.

`verifier` refait l'analyse sur le commit enregistré de chaque instantané,
et compare par empreinte (`comparer`) **toutes** les trouvailles, exemptées
comprises : apparues, disparues, et **modifiées** — même empreinte, mais
ligne, message ou exemption différents. Les avertissements (exemptions
inutiles ou invalides…) sont comparés aussi.

`corpus/` est ignoré par git : les instantanés des cours privés citent leur
texte (messages de P3) et restent sur la machine du mainteneur.

Les sous-modules du cours (`template/`, `conventions/`) sont extraits à leur
commit épinglé, s'ils sont initialisés dans le dépôt (S5.0) : l'analyse voit
le même template que le cours — la voie des guillemets (C4) en dépend, et le
vocabulaire des boîtes en dépendra. L'instantané note, pour chaque
sous-module, le commit extrait ou son absence ; `verifier` signale un
sous-module qui n'est plus extrait comme au figeage. La voie de chaque
trouvaille est comparée.

Sorties : 0 si rien n'a bougé, 1 sinon, 2 pour une demande invalide.
"""

import json
import os
import sys
from pathlib import Path

from ocots_lint import __version__, comparer, sorties
from ocots_lint.reference import ErreurReference, _git, dans, extraire, sous_modules
from ocots_lint.regles import REGLES
from ocots_lint.verifier import analyser

DOSSIER = "corpus"


def extraits(depot, commit):
    """{chemin: commit extrait, ou None s'il ne l'est pas} des sous-modules."""
    return {chemin: sha if dispo else None
            for chemin, sha, dispo in sous_modules(commit, depot=depot)}


def analyser_revision(depot, commit):
    """Le document JSON de `verifier` pour `depot` à `commit`."""
    noms = sorted(REGLES)
    with extraire(commit, depot=depot) as base, dans(base):
        trouvailles, avertissements = analyser(["."], noms)
        return json.loads(sorties.json_(trouvailles, noms, avertissements))


def figer(nom, depot, ref="HEAD", dossier=DOSSIER):
    """Écrit `dossier/nom.json` ; renvoie son chemin et le document."""
    depot = os.path.abspath(os.path.expanduser(depot))
    commit = _git("rev-parse", "--verify", f"{ref}^{{commit}}", dossier=depot)
    doc = analyser_revision(depot, commit)
    doc["corpus"] = {"nom": nom, "depot": depot, "commit": commit,
                     "ocots_lint": __version__,
                     "sous_modules": extraits(depot, commit)}
    os.makedirs(dossier, exist_ok=True)
    chemin = Path(dossier) / f"{nom}.json"
    chemin.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    return chemin, doc


def _identite(t):
    return t["ligne"], t["message"], t.get("exemption"), t.get("voie")


def _avertissements(doc):
    return {(a["fichier"], a["ligne"], a["message"]) for a in doc["avertissements"]}


def ecart(avant, apres):
    """L'écart de `comparer` sur toutes les trouvailles (exemptées
    comprises), plus les trouvailles modifiées — même empreinte, ligne,
    message ou exemption différents — et les avertissements."""
    a = {t["empreinte"]: t for t in avant["trouvailles"]}
    b = {t["empreinte"]: t for t in apres["trouvailles"]}
    resultat = comparer.comparer((a, True), (b, True))
    resultat["modifiees"] = sorted(
        ({"avant": a[k], "apres": b[k]} for k in a.keys() & b.keys()
         if _identite(a[k]) != _identite(b[k])),
        key=lambda m: (m["apres"]["fichier"], m["apres"]["ligne"]))
    resultat["inchangees"] -= len(resultat["modifiees"])
    av, ap = _avertissements(avant), _avertissements(apres)
    resultat["avertissements"] = {"apparus": sorted(ap - av),
                                  "disparus": sorted(av - ap)}
    return resultat


def bouge(e):
    return bool(e["apparues"] or e["disparues"] or e["modifiees"]
                or e["avertissements"]["apparus"] or e["avertissements"]["disparus"]
                or e.get("sous_modules"))


def verifier(dossier=DOSSIER):
    """(code de sortie, [(nom, méta, écart)]) pour chaque instantané du dossier."""
    fichiers = sorted(Path(dossier).glob("*.json"))
    if not fichiers:
        raise ErreurReference(f"aucun instantané dans {dossier}/ — "
                              f"commencer par `figer`")
    resultats = []
    for f in fichiers:
        fige = json.loads(f.read_text(encoding="utf-8"))
        meta = fige["corpus"]
        actuel = analyser_revision(meta["depot"], meta["commit"])
        e = ecart(fige, actuel)
        avant, maintenant = meta.get("sous_modules", {}), extraits(meta["depot"],
                                                                   meta["commit"])
        if avant != maintenant:
            e["sous_modules"] = {"avant": avant, "apres": maintenant}
        resultats.append((meta["nom"], meta, e))
    return (1 if any(bouge(e) for _, _, e in resultats) else 0), resultats


def _afficher(nom, meta, e):
    etat = "a bougé" if bouge(e) else "inchangé"
    print(f"{nom} ({meta['commit'][:7]}, figé avec ocots-lint "
          f"{meta['ocots_lint']}) : {etat} — {e['inchangees']} inchangée(s)")
    for signe, cle in (("+", "apparues"), ("-", "disparues")):
        for t in e[cle]:
            exemptee = " (exemptée)" if t.get("exemption") else ""
            print(f"  {signe} {t['fichier']}:{t['ligne']}: [{t['regle']}] "
                  f"{t['message']}{exemptee}")
    for m in e["modifiees"]:
        a, b = m["avant"], m["apres"]
        print(f"  ~ {b['fichier']}:{a['ligne']}→{b['ligne']}: [{b['regle']}] "
              f"{_identite(a)[1:]!r} → {_identite(b)[1:]!r}")
    for signe, cle in (("+", "apparus"), ("-", "disparus")):
        for fichier, ligne, message in e["avertissements"][cle]:
            print(f"  {signe} {fichier}:{ligne}: [avertissement] {message}")
    if "sous_modules" in e:
        avant, apres = e["sous_modules"]["avant"], e["sous_modules"]["apres"]
        for chemin in sorted(avant.keys() | apres.keys()):
            a, b = avant.get(chemin), apres.get(chemin)
            if a != b:
                print(f"  ! sous-module {chemin} : {_court(a)} au figeage, "
                      f"{_court(b)} maintenant — refiger, ou l'initialiser")


def _court(sha):
    return sha[:7] if sha else "non extrait"


USAGE = ("usage : python -m ocots_lint.instantane figer NOM DÉPÔT [RÉF] "
         "[--dossier D]\n"
         "        python -m ocots_lint.instantane verifier [--dossier D]")


def main(argv):
    dossier = DOSSIER
    if "--dossier" in argv:
        i = argv.index("--dossier")
        if i + 1 >= len(argv):
            print(USAGE, file=sys.stderr)
            return 2
        dossier = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    try:
        if argv[:1] == ["figer"] and len(argv) in (3, 4):
            chemin, doc = figer(*argv[1:], dossier=dossier)
            print(f"{chemin} : {len(doc['trouvailles'])} trouvaille(s) au commit "
                  f"{doc['corpus']['commit'][:7]}")
            return 0
        if argv == ["verifier"]:
            code, resultats = verifier(dossier)
            for nom, meta, e in resultats:
                _afficher(nom, meta, e)
            return code
    except ErreurReference as e:
        print(e, file=sys.stderr)
        return 2
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
