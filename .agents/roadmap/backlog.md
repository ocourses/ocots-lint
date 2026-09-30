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

- `verifier` sur une copie de travail : ignorer les dossiers ignorés par git
  (ex. `.claude/worktrees/`, copies de cours entières), qui doublent
  aujourd'hui les trouvailles en local — constaté en S4.0 sur le cours de
  mesure (42 au lieu de 21). La CI et `synchroniser` partent d'un clone
  propre et ne sont pas touchés.
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
- Monter automatique et calcul-diff en conventions `v2.4.0` et template
  `v1.1.0`, avec le renvoi d'`AGENTS.md` à `methode.md` et
  `conventions-pr.yml` (reporté de S4.9) : suivi par
  [automatique-enseignants#322](https://github.com/ocourses/automatique-enseignants/issues/322)
  et
  [calcul-differentiel-edo-enseignants#83](https://github.com/ocourses/calcul-differentiel-edo-enseignants/issues/83).
  Ensuite seulement : retirer le chemin historique en bash de
  `agents/scripts/checkers/conventions.sh`.
