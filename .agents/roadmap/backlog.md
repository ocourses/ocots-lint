<!-- LTeX: language=fr-FR -->

# Backlog

Stories non planifiées. Une story entre dans un sprint au moment où on le
prépare ; une story reportée d'un sprint revient ici avec son numéro et la
raison.

## Règles candidates à un vérificateur

Repérées comme probablement mécaniques ; à confirmer en lisant la règle.

- `TD3` — questions numérotées à la main au lieu des environnements.
- `TD8` — `question` rouverte dans un `\solution`.
- `EX3` — barème écrit à la main au lieu des clés.
- `SL8` — réglage de thème posé localement au lieu de globalement.
- `C3` — les mesures actuelles (ancienne syntaxe `{titre}{label}`,
  `\emph{\textbf{…}}`) deviennent bloquantes quand le corpus est propre.

## Outillage

- Prose française (`C1`, orthographe) : brancher LTeX/LanguageTool plutôt
  que de réécrire des règles de langue.
- Cohérence terminologique (`C2`) : table de variantes par cours, comptée par
  l'outil.
- Intégration `pre-commit`.
- CI du template qui compile `examples/` (TeX Live dans GitHub Actions) :
  prérequis des tests d'instrumentation de S6.
- Monter `ocots-lint` dans un cours en une étape : une release d'`ocots-lint`
  ouvre d'elle-même la PR qui met à jour `OCOTS_LINT_VERSION` dans
  `ocots-conventions/bin/` (reporté de S3). Suivi :
  [#27](https://github.com/ocourses/ocots-lint/issues/27).
