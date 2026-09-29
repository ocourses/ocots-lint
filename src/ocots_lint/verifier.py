"""`ocots-lint verifier` — règles mécaniques sur des sources LaTeX.

    ocots-lint verifier            toutes les règles, sur le dépôt courant
    ocots-lint verifier P2         une règle
    ocots-lint verifier P2 poly/   une règle, un périmètre
    ocots-lint verifier --list     les règles implémentées
    ocots-lint verifier --mesure   compte des motifs non bloquants
    ocots-lint verifier --sans-exemptions   ignore les `% ocots-lint: ignore …`
    ocots-lint verifier --format json|sarif|github  sortie pour une CI (défaut : texte)
    ocots-lint verifier --nouvelles origin/main     seulement ce qui est nouveau

Sortie 1 si au moins une infraction est trouvée, 2 pour un argument inconnu,
0 sinon : utilisable en CI.

Sans exemption dans les sources, arguments et sorties sont identiques à
`ocots-conventions/bin/verifier` (parité, jusqu'au sprint S4).
"""

import os
import sys

from ocots_lint import empreintes, reference, sorties, voies
from ocots_lint.arbre import lire_arbre
from ocots_lint.exemptions import Exemptions
from ocots_lint.lecture import sources
from ocots_lint.mesures import MESURES, mesurer
from ocots_lint.regles import REGLES, SUR_ARBRE

FORMATS = ("texte", "json", "sarif", "github")


def extraire_option(argv, nom):
    """(valeur ou None, argv sans l'option) ; accepte `--nom v` et `--nom=v`."""
    reste, valeur, i = [], None, 0
    while i < len(argv):
        a = argv[i]
        if a == nom:
            if i + 1 >= len(argv):
                raise ValueError(f"{nom} attend une valeur")
            valeur, i = argv[i + 1], i + 2
            continue
        if a.startswith(nom + "="):
            valeur = a.split("=", 1)[1]
        else:
            reste.append(a)
        i += 1
    return valeur, reste


def extraire_format(argv):
    """(format, argv sans l'option) ; ValueError si la valeur est inconnue."""
    fmt, reste = extraire_option(argv, "--format")
    fmt = fmt or "texte"
    if fmt not in FORMATS:
        raise ValueError(f"format inconnu : {fmt} ({', '.join(FORMATS)})")
    return fmt, reste


def analyser(racines, noms, exemptions_actives=True):
    """(trouvailles, avertissements) : l'analyse commune à `verifier` et à
    `synchroniser`. Les trouvailles exemptées sont incluses (exemption non
    nulle) ; chacune porte son empreinte et sa voie."""
    exemptions = Exemptions(actives=exemptions_actives)
    resultats = []
    for nom in noms:
        for chemin, ligne, message in REGLES[nom](racines):
            directive = exemptions.exempte(chemin, ligne, nom)
            resultats.append(sorties.Trouvaille(
                nom, os.path.relpath(chemin), ligne, message,
                directive.raison if directive else None))
    resultats = voies.attribuer(empreintes.attribuer(resultats), racines)
    avertissements = [
        sorties.Avertissement(os.path.relpath(chemin), ligne, message)
        for chemin, ligne, message in exemptions.avertissements(sources(racines), noms)]
    avertissements += refus_d_analyse(racines, noms)
    return resultats, avertissements


def refus_d_analyse(racines, noms):
    """Un avertissement par fichier que l'analyse syntaxique refuse, si une
    des règles demandées lit l'arbre : ces règles s'y replient sur les
    masques, ce qui doit se voir (décision 0004)."""
    sur_arbre = sorted(SUR_ARBRE.intersection(noms))
    if not sur_arbre:
        return []
    refus = []
    for chemin in sources(racines):
        a = lire_arbre(chemin)
        if a.erreur is not None:
            ligne, colonne = a.position(a.erreur.debut)
            refus.append(sorties.Avertissement(
                os.path.relpath(chemin), ligne,
                f"analyse syntaxique refusée (colonne {colonne} : "
                f"{a.erreur.message}) — {', '.join(sur_arbre)} lu par les "
                f"masques de secours, avec leurs limites"))
    return refus


def main(argv):
    try:
        fmt, argv = extraire_format(argv)
        nouvelles, argv = extraire_option(argv, "--nouvelles")
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2

    if "--list" in argv:
        print("Règles implémentées :")
        for nom, fn in sorted(REGLES.items()):
            print(f"  {nom}  {fn.__doc__.splitlines()[0]}")
        print("Mesures (--mesure, jamais bloquantes) :")
        for regle, _, message, _ in MESURES:
            print(f"  {regle}  {message}")
        return 0

    if "--mesure" in argv:
        racines = [a for a in argv if not a.startswith("-")] or ["."]
        return mesurer(racines)

    noms = [a for a in argv if a in REGLES]
    racines = [a for a in argv if a not in REGLES and not a.startswith("-")] or ["."]
    inconnues = [a for a in argv
                 if a not in REGLES and not a.startswith("-")
                 and not os.path.exists(a)]
    if inconnues:
        print(f"chemin ou règle inconnu : {', '.join(inconnues)}", file=sys.stderr)
        print(f"règles : {', '.join(sorted(REGLES))}", file=sys.stderr)
        return 2
    if not noms:
        noms = sorted(REGLES)

    resultats, avertissements = analyser(
        racines, noms, exemptions_actives="--sans-exemptions" not in argv)
    if nouvelles:
        try:
            anciennes = reference.empreintes_actives(nouvelles, racines, noms,
                                                     analyser)
        except reference.ErreurReference as e:
            print(e, file=sys.stderr)
            return 2
        resultats = [t for t in resultats
                     if not t.exemption and t.empreinte not in anciennes]

    total = 0
    for nom in noms:
        retenues = [t for t in resultats if t.regle == nom and not t.exemption]
        exemptees = sum(1 for t in resultats if t.regle == nom and t.exemption)
        if fmt == "texte":
            for t in retenues:
                print(f"{t.fichier}:{t.ligne}: [{nom}] {t.message}")
        bilan = f"{nom} : {len(retenues)} infraction(s)"
        if nouvelles:
            bilan += f" nouvelle(s) depuis {nouvelles}"
        if exemptees:
            bilan += f" (+ {exemptees} exemptée(s))"
        print(bilan, file=sys.stderr)
        total += len(retenues)

    if fmt == "json":
        print(sorties.json_(resultats, noms, avertissements))
    elif fmt == "sarif":
        print(sorties.sarif(resultats, noms))
    elif fmt == "github":
        annotations = sorties.github(resultats, noms)
        if annotations:
            print(annotations)

    for a in avertissements:
        print(f"{a.fichier}:{a.ligne}: [ocots-lint] {a.message}", file=sys.stderr)

    return 1 if total else 0
