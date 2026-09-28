"""P3 — amorces passe-partout et phrases qui se jettent dans la boîte."""

import re

from ocots_lint.lecture import BOX, est_transparent, hors_math, lire, sources

# L'amorce est passe-partout si la phrase *s'arrête* à l'annonce. Une phrase
# qui commence pareil mais poursuit (« … qui n'est qu'un cas particulier de
# \cite{…}, nous assurant … ») est correcte : elle apporte une information.
RE_PASSE_PARTOUT = re.compile(
    r"(?:nous avons|on a\b|voici|nous donnons|donnons|énonçons|nous énonçons"
    r"|on (?:en )?déduit|nous (?:en )?déduisons|on obtient|nous obtenons"
    r"|introduisons|nous introduisons|on peut (?:donc )?(?:donner|énoncer))"
    r"[^.!?]{0,45}?"
    r"(?:théorème|résultat|proposition|définition|lemme|corollaire|propriété)"
    r"s?\s+suivante?s?\s*[.:]\s*$",
    re.I)

RE_BOITE_OUVRANTE = re.compile(r"^[^\S\n]*\\begin\{(" + BOX + r")\}", re.M)

# Commandes de mise en page ou d'indexation : ce ne sont pas des phrases.
RE_BRUIT = re.compile(
    r"\\(?:index|label|nopagebreak|pagebreak|vspace\*?|hspace\*?)\{[^}]*\}"
    r"|\\(?:clearpage|cleardoublepage|newpage|noindent|bigskip|medskip"
    r"|smallskip|par|leavevmode|reqnomode|leqnomode)\b\*?")


def nettoyer(ligne):
    """Ôte commentaires et commandes de mise en page ; garde la prose."""
    ligne = re.sub(r"(?<!\\)%.*$", "", ligne)
    return RE_BRUIT.sub("", ligne).strip()


def _serrer(xs):
    return re.sub(r"\s+", " ", " ".join(xs))


def regle_P3(racines):
    """P3 — amorces passe-partout et phrases qui se jettent dans la boîte."""
    for chemin in sources(racines):
        if est_transparent(chemin):
            continue  # slides.md#sl4 : P3 ne s'applique pas aux transparents
        brut = lire(chemin)
        texte = hors_math(brut)               # détection hors mode maths…
        lignes, lignes_brutes = texte.split("\n"), brut.split("\n")
        for m in RE_BOITE_OUVRANTE.finditer(texte):
            no = texte.count("\n", 0, m.start())          # index 0
            # dernières lignes utiles avant la boîte
            masquees, reelles = [], []
            i = no - 1
            while i >= 0 and len(masquees) < 4:
                propre = nettoyer(lignes[i])
                if propre:
                    masquees.insert(0, propre)
                    reelles.insert(0, nettoyer(lignes_brutes[i]))
                elif not lignes[i].strip() and masquees:
                    break
                i -= 1
            if not masquees:
                continue                      # P2 couvre déjà l'absence de texte
            derniere = re.split(r"(?<=[.!?])\s+", _serrer(masquees))[-1].strip()
            # Assez de prose pour qu'il y ait une phrase à juger ?
            if len(re.sub(r"[^A-Za-zÀ-ÿ]", "", derniere)) < 15:
                continue
            # …mais on montre le texte réel, maths comprises.
            montre = _serrer(reelles)[-110:]
            if RE_PASSE_PARTOUT.search(derniere):
                yield chemin, no + 1, f"amorce passe-partout : « …{montre} »"
            elif derniere[-1] not in ".!?:;»)]}":
                yield chemin, no + 1, (
                    f"phrase qui se jette dans la boîte : « …{montre} »")
