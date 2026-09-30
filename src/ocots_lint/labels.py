"""Labels et renvois d'un cours, lus dans la source (S6, décision 0006).

    labels, renvois = labels.lire(chemin, vocabulaire.charger())
    index = labels.index_du_cours(vocabulaire.charger())   # tout le cours

Un label est posé par `\\label{clé}`, par l'option `label=clé` d'une boîte
du template, ou par l'ancienne syntaxe (`{titre}{clé}`, `<clé>`), où le
template ajoute un préfixe que publie son vocabulaire (`ancienne_syntaxe`).
Chaque label porte l'**objet** qu'il désigne : la boîte, l'environnement de
maths ou de figure qui le contient, sinon la dernière commande de
sectionnement qui le précède.

Un renvoi est `\\ref`, `\\eqref`, `\\cref`… ou `\\hyperref[clé]` ; une liste
`\\cref{a,b}` donne un renvoi par clé.

Lu sur l'arbre : rien dans un commentaire ni dans un verbatim. Pour un
fichier que l'analyse refuse, repli sur les commentaires retirés, sans objet
(`None`).
"""

import os
import re
from dataclasses import dataclass

from ocots_lint.arbre import lire_arbre
from ocots_lint.lecture import ligne_de, sans_commentaires, sources

RENVOIS = frozenset({"ref", "eqref", "cref", "Cref", "autoref", "pageref",
                     "nameref", "vref", "cpageref", "Cpageref", "labelcref"})
SECTIONNEMENT = frozenset({"part", "chapter", "section", "subsection",
                           "subsubsection", "paragraph"})


@dataclass(frozen=True)
class Label:
    cle: str
    fichier: str
    ligne: int
    objet: str | None       # environnement, ou commande de sectionnement


@dataclass(frozen=True)
class Renvoi:
    cle: str
    fichier: str
    ligne: int
    commande: str


# ------------------------------------------------------------ texte

def _sauter_blancs(texte, i):
    while i < len(texte) and texte[i].isspace():
        i += 1
    return i


def _groupe(texte, i, ouvre="{", ferme="}"):
    """(contenu, position après) du groupe équilibré ouvert en texte[i]
    (blancs sautés), ou (None, i)."""
    i = _sauter_blancs(texte, i)
    if texte[i:i + 1] != ouvre:
        return None, i
    profondeur, j = 0, i
    while j < len(texte):
        c = texte[j]
        if c == "\\":
            j += 2
            continue
        if c == ouvre:
            profondeur += 1
        elif c == ferme:
            profondeur -= 1
            if profondeur == 0:
                return texte[i + 1:j], j + 1
        j += 1
    return None, i


def _options(chaine):
    """{clé: valeur} d'une liste `a=b, c={d,e}` (virgules de premier niveau)."""
    morceaux, profondeur, courant = [], 0, ""
    for c in chaine:
        if c == "," and profondeur == 0:
            morceaux.append(courant)
            courant = ""
            continue
        profondeur += (c == "{") - (c == "}")
        courant += c
    morceaux.append(courant)
    options = {}
    for m in morceaux:
        if "=" in m:
            k, v = m.split("=", 1)
            v = v.strip()
            if v.startswith("{") and v.endswith("}"):
                v = v[1:-1]
            options[k.strip()] = v.strip()
    return options


def _avec_prefixe(cle, syntaxe):
    prefixe = syntaxe["prefixe"]
    if syntaxe.get("sans_doublon") and cle.startswith(prefixe):
        return cle
    return prefixe + cle


# ------------------------------------------------------------ arbre

def _label_de_boite(noeud, texte, v):
    """(clé, décalage de la clé) posée par l'en-tête d'un environnement du
    template, ou None."""
    fin_begin = texte.index("}", noeud.debut) + 1          # \begin{nom}
    i = fin_begin
    options, j = _groupe(texte, i, "[", "]")
    if options is not None:
        cle = _options(options).get("label")
        if cle:
            return cle, texte.index(cle, i)
        i = j
    syntaxe = (v.environnements.get(noeud.nom) or {}).get("ancienne_syntaxe")
    if not syntaxe:
        return None
    if syntaxe["forme"] == "<clé>":
        cle, _ = _groupe(texte, i, "<", ">")
        debut = texte.find("<", i) + 1
    else:                                                   # {titre}{clé}
        titre, j = _groupe(texte, i)
        cle, _ = _groupe(texte, j) if titre is not None else (None, i)
        debut = texte.find("{", j) + 1
    if not cle or not cle.strip():
        return None
    return _avec_prefixe(cle.strip(), syntaxe), debut


