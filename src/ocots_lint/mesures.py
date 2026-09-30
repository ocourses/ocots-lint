"""Mesures — `verifier --mesure`.

Des motifs sûrs, mais trop répandus aujourd'hui pour bloquer : on les compte
pour suivre leur baisse au fil des relectures, sans faire échouer la CI. Une
mesure devient une règle quand le corpus est propre.
"""

import os
import re
import sys

from ocots_lint import vocabulaire
from ocots_lint.lecture import (
    hors_math,
    ligne_de,
    lire,
    motif,
    sans_commentaires,
    sources,
)
from ocots_lint.regles.c6 import RE_ESPACE_MANUEL


def ancienne_syntaxe(v):
    """`\\begin{theorem}{titre}{label}` : l'ancienne syntaxe des résultats et
    définitions. Pas les alias `my…`, dont c'est la syntaxe normale."""
    noms = {n for n in v.noms("resultat", "definition")
            if "alias_de" not in v.environnements[n]}
    return re.compile(r"\\begin\{" + motif(noms) + r"\}\{")


# (règle, motif, message, cherché hors mode maths ?). Un motif qui dépend du
# vocabulaire du template est une fonction de ce vocabulaire.
MESURES = (
    ("C3", ancienne_syntaxe,
     "ancienne syntaxe {titre}{label} — [title=…, label=…]", False),
    ("C3", re.compile(r"\\emph\{\\textbf\{"),
     "\\emph{\\textbf{…}} — \\keyword{…}", False),
    ("C3", re.compile(r"\{\{[^{}\\$\n]+\}\}"),
     "accolades doublées {{…}}, reste de migration", True),
    ("C4", re.compile(r"^[^\S\n]*\(?(?:i|ii|iii|iv|v|vi)\)[^\S\n]", re.M),
     "étape numérotée à la main — \\newstep[Point i)]", False),
    ("C1", re.compile(r"\bt\.q\."),
     "abréviation « t.q. » — « tel que »", False),
    ("C6", RE_ESPACE_MANUEL,
     "espace vertical manuel", False),
)


def mesurer(racines):
    v = vocabulaire.charger()
    mesures = [(regle, m(v) if callable(m) else m, message, hors_maths)
               for regle, m, message, hors_maths in MESURES]
    comptes = {}
    for chemin in sources(racines):
        brut = sans_commentaires(lire(chemin))
        texte_hors_math = hors_math(brut)
        for regle, motif_, message, hors_maths in mesures:
            texte = texte_hors_math if hors_maths else brut
            for m in motif_.finditer(texte):
                print(f"{os.path.relpath(chemin)}:{ligne_de(texte, m.start())}: "
                      f"[mesure {regle}] {message}")
                comptes[(regle, message)] = comptes.get((regle, message), 0) + 1
    for regle, _, message, _ in MESURES:
        print(f"mesure {regle} : {comptes.get((regle, message), 0):4d}  {message}",
              file=sys.stderr)
    return 0
