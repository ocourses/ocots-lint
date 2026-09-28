"""`ocots-lint verifier` — règles mécaniques sur des sources LaTeX.

    ocots-lint verifier            toutes les règles, sur le dépôt courant
    ocots-lint verifier P2         une règle
    ocots-lint verifier P2 poly/   une règle, un périmètre
    ocots-lint verifier --list     les règles implémentées
    ocots-lint verifier --mesure   compte des motifs non bloquants
    ocots-lint verifier --sans-exemptions   ignore les `% ocots-lint: ignore …`
    ocots-lint verifier --format json|sarif|github  sortie pour une CI (défaut : texte)

Sortie 1 si au moins une infraction est trouvée, 2 pour un argument inconnu,
0 sinon : utilisable en CI.

Sans exemption dans les sources, arguments et sorties sont identiques à
`ocots-conventions/bin/verifier` (parité, jusqu'au sprint S4).
"""

import os
import sys

from ocots_lint import empreintes, sorties
from ocots_lint.exemptions import Exemptions
from ocots_lint.lecture import sources
from ocots_lint.mesures import MESURES, mesurer
from ocots_lint.regles import REGLES

FORMATS = ("texte", "json", "sarif", "github")


def extraire_format(argv):
    """(format, argv sans l'option) ; ValueError si la valeur est inconnue."""
    reste, fmt, i = [], "texte", 0
    while i < len(argv):
        a = argv[i]
        if a == "--format":
            if i + 1 >= len(argv):
                raise ValueError("--format attend une valeur")
            fmt, i = argv[i + 1], i + 2
            continue
        if a.startswith("--format="):
            fmt = a.split("=", 1)[1]
        else:
            reste.append(a)
        i += 1
    if fmt not in FORMATS:
        raise ValueError(f"format inconnu : {fmt} ({', '.join(FORMATS)})")
    return fmt, reste


def main(argv):
    try:
        fmt, argv = extraire_format(argv)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2

    if "--list" in argv:
        print("Règles implémentées :")
        for nom, fn in sorted(REGLES.items()):
            print(f"  {nom}  {fn.__doc__.splitlines()[0]}")
        print("Mesures (--mesure, jamais bloquantes) :")
        for regle, _, message, _ in MESURES:
            print(f"  {regle}  {message}")
        return 0

    if "--mesure" in argv:
        racines = [a for a in argv if not a.startswith("-")] or ["."]
        return mesurer(racines)

    noms = [a for a in argv if a in REGLES]
    racines = [a for a in argv if a not in REGLES and not a.startswith("-")] or ["."]
    inconnues = [a for a in argv
                 if a not in REGLES and not a.startswith("-")
                 and not os.path.exists(a)]
    if inconnues:
        print(f"chemin ou règle inconnu : {', '.join(inconnues)}", file=sys.stderr)
        print(f"règles : {', '.join(sorted(REGLES))}", file=sys.stderr)
        return 2
    if not noms:
        noms = sorted(REGLES)

    exemptions = Exemptions(actives="--sans-exemptions" not in argv)
    resultats = []
    for nom in noms:
        for chemin, ligne, message in REGLES[nom](racines):
            directive = exemptions.exempte(chemin, ligne, nom)
            resultats.append(sorties.Trouvaille(
                nom, os.path.relpath(chemin), ligne, message,
                directive.raison if directive else None))
    resultats = empreintes.attribuer(resultats)
    avertissements = [
        sorties.Avertissement(os.path.relpath(chemin), ligne, message)
        for chemin, ligne, message in exemptions.avertissements(sources(racines), noms)]

    total = 0
    for nom in noms:
        retenues = [t for t in resultats if t.regle == nom and not t.exemption]
        exemptees = sum(1 for t in resultats if t.regle == nom and t.exemption)
        if fmt == "texte":
            for t in retenues:
                print(f"{t.fichier}:{t.ligne}: [{nom}] {t.message}")
        bilan = f"{nom} : {len(retenues)} infraction(s)"
        if exemptees:
            bilan += f" (+ {exemptees} exemptée(s))"
        print(bilan, file=sys.stderr)
        total += len(retenues)

    if fmt == "json":
        print(sorties.json_(resultats, noms, avertissements))
    elif fmt == "sarif":
        print(sorties.sarif(resultats, noms))
    elif fmt == "github":
        annotations = sorties.github(resultats, noms)
        if annotations:
            print(annotations)

    for a in avertissements:
        print(f"{a.fichier}:{a.ligne}: [ocots-lint] {a.message}", file=sys.stderr)

    return 1 if total else 0
