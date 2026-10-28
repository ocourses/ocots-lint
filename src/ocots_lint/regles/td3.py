"""TD3 — questions : les environnements, pas la numérotation manuelle.

Trois gestes que td.md#td3 exclut, lus dans l'arbre d'un TD ou d'un sujet :

- un `enumerate` posé directement dans un exercice : il numérote les
  questions à la place de `question` (cas de mesure, 18 dans ses examens) ;
- une ligne d'énoncé qui commence par un numéro saisi à la main
  (« 1) », « 2. », `\\textbf{3.}`) ;
- un titre libre passé à l'exercice (`[Fourier]`) : l'en-tête n'accepte que
  des clés, la citation d'une source va dans le texte d'intro.

Garantie `heuristique` : un `enumerate` dans l'intro d'un exercice peut
lister des données, pas des questions. Un corrigé (`correction`) n'est pas
lu : il peut énumérer ses étapes comme il veut.
"""

import re

from ocots_lint import labels, vocabulaire
from ocots_lint.regles.supports import EXERCICE, EXERCICES, arbres

# Les clés sans valeur de l'en-tête d'un exercice (template, doc/commandes.md).
DRAPEAUX = frozenset({"nosolution"})

RE_NUMERO = re.compile(r"\(?\d{1,2}[.)](?=\s|\})")
RE_NUMERO_GRAS = re.compile(r"\\textbf\s*\{\s*" + RE_NUMERO.pattern + r"\s*\}")


def _en_debut_de_ligne(texte, position):
    return not texte[texte.rfind("\n", 0, position) + 1:position].strip()


def _numeros(n, texte):
    """Les positions des numéros saisis à la main en tête de ligne du nœud."""
    if n.genre == "macro" and n.nom == "textbf":
        if RE_NUMERO_GRAS.match(texte, n.debut) and _en_debut_de_ligne(texte, n.debut):
            yield n.debut
    elif n.genre == "texte":
        for m in RE_NUMERO.finditer(texte, n.debut, n.fin):
            if _en_debut_de_ligne(texte, m.start()):
                yield m.start()


def regle_TD3(racines):
    """TD3 — enumerate pour les questions, numéro saisi à la main, titre libre d'exercice."""  # noqa: E501
    v = vocabulaire.charger()
    for chemin, arbre in arbres(racines, v, EXERCICES):
        texte = arbre.texte
        for n, ancetres in arbre.avec_ancetres():
            parent = ancetres[0] if ancetres else None
            famille = v.famille(parent.nom) if parent is not None else None
            if n.genre == "environnement" and v.famille(n.nom) == EXERCICE:
                options, _ = labels.en_tete(n, texte)
                libres = [e for e in labels.morceaux(options or "")
                          if "=" not in e and e not in DRAPEAUX]
                if libres:      # une citation à virgules : un seul titre
                    yield chemin, arbre.position(n.debut)[0], (
                        f"titre libre « {', '.join(libres)} » passé à {n.nom} "
                        f"— l'en-tête ne prend que des clés ; la source va "
                        f"dans le texte d'intro")
            if famille == EXERCICE and n.genre == "environnement" \
                    and n.nom == "enumerate":
                yield chemin, arbre.position(n.debut)[0], (
                    f"enumerate qui numérote les questions de {parent.nom} — "
                    f"une question par environnement de la famille « question »")
            enonce = famille == EXERCICE or (
                famille == vocabulaire.QUESTION and not v.est_corrige(parent.nom))
            if enonce:
                for position in _numeros(n, texte):
                    yield chemin, arbre.position(position)[0], (
                        "numéro de question saisi à la main — utiliser les "
                        "environnements de la famille « question »")
