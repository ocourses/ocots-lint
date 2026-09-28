"""Point d'entrée `ocots-lint <commande> …`.

Chaque commande reçoit ses arguments tels quels : `ocots-lint verifier …` se
comporte exactement comme `conventions/bin/verifier …` (parité, sprint S1).
"""

import sys

from ocots_lint import __version__, verifier

COMMANDES = {
    "verifier": (verifier.main, "règles mécaniques sur des sources LaTeX"),
}

AIDE = """\
usage : ocots-lint <commande> [arguments]

Commandes :
{commandes}

  ocots-lint verifier            toutes les règles, sur le dépôt courant
  ocots-lint verifier P2 poly/   une règle, un périmètre
  ocots-lint verifier --list     les règles implémentées
  ocots-lint verifier --mesure   compte des motifs non bloquants
  ocots-lint --version
"""


def aide():
    lignes = [f"  {nom:<10} {doc}" for nom, (_, doc) in COMMANDES.items()]
    return AIDE.format(commandes="\n".join(lignes))


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] in ("-h", "--help", "aide"):
        print(aide())
        return 0
    if argv[0] == "--version":
        print(f"ocots-lint {__version__}")
        return 0
    commande = COMMANDES.get(argv[0])
    if commande is None:
        print(f"commande inconnue : {argv[0]}\n", file=sys.stderr)
        print(aide(), file=sys.stderr)
        return 2
    return commande[0](argv[1:])
