"""C6 — fin de preuve ou d'exemple, et espace collé à un \\footnotetext."""

import re

from ocots_lint.lecture import ligne_de, lire, sans_commentaires, sources

# Le symbole de fin d'une preuve ou d'un exemple est posé à \end{…}. Si la
# boîte se termine par une liste ou une équation hors texte, il passe seul sur
# une nouvelle ligne, sauf \qedhere à l'endroit voulu. Le défaut est silencieux
# (compilation sans avertissement) : il se lit dans la source.
RE_BOITE_QED = re.compile(
    r"\\begin\{(proof|proofend|example\*?)\}(.*?)\\end\{\1\}", re.S)

# Fins de boîte qui rejettent le symbole, et l'ouverture correspondante : le
# \qedhere doit se trouver entre la dernière ouverture et la fin.
FINS_QED = (
    (re.compile(r"\\end\{(?:itemize|enumerate|description)\}\s*$"),
     re.compile(r"\\item\b"), "liste"),
    (re.compile(r"\\\]\s*$"), re.compile(r"\\\["), "équation hors texte"),
    (re.compile(r"\\end\{(align|gather|multline|equation|flalign)\*?\}\s*$"),
     re.compile(r"\\begin\{(?:align|gather|multline|equation|flalign)\*?\}"),
     "équation hors texte"),
)

RE_FOOTNOTETEXT = re.compile(r"\\footnotetext(?:\[[^\]]*\])?\{")
RE_ESPACE_MANUEL = re.compile(r"\\vspace\*?\{[^}]*\}|\\(?:small|med|big)skip\b")


def fin_sans_qedhere(corps):
    """Le genre de fin (« liste »…) si la boîte finit sans \\qedhere, sinon None."""
    corps = corps.rstrip()
    for fin, ouverture, genre in FINS_QED:
        if not fin.search(corps):
            continue
        debuts = list(ouverture.finditer(corps))
        dernier = corps[debuts[-1].start():] if debuts else corps
        return None if "\\qedhere" in dernier else genre
    return None


def accolades(texte, i):
    """Position qui suit le groupe {…} ouvert en texte[i], ou -1."""
    profondeur, j = 0, i
    while j < len(texte):
        c = texte[j]
        if c == "\\":
            j += 2                            # \{ et \} ne comptent pas
            continue
        if c == "{":
            profondeur += 1
        elif c == "}":
            profondeur -= 1
            if profondeur == 0:
                return j + 1
        j += 1
    return -1


def regle_C6(racines):
    """C6 — \\qedhere manquant en fin de liste ou d'équation ; \\vspace qui compense un \\footnotetext."""  # noqa: E501
    for chemin in sources(racines):
        texte = sans_commentaires(lire(chemin))
        for m in RE_BOITE_QED.finditer(texte):
            genre = fin_sans_qedhere(m.group(2))
            if genre:
                yield chemin, ligne_de(texte, m.end()), (
                    f"{m.group(1)} finie par une {genre} sans \\qedhere — "
                    f"le symbole de fin passe seul sur sa ligne")
        # Depuis ocots-latex-template#51, un \footnotetext entre deux boîtes
        # ne double plus l'espace : un \vspace collé à lui compense un défaut
        # disparu, et resserre désormais la page.
        for m in RE_FOOTNOTETEXT.finditer(texte):
            fin = accolades(texte, m.end() - 1)
            if fin < 0:
                continue
            avant = texte[:m.start()].rstrip()
            apres = texte[fin:].lstrip()
            if RE_ESPACE_MANUEL.match(apres) or re.search(
                    r"(?:" + RE_ESPACE_MANUEL.pattern + r")$", avant):
                yield chemin, ligne_de(texte, m.start()), (
                    "espace manuel collé à un \\footnotetext — à retirer "
                    "(ocots-latex-template#51)")
