"""`ocots-lint verifier` — règles mécaniques sur des sources LaTeX.

    ocots-lint verifier            toutes les règles, sur le dépôt courant
    ocots-lint verifier P2         une règle
    ocots-lint verifier P2 poly/   une règle, un périmètre
    ocots-lint verifier --list     les règles implémentées
    ocots-lint verifier --mesure   compte des motifs non bloquants
    ocots-lint verifier --sans-exemptions   ignore les `% ocots-lint: ignore …`

Sortie 1 si au moins une infraction est trouvée, 2 pour un argument inconnu,
0 sinon : utilisable en CI.

Sans exemption dans les sources, arguments et sorties sont identiques à
`ocots-conventions/bin/verifier` (parité, jusqu'au sprint S3).
"""

import os
import sys

from ocots_lint.exemptions import Exemptions
from ocots_lint.lecture import sources
from ocots_lint.mesures import MESURES, mesurer
from ocots_lint.regles import REGLES


def main(argv):
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
    total = 0
    for nom in noms:
        trouvailles, exemptees = [], 0
        for chemin, ligne, message in REGLES[nom](racines):
            if exemptions.exempte(chemin, ligne, nom):
                exemptees += 1
            else:
                trouvailles.append((chemin, ligne, message))
        for chemin, ligne, message in trouvailles:
            print(f"{os.path.relpath(chemin)}:{ligne}: [{nom}] {message}")
        bilan = f"{nom} : {len(trouvailles)} infraction(s)"
        if exemptees:
            bilan += f" (+ {exemptees} exemptée(s))"
        print(bilan, file=sys.stderr)
        total += len(trouvailles)

    for chemin, ligne, message in exemptions.avertissements(sources(racines), noms):
        print(f"{os.path.relpath(chemin)}:{ligne}: [ocots-lint] {message}",
              file=sys.stderr)

    return 1 if total else 0