def _parcourir(noeuds, texte, v, objet, sortie):
    """Ajoute à `sortie` les (label|renvoi, décalage) de ces nœuds frères.
    `objet` : l'objet englobant, à défaut de sectionnement plus proche."""
    section = objet
    for n in noeuds:
        if n.genre in ("commentaire", "verbatim"):
            continue
        if n.genre == "macro" and n.nom in SECTIONNEMENT:
            section = n.nom
        elif n.genre == "macro" and n.nom == "label":
            cle, _ = _groupe(texte, texte.index("label", n.debut) + 5)
            if cle:
                sortie.append((Label(cle.strip(), None, 0, section), n.debut))
        elif n.genre == "macro" and n.nom in RENVOIS:
            j = _sauter_blancs(texte, n.debut + len(n.nom) + 1)
            if texte[j:j + 1] == "*":
                j += 1
            cles, _ = _groupe(texte, j)
            for cle in (cles or "").split(","):
                if cle.strip():
                    sortie.append((Renvoi(cle.strip(), None, 0, n.nom), n.debut))
        elif n.genre == "macro" and n.nom == "hyperref":
            cle, _ = _groupe(texte, n.debut + len("\\hyperref"), "[", "]")
            if cle:
                sortie.append((Renvoi(cle.strip(), None, 0, "hyperref"), n.debut))
        if n.genre in ("environnement", "maths") and n.nom not in ("inline", "display"):
            interieur = n.nom
            if n.genre == "environnement" and n.nom in v.environnements:
                trouve = _label_de_boite(n, texte, v)
                if trouve:
                    sortie.append((Label(trouve[0], None, 0, n.nom), trouve[1]))
            _parcourir(n.enfants, texte, v, interieur, sortie)
        elif n.genre == "maths":
            _parcourir(n.enfants, texte, v, "equation", sortie)
        else:
            _parcourir(n.arguments, texte, v, section, sortie)
            _parcourir(n.enfants, texte, v, section, sortie)


RE_LABEL = re.compile(r"\\label\{([^}]+)\}")
RE_RENVOI = re.compile(r"\\(" + "|".join(sorted(RENVOIS)) + r")\*?\{([^}]+)\}"
                       r"|\\(hyperref)\[([^\]]+)\]")


def lire(chemin, v):
    """([Label], [Renvoi]) du fichier, dans l'ordre du texte."""
    arbre = lire_arbre(chemin)
    fichier = os.path.relpath(chemin)
    trouves = []
    if arbre.erreur is None:
        _parcourir(arbre.noeuds, arbre.texte, v, None, trouves)
        position = arbre.position
    else:                                   # repli : sans objet
        texte = sans_commentaires(arbre.texte)
        for m in RE_LABEL.finditer(texte):
            trouves.append((Label(m.group(1).strip(), None, 0, None), m.start()))
        for m in RE_RENVOI.finditer(texte):
            commande, cles = (m.group(1), m.group(2)) if m.group(1) else (
                m.group(3), m.group(4))
            for cle in cles.split(","):
                if cle.strip():
                    trouves.append((Renvoi(cle.strip(), None, 0, commande), m.start()))

        def position(decalage):
            return ligne_de(texte, decalage), 0
    labels, renvois = [], []
    for element, decalage in sorted(trouves, key=lambda t: t[1]):
        ligne = position(decalage)[0]
        if isinstance(element, Label):
            labels.append(Label(element.cle, fichier, ligne, element.objet))
        else:
            renvois.append(Renvoi(element.cle, fichier, ligne, element.commande))
    return labels, renvois


def index_du_cours(v, racine="."):
    """(labels, renvois) de tout le cours sous `racine` — le croisement de
    P12 porte sur le cours entier, quel que soit le périmètre vérifié."""
    labels, renvois = [], []
    for chemin in sources([racine]):
        lus, cites = lire(chemin, v)
        labels.extend(lus)
        renvois.extend(cites)
    return labels, renvois
