"""Lecture commune des sources : parcours des fichiers et masques.

Toutes les règles passent par ici. Les masques gardent longueur et retours à
la ligne : une position trouvée dans le texte masqué désigne les mêmes octets
dans l'original, et les numéros de ligne restent justes.

Porté tel quel de `ocots-conventions/bin/verifier` (sprint S1, parité). Les
limites de ces masques par regex sont écrites dans `tests/fixtures/*/limites/`.
"""

import os
import re

SKIP = ("/template/", "/build/", "/conventions/", "/.git/")

BOX = (r"(?:my)?(?:definition|theorem|proposition|corollary|lemma|example"
       r"|remark|assumption|exercisecb|exercise)\*?")


def sources(racines):
    for racine in racines:
        if os.path.isfile(racine):
            yield racine
            continue
        for dossier, _, fichiers in os.walk(racine):
            chemin = dossier + "/"
            if any(s in chemin for s in SKIP):
                continue
            for f in sorted(fichiers):
                if f.endswith(".tex"):
                    yield os.path.join(dossier, f)


def est_transparent(chemin):
    """Vrai si le fichier vit sous un dossier `slides/` — le support
    « transparent » où slides.md#sl4 dispense explicitement des règles
    d'amorce et de reprise du polycopié (P3, P4) : le texte y est
    télégraphique, c'est l'enseignant qui fait la liaison à l'oral."""
    return "slides" in os.path.normpath(chemin).split(os.sep)[:-1]


def lire(chemin):
    with open(chemin, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def ligne_de(texte, position):
    return texte.count("\n", 0, position) + 1


# Un `%` non échappé ouvre un commentaire LaTeX jusqu'à fin de ligne : jamais
# compilé, jamais rendu. Sans ce masque, P2/P5/C4 lisaient le texte brut et
# pouvaient signaler du contenu mort — un `~:` dans une légende commentée
# (C4), ou un `\end{définition}`/`\begin{définition}` commenté qui referme ou
# ouvre une fausse chaîne P2/P5.
RE_COMMENTAIRE = re.compile(r"(?<!\\)%.*$", re.M)


def sans_commentaires(texte):
    """Blanchit les commentaires LaTeX, longueur et retours à la ligne
    conservés."""
    return RE_COMMENTAIRE.sub(lambda m: " " * len(m.group(0)), texte)


# Zones où « ~ » est une espace mathématique et non une décoration : les
# masquer avant tout contrôle de typographie, sinon on propose de « corriger »
# des formules.
ENV_MATH = ("equation", "align", "aligned", "array", "gather", "multline",
            "cases", "split", "eqnarray", "displaymath", "verbatim",
            "lstlisting", "tikzpicture", "pmatrix", "bmatrix", "vmatrix")

RE_MATH = re.compile(
    r"\\begin\{(?:" + "|".join(ENV_MATH) + r")\*?\}.*?\\end\{(?:"
    + "|".join(ENV_MATH) + r")\*?\}"
    r"|\\\[.*?\\\]"
    r"|\\\(.*?\\\)"
    r"|(?<!\\)\$\$.*?(?<!\\)\$\$"
    r"|(?<!\\)\$.*?(?<!\\)\$",
    re.S)


def hors_math(texte):
    """Remplace les zones mathématiques par des blancs de même longueur."""
    def blanchir(m):
        return "".join(c if c == "\n" else " " for c in m.group(0))
    return RE_MATH.sub(blanchir, texte)
