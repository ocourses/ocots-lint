"""`ocots-lint couverture` — quelles règles sont outillées, et avec quelle garantie.

    ocots-lint couverture                      conventions du cours (./conventions)
    ocots-lint couverture --conventions CHEMIN
    ocots-lint couverture --markdown           tableau à coller dans un rapport

Une absence de trouvaille ne dit rien d'une règle non outillée : ce tableau
dit, règle par règle, ce qu'on peut conclure.

Sortie 2 si l'outil cite une règle que ces conventions ne connaissent pas
(renumérotation, retrait) : ses résultats n'y seraient pas interprétables.
"""

import sys

from ocots_lint import conventions
from ocots_lint.mesures import MESURES
from ocots_lint.regles import REGISTRE

NON_OUTILLEE = "non outillée"


def outillage():
    """{règle: [garanties]} : vérificateurs d'abord, puis mesure s'il y en a."""
    table = {}
    for v in REGISTRE:
        table.setdefault(v.regle, []).append(v.garantie)
    for regle, *_ in MESURES:
        if "mesure" not in table.setdefault(regle, []):
            table[regle].append("mesure")
    return table


def inconnues(regles_connues):
    """Règles citées par l'outil mais absentes des conventions."""
    idents = {r.ident for r in regles_connues}
    return sorted(set(outillage()) - idents)


def _options(argv):
    chemin, markdown, reste = None, False, list(argv)
    if "--markdown" in reste:
        markdown = True
        reste.remove("--markdown")
    if "--conventions" in reste:
        i = reste.index("--conventions")
        if i + 1 >= len(reste):
            raise ValueError("--conventions attend un chemin")
        chemin = reste[i + 1]
        del reste[i:i + 2]
    if reste:
        raise ValueError(f"argument inconnu : {' '.join(reste)}")
    return chemin, markdown


def main(argv):
    try:
        chemin, markdown = _options(argv)
        dossier = conventions.trouver(chemin)
    except (ValueError, conventions.ConventionsIntrouvables) as e:
        print(e, file=sys.stderr)
        return 2

    liste = conventions.regles(dossier)
    table = outillage()
    version = conventions.version(dossier) or "version inconnue"

    if markdown:
        print(f"Conventions : `ocots-conventions {version}`\n")
        print("| Règle | Titre | Outillage |")
        print("|---|---|---|")
        for r in liste:
            garanties = " + ".join(table.get(r.ident, [])) or NON_OUTILLEE
            titre = r.titre.replace("|", "\\|")
            print(f"| [`{r.ident}`]({conventions.lien(dossier, r)}) "
                  f"| {titre} | {garanties} |")
    else:
        print(f"Conventions : ocots-conventions {version} ({dossier})\n")
        for r in liste:
            garanties = " + ".join(table.get(r.ident, [])) or NON_OUTILLEE
            titre = r.titre if len(r.titre) <= 52 else r.titre[:51] + "…"
            print(f"{r.ident:<5} {titre:<52}  {garanties}")

    verifiees = sum(1 for r in liste
                    if set(table.get(r.ident, [])) - {"mesure"})
    mesurees = sum(1 for r in liste if table.get(r.ident) == ["mesure"])
    print(f"\n{len(liste)} règles : {verifiees} vérifiées, {mesurees} mesurées "
          f"seulement, {len(liste) - verifiees - mesurees} non outillées.",
          file=sys.stderr)

    absentes = inconnues(liste)
    if absentes:
        print(f"règles outillées absentes de ces conventions : "
              f"{', '.join(absentes)} — conventions renumérotées ?",
              file=sys.stderr)
        return 2
    return 0
