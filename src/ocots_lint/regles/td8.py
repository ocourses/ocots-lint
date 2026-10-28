"""TD8 — un corrigé au fil des questions.

Chaque `correction` suit la question qu'elle corrige, **à l'intérieur** de
l'`exercise`, et en est la sœur, pas un environnement imbriqué dedans
(td.md#td8, réécrite par ocots-conventions#26). Deux places se lisent sans
ambiguïté dans l'arbre, d'où la garantie `exact` :

- hors de tout exercice : le corrigé n'est rattaché à aucun énoncé ;
- dans une question ou une sous-question, sans suivre une sous-question
  qu'elle corrigerait : la question est rouverte pour porter son corrigé.
  Le corrigé d'une sous-question vit, lui, dans la question qui la
  contient, juste après elle : il en est la sœur.

Ce qui reste au jugement — la correction qui annonce corriger plusieurs
questions, l'ordre au sein d'un exercice sans question — n'est pas vu.
Vaut pour les TD et les examens (EX6).
"""

from ocots_lint import vocabulaire
from ocots_lint.regles.supports import EXERCICES, arbres, dans_un_exercice


def _precedent(n, freres, texte):
    """Le frère qui précède `n`, blancs et commentaires sautés, ou None."""
    i = next(k for k, f in enumerate(freres) if f is n)
    for f in reversed(freres[:i]):
        if f.genre == "commentaire" or (
                f.genre == "texte" and not texte[f.debut:f.fin].strip()):
            continue
        return f
    return None


def regle_TD8(racines):
    """TD8 — correction hors de tout exercice, ou imbriquée dans une question."""
    v = vocabulaire.charger()

    def est_question(n):
        return (n is not None and n.genre == "environnement"
                and v.famille(n.nom) == vocabulaire.QUESTION)

    for chemin, arbre in arbres(racines, v, EXERCICES):
        for n, ancetres in arbre.avec_ancetres():
            if n.genre != "environnement" or not v.est_corrige(n.nom):
                continue
            ligne = arbre.position(n.debut)[0]
            if ancetres and est_question(ancetres[0]) \
                    and not v.est_corrige(ancetres[0].nom):
                question = ancetres[0]
                # après une sous-question (ou son corrigé) : il en est la sœur
                if est_question(_precedent(n, question.enfants, arbre.texte)):
                    continue
                yield chemin, ligne, (
                    f"{n.nom} dans une {question.nom} — la placer juste après "
                    f"\\end{{{question.nom}}}, en sœur")
            elif dans_un_exercice(ancetres, v) is None:
                yield chemin, ligne, (
                    f"{n.nom} hors de tout exercice — la placer après la "
                    f"question qu'elle corrige, dans l'exercice")
