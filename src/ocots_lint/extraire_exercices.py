"""`ocots-lint extraire --exercices` — l'inventaire des exercices des TD et
des examens (S8.5, décision 0009).

    ocots-lint extraire --exercices              td/ et exams/
    ocots-lint extraire --exercices td/td1/      un TD

Pour les règles qu'aucun outil ne tranche — progression (TD4), citer le
cours (TD5) ou s'en passer (EX1), calibrage des corrigés (TD6), consignes
(EX2), parties (EX4), barème par question (EX6) —, chaque exercice est
donné avec ce qu'il faut pour en juger, et rien d'autre : son label, ses
`points`, son texte d'intro, ses questions numérotées comme le document les
compose, la correction rattachée à chacune et sa place, ses renvois et le
fichier qui définit leur cible. Chaque document (un fichier qui déclare sa
classe) est donné avec son mode de corrigés (`solutions=`), ses champs
d'examen et ce qu'il inclut ; les consignes et les parties, là où elles
sont écrites. **L'outil ne juge pas.**

Une question est un environnement de la famille « question » du
vocabulaire, une sous-question un autre membre de cette famille que le
corrigé ; un corrigé est rattaché à la question qu'il suit (« après »), ou à
celle qui le contient s'il ne suit aucune sous-question (« dans ») — sinon
à l'exercice. Un corrigé hors de tout exercice est donné à part. Seuls les
fichiers des supports TD et examen sont lus.

Un fichier que l'analyse syntaxique refuse n'est pas extrait : il est
signalé dans `avertissements`, avec le nombre d'exercices qu'il contient.
"""

import json
import os
import re
import sys

from ocots_lint import __version__, empreintes, labels, vocabulaire
from ocots_lint.arbre import lire_arbre, precedent
from ocots_lint.extraire import _borner, _groupe, paragraphes, prose
from ocots_lint.lecture import (
    RE_CLASSE,
    lire,
    motif,
    sans_commentaires,
    sources,
    support_de,
)
from ocots_lint.regles.supports import EXERCICE, EXERCICES, STRUCTURE

SCHEMA = 1
CONSIGNE = "consigne"           # famille : consignes d'un TD ou d'un examen
# Les champs d'un sujet, composés par \maketitle (template, ocots-exam).
CHAMPS = ("duree", "documents", "calculatrice", "examnote")
RE_CHAMP = re.compile(r"\\(" + "|".join(CHAMPS) + r")\s*\{")
RE_TITRE = re.compile(r"\\title\s*\{")
RE_SOLUTIONS = re.compile(r"\bsolutions\s*=\s*(\w+)")
RE_INCLUSION = re.compile(r"\\(?:input|include|subfile)\s*\{([^}]+)\}")


# ------------------------------------------------------------ documents

def _argument(texte, motif_):
    """Le contenu en prose du groupe qui suit `motif_`, ou None."""
    m = motif_.search(texte)
    if not m:
        return None
    contenu, _ = _groupe(texte, m.end() - 1)
    return prose(contenu) if contenu is not None else None


def decrire_document(chemin, arbre, v, support):
    """Un fichier qui déclare sa classe : ce que l'étudiant lit avant les
    exercices (EX2), et ce qu'il inclut."""
    texte = sans_commentaires(arbre.texte)
    solutions = RE_SOLUTIONS.search(texte)
    champs = {}
    for m in RE_CHAMP.finditer(texte):
        contenu, _ = _groupe(texte, m.end() - 1)
        if contenu is not None:
            champs[m.group(1)] = prose(contenu)
    return {
        "fichier": os.path.relpath(chemin),
        "support": support,
        "classe": RE_CLASSE.search(arbre.texte).group(1).strip(),
        "titre": _argument(texte, RE_TITRE),
        "solutions": solutions.group(1) if solutions else None,
        "champs": champs,
        "inclut": [os.path.relpath(os.path.normpath(os.path.join(
            os.path.dirname(chemin), c if c.endswith(".tex") else c + ".tex")))
            for c in (m.group(1).strip() for m in RE_INCLUSION.finditer(texte))],
    }


# ------------------------------------------------------------ exercices

