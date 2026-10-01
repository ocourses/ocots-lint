"""`ocots-lint extraire` — l'inventaire des boîtes d'un polycopié (S7,
décision 0007).

    ocots-lint extraire               le polycopié (`poly/`), JSON sur la sortie
    ocots-lint extraire poly/ch1.tex  un fichier, un dossier

Pour les règles qu'aucun outil ne tranche — P1 (hypothèses d'un résultat
cité de loin), P3 (amorce motivée), P4 (reprise) — chaque boîte est donnée
avec ce qu'il faut pour la juger, et rien d'autre : sa section, son label et
ses citations dans tout le cours (index de S6), le paragraphe qui l'amène,
sa preuve, et le paragraphe qui suit l'unité énoncé-preuve. **L'outil ne juge
pas** : il décrit, un agent ou l'auteur décide.

Une boîte est un environnement d'une famille marquée boîte dans le
vocabulaire du template. L'amorce est le dernier paragraphe du texte qui la
précède, depuis l'objet précédent (boîte, figure, titre de section…) ; une
liste (`itemize`…) fait partie du texte. La reprise est le premier
paragraphe après la boîte et sa preuve, si une preuve la suit immédiatement.
Une phrase d'amorce s'appuie souvent sur la précédente : le paragraphe
entier est donné.

La section d'une boîte suit les fichiers inclus : un chapitre déclaré dans
`main.tex` avant `\\input{chapitre}` est celui des boîtes du chapitre.

La carte des sections (S7.2), pour P7 et P4 en fin de section : chaque
chapitre, section, sous-section… dans l'ordre de lecture (fichiers inclus
suivis), avec son ouverture — le texte avant le premier objet, les
environnements de structure du template (introduction de chapitre…) et
`\\minitoc` —, la suite de ce qu'elle contient (boîtes, sous-sections,
figures, texte), les hypothèses posées, et ce qui la termine.

Un fichier que l'analyse syntaxique refuse n'est pas extrait : il est
signalé dans `avertissements`, avec le nombre de boîtes qu'il contient.

Sortie 0 ; 2 pour un chemin inconnu.
"""

import json
import os
import re
import sys

from ocots_lint import __version__, empreintes, labels, vocabulaire
from ocots_lint.arbre import lire_arbre
from ocots_lint.lecture import lire, motif, sans_commentaires, sources

SCHEMA = 1
NIVEAUX = ("part", "chapter", "section", "subsection", "subsubsection")
LISTES = frozenset({"itemize", "enumerate", "description"})
PREUVE = "preuve"
STRUCTURE = "structure"           # famille : introduction de chapitre…
HYPOTHESE = "hypothese"
INCLUSIONS = frozenset({"input", "include", "subfile"})
LONGUEUR = 800          # une amorce, une reprise : un paragraphe, borné

RE_DEF = re.compile(r"\\(?:def|renewcommand|newcommand)\s*\{?\\([A-Za-z@]+)\}?\s*\{")
RE_MACRO_SEULE = re.compile(r"^\s*\\([A-Za-z@]+)\s*$")
RE_INCLUSION = re.compile(r"\\(?:input|include|subfile)\s*\{([^}]+)\}")
RE_LIGNE_COMMENTAIRE = re.compile(r"^[ \t]*%.*\n?", re.M)


# ------------------------------------------------------------ texte

def _groupe(texte, i):
    """(contenu, fin) du groupe {…} ouvert en texte[i], ou (None, i)."""
    if texte[i:i + 1] != "{":
        return None, i
    profondeur, j = 0, i
    while j < len(texte):
        c = texte[j]
        if c == "\\":
            j += 2
            continue
        profondeur += (c == "{") - (c == "}")
        if profondeur == 0:
            return texte[i + 1:j], j + 1
        j += 1
    return None, i


