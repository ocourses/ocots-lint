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

# Préfixes de chemins exclus par le cours, relatifs à sa racine (le dossier
# courant) : un document rangé (`attic/`, `archived/`) ne produit plus de
# trouvailles. Le même fichier sert à `synchroniser` et aux détecteurs de
# `ocourses/agents`.
AGENTS_IGNORE = ".agents-ignore"


def lire_ignores(chemin=AGENTS_IGNORE):
    """Préfixes de `.agents-ignore` (lignes non vides, `#` commente)."""
    if not chemin or not os.path.isfile(chemin):
        return []
    with open(chemin, encoding="utf-8") as fh:
        return [ligne.strip() for ligne in fh
                if ligne.strip() and not ligne.strip().startswith("#")]


def est_ignore(fichier, ignores):
    return any(fichier.startswith(p) for p in ignores)



def motif(noms):
    """Une alternative regex qui reconnaît exactement ces noms
    d'environnement (les plus longs d'abord : `remark*` avant `remark`)."""
    return "(?:" + "|".join(re.escape(n) for n in
                            sorted(noms, key=lambda n: (-len(n), n))) + ")"


def _relatif(chemin):
    return os.path.normpath(os.path.relpath(chemin)).replace(os.sep, "/")


def sources(racines):
    """Les `.tex` des racines. Le parcours d'un dossier saute `SKIP` et les
    préfixes de `.agents-ignore` ; ce qu'on désigne explicitement (un
    fichier, ou un dossier lui-même exclu) reste lu."""
    ignores = lire_ignores()
    for racine in racines:
        if os.path.isfile(racine):
            yield racine
            continue
        filtre = ignores and not est_ignore(_relatif(racine) + "/", ignores)
        for dossier, _, fichiers in os.walk(racine):
            chemin = dossier + "/"
            if any(s in chemin for s in SKIP):
                continue
            for f in sorted(fichiers):
                if f.endswith(".tex"):
                    complet = os.path.join(dossier, f)
                    if filtre and est_ignore(_relatif(complet), ignores):
                        continue
                    yield complet


RE_CLASSE = re.compile(r"^[^%\n]*?\\documentclass(?:\[[^\]]*\])?\{([^}]+)\}", re.M)

# Le support « diapositives » du vocabulaire du template.
DIAPOSITIVES = "slides"


def est_transparent(chemin, texte, v):
    """Vrai si le fichier est un transparent — le support où slides.md#sl4
    dispense explicitement des règles d'amorce et de reprise du polycopié
    (P3, P4) : le texte y est télégraphique, c'est l'enseignant qui fait la
    liaison à l'oral.

    Un fichier qui déclare sa classe (`\\documentclass{beamer}`) est reconnu
    par elle, selon les supports du vocabulaire du template (S5.4), où qu'il
    soit rangé. Un fichier sans classe — un chapitre inclus par un fichier
    principal — l'est par son dossier : sous `slides/`."""
    m = RE_CLASSE.search(texte)
    if m:
        return v.support(m.group(1).strip()) == DIAPOSITIVES
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