class _Lecteur:
    """Décrit les exercices d'un fichier analysé."""

    def __init__(self, chemin, arbre, v, cibles):
        self.chemin, self.arbre, self.v, self.cibles = chemin, arbre, v, cibles
        self.fichier = os.path.relpath(chemin)
        self.texte = arbre.texte
        self.lignes = lire(chemin).split("\n")
        self.labels, self.renvois = labels.lire(chemin, v)

    def ligne(self, position):
        return self.arbre.position(position)[0]

    def etendue(self, n):
        return {"ligne": self.ligne(n.debut), "fin": self.ligne(n.fin - 1)}

    def label(self, n):
        """Le label posé par l'environnement lui-même (`label=`, ou
        `\\label` dans son texte), pas celui d'une question qu'il contient."""
        debut, fin = self.ligne(n.debut), self.ligne(n.fin - 1)
        return next((x.cle for x in self.labels
                     if x.objet == n.nom and debut <= x.ligne <= fin), None)

    def est_question(self, n):
        return (n is not None and n.genre == "environnement"
                and self.v.famille(n.nom) == vocabulaire.QUESTION
                and not self.v.est_corrige(n.nom))

    def est_corrige(self, n):
        return n.genre == "environnement" and self.v.est_corrige(n.nom)

    def corps(self, n, sauf_question=False):
        """Le texte d'un environnement en prose, sans ses questions ni ses
        corrigés si `sauf_question` (l'énoncé propre d'une question)."""
        if not n.enfants:
            return ""
        if not sauf_question:
            debut, fin = n.enfants[0].debut, n.enfants[-1].fin
            return " ".join(paragraphes(self.texte[debut:fin]))
        morceaux = [self.texte[e.debut:e.fin] for e in n.enfants
                    if not self.est_question(e) and not self.est_corrige(e)]
        return " ".join(paragraphes("".join(morceaux)))

    def correction(self, n, place):
        corps = self.texte[n.debut:n.fin].split("\n")[1:-1]
        return {**self.etendue(n), "environnement": n.nom, "place": place,
                "lignes": sum(1 for x in corps if x.strip()
                              and not x.strip().startswith("%"))}

    def questions(self, exercice):
        """(questions, corrections de l'exercice) dans l'ordre du texte."""
        questions, orphelines = [], []
        compteur = [0, 0]

        def numero(n):
            if self.v.canonique(n.nom) == vocabulaire.QUESTION:
                compteur[0] += 1
                compteur[1] = 0
                return str(compteur[0])
            compteur[1] += 1
            return f"{compteur[0]}.{compteur[1]}"

        def parcourir(freres, englobante):
            for i, n in enumerate(freres):
                if self.est_question(n):
                    q = {"numero": numero(n), "environnement": n.nom,
                         **self.etendue(n), "label": self.label(n),
                         "enonce": _borner(self.corps(n, sauf_question=True),
                                           a_gauche=False),
                         "corrections": []}
                    questions.append(q)
                    parcourir(n.enfants, q)
                elif self.est_corrige(n):
                    # deux corrigés de suite corrigent la même question
                    avant = precedent(freres, i, self.texte, self.est_corrige)
                    if self.est_question(avant):
                        cible = next(q for q in reversed(questions)
                                     if q["ligne"] == self.ligne(avant.debut))
                        cible["corrections"].append(self.correction(n, "apres"))
                    elif englobante is not None:
                        englobante["corrections"].append(self.correction(n, "dans"))
                    else:
                        orphelines.append(self.correction(n, "exercice"))
                elif n.genre in ("environnement", "groupe") and n.enfants \
                        and self.v.famille(n.nom) != EXERCICE:
                    parcourir(n.enfants, englobante)

        parcourir(exercice.enfants, None)
        return questions, orphelines

    def intro(self, exercice):
        """Le texte entre l'en-tête et la première question ou le premier
        corrigé."""
        _, debut = labels.en_tete(exercice, self.texte)
        fin = next((e.debut for e in exercice.enfants
                    if self.est_question(e) or self.est_corrige(e)),
                   exercice.enfants[-1].fin if exercice.enfants else debut)
        return [_borner(p, a_gauche=False)
                for p in paragraphes(self.texte[debut:max(debut, fin)])]

    def decrire(self, exercice, partie, rang):
        questions, orphelines = self.questions(exercice)
        etendue = self.etendue(exercice)
        options = labels.options_de(exercice, self.texte)
        renvois = [{"cle": r.cle, "ligne": r.ligne, "commande": r.commande,
                    "cible": self.cibles.get(r.cle)}
                   for r in self.renvois
                   if etendue["ligne"] <= r.ligne <= etendue["fin"]]
        cle = empreintes.cle(f"extraire:{exercice.nom}", self.fichier,
                             empreintes.contexte(self.lignes, etendue["ligne"]))
        rang[cle] = rang.get(cle, -1) + 1
        return {
            "empreinte": f"{cle}:{rang[cle]}",
            "fichier": self.fichier,
            **etendue,
            "environnement": exercice.nom,
            "support": support_de(self.chemin, self.texte, self.v),
            "partie": partie,
            "label": self.label(exercice),
            "points": options.get("points"),
            "intro": self.intro(exercice),
            "questions": questions,
            "corrections": orphelines,
            "renvois": renvois,
        }

    def ouverture(self, n):
        """Les paragraphes d'un environnement avant son premier exercice :
        le titre d'une partie et ce qu'elle annonce (EX4)."""
        fin = next((e.debut for e in n.enfants
                    if e.genre == "environnement"
                    and self.v.famille(e.nom) == EXERCICE),
                   n.enfants[-1].fin if n.enfants else n.fin)
        debut = n.enfants[0].debut if n.enfants else fin
        return [_borner(p, a_gauche=False)
                for p in paragraphes(self.texte[debut:fin])]

    def bloc(self, n):
        return {"fichier": self.fichier, **self.etendue(n),
                "environnement": n.nom, "label": self.label(n),
                "paragraphes": self.ouverture(n)}

    def consignes(self):
        """Les consignes (EX2), là où elles sont écrites : souvent dans le
        contenu commun, pas dans le fichier qui déclare la classe."""
        return [self.bloc(n) for n, _ in self.arbre.avec_ancetres()
                if n.genre == "environnement" and self.v.famille(n.nom) == CONSIGNE]

    def exercices(self):
        """(exercices, parties) dans l'ordre du texte. La partie d'un
        exercice (environnement de structure : `docpart`…) est celle qui le
        contient, sinon la dernière posée avant lui dans le fichier : le
        template compose `docpart` comme un titre, mesure y range ses
        exercices."""
        sortie, parties, rang, posee = [], [], {}, None
        for n, ancetres in self.arbre.avec_ancetres():
            if n.genre != "environnement":
                continue
            if self.v.famille(n.nom) == STRUCTURE:
                posee = self.bloc(n)
                parties.append(posee)
            elif self.v.famille(n.nom) == EXERCICE and not any(
                    self.v.famille(a.nom) == EXERCICE for a in ancetres):
                englobante = next((a for a in ancetres
                                   if self.v.famille(a.nom) == STRUCTURE), None)
                partie = posee if englobante is None else next(
                    p for p in parties if p["ligne"] == self.ligne(englobante.debut))
                reference = None if partie is None else {
                    "fichier": partie["fichier"], "ligne": partie["ligne"]}
                sortie.append(self.decrire(n, reference, rang))
        return sortie, parties

    def hors_exercice(self):
        """Les corrigés qu'aucun exercice ne contient (TD8 les signale)."""
        return [{"fichier": self.fichier, **self.correction(n, "hors_exercice")}
                for n, ancetres in self.arbre.avec_ancetres()
                if self.est_corrige(n)
                and not any(self.v.famille(a.nom) == EXERCICE for a in ancetres)]


