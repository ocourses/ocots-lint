"""Exemptions écrites dans la source : une trouvaille justifiée ne bloque plus.

    \\end{theorem} % ocots-lint: ignore P2 — la proposition est un corollaire immédiat
    % ocots-lint: ignore P5, P2 — quatre vrais apartés, relus avec l'auteur
    \\begin{remark}

Une directive en fin de ligne couvre sa propre ligne ; une directive seule
sur sa ligne couvre la ligne suivante. La **raison est obligatoire** : sans
elle, la directive est ignorée et signalée. Une directive qui n'exempte plus
rien est signalée aussi, pour ne pas laisser d'exemption morte.
"""

import re
from dataclasses import dataclass, field

from ocots_lint.lecture import lire

RE_DIRECTIVE = re.compile(r"(?<!\\)%\s*ocots-lint:\s*ignore\b(.*)$")
RE_CONTENU = re.compile(
    r"^\s*([A-Z]{1,2}\d+(?:\s*,\s*[A-Z]{1,2}\d+)*)\s*(?:—|--|-|:)\s*(\S.*)$")
RE_IDENT = re.compile(r"[A-Z]{1,2}\d+")


@dataclass
class Directive:
    ligne: int                  # ligne où la directive est écrite
    couverte: int               # ligne dont elle exempte les trouvailles
    regles: frozenset
    raison: str
    utilisees: set = field(default_factory=set)


def lire_directives(texte):
    """(directives valides, [(ligne, message)] des directives invalides)."""
    valides, invalides = [], []
    for no, ligne in enumerate(texte.split("\n"), start=1):
        m = RE_DIRECTIVE.search(ligne)
        if not m:
            continue
        contenu = RE_CONTENU.match(m.group(1))
        if not contenu:
            invalides.append((no, "exemption sans règle ou sans raison, ignorée — "
                                  "« % ocots-lint: ignore P5 — raison »"))
            continue
        seule = not ligne[:m.start()].strip()
        valides.append(Directive(
            no, no + 1 if seule else no,
            frozenset(RE_IDENT.findall(contenu.group(1))),
            contenu.group(2).strip()))
    return valides, invalides


class Exemptions:
    """Décide, trouvaille par trouvaille, si une directive l'exempte."""

    def __init__(self, actives=True):
        self.actives = actives
        self._fichiers = {}

    def _directives(self, chemin):
        if chemin not in self._fichiers:
            self._fichiers[chemin] = lire_directives(lire(chemin))
        return self._fichiers[chemin]

    def exempte(self, chemin, ligne, regle):
        if not self.actives:
            return False
        for d in self._directives(chemin)[0]:
            if d.couverte == ligne and regle in d.regles:
                d.utilisees.add(regle)
                return True
        return False

    def avertissements(self, chemins, regles_lancees):
        """(chemin, ligne, message) : directives invalides, ou inutiles pour
        les règles lancées (une règle non lancée ne rend rien inutile)."""
        if not self.actives:
            return
        for chemin in chemins:
            valides, invalides = self._directives(chemin)
            for no, message in invalides:
                yield chemin, no, message
            for d in valides:
                for regle in sorted((d.regles & set(regles_lancees)) - d.utilisees):
                    yield chemin, d.ligne, (
                        f"exemption {regle} inutile — plus rien à exempter ici")
