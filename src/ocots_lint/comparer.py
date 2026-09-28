"""`ocots-lint comparer` — ce qui apparaît et disparaît entre deux analyses (S3.9).

    ocots-lint comparer avant.json apres.json
    ocots-lint comparer avant.json apres.json --format json

Les deux fichiers sont des sorties de `verifier --format json`. Recettes :

    # deux versions de l'outil, sur le même cours (avant une montée de version)
    OL=git+https://github.com/ocourses/ocots-lint
    uvx --from $OL@v0.3.0 ocots-lint verifier --format json > avant.json
    uvx --from $OL@v0.4.0 ocots-lint verifier --format json > apres.json

    # deux révisions du cours, avec la même version
    git stash; ocots-lint verifier --format json > avant.json; git stash pop
    ocots-lint verifier --format json > apres.json

Seules les trouvailles actives (non exemptées) comptent. L'identité est
l'empreinte ; une sortie sans empreinte (antérieure à v0.3.0) est comparée
par (règle, fichier, ligne, message), ce qui est signalé.

Le bilan dit aussi quels fichiers gagneraient ou perdraient leur issue
`[conventions]` — ce que `synchroniser` fera à la prochaine exécution.

Sortie 0 si rien ne change, 1 sinon, 2 pour une entrée illisible (comme diff).
"""

import json
import sys
from collections import Counter

from ocots_lint.lecture import lire


class EntreeIllisible(Exception):
    pass


def charger(chemin):
    """(trouvailles actives {identité: trouvaille}, par empreinte ?)"""
    try:
        doc = json.loads(lire(chemin))
        trouvailles = [t for t in doc["trouvailles"] if not t.get("exemption")]
    except (OSError, ValueError, KeyError, TypeError) as e:
        raise EntreeIllisible(f"{chemin} : pas une sortie de verifier --format "
                              f"json ({e})") from e
    par_empreinte = all(t.get("empreinte") for t in trouvailles)
    table = {}
    for t in trouvailles:
        cle = (t["empreinte"] if par_empreinte
               else (t["regle"], t["fichier"], t["ligne"], t["message"]))
        table[cle] = t
    return table, par_empreinte


def comparer(avant, apres):
    """{"apparues": [...], "disparues": [...], "inchangees": n, "fichiers": {...}}"""
    (a, emp_a), (b, emp_b) = avant, apres
    if emp_a != emp_b:          # une seule des deux a des empreintes
        a = {(t["regle"], t["fichier"], t["ligne"], t["message"]): t
             for t in a.values()}
        b = {(t["regle"], t["fichier"], t["ligne"], t["message"]): t
             for t in b.values()}
    apparues = [b[k] for k in b if k not in a]
    disparues = [a[k] for k in a if k not in b]
    fichiers_a = {t["fichier"] for t in a.values()}
    fichiers_b = {t["fichier"] for t in b.values()}
    def cle(t):
        return (t["fichier"], t["ligne"], t["regle"])

    return {
        "par_empreinte": emp_a and emp_b,
        "apparues": sorted(apparues, key=cle),
        "disparues": sorted(disparues, key=cle),
        "inchangees": len(set(a) & set(b)),
        "fichiers": {
            "nouvelle_issue": sorted(fichiers_b - fichiers_a),
            "issue_fermee": sorted(fichiers_a - fichiers_b),
        },
    }


def afficher(ecart):
    for signe, nom in (("+", "apparues"), ("-", "disparues")):
        liste = ecart[nom]
        print(f"{signe} {nom} ({len(liste)})")
        for t in liste:
            print(f"  {t['fichier']}:{t['ligne']}: [{t['regle']}] {t['message']}")
    print(f"= inchangées : {ecart['inchangees']}")
    plus = Counter(t["regle"] for t in ecart["apparues"])
    moins = Counter(t["regle"] for t in ecart["disparues"])
    if plus or moins:
        print("Par règle : " + " ; ".join(
            f"{r} +{plus[r]} −{moins[r]}" for r in sorted(set(plus) | set(moins))))
    f = ecart["fichiers"]
    if f["nouvelle_issue"]:
        print("Issues à créer : " + ", ".join(f["nouvelle_issue"]))
    if f["issue_fermee"]:
        print("Issues à fermer : " + ", ".join(f["issue_fermee"]))


def main(argv):
    fmt = "texte"
    if "--format" in argv:
        i = argv.index("--format")
        fmt = argv[i + 1] if i + 1 < len(argv) else ""
        argv = argv[:i] + argv[i + 2:]
    if len(argv) != 2 or fmt not in ("texte", "json"):
        print("usage : ocots-lint comparer AVANT.json APRES.json "
              "[--format texte|json]", file=sys.stderr)
        return 2
    try:
        ecart = comparer(charger(argv[0]), charger(argv[1]))
    except EntreeIllisible as e:
        print(e, file=sys.stderr)
        return 2
    if not ecart["par_empreinte"]:
        print("sans empreintes d'un côté au moins (sortie antérieure à "
              "v0.3.0) : comparaison par règle, fichier, ligne et message — "
              "un décalage de lignes compte comme un changement.",
              file=sys.stderr)
    if fmt == "json":
        print(json.dumps(ecart, ensure_ascii=False, indent=2))
    else:
        afficher(ecart)
    return 1 if ecart["apparues"] or ecart["disparues"] else 0
