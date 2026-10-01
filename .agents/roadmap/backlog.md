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
- Journal de compilation instrumenté (ébauche initiale de S6) : un `.sty`
  injecté à une compilation de vérification, qui voit le document tel que
  LaTeX l'a composé. Écarté par la décision 0006 (la source donne tous les
  labels mesurés). Critère de retour : un cas réel que la source ne peut pas
  lire — par exemple une boîte ouverte par une macro
  (`P2/limites/boite_par_macro.tex`) trouvée dans un cours.
- CI du template qui compile `examples/` (TeX Live dans GitHub Actions) :
  `make check` (dont le témoin des labels dupliqués de `variants/compat`,
  S6.5) ne tourne aujourd'hui qu'en local.
- C5 : un renvoi écrit par une macro propre au cours
  (`\newcommand{\thmref}[1]{…\ref{#1}}`) n'est pas lu, le label est
  signalé à tort (`C5/limites/renvoi_par_macro.tex`). Aucun cours n'en
  définit (S6.2). Critère d'entrée : un cas réel.
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
  `agents/scripts/checkers/conventions.sh`. Cibles portées à template
  `v1.2.0` et conventions `v2.5.0` le 2026-09-30 (S5.6), puis à template
  `v1.5.1` et conventions `v2.6.0` le 2026-10-01 (S6.6) — calcul-diff en
  a besoin : ses transparents à clé vide font échouer les PR qui les
  touchent (agents#41) tant que le template n'est pas monté.
- Transparents : un fichier **sans classe**, inclus par un transparent rangé
  hors de `slides/`, reçoit P3 (reconnaître un fichier par le document qui
  l'inclut). Non constaté au corpus (S5.4).