# ------------------------------------------------------------ entrée

def _racines_par_defaut():
    return [d for d in ("td", "exams") if os.path.isdir(d)] or ["."]


def extraire(racines):
    """Le document JSON de l'extraction des exercices (dict)."""
    v = vocabulaire.charger()
    definis, _ = labels.index_du_cours(v)
    cibles = {x.cle: os.path.relpath(x.fichier) for x in definis}
    documents, exercices, parties, consignes = [], [], [], []
    hors_exercice, avertissements = [], []
    for chemin in sources(racines):
        arbre = lire_arbre(chemin)
        support = support_de(chemin, arbre.texte, v)
        if support not in EXERCICES:
            continue
        if arbre.erreur is not None:
            n = len(re.findall(r"\\begin\{" + motif(v.noms(EXERCICE)) + r"\}",
                               sans_commentaires(arbre.texte)))
            if n:
                ligne, colonne = arbre.position(arbre.erreur.debut)
                avertissements.append({
                    "fichier": os.path.relpath(chemin), "ligne": ligne, "message":
                    f"analyse syntaxique refusée (colonne {colonne} : "
                    f"{arbre.erreur.message}) — {n} exercice(s) non extrait(s)"})
            continue
        if RE_CLASSE.search(arbre.texte):
            documents.append(decrire_document(chemin, arbre, v, support))
        lecteur = _Lecteur(chemin, arbre, v, cibles)
        e, p = lecteur.exercices()
        exercices.extend(e)
        parties.extend(p)
        consignes.extend(lecteur.consignes())
        hors_exercice.extend(lecteur.hors_exercice())
    return {
        "schema": SCHEMA,
        "outil": "ocots-lint",
        "version": __version__,
        "extraction": "exercices",
        "racines": list(racines),
        "documents": documents,
        "consignes": consignes,
        "parties": parties,
        "exercices": exercices,
        "hors_exercice": hors_exercice,
        "avertissements": avertissements,
    }


def main(argv):
    inconnues = [a for a in argv if a.startswith("-") or not os.path.exists(a)]
    if inconnues:
        print(f"argument ou chemin inconnu : {', '.join(inconnues)}", file=sys.stderr)
        return 2
    doc = extraire(argv or _racines_par_defaut())
    print(json.dumps(doc, ensure_ascii=False, indent=2))
    for a in doc["avertissements"]:
        print(f"{a['fichier']}:{a['ligne']}: [ocots-lint] {a['message']}",
              file=sys.stderr)
    questions = sum(len(e["questions"]) for e in doc["exercices"])
    print(f"{len(doc['exercices'])} exercice(s), {questions} question(s), "
          f"{len(doc['documents'])} document(s) extrait(s)", file=sys.stderr)
    return 0
