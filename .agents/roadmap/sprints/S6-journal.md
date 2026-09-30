<!-- LTeX: language=fr-FR -->

# S6 — Labels et renvois

**Objectif** : outiller C5 (« la clé qu'on écrit est la clé qu'on
référence ») et P12 (un label ne se pose que si l'objet est cité), en
croisant les labels et les renvois de **tout le cours** — polycopié, TD,
transparents, examens.

**Lecture** : [décision 0006](../decisions/0006-labels.md) — **acceptée**
(option B) : labels et renvois lus dans la source (arbre, fichiers inclus
suivis), `??` et labels dupliqués dans le `.log` que la CI des cours
produit déjà ; pas de `.sty` d'instrumentation (l'ébauche de ce sprint),
faute de cas réel que la source manque.

**Version livrée** : `v0.7.0`.

## État des lieux (mesuré le 2026-09-30)

- La source donne tous les labels : 148 sur 148 (polycopié de mesure,
  comparé au `.aux`), 10 sur 10 (transparents, chapitre 5).
- La CI des cours compile chaque document touché par une PR, mais les
  références non résolues et labels dupliqués n'y sont que des
  avertissements : ils passent. Sur `main` (poly et chapitre 5 de mesure) :
  aucun.
- Prototype sur le corpus (commits figés) :

  | Cours | Labels | De résultats | Jamais cités | Préfixe ≠ objet | `\ref{hyp:…}` |
  |---|---|---|---|---|---|
  | mesure | 107 | 67 | 7 | 38 | 0 |
  | automatique | 80 | 37 | 8 | 1 | 0 |
  | calcul-diff | 142 | 77 | 18 | 0 | 0 |
  | démo | 14 | 10 | 7 | 0 | 0 |

  Les 38 de mesure sont des exercices étiquetés `exo:` quand C5 écrit
  `ex:`. **Tranché par l'auteur** : C5 ne change pas, les 38 labels (et
  leurs renvois) seront signalés puis corrigés.

## Critères d'acceptation

1. **Les trouvailles existantes ne bougent pas** (empreinte, message) :
   `instantane verifier` n'a que des apparitions, des nouvelles règles.
2. **Chaque nouvelle trouvaille est relue** sur le corpus : liste par
   règle dans le journal, avec les faux positifs corrigés ou écrits en
   limites.
3. **Garantie déclarée** pour chaque vérificateur (registre S2), et
   exemptions opérantes (`% ocots-lint: ignore P12 — raison`).
4. **Une information, un propriétaire** : la table des préfixes est celle
   de C5 dans les conventions, lue par l'outil (comme les identifiants de
   règle) ; le préfixe que le template ajoute à l'ancienne syntaxe vient
   de `vocabulaire.json`.
5. **Effet sur les issues mesuré** avant la montée d'un cours
   (`synchroniser --dry-run`) : de nouvelles règles ouvrent de nouvelles
   issues, le volume doit être annoncé.
6. Contrat inchangé (JSON schéma 1) ; temps sous l'alarme de 30 s.

## Stories

- [ ] **S6.1** — Lecture des labels et des renvois (`labels.py`) : sur
  l'arbre, pour chaque fichier du cours — `\label{…}`, `label=…` des boîtes,
  ancienne syntaxe `{titre}{clé}` avec le préfixe du vocabulaire ; renvois
  `\ref`, `\eqref`, `\cref`, `\Cref`, `\autoref`, `\pageref`, `\nameref`,
  `\hyperref[…]`, listes `\cref{a,b}`. Index des renvois bâti sur **tout le
  cours** (dossier courant), quel que soit le périmètre vérifié.
  - Critère : sur le polycopié et un chapitre de transparents de mesure,
    labels lus = labels du `.aux`.
  - Dans le template : `prefixe` dans `vocabulaire.json` pour les
    environnements à ancienne syntaxe (ajout compatible au schéma 1).
- [ ] **S6.2** — En tant qu'*auteur*, je veux que l'outil signale un label
  jamais cité dans le cours (P12, C5), afin de ne pas maintenir des clés
  pour rien.
- [ ] **S6.3** — En tant qu'*auteur*, je veux que l'outil signale un
  préfixe qui ne correspond pas à l'objet étiqueté (C5 : `thm:` pour un
  théorème…), la table étant lue dans les conventions.
- [ ] **S6.4** — En tant qu'*auteur*, je veux qu'une hypothèse citée par
  `\ref` au lieu de `\eqref` soit signalée (C5) — aucune au corpus
  aujourd'hui : la règle verrouille l'usage.
- [ ] **S6.5** — Dans `ocourses/agents`, `latex-pr.yml` : les références
  non résolues et labels multiplement définis du `.log` **font échouer la
  PR** (tranché par l'auteur ; C5 : « un `??` est un bug »), avec la liste
  dans le rapport.
- [ ] **S6.6** — Release `v0.7.0`, relais des conventions, montée des
  cours, avec `comparer` et `synchroniser --dry-run`.

## Journal

- 2026-09-30 — Préparation : mesures (labels du `.aux` contre la source,
  coût de compilation, prototype C5/P12 sur le corpus), décision 0006
  proposée, sprint réécrit. Tranché par l'auteur : 0006 option B (le
  journal instrumenté passe au backlog) ; C5 garde `ex:` ; `??` en échec de
  PR.

## Bilan

*À écrire en fin de sprint.*
