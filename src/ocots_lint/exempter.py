"""`ocots-lint exempter` — consigner un rejet dans la source, et rien d'autre.

    ocots-lint exempter poly/ch1.tex:42 P2 "la proposition en découle"
    ocots-lint exempter poly/ch1.tex@3f9a0c2e71b84d55:0 P2 "…"   (par empreinte)
    ocots-lint exempter --controler modif.diff                 (ou - pour stdin)

La première forme ajoute **une seule ligne**, un commentaire, au-dessus de la
trouvaille, à la même indentation :

    % ocots-lint: ignore P2 — la proposition en découle

Elle refuse s'il n'y a pas de trouvaille active de cette règle à cet endroit,
si la raison est vide, ou si la ligne est dans un environnement verbatim (le
commentaire y serait imprimé). Après écriture, la trouvaille doit avoir
disparu ; sinon le fichier est restauré.

`--controler` vérifie qu'un diff unifié (`git diff`) ne fait **qu'ajouter des
directives valides** dans des `.tex` : c'est ce qui permet de laisser un agent
de tri exempter sans pouvoir toucher au contenu.

Sorties : 0 si c'est fait (ou si le diff est conforme), 1 si le diff ne l'est
pas, 2 pour une demande invalide.
"""

import os
import re
import sys

from ocots_lint import empreintes
from ocots_lint.exemptions import RE_CONTENU, RE_DIRECTIVE, Exemptions
from ocots_lint.lecture import lire
from ocots_lint.regles import REGLES
from ocots_lint.sorties import Trouvaille

RE_CIBLE_LIGNE = re.compile(r"^(.+):(\d+)$")
RE_CIBLE_EMPREINTE = re.compile(r"^(.+)@([0-9a-f]{16}:\d+)$")
RE_VERBATIM = re.compile(
    r"\\begin\{(verbatim\*?|Verbatim|lstlisting|minted)\}.*?\\end\{\1\}", re.S)


class Refus(Exception):
    pass


def trouvailles_actives(fichier, regle):
    """Trouvailles non exemptées de `regle` dans `fichier`, avec empreintes."""
    exemptions = Exemptions()
    liste = [Trouvaille(regle, os.path.relpath(chemin), ligne, message)
             for chemin, ligne, message in REGLES[regle]([fichier])
             if not exemptions.exempte(chemin, ligne, regle)]
    return empreintes.attribuer(liste)


def localiser(cible, regles):
    """(fichier, ligne) de la trouvaille désignée, active pour chaque règle."""
    m = RE_CIBLE_EMPREINTE.match(cible) or RE_CIBLE_LIGNE.match(cible)
    if not m:
        raise Refus(f"cible illisible : {cible} (attendu FICHIER:LIGNE "
                    f"ou FICHIER@EMPREINTE)")
    fichier = m.group(1)
    if not os.path.isfile(fichier):
        raise Refus(f"fichier introuvable : {fichier}")
    par_empreinte = m.re is RE_CIBLE_EMPREINTE
    ligne = None if par_empreinte else int(m.group(2))

    for regle in regles:
        actives = trouvailles_actives(fichier, regle)
        if par_empreinte:
            trouvee = [t for t in actives if t.empreinte == m.group(2)]
            if trouvee:
                ligne = trouvee[0].ligne
        else:
            trouvee = [t for t in actives if t.ligne == ligne]
        if not trouvee:
            raise Refus(f"aucune trouvaille {regle} active en {cible}")
        if trouvee[0].ligne != ligne:
            raise Refus(f"les règles {', '.join(regles)} ne désignent pas la "
                        f"même ligne en {cible}")
    return fichier, ligne


def dans_verbatim(texte, ligne):
    debut = sum(len(x) + 1 for x in texte.split("\n")[:ligne - 1])
    return any(m.start() < debut < m.end() for m in RE_VERBATIM.finditer(texte))


