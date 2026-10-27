"""Motif P7 mesuré : chapitre étoilé ajouté à la table sans `adjustmtc`."""

import re

# Le motif s'arrête au prochain chapitre pour ne pas associer un chapitre étoilé
# à un addcontentsline d'un chapitre suivant. Il exige l'absence d'`adjustmtc`
# immédiatement après l'ajout à la table, qui est la convention du template.
RE_CHAPITRE_AJUSTEMENT = re.compile(
    r"\\chapter\*\{[^}\n]*\}"
    r"(?:(?!\\chapter\*?\{).)*?"
    r"\\addcontentsline\{toc\}\{chapter\}\{[^}\n]*\}"
    r"(?!\s*\\adjustmtc)",
    re.S,
)
