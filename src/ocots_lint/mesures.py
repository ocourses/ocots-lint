"""Mesures — `verifier --mesure`.

Des motifs sûrs, mais trop répandus aujourd'hui pour bloquer : on les compte
pour suivre leur baisse au fil des relectures, sans faire échouer la CI. Une
mesure devient une règle quand le corpus est propre.
"""

import os
import re
import sys

from ocots_lint.lecture import hors_math, ligne_de, lire, sans_commentaires, sources
from ocots_lint.regles.c6 import RE_ESPACE_MANUEL

# (règle, motif, message, cherché hors mode maths ?)
MESURES = (
    ("C3", re.compile(r"\\begin\{(?:definition|theorem|proposition|corollary"
                      r"|lemma|conjecture)\}\{"),
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
    comptes = {}
    for chemin in sources(racines):
        brut = sans_commentaires(lire(chemin))
        texte_hors_math = hors_math(brut)
        for regle, motif, message, hors_maths in MESURES:
            texte = texte_hors_math if hors_maths else brut
            for m in motif.finditer(texte):
                print(f"{os.path.relpath(chemin)}:{ligne_de(texte, m.start())}: "
                      f"[mesure {regle}] {message}")
                comptes[(regle, message)] = comptes.get((regle, message), 0) + 1
    for regle, _, message, _ in MESURES:
        print(f"mesure {regle} : {comptes.get((regle, message), 0):4d}  {message}",
              file=sys.stderr)
    return 0
