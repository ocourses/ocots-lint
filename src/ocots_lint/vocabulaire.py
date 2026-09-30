"""Vocabulaire des environnements, publié par le template (S5, décision 0005).

    v = vocabulaire.charger()
    v.boites                 # noms des environnements-boîtes, alias compris
    v.noms("remarque")       # ceux d'une famille
    v.famille("myremark*")   # "remarque" : un alias hérite de sa cible

L'outil ne code pas en dur les noms d'environnements du template : il lit
`template/vocabulaire.json` dans le dossier courant (le template que le cours
épingle). À défaut, il lit la copie embarquée (`donnees/vocabulaire.json`,
celle du template qu'`ocots-lint` connaît à sa release) :

- sans dossier `template/` (un fichier isolé, les fixtures) : en silence ;
- avec un `template/` sans vocabulaire (template antérieur à `v1.2.0`, ou
  sous-module non initialisé) : un avertissement, une fois par exécution,
  sur la sortie d'erreur — jamais dans les trouvailles ni dans les issues.

Un vocabulaire illisible ou d'un schéma inconnu lève `VocabulaireIllisible` :
la commande s'arrête (sortie 2) plutôt que de rendre zéro trouvaille.
"""

import functools
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

SCHEMA = 1
FICHIER = os.path.join("template", "vocabulaire.json")
EMBARQUE = Path(__file__).parent / "donnees" / "vocabulaire.json"


class VocabulaireIllisible(Exception):
    pass


@dataclass(frozen=True)
class Vocabulaire:
    source: str
    familles: dict
    environnements: dict
    supports: dict

    def _cible(self, nom):
        e = self.environnements.get(nom)
        return self.environnements.get(e["alias_de"]) if e and "alias_de" in e else e

    def famille(self, nom):
        """La famille de `nom` (celle de sa cible pour un alias), ou None."""
        e = self._cible(nom)
        return e["famille"] if e else None

    def noms(self, *familles):
        """Les environnements de ces familles, alias compris."""
        return frozenset(n for n in self.environnements
                         if self.famille(n) in familles)

    @functools.cached_property
    def boites(self):
        return self.noms(*(f for f, d in self.familles.items() if d["boite"]))

    @functools.cached_property
    def symbole_de_fin(self):
        """Les environnements qui posent un symbole de fin à `\\end`."""
        return frozenset(n for n in self.environnements
                         if (self._cible(n) or {}).get("symbole_de_fin"))

    def support(self, classe):
        """Le support qu'une classe de document choisit."""
        return self.supports["classes"].get(classe, self.supports["defaut"])


def _valider(doc, source):
    def refus(message):
        return VocabulaireIllisible(f"vocabulaire illisible ({source}) : {message}")
    if not isinstance(doc, dict):
        raise refus("un objet JSON est attendu")
    if doc.get("schema") != SCHEMA:
        raise refus(
            f"schéma {doc.get('schema')!r}, alors que cette version d'ocots-lint lit "
            f"le schéma {SCHEMA} — monter ocots-lint (via les conventions du cours), "
            f"ou épingler un template compatible")
    for cle in ("familles", "environnements", "supports"):
        if not isinstance(doc.get(cle), dict):
            raise refus(f"clé « {cle} » absente ou invalide")
    familles, envs = doc["familles"], doc["environnements"]
    for nom, f in familles.items():
        if not isinstance(f, dict) or not isinstance(f.get("boite"), bool):
            raise refus(f"famille « {nom} » sans « boite » (vrai ou faux)")
    for nom, e in envs.items():
        if "alias_de" in e:
            cible = envs.get(e["alias_de"])
            if cible is None or "alias_de" in cible:
                raise refus(f"« {nom} » est l'alias de « {e['alias_de']} », "
                            f"qui n'est pas un environnement du vocabulaire")
        elif e.get("famille") not in familles:
            raise refus(f"« {nom} » : famille {e.get('famille')!r} inconnue")
    if "defaut" not in doc["supports"] or not isinstance(
            doc["supports"].get("classes"), dict):
        raise refus("« supports » doit porter « classes » et « defaut »")
    return Vocabulaire(source, familles, envs, doc["supports"])


@functools.lru_cache(maxsize=8)
def _lire(chemin, _date):
    try:
        doc = json.loads(Path(chemin).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise VocabulaireIllisible(f"vocabulaire illisible ({chemin}) : {e}") from e
    return _valider(doc, chemin)


_averti = set()


def charger():
    """Le vocabulaire du template du dossier courant, sinon la copie embarquée."""
    if os.path.isfile(FICHIER):
        chemin = os.path.abspath(FICHIER)
        return _lire(chemin, os.stat(chemin).st_mtime_ns)
    if os.path.isdir("template") and os.path.abspath("template") not in _averti:
        _averti.add(os.path.abspath("template"))
        print(f"ocots-lint : {FICHIER} absent (template antérieur à v1.2.0, ou "
              f"sous-module non initialisé) — vocabulaire embarqué utilisé",
              file=sys.stderr)
    return _lire(str(EMBARQUE), 0)