def _sans_definitions(texte):
    """Retire `\\def\\x{…}` (et `\\newcommand`) : de la mécanique, pas du
    texte — mesure pose ainsi le titre de ses sous-sections."""
    morceaux, i = [], 0
    for m in RE_DEF.finditer(texte):
        if m.start() < i:
            continue
        _, fin = _groupe(texte, m.end() - 1)
        morceaux.append(texte[i:m.start()])
        i = fin
    morceaux.append(texte[i:])
    return "".join(morceaux)


def prose(texte):
    """Le texte d'un intervalle de source, tel qu'un relecteur le lit :
    sans commentaires, sans définitions de macros, sans `\\label`, espaces
    réduits. Les formules restent en LaTeX."""
    texte = _sans_definitions(sans_commentaires(texte))
    texte = re.sub(r"\\(?:label|index)\s*\{[^}]*\}", " ", texte)
    return " ".join(texte.split())


def _borner(phrase, a_gauche):
    if len(phrase) <= LONGUEUR:
        return phrase
    return "…" + phrase[-LONGUEUR:] if a_gauche else phrase[:LONGUEUR] + "…"


RE_COMMANDES_SEULES = re.compile(r"^(?:\\[A-Za-z@]+\*?\s*)+$")


def paragraphes(texte):
    """Les paragraphes d'un intervalle de source, en prose. Une ligne de
    commentaire seul ne coupe pas un paragraphe (pour LaTeX non plus) ; un
    paragraphe fait de commandes seules (`\\clearpage`, `\\minitoc`)
    n'est pas du texte."""
    texte = RE_LIGNE_COMMENTAIRE.sub("", texte)
    return [p for p in (prose(x) for x in re.split(r"\n[ \t]*\n", texte))
            if p and not RE_COMMANDES_SEULES.match(p)]


def dernier_paragraphe(texte):
    ps = paragraphes(texte)
    return _borner(ps[-1], a_gauche=True) if ps else ""


def premier_paragraphe(texte):
    ps = paragraphes(texte)
    return _borner(ps[0], a_gauche=False) if ps else ""


# ------------------------------------------------------------ sections

def _definitions(texte):
    """[(position, nom, valeur)] des `\\def\\nom{valeur}` du fichier."""
    trouvees = []
    for m in RE_DEF.finditer(texte):
        valeur, _ = _groupe(texte, m.end() - 1)
        if valeur is not None:
            trouvees.append((m.start(), m.group(1), valeur))
    return trouvees


def titre(noeud, texte, definitions):
    """Le titre d'une commande de sectionnement ; un titre fait d'une seule
    macro définie plus haut par `\\def` est remplacé par sa valeur."""
    i = noeud.debut + len(noeud.nom) + 1
    while i < len(texte) and texte[i] in " *\t":
        i += 1
    if texte[i:i + 1] == "[":
        i = texte.find("]", i) + 1
    brut, _ = _groupe(texte, i)
    if brut is None:
        return ""
    m = RE_MACRO_SEULE.match(brut)
    if m:
        valeurs = [v for p, nom, v in definitions
                   if nom == m.group(1) and p < noeud.debut]
        if valeurs:
            brut = valeurs[-1]
    return prose(brut)


def _sections(arbre, definitions):
    """[(position, niveau, titre)] dans l'ordre du texte."""
    return [(n.debut, n.nom, titre(n, arbre.texte, definitions))
            for n in arbre.parcourir()
            if n.genre == "macro" and n.nom in NIVEAUX]


def section_de(sections, position, entree=None):
    """{niveau: titre} en vigueur à `position` : un titre efface ceux des
    niveaux inférieurs. `entree` : le contexte où le fichier est inclus."""
    courant = dict(entree or {})
    for debut, niveau, intitule in sections:
        if debut >= position:
            break
        rang = NIVEAUX.index(niveau)
        courant = {k: t for k, t in courant.items() if NIVEAUX.index(k) < rang}
        courant[niveau] = intitule
    return courant


