"""Lecture des règles de ocots-conventions : identifiants, titres, ancres.

L'outil ne recopie pas la liste des règles : il la lit dans le dépôt des
conventions, à la version épinglée par le cours (`./conventions`).
"""

import os
import re
import subprocess
from dataclasses import dataclass

FICHIERS = ("communes.md", "poly.md", "slides.md", "td.md", "exam.md")
DEPOT = "https://github.com/ocourses/ocots-conventions"

RE_REGLE = re.compile(r"^## ((?:C|P|SL|TD|EX)\d+) — (.+?)\s*$", re.M)


class ConventionsIntrouvables(Exception):
    pass


@dataclass(frozen=True)
class Regle:
    ident: str
    titre: str
    fichier: str

    @property
    def ancre(self):
        return ancre(f"{self.ident} — {self.titre}")


def ancre(titre):
    """Reproduit la fabrication d'ancre de GitHub (comme `bin/liens`)."""
    titre = re.sub(r"`([^`]*)`", r"\1", titre)
    titre = re.sub(r"\*\*?([^*]*)\*\*?", r"\1", titre)
    titre = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", titre)
    titre = "".join(c for c in titre.strip().lower() if c.isalnum() or c in " -_")
    return titre.replace(" ", "-")


def trouver(chemin=None):
    """Le dossier des conventions : celui donné, sinon `./conventions`."""
    dossier = chemin or "conventions"
    if not all(os.path.isfile(os.path.join(dossier, f)) for f in FICHIERS):
        raise ConventionsIntrouvables(
            f"conventions introuvables dans « {dossier} » "
            f"(attendu : {', '.join(FICHIERS)}) — préciser --conventions CHEMIN")
    return dossier


def regles(dossier):
    """Les règles, dans l'ordre des fichiers puis du texte."""
    trouvees = []
    for fichier in FICHIERS:
        with open(os.path.join(dossier, fichier), encoding="utf-8") as fh:
            for m in RE_REGLE.finditer(fh.read()):
                trouvees.append(Regle(m.group(1), m.group(2), fichier))
    return trouvees


def _git(dossier, *args):
    try:
        r = subprocess.run(["git", "-C", dossier, *args],
                           capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return r.stdout.strip() or None


def version(dossier):
    """`git describe` du dossier (`v2.0.0`, `v2.0.0-3-gabc1234`), ou None."""
    return _git(dossier, "describe", "--tags", "--always")


def lien(dossier, regle):
    """URL de la règle sur GitHub, à la révision exacte du dossier."""
    revision = _git(dossier, "rev-parse", "HEAD") or "main"
    return f"{DEPOT}/blob/{revision}/{regle.fichier}#{regle.ancre}"
