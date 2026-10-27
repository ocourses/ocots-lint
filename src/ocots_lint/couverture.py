"""`ocots-lint couverture` — quelles règles sont outillées, et avec quelle garantie.

    ocots-lint couverture                      conventions du cours (./conventions)
    ocots-lint couverture --conventions CHEMIN
    ocots-lint couverture --markdown           tableau à coller dans un rapport
    ocots-lint couverture --support td         seulement les règles applicables aux TD
    ocots-lint couverture --support site       règles des sites (WEB*, hors ocots-lint)

Une absence de trouvaille ne dit rien d'une règle non outillée : ce tableau
dit, règle par règle, ce qu'on peut conclure.

Les règles des sites (`WEB*`, `site.md`) sont vérifiées par le socle
`ocots-site`, pas par cet outil (décision 0008) : elles sont listées « hors
ocots-lint » et comptées à part.

Sortie 2 si l'outil cite une règle que ces conventions ne connaissent pas
(renumérotation, retrait) : ses résultats n'y seraient pas interprétables.
"""

import sys

from ocots_lint import conventions
from ocots_lint.mesures import MESURES
from ocots_lint.regles import REGISTRE

NON_OUTILLEE = "non outillée"
HORS_OUTIL = "hors ocots-lint"
AILLEURS = ("WEB",)   # vérifiées par ocots-site (décision 0008)
SUPPORTS = {
    "commun": ("C",),
    "poly": ("C", "P"),
    "slides": ("C", "SL"),
    "td": ("C", "TD"),
    "exam": ("C", "EX"),
    "site": ("WEB",),
}


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
    chemin, markdown, support, reste = None, False, None, list(argv)
    if "--markdown" in reste:
        markdown = True
        reste.remove("--markdown")
    if "--conventions" in reste:
        i = reste.index("--conventions")
        if i + 1 >= len(reste):
            raise ValueError("--conventions attend un chemin")
        chemin = reste[i + 1]
        del reste[i:i + 2]
    if "--support" in reste:
        i = reste.index("--support")
        if i + 1 >= len(reste):
            raise ValueError(f"--support attend {', '.join(SUPPORTS)}")
        support = reste[i + 1]
        del reste[i:i + 2]
        if support not in SUPPORTS:
            raise ValueError(f"support inconnu : {support} ({', '.join(SUPPORTS)})")
    if reste:
        raise ValueError(f"argument inconnu : {' '.join(reste)}")
    return chemin, markdown, support


def _garanties(regle, table):
    if regle.ident.startswith(AILLEURS):
        return HORS_OUTIL
    return " + ".join(table.get(regle.ident, [])) or NON_OUTILLEE


def main(argv):
    try:
        chemin, markdown, support = _options(argv)
        dossier = conventions.trouver(chemin)
    except (ValueError, conventions.ConventionsIntrouvables) as e:
        print(e, file=sys.stderr)
        return 2

    liste = conventions.regles(dossier)
    if support:
        prefixes = SUPPORTS[support]
        liste = [r for r in liste if r.ident.startswith(prefixes)]
    table = outillage()
    version = conventions.version(dossier) or "version inconnue"

    if markdown:
        print(f"Conventions : `ocots-conventions {version}`\n")
        print("| Règle | Titre | Outillage |")
        print("|---|---|---|")
        for r in liste:
            garanties = _garanties(r, table)
            titre = r.titre.replace("|", "\\|")
            print(f"| [`{r.ident}`]({conventions.lien(dossier, r)}) "
                  f"| {titre} | {garanties} |")
    else:
        print(f"Conventions : ocots-conventions {version} ({dossier})\n")
        for r in liste:
            garanties = _garanties(r, table)
            titre = r.titre if len(r.titre) <= 52 else r.titre[:51] + "…"
            print(f"{r.ident:<5} {titre:<52}  {garanties}")

    ailleurs = sum(1 for r in liste if r.ident.startswith(AILLEURS))
    verifiees = sum(1 for r in liste
                    if set(table.get(r.ident, [])) - {"mesure"})
    mesurees = sum(1 for r in liste if table.get(r.ident) == ["mesure"])
    contexte = f" applicables au support « {support} »" if support else ""
    hors = (f", {ailleurs} hors ocots-lint (site.md, « Vérifié par »)"
            if ailleurs else "")
    print(f"\n{len(liste)} règles{contexte} : {verifiees} vérifiées, "
          f"{mesurees} mesurées seulement, "
          f"{len(liste) - verifiees - mesurees - ailleurs} non outillées{hors}.",
          file=sys.stderr)

    cites = set(table)
    if support:
        cites = {ident for ident in cites if ident.startswith(SUPPORTS[support])}
    absentes = sorted(cites - {r.ident for r in liste})
    if absentes:
        print(f"règles outillées absentes de ces conventions : "
              f"{', '.join(absentes)} — conventions renumérotées ?",
              file=sys.stderr)
        return 2
    return 0
