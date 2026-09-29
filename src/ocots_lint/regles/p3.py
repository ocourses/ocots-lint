"""P3 — amorces passe-partout et phrases qui se jettent dans la boîte.

Lu sur l'arbre syntaxique (S4.5) : la phrase qui précède une boîte est
cherchée dans la prose (`arbre.prose`), maths, commentaires et verbatim
blanchis. Une formule hors texte **ponctuée** termine la phrase qui
l'introduit : sa ponctuation finale est reportée à sa place, et « … définie
par \\[ f(x) = 0. \\] » n'est plus une phrase qui se jette dans la boîte.
Une formule non ponctuée reste transparente, comme avant. Pour un fichier
que l'analyse refuse, repli sur les masques par regex.
"""

import re

from ocots_lint.arbre import lire_arbre, prose
from ocots_lint.lecture import BOX, est_transparent, hors_math, sources

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


PONCTUATION = ".,;:!?"

# Ce qui peut suivre la ponctuation d'une formule sans rien dire : blancs,
# `\\`, petites espaces, `\quad`, étiquettes.
RE_QUEUE = re.compile(
    r"(?:\s|\\\\(?:\[[^]]*\])?|\\[,;:! ]|\\q?quad\b|\\(?:nonumber|notag)\b"
    r"|\\label\{[^}]*\})+$")
RE_TEXTE_PONCTUE = re.compile(r"\\(?:text|mbox|textrm)\{\s*([.,;:!?])\s*\}$")
RE_DELIMITEURS = re.compile(r"^(?:\\\[|\$\$|\\begin\{[^}]*\})"
                            r"|(?:\\\]|\$\$|\\end\{[^}]*\})$")


def ponctuation_finale(source):
    """La ponctuation qui termine une formule hors texte, ou None."""
    corps = RE_QUEUE.sub("", RE_DELIMITEURS.sub("", source.strip()))
    m = RE_TEXTE_PONCTUE.search(corps)
    if m:
        return m.group(1)
    return corps[-1] if corps and corps[-1] in PONCTUATION else None


def _hors_texte(noeuds):
    """Les formules hors texte, sans descendre dans ce qui n'est pas de la
    prose (une formule dans une formule ne termine pas de phrase)."""
    for n in noeuds:
        if n.genre == "maths":
            if n.nom not in ("inline", "ensuremath"):
                yield n
        elif n.genre not in ("commentaire", "verbatim"):
            yield from _hors_texte(n.arguments)
            yield from _hors_texte(n.enfants)


def texte_p3(arbre):
    """La prose, où chaque formule hors texte ponctuée laisse sa
    ponctuation à la place de son premier caractère ; le masque des maths
    pour un fichier refusé.

    Au premier caractère, et non au dernier : en remontant depuis la boîte,
    les lignes blanchies de la formule ne coupent rien tant qu'aucune prose
    n'est lue, et la ponctuation se lit collée à la phrase qu'elle termine,
    sur la ligne où la formule s'ouvre."""
    if arbre.erreur is not None:
        return hors_math(arbre.texte)
    texte = list(prose(arbre))
    for n in _hors_texte(arbre.noeuds):
        p = ponctuation_finale(arbre.texte[n.debut:n.fin])
        if p:
            texte[n.debut] = p
    return "".join(texte)


def _serrer(xs):
    return re.sub(r"\s+", " ", " ".join(xs))


def regle_P3(racines):
    """P3 — amorces passe-partout et phrases qui se jettent dans la boîte."""
    for chemin in sources(racines):
        if est_transparent(chemin):
            continue  # slides.md#sl4 : P3 ne s'applique pas aux transparents
        arbre = lire_arbre(chemin)
        brut = arbre.texte
        texte = texte_p3(arbre)               # détection dans la prose…
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
