"""C4 — typographie.

Lu sur l'arbre syntaxique (S4.3) : les contrôles portent sur la prose seule
— commentaires, maths (`\\ensuremath` compris), verbatim (`\\verb`, `\\url`,
`lstlisting`, `minted`…) et figures TikZ blanchis. Pour un fichier que
l'analyse refuse, repli sur les masques par regex (`lecture.py`).
"""

import re

from ocots_lint import labels, prefixes, vocabulaire
from ocots_lint.arbre import lire_arbre, prose_ou_repli
from ocots_lint.lecture import ligne_de, sources
from ocots_lint.regles.c5 import prefixe_de

RE_TILDE_DEUX_POINTS = re.compile(r"~:")
RE_GUILLEMETS = re.compile(r"``|\\og\b")
RE_APOSTROPHE = re.compile("\u2019")
RE_RENVOI_BAS_DE_CASSE = re.compile(
    r"(?<!Sous-)\b(théorème|définition|proposition|corollaire|lemme|figure|tableau"
    r"|exemple|section|exercice)[ ~]*\\ref\{")
RE_SOUS = re.compile(r"\bsous (section|espace|ensemble|groupe|suite)\b")

CONTROLES = (
    (RE_TILDE_DEUX_POINTS, "`~:` inutile — babel-french pose l'espace seul"),
    (RE_GUILLEMETS, "guillemets : utiliser \\enquote{…}"),
    (RE_APOSTROPHE, "apostrophe U+2019 — utiliser U+0027"),
    (RE_RENVOI_BAS_DE_CASSE, "renvoi en bas de casse — « Théorème~\\ref{…} »"),
    (RE_SOUS, "mot composé — trait d'union"),
)


# Le mot du renvoi nomme le niveau de la cible, que dit le préfixe du label
# (table de C5, `prefixes.py`) : `Section~\\ref{ssec:…}` est faux. Seul `\\ref`
# écrit le mot ; `\\cref` et `\\autoref` le posent eux-mêmes.
NIVEAUX = {"section": "section", "subsection": "sous-section"}


def _niveaux_par_prefixe():
    table = prefixes.charger()
    return {table[objet]: niveau for objet, niveau in NIVEAUX.items()
            if objet in table}


def _renvois_au_mauvais_niveau(chemin, v, niveaux):
    for r in labels.lire(chemin, v)[1]:
        attendu = niveaux.get(prefixe_de(r.cle))
        if r.niveau and attendu and r.niveau != attendu:
            yield r.ligne, (
                f"renvoi {r.niveau} vers {r.cle} — le label est une {attendu} : "
                f"« {attendu.capitalize()}~\\ref{{…}} »")


def regle_C4(racines):
    """C4 — typographie : ~:, guillemets, apostrophes, renvois, mots composés."""
    v = vocabulaire.charger()
    niveaux = _niveaux_par_prefixe()
    for chemin in sources(racines):
        for ligne, message in _renvois_au_mauvais_niveau(chemin, v, niveaux):
            yield chemin, ligne, message
        texte = prose_ou_repli(lire_arbre(chemin))
        for motif, message in CONTROLES:
            for m in motif.finditer(texte):
                yield chemin, ligne_de(texte, m.start()), message