def contextes_d_entree(chemins):
    """{fichier inclus: {niveau: titre}} : le contexte de section au point
    où un fichier en inclut un autre (`\\input{…}`, chemin relatif à
    l'incluant), un niveau d'inclusion suffit au polycopié."""
    contextes = {}
    for chemin in chemins:
        texte = sans_commentaires(lire(chemin))
        inclusions = list(RE_INCLUSION.finditer(texte))
        if not inclusions:
            continue
        arbre = lire_arbre(chemin)
        if arbre.erreur is not None:
            continue
        sections = _sections(arbre, _definitions(arbre.texte))
        for m in inclusions:
            cible = m.group(1).strip()
            cible = cible if cible.endswith(".tex") else cible + ".tex"
            cible = os.path.normpath(os.path.join(os.path.dirname(chemin), cible))
            contextes[os.path.relpath(cible)] = section_de(sections, m.start())
    return contextes


# ------------------------------------------------------------ boîtes

def _est_texte(n):
    """Ce qui appartient au texte courant, entre deux objets."""
    if n.genre in ("texte", "maths", "groupe", "special", "commentaire"):
        return True
    if n.genre == "macro":
        return n.nom not in NIVEAUX
    return n.genre == "environnement" and n.nom in LISTES


def _nom(n):
    return n.nom if n.genre in ("environnement", "macro") else n.genre


def _entre_enonce_et_preuve(n, texte):
    """Ce qui peut séparer un énoncé de sa preuve sans les délier : blancs,
    commentaires, macros et leurs groupes (`\\footnotetext{…}` d'une note
    de l'énoncé, `\\index`, espacements)."""
    return n.genre in ("commentaire", "groupe") or (
        n.genre == "macro" and n.nom not in NIVEAUX) or (
        n.genre == "texte" and not texte[n.debut:n.fin].strip())


def _boites_de(noeuds, texte, v, sortie):
    """Ajoute à `sortie` (nœud, frères, indice) de chaque boîte, imbriquées
    comprises."""
    for i, n in enumerate(noeuds):
        if n.genre == "environnement" and n.nom in v.boites:
            sortie.append((n, noeuds, i))
        if n.genre == "environnement":
            _boites_de(n.enfants, texte, v, sortie)


def _decrire(n, freres, i, arbre, v):
    texte = arbre.texte
    # amorce : depuis l'objet précédent
    j = i - 1
    while j >= 0 and _est_texte(freres[j]):
        j -= 1
    debut_amorce = freres[j].fin if j >= 0 else 0
    precede_par = _nom(freres[j]) if j >= 0 else "début"
    # preuve qui suit immédiatement
    k = i + 1
    while k < len(freres) and _entre_enonce_et_preuve(freres[k], texte):
        k += 1
    preuve = None
    fin_unite = n.fin
    if (k < len(freres) and freres[k].genre == "environnement"
            and v.famille(freres[k].nom) == PREUVE):
        preuve = freres[k]
        fin_unite = preuve.fin
        k += 1
    else:
        k = i + 1
    # reprise : jusqu'à l'objet suivant
    m = k
    while m < len(freres) and _est_texte(freres[m]):
        m += 1
    fin_reprise = freres[m].debut if m < len(freres) else len(texte)
    suivi_par = _nom(freres[m]) if m < len(freres) else "fin"
    return {
        "precede_par": precede_par,
        "amorce": dernier_paragraphe(texte[debut_amorce:n.debut]),
        "preuve": None if preuve is None else {
            "environnement": preuve.nom,
            "ligne": arbre.position(preuve.debut)[0],
            "fin": arbre.position(preuve.fin - 1)[0]},
        "reprise": premier_paragraphe(texte[fin_unite:fin_reprise]),
        "suivi_par": suivi_par,
    }


