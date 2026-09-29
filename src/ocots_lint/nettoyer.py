"""`ocots-lint nettoyer` — corrections mécaniques de ocots-conventions.

    ocots-lint nettoyer C4 poly/              aperçu, rien n'est écrit
    ocots-lint nettoyer C4 poly/ --appliquer  écrit les fichiers
    ocots-lint nettoyer --list

À la différence de `verifier`, qui **analyse**, celui-ci **modifie**. Il
n'automatise que les corrections dont l'équivalence a été vérifiée :

  ~:  ->  :        babel-french pose l'espace lui-même (mesuré : « mot: fin »,
                   « mot : fin » et « mot~: fin » font 44.37804pt à l'identique)
  ``…''  ->  \\enquote{…}   les guillemets anglais deviennent français, et
                   suivent lang= (csquotes, autostyle)

**Seule la prose est corrigée** : le texte est lu sur l'arbre syntaxique,
comme par `verifier` pour C4 (S4.3). Maths, commentaires, verbatim (`\\url`,
`\\verb`, `lstlisting`…) et figures TikZ ne sont jamais touchés : `~` est une
espace en mode mathématique, et un remplacement aveugle dans
`\\forall h \\in E ~:~ J'(x) \\cdot h = 0` casserait la formule, comme dans
une URL. Un fichier que l'analyse refuse est lu par les masques de secours,
comme par C4, et l'aperçu le signale.

Par défaut rien n'est écrit : l'aperçu montre chaque remplacement, en contexte.

**Une ligne exemptée pour la règle (`% ocots-lint: ignore C4 — …`) n'est pas
corrigée** : l'exemption dit que la forme est voulue.

Porté de `ocots-conventions/bin/nettoyer` (sprint S2, parité), puis passé
sur l'arbre (S4.3).
"""

import os
import re
import sys

from ocots_lint.arbre import analyser, prose_ou_repli
from ocots_lint.exemptions import Exemptions
from ocots_lint.lecture import sources

RE_TILDE = re.compile(r"~(?=:)")
RE_GUILLEMETS = re.compile(r"``(?!`)(.+?)''", re.S)


def csquotes_disponible(racines):
    """`\\enquote` n'existe que si csquotes est chargé — par le document ou par
    le template. Sans lui, réécrire les guillemets casse la compilation."""
    a_voir = list(racines) + ["template", "../template"]
    motif = re.compile(r"\{csquotes\}|csquotes\}")
    for racine in a_voir:
        if not os.path.exists(racine):
            continue
        for dossier, _, fichiers in os.walk(racine):
            if "/.git/" in dossier + "/":
                continue
            for f in fichiers:
                if not f.endswith((".tex", ".sty", ".cls")):
                    continue
                try:
                    with open(os.path.join(dossier, f), encoding="utf-8",
                              errors="replace") as fh:
                        if motif.search(fh.read()):
                            return True
                except OSError:
                    pass
    return False


def corrections_C4(brut, guillemets=True):
    """typographie : ~: inutiles, guillemets anglais -> \\enquote{…}"""
    masque = prose_ou_repli(analyser(brut))
    trouvailles = []

    for m in RE_TILDE.finditer(masque):
        trouvailles.append((m.start(), m.end(), "", "~: inutile"))

    if guillemets:
        for m in RE_GUILLEMETS.finditer(masque):
            contenu = brut[m.start(1):m.end(1)]
            # Une paire qui enjambe un paragraphe n'en est probablement pas une.
            if "\n\n" in contenu or len(contenu) > 400 or "``" in contenu:
                continue
            trouvailles.append((m.start(), m.end(),
                                "\\enquote{" + contenu + "}", "guillemets"))

    return sorted(trouvailles)


CORRECTIONS = {"C4": corrections_C4}


def contexte(texte, debut, fin, marge=42):
    avant = texte[max(0, debut - marge):debut].replace("\n", " ")
    apres = texte[fin:fin + marge].replace("\n", " ")
    return re.sub(r"\s+", " ", f"…{avant}⟪{texte[debut:fin]}⟫{apres}…")


def appliquer_corrections(brut, trouvailles):
    """Le texte après remplacement, de la fin vers le début."""
    neuf = brut
    for debut, fin, remplacement, _ in reversed(trouvailles):
        neuf = neuf[:debut] + remplacement + neuf[fin:]
    return neuf


def main(argv):
    if "--list" in argv:
        print("Corrections disponibles :")
        for nom, fn in sorted(CORRECTIONS.items()):
            print(f"  {nom}  {fn.__doc__.splitlines()[0]}")
        return 0

    appliquer = "--appliquer" in argv
    argv = [a for a in argv if a != "--appliquer"]
    noms = [a for a in argv if a in CORRECTIONS] or sorted(CORRECTIONS)
    racines = [a for a in argv if a not in CORRECTIONS and not a.startswith("-")]
    if not racines:
        racines = ["."]
    manquants = [r for r in racines if not os.path.exists(r)]
    if manquants:
        print(f"chemin inconnu : {', '.join(manquants)}", file=sys.stderr)
        return 2

    guillemets = csquotes_disponible(racines)
    if not guillemets:
        print("csquotes introuvable : les guillemets ne sont PAS réécrits.\n"
              "  `\\enquote` serait indéfini et le document ne compilerait plus.\n"
              "  Voir le chantier 3 de template.md.\n", file=sys.stderr)

    exemptions = Exemptions()
    total, fichiers_touches = 0, 0
    for chemin in sources(racines):
        with open(chemin, encoding="utf-8") as fh:
            brut = fh.read()

        arbre = analyser(brut)
        if arbre.erreur is not None:
            ligne, colonne = arbre.position(arbre.erreur.debut)
            print(f"{os.path.relpath(chemin)}:{ligne}: analyse syntaxique "
                  f"refusée (colonne {colonne} : {arbre.erreur.message}) — "
                  f"lu par les masques de secours, avec leurs limites",
                  file=sys.stderr)

        trouvailles = []
        for nom in noms:
            trouvailles.extend(
                c for c in CORRECTIONS[nom](brut, guillemets=guillemets)
                if not exemptions.exempte(chemin, brut.count("\n", 0, c[0]) + 1, nom))
        trouvailles.sort()
        if not trouvailles:
            continue

        print(f"\n{os.path.relpath(chemin)} — {len(trouvailles)} correction(s)")
        for debut, fin, _, etiquette in trouvailles[:6]:
            print(f"    {etiquette:12} {contexte(brut, debut, fin)}")
        if len(trouvailles) > 6:
            print(f"    … et {len(trouvailles) - 6} autre(s)")

        if appliquer:
            with open(chemin, "w", encoding="utf-8") as fh:
                fh.write(appliquer_corrections(brut, trouvailles))

        total += len(trouvailles)
        fichiers_touches += 1

    verbe = "appliquée(s)" if appliquer else "possible(s)"
    print(f"\n{total} correction(s) {verbe} dans {fichiers_touches} fichier(s).")
    if total and not appliquer:
        print("Rien n'a été écrit. Relancer avec --appliquer.", file=sys.stderr)
    if appliquer and total:
        print("Recompiler et relire le diff avant de commiter.", file=sys.stderr)
    return 0
