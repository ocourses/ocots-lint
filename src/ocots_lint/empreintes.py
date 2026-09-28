"""Empreinte stable d'une trouvaille : son identité, indépendante du numéro de
ligne.

Une trouvaille est identifiée par sa règle, son fichier et son **contexte** :
la ligne signalée et ses voisines non vides, commentaires retirés et espaces
réduits. Insérer ou retirer des lignes ailleurs dans le fichier ne change pas
l'empreinte ; modifier la ligne signalée ou ses voisines la change — c'est
alors, légitimement, une autre trouvaille.

- Une ligne de commentaire seul est ignorée : poser une exemption au-dessus
  d'une trouvaille (`ocots-lint exempter`) ne change pas son empreinte.
- Deux trouvailles de même règle et de même contexte (deux `~:` sur une même
  ligne) se distinguent par leur rang, dans l'ordre du fichier.

Format : `<16 hex>:<rang>`, par exemple `3f9a0c2e71b84d55:0`. Le préfixe `v1`
du calcul change si la méthode change ; les empreintes d'avant ne se
comparent plus alors à celles d'après.
"""

import hashlib
import re
from dataclasses import replace
from pathlib import PurePath

from ocots_lint.lecture import lire

METHODE = "v1"
RE_COMMENTAIRE = re.compile(r"(?<!\\)%.*$")


def normaliser(ligne):
    """La ligne sans commentaire, espaces réduits : ce qui compte pour LaTeX."""
    return " ".join(RE_COMMENTAIRE.sub("", ligne).split())


def contexte(lignes, no):
    """(précédente, signalée, suivante) normalisées ; `no` commence à 1.
    Les voisines sont les plus proches lignes non vides après normalisation."""
    normalisees = [normaliser(ligne) for ligne in lignes]

    def voisine(indices):
        return next((normalisees[i] for i in indices if normalisees[i]), "")

    i = no - 1
    courante = normalisees[i] if 0 <= i < len(normalisees) else ""
    return (voisine(range(i - 1, -1, -1)), courante,
            voisine(range(i + 1, len(normalisees))))


def cle(regle, fichier, ctx):
    donnees = "\x1f".join((METHODE, regle, PurePath(fichier).as_posix(), *ctx))
    return hashlib.sha256(donnees.encode("utf-8")).hexdigest()[:16]


def attribuer(trouvailles, lire_fichier=lire):
    """Les mêmes trouvailles, chacune avec son `empreinte`, dans le même ordre.

    Le rang se compte parmi les trouvailles de même clé, triées par ligne puis
    par ordre d'émission : il ne dépend pas de l'ordre des règles."""
    lignes_par_fichier = {}
    cles = []
    for t in trouvailles:
        if t.fichier not in lignes_par_fichier:
            lignes_par_fichier[t.fichier] = lire_fichier(t.fichier).split("\n")
        ctx = contexte(lignes_par_fichier[t.fichier], t.ligne)
        cles.append(cle(t.regle, t.fichier, ctx))

    rangs, vus = [0] * len(trouvailles), {}
    for i in sorted(range(len(trouvailles)), key=lambda i: (trouvailles[i].ligne, i)):
        rangs[i] = vus.get(cles[i], 0)
        vus[cles[i]] = rangs[i] + 1

    return [replace(t, empreinte=f"{k}:{r}")
            for t, k, r in zip(trouvailles, cles, rangs, strict=True)]