def extraire_fichier(chemin, v, citations, entree=None):
    """(boîtes, avertissements) d'un fichier ; `entree` : le contexte de
    section où il est inclus."""
    arbre = lire_arbre(chemin)
    fichier = os.path.relpath(chemin)
    if arbre.erreur is not None:
        n = len(re.findall(r"\\begin\{" + motif(v.boites) + r"\}",
                           sans_commentaires(arbre.texte)))
        ligne, colonne = arbre.position(arbre.erreur.debut)
        return [], ([{"fichier": fichier, "ligne": ligne, "message":
                     f"analyse syntaxique refusée (colonne {colonne} : "
                     f"{arbre.erreur.message}) — {n} boîte(s) non extraite(s)"}]
                    if n else [])
    definitions = _definitions(arbre.texte)
    sections = _sections(arbre, definitions)
    lus, _ = labels.lire(chemin, v)
    lignes = lire(chemin).split("\n")
    trouvees = []
    _boites_de(arbre.noeuds, arbre.texte, v, trouvees)
    boites, rangs = [], {}
    for n, freres, i in sorted(trouvees, key=lambda t: t[0].debut):
        ligne = arbre.position(n.debut)[0]
        fin = arbre.position(n.fin - 1)[0]
        label = next((x.cle for x in lus
                      if x.objet == n.nom and ligne <= x.ligne <= fin), None)
        cites = citations.get(label, []) if label else []
        cle = empreintes.cle(f"extraire:{n.nom}", fichier,
                             empreintes.contexte(lignes, ligne))
        rangs[cle] = rangs.get(cle, -1) + 1
        boites.append({
            "empreinte": f"{cle}:{rangs[cle]}",
            "fichier": fichier,
            "ligne": ligne,
            "fin": fin,
            "environnement": n.nom,
            "famille": v.famille(n.nom),
            "section": section_de(sections, n.debut, entree),
            "label": label,
            "citations": {
                "total": len(cites),
                "fichiers": sorted(set(cites)),
                "ailleurs": any(f != fichier for f in cites),
            },
            **_decrire(n, freres, i, arbre, v),
        })
    return boites, []


# ------------------------------------------------------------ carte

def _cible(chemin, argument):
    cible = argument.strip()
    cible = cible if cible.endswith(".tex") else cible + ".tex"
    return os.path.normpath(os.path.join(os.path.dirname(chemin), cible))


def _conteneur(n):
    """Un environnement ou un groupe `{…}` qui contient des titres de section
    ou des fichiers inclus (`document`, `appendix`, un groupe qui règle le
    style de page de l'avant-propos…) : son contenu se lit dans l'ordre,
    comme le reste du document."""
    pile = list(n.enfants)
    while pile:
        x = pile.pop()
        if x.genre == "macro" and (x.nom in NIVEAUX or x.nom in INCLUSIONS):
            return True
        pile.extend(x.enfants)
    return False


RE_TITRE = re.compile(r"\\(?:" + "|".join(NIVEAUX) + r")\*?\s*[\[{]")


