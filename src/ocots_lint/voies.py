"""Voie d'une trouvaille : qui doit s'en occuper (S3.6).

- `mecanique` : `nettoyer` sait la corriger, à cette ligne, dans ce document
  (les guillemets seulement si `csquotes` est chargé). Aucun modèle.
- `correction` : la garantie est `exact` ; il n'y a rien à trier, seulement
  à corriger.
- `tri` : garantie `heuristique` ou `signal` ; un jugement est nécessaire.

On ne paie un modèle que pour la voie `tri`.
"""

from dataclasses import replace

from ocots_lint import nettoyer
from ocots_lint.lecture import lire
from ocots_lint.regles import REGISTRE

VOIES = ("mecanique", "correction", "tri")

# Message de verifier -> étiquette de la correction de nettoyer.
CORRIGEABLES = {
    ("C4", "`~:` inutile"): "~: inutile",
    ("C4", "guillemets"): "guillemets",
}


def _etiquette(trouvaille):
    for (regle, debut), etiquette in CORRIGEABLES.items():
        if trouvaille.regle == regle and trouvaille.message.startswith(debut):
            return etiquette
    return None


def _corrections_par_ligne(fichier, guillemets):
    """{ligne: {étiquettes}} des corrections que nettoyer ferait."""
    texte = lire(fichier)
    table = {}
    for corriger in nettoyer.CORRECTIONS.values():
        for debut, _, _, etiquette in corriger(texte, guillemets=guillemets):
            table.setdefault(texte.count("\n", 0, debut) + 1, set()).add(etiquette)
    return table


def attribuer(trouvailles, racines):
    """Les mêmes trouvailles, chacune avec sa `voie`."""
    garanties = {v.regle: v.garantie for v in REGISTRE}
    guillemets = None
    corrections = {}
    resultat = []
    for t in trouvailles:
        voie = "correction" if garanties.get(t.regle) == "exact" else "tri"
        etiquette = _etiquette(t)
        if etiquette:
            if guillemets is None:
                guillemets = nettoyer.csquotes_disponible(racines)
            if t.fichier not in corrections:
                corrections[t.fichier] = _corrections_par_ligne(t.fichier, guillemets)
            if etiquette in corrections[t.fichier].get(t.ligne, ()):
                voie = "mecanique"
        resultat.append(replace(t, voie=voie))
    return resultat
