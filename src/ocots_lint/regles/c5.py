"""C5 — labels et renvois, croisés sur tout le cours (S6, décision 0006)."""

import os

from ocots_lint import labels, prefixes, vocabulaire
from ocots_lint.lecture import sources

# Un label ne se pose que si l'objet est cité (C5, et P12 pour le
# polycopié) : cité **nulle part dans le cours** — polycopié, TD,
# transparents, examens —, il n'ajoute qu'une clé à maintenir. Les renvois
# sont donc lus dans tout le dossier courant (la racine du cours), quel que
# soit le périmètre vérifié : seuls les labels signalés s'y limitent.
#
# Le préfixe fait partie de la clé et nomme l'objet (`thm:` pour un
# théorème) : la table est celle de C5, lue dans les conventions
# (`prefixes.py`). Un alias du template suit sa cible (`mytheorem` →
# `theorem`) ; un objet absent de la table n'est pas vérifié.


def objet_de_table(objet, v):
    """Le nom sous lequel la table de C5 connaît cet objet."""
    if objet is None:
        return None
    e = v.environnements.get(objet)
    if e is not None:
        return e.get("alias_de", objet)
    return objet.rstrip("*")            # figure*, align* : même objet


def prefixe_de(cle):
    return cle.split(":", 1)[0] + ":" if ":" in cle else None


def regle_C5(racines):
    """C5 — label jamais cité dans le cours (P12), ou dont le préfixe ne nomme pas l'objet."""  # noqa: E501
    v = vocabulaire.charger()
    table = prefixes.charger()
    tous, renvois = labels.index_du_cours(v)
    cites = {r.cle for r in renvois}
    perimetre = {os.path.normpath(os.path.relpath(c)) for c in sources(racines)}
    for label in tous:
        if os.path.normpath(label.fichier) not in perimetre:
            continue
        if label.cle not in cites:
            yield label.fichier, label.ligne, (
                f"label {label.cle} jamais cité dans le cours — à retirer tant "
                f"qu'aucun renvoi n'en a besoin")
        attendu = table.get(objet_de_table(label.objet, v))
        ecrit = prefixe_de(label.cle)
        if attendu and ecrit != attendu:
            etat = f"préfixe {ecrit}" if ecrit else "sans préfixe"
            yield label.fichier, label.ligne, (
                f"label {label.cle} ({etat}) sur un {label.objet} — "
                f"C5 veut {attendu}")