def _evenements(chemin, v, vus, avertissements):
    """Le fichier en événements, dans l'ordre de lecture ; un `\\input`
    est remplacé par les événements du fichier inclus. Un fichier refusé
    par l'analyse est signalé dans `avertissements` s'il a des titres."""
    if chemin in vus or not os.path.isfile(chemin):
        return
    vus.add(chemin)
    arbre = lire_arbre(chemin)
    if arbre.erreur is not None:
        n = len(RE_TITRE.findall(sans_commentaires(arbre.texte)))
        if n:
            ligne, colonne = arbre.position(arbre.erreur.debut)
            avertissements.append({
                "fichier": os.path.relpath(chemin), "ligne": ligne, "message":
                f"analyse syntaxique refusée (colonne {colonne} : "
                f"{arbre.erreur.message}) — {n} titre(s) absent(s) de la "
                f"carte des sections"})
        return
    fichier = os.path.relpath(chemin)
    texte = arbre.texte
    definitions = _definitions(texte)
    lus, _ = labels.lire(chemin, v)

    def ligne(n):
        return arbre.position(n.debut)[0]

    def prose_reelle(n):
        """Des mots ou une formule : ce qui fait d'un intervalle du texte, pas
        seulement des commandes (`\\footnotetext{…}` entre un énoncé et sa
        preuve, `\\medskip`)."""
        return (n.genre == "maths" or (
            n.genre == "texte" and texte[n.debut:n.fin].strip()) or (
            n.genre == "environnement" and n.nom in LISTES))

    def parcourir(noeuds, fin):
        courant = []                    # nœuds du texte en cours

        def vider(jusqu_a):
            if courant and any(prose_reelle(x) for x in courant):
                yield ("texte", fichier, courant[0].debut,
                       texte[courant[0].debut:jusqu_a])
            courant.clear()

        for n in noeuds:
            if n.genre == "macro" and n.nom in INCLUSIONS:
                m = RE_INCLUSION.match(texte, n.debut)
                if m:
                    yield from vider(n.debut)
                    yield from _evenements(_cible(chemin, m.group(1)), v, vus,
                                           avertissements)
                    continue
            if n.genre == "groupe" and _conteneur(n):
                yield from vider(n.debut)
                yield from parcourir(n.enfants, n.fin - 1)
                continue
            if _est_texte(n):
                if n.genre == "macro" and n.nom == "minitoc":
                    yield ("minitoc", fichier, ligne(n))
                courant.append(n)
                continue
            yield from vider(n.debut)
            if n.genre == "macro":                       # titre de section
                lig = ligne(n)
                label = next((x.cle for x in lus if x.objet == n.nom
                              and lig <= x.ligne <= lig + 2), None)
                yield ("titre", fichier, lig, n.nom,
                       titre(n, texte, definitions), label)
            elif n.genre == "environnement" and n.nom in v.boites:
                yield ("boite", fichier, ligne(n), n.nom)
            elif (n.genre == "environnement"
                  and v.famille(n.nom) == STRUCTURE):
                corps = (texte[n.enfants[0].debut:n.enfants[-1].fin]
                         if n.enfants else "")
                yield ("structure", fichier, ligne(n), n.nom,
                       premier_paragraphe(corps))
            elif n.genre == "environnement" and v.famille(n.nom) == PREUVE:
                yield ("preuve", fichier, ligne(n), n.nom)
            elif n.genre == "environnement" and _conteneur(n):
                yield from parcourir(n.enfants, n.enfants[-1].fin)
            elif n.genre == "environnement":
                yield ("objet", fichier, ligne(n), n.nom)
        yield from vider(fin)

    yield from parcourir(arbre.noeuds, len(texte))


