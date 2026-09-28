"""Formats de sortie de `verifier` pour une CI : JSON, SARIF 2.1.0, GitHub.

SARIF est le format que GitHub lit pour annoter une PR (code scanning). Une
trouvaille exemptée y figure avec sa raison, comme suppression « inSource » :
elle reste traçable sans être affichée comme une alerte.
"""

import json
from dataclasses import asdict, dataclass
from pathlib import PurePath
from typing import Optional

from ocots_lint import __version__
from ocots_lint.regles import REGISTRE

DEPOT = "https://github.com/ocourses/ocots-lint"
SCHEMA_SARIF = "https://json.schemastore.org/sarif-2.1.0.json"

# Une trouvaille « signal » dit où regarder : avertissement, pas erreur.
NIVEAUX = {"exact": "error", "heuristique": "error", "signal": "warning"}


@dataclass(frozen=True)
class Trouvaille:
    regle: str
    fichier: str            # relatif au dossier courant
    ligne: int
    message: str
    exemption: Optional[str] = None    # raison, si exemptée


def _verificateurs(noms):
    return [v for v in REGISTRE if v.regle in noms]


def json_(trouvailles, noms):
    garanties = {v.regle: v.garantie for v in REGISTRE}
    return json.dumps({
        "outil": "ocots-lint",
        "version": __version__,
        "regles": {v.regle: {"garantie": v.garantie, "resume": v.resume}
                   for v in _verificateurs(noms)},
        "trouvailles": [dict(asdict(t), garantie=garanties[t.regle])
                        for t in trouvailles],
    }, ensure_ascii=False, indent=2)


def sarif(trouvailles, noms):
    verificateurs = _verificateurs(noms)
    index = {v.regle: i for i, v in enumerate(verificateurs)}
    garanties = {v.regle: v.garantie for v in verificateurs}
    resultats = []
    for t in trouvailles:
        r = {
            "ruleId": t.regle,
            "ruleIndex": index[t.regle],
            "level": NIVEAUX[garanties[t.regle]],
            "message": {"text": t.message},
            "locations": [{"physicalLocation": {
                "artifactLocation": {"uri": PurePath(t.fichier).as_posix(),
                                     "uriBaseId": "%SRCROOT%"},
                "region": {"startLine": t.ligne},
            }}],
        }
        if t.exemption:
            r["suppressions"] = [{"kind": "inSource",
                                  "justification": t.exemption}]
        resultats.append(r)
    return json.dumps({
        "$schema": SCHEMA_SARIF,
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {
                "name": "ocots-lint",
                "version": __version__,
                "informationUri": DEPOT,
                "rules": [{
                    "id": v.regle,
                    "shortDescription": {"text": v.resume},
                    "defaultConfiguration": {"level": NIVEAUX[v.garantie]},
                    "properties": {"garantie": v.garantie},
                } for v in verificateurs],
            }},
            "results": resultats,
        }],
    }, ensure_ascii=False, indent=2)


def _echapper(texte, propriete=False):
    """Échappement des commandes de workflow GitHub Actions."""
    texte = texte.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
    if propriete:
        texte = texte.replace(":", "%3A").replace(",", "%2C")
    return texte


def github(trouvailles, noms):
    """Annotations de workflow (`::error file=…,line=…::…`) : affichées dans
    la PR sans code scanning, donc aussi pour un dépôt privé. Les trouvailles
    exemptées sont omises."""
    garanties = {v.regle: v.garantie for v in REGISTRE}
    lignes = []
    for t in trouvailles:
        if t.exemption:
            continue
        niveau = NIVEAUX[garanties[t.regle]]
        titre = f"{t.regle} ({garanties[t.regle]})"
        lignes.append(
            f"::{niveau} file={_echapper(PurePath(t.fichier).as_posix(), True)},"
            f"line={t.ligne},title={_echapper(titre, True)}::{_echapper(t.message)}")
    return "\n".join(lignes)