def exempter(cible, regles, raison):
    """Pose la directive ; renvoie (fichier, ligne de la directive)."""
    inconnues = [r for r in regles if r not in REGLES]
    if inconnues:
        raise Refus(f"règle sans vérificateur : {', '.join(inconnues)}")
    raison = raison.strip()
    if not raison or "\n" in raison:
        raise Refus("la raison est obligatoire, sur une seule ligne")

    fichier, ligne = localiser(cible, regles)
    texte = lire(fichier)
    if dans_verbatim(texte, ligne):
        raise Refus(f"{fichier}:{ligne} est dans un environnement verbatim : "
                    f"un commentaire y serait imprimé")

    lignes = texte.split("\n")
    indentation = re.match(r"[ \t]*", lignes[ligne - 1]).group(0)
    directive = f"{indentation}% ocots-lint: ignore {', '.join(regles)} — {raison}"
    lignes.insert(ligne - 1, directive)
    with open(fichier, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lignes))

    restantes = [r for r in regles
                 if any(t.ligne == ligne + 1 for t in trouvailles_actives(fichier, r))]
    if restantes:
        with open(fichier, "w", encoding="utf-8") as fh:
            fh.write(texte)
        raise Refus(f"la directive n'exempte pas {', '.join(restantes)} en "
                    f"{fichier}:{ligne} — fichier restauré")
    return fichier, ligne


# ------------------------------------------------------------ --controler

def controler(diff):
    """Problèmes [(fichier, message)] d'un diff unifié : tout ce qui n'est pas
    l'ajout d'une directive valide dans un `.tex`."""
    problemes, fichier = [], None
    for ligne in diff.split("\n"):
        if ligne.startswith("diff --git "):
            fichier = ligne.split(" b/", 1)[-1]
            continue
        if ligne.startswith(("new file mode", "deleted file mode", "rename from",
                             "copy from", "old mode", "Binary files")):
            problemes.append((fichier, f"changement de fichier interdit : {ligne}"))
            continue
        if ligne.startswith("+++ "):
            cible = ligne[4:].strip()
            if cible != "/dev/null":
                fichier = cible[2:] if cible.startswith("b/") else cible
            continue
        if ligne.startswith(("--- ", "index ", "@@", "\\ No newline")):
            continue
        if ligne.startswith("-"):
            problemes.append((fichier, f"ligne retirée : {ligne[1:].strip()}"))
        elif ligne.startswith("+"):
            ajout = ligne[1:]
            if not (fichier or "").endswith(".tex"):
                problemes.append((fichier, "fichier autre qu'un .tex"))
                continue
            m = RE_DIRECTIVE.search(ajout)
            if not m or ajout[:m.start()].strip():
                problemes.append((fichier, f"ajout qui n'est pas une directive "
                                           f"seule : {ajout.strip()}"))
            elif not RE_CONTENU.match(m.group(1)):
                problemes.append((fichier, f"directive sans règle ou sans "
                                           f"raison : {ajout.strip()}"))
    return problemes


def main(argv):
    if argv[:1] == ["--controler"]:
        if len(argv) != 2:
            print("usage : ocots-lint exempter --controler DIFF|-", file=sys.stderr)
            return 2
        diff = sys.stdin.read() if argv[1] == "-" else lire(argv[1])
        problemes = controler(diff)
        for fichier, message in problemes:
            print(f"{fichier}: {message}")
        print(f"{len(problemes)} problème(s) : le diff "
              f"{'ne fait pas que' if problemes else 'ne fait que'} poser des "
              f"exemptions.", file=sys.stderr)
        return 1 if problemes else 0

    if len(argv) != 3:
        print('usage : ocots-lint exempter FICHIER:LIGNE|FICHIER@EMPREINTE '
              'RÈGLE[,RÈGLE] "raison"', file=sys.stderr)
        return 2
    cible, regles, raison = argv
    regles = [r.strip() for r in regles.split(",") if r.strip()]
    try:
        fichier, ligne = exempter(cible, regles, raison)
    except Refus as e:
        print(f"refusé : {e}", file=sys.stderr)
        return 2
    print(f"{fichier}:{ligne}: exemption {', '.join(regles)} posée — {raison.strip()}")
    return 0
