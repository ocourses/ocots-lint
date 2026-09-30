"""C5 — labels et renvois, croisés sur tout le cours (S6, décision 0006)."""

import os

from ocots_lint import labels, vocabulaire
from ocots_lint.lecture import sources

# Un label ne se pose que si l'objet est cité (C5, et P12 pour le
# polycopié) : cité **nulle part dans le cours** — polycopié, TD,
# transparents, examens —, il n'ajoute qu'une clé à maintenir. Les renvois
# sont donc lus dans tout le dossier courant (la racine du cours), quel que
# soit le périmètre vérifié : seuls les labels signalés s'y limitent.


def regle_C5(racines):
    """C5 — label jamais cité dans le cours (P12 : ne poser un label que si l'objet est cité)."""  # noqa: E501
    v = vocabulaire.charger()
    tous, renvois = labels.index_du_cours(v)
    cites = {r.cle for r in renvois}
    perimetre = {os.path.normpath(os.path.relpath(c)) for c in sources(racines)}
    for label in tous:
        if label.cle not in cites and os.path.normpath(label.fichier) in perimetre:
            yield label.fichier, label.ligne, (
                f"label {label.cle} jamais cité dans le cours — à retirer tant "
                f"qu'aucun renvoi n'en a besoin")