def carte(racines, v, boites, avertissements):
    """Les sections, dans l'ordre de lecture, depuis les fichiers du
    périmètre qu'aucun autre fichier du périmètre n'inclut ; les fichiers
    refusés par l'analyse s'ajoutent à `avertissements`."""
    perimetre = [os.path.normpath(c) for c in sources(racines)]
    inclus = set()
    for c in perimetre:
        for m in RE_INCLUSION.finditer(sans_commentaires(lire(c))):
            inclus.add(_cible(c, m.group(1)))
    par_position = {(b["fichier"], b["ligne"]): b for b in boites}
    sections, ouvertes, vus = [], [], set()
    derniere = None                     # la section qui reçoit le contenu

    def fermer(rang):
        while ouvertes and NIVEAUX.index(ouvertes[-1]["niveau"]) >= rang:
            ouvertes.pop()

    for racine in perimetre:
        if racine in inclus:
            continue
        for e in _evenements(racine, v, vus, avertissements):
            if e[0] == "titre":
                _, fichier, lig, niveau, intitule, label = e
                fermer(NIVEAUX.index(niveau))
                derniere = {
                    "fichier": fichier, "ligne": lig, "niveau": niveau,
                    "titre": intitule, "label": label,
                    "parents": {s["niveau"]: s["titre"] for s in ouvertes},
                    "ouverture": {"texte": [], "structure": [], "minitoc": False},
                    "contenu": [], "hypotheses": [], "termine_par": "rien",
                }
                if ouvertes:
                    ouvertes[-1]["contenu"].append(
                        {"type": "titre", "niveau": niveau, "titre": intitule,
                         "fichier": fichier, "ligne": lig})
                    ouvertes[-1]["termine_par"] = niveau
                ouvertes.append(derniere)
                sections.append(derniere)
                continue
            if derniere is None:
                continue
            avant_tout = not derniere["contenu"]
            if e[0] == "texte":
                paragraphes_ = paragraphes(e[3])
                if not paragraphes_:
                    continue
                if avant_tout:
                    derniere["ouverture"]["texte"].extend(
                        _borner(p, a_gauche=False) for p in paragraphes_)
                else:
                    derniere["contenu"].append(
                        {"type": "texte", "paragraphes": len(paragraphes_)})
                derniere["termine_par"] = "texte"
            elif e[0] == "minitoc":
                derniere["ouverture"]["minitoc"] = True
            elif e[0] == "structure":
                _, fichier, lig, nom, debut = e
                if avant_tout:
                    derniere["ouverture"]["structure"].append(
                        {"environnement": nom, "ligne": lig, "debut": debut})
                else:
                    derniere["contenu"].append(
                        {"type": "structure", "environnement": nom,
                         "fichier": fichier, "ligne": lig})
            elif e[0] == "boite":
                _, fichier, lig, nom = e
                b = par_position.get((fichier, lig))
                entree = {"type": "boite", "environnement": nom,
                          "fichier": fichier, "ligne": lig,
                          "empreinte": b["empreinte"] if b else None}
                derniere["contenu"].append(entree)
                derniere["termine_par"] = nom
                if v.famille(nom) == HYPOTHESE:
                    for s in ouvertes:
                        s["hypotheses"].append(entree["empreinte"])
            elif e[0] in ("objet", "preuve"):
                _, fichier, lig, nom = e
                derniere["contenu"].append(
                    {"type": e[0], "environnement": nom,
                     "fichier": fichier, "ligne": lig})
                derniere["termine_par"] = nom
    return sections


def extraire(racines):
    """Le document JSON de l'extraction (dict)."""
    v = vocabulaire.charger()
    _, renvois = labels.index_du_cours(v)
    citations = {}
    for r in renvois:
        citations.setdefault(r.cle, []).append(os.path.relpath(r.fichier))
    entrees = contextes_d_entree(list(sources(["."])))
    boites, avertissements = [], []
    for chemin in sources(racines):
        b, a = extraire_fichier(chemin, v, citations,
                                entrees.get(os.path.relpath(chemin)))
        boites.extend(b)
        avertissements.extend(a)
    sections = carte(racines, v, boites, avertissements)
    return {
        "schema": SCHEMA,
        "outil": "ocots-lint",
        "version": __version__,
        "extraction": "polycopie",
        "racines": list(racines),
        "boites": boites,
        "sections": sections,
        "avertissements": avertissements,
    }


def main(argv):
    inconnues = [a for a in argv if a.startswith("-") or not os.path.exists(a)]
    if inconnues:
        print(f"argument ou chemin inconnu : {', '.join(inconnues)}", file=sys.stderr)
        return 2
    racines = argv or (["poly"] if os.path.isdir("poly") else ["."])
    doc = extraire(racines)
    print(json.dumps(doc, ensure_ascii=False, indent=2))
    for a in doc["avertissements"]:
        print(f"{a['fichier']}:{a['ligne']}: [ocots-lint] {a['message']}",
              file=sys.stderr)
    print(f"{len(doc['boites'])} boîte(s), {len(doc['sections'])} section(s) "
          f"extraite(s)", file=sys.stderr)
    return 0
