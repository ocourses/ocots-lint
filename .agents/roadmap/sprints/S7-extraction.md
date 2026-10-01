<!-- LTeX: language=fr-FR -->

# S7 — Extraction pour les règles de jugement

**Objectif** : pour les règles qu'aucun outil ne tranche — P1 (hypothèses
d'un résultat cité de loin), P3 (amorce motivée), P4 (reprise), P7
(ouverture de chapitre et de section) —, donner au relecteur, agent ou
auteur, **tout le matériau de la décision et rien d'autre** : chaque boîte
du polycopié avec ce qui l'amène et ce qui la suit, et la carte de chaque
section. L'outil ne rend aucun verdict.

**Lecture** : [décision 0007](../decisions/0007-extraction.md) — **acceptée**
(option A) : inventaire à lire ; un nouveau rôle d'agent l'éprouve, en local
puis sur Albert ; polycopié seulement.

**Version livrée** : `v0.8.0`.

## État des lieux (mesuré le 2026-10-01)

- Aujourd'hui, P1, P3 (au-delà des deux signaux outillés), P4 et P7 ne sont
  vues que par hasard (étape 6 du tri, `conventions-reviewer`) ou en passe
  menée avec l'auteur, fichiers relus en entier.
- Prototype d'extraction sur `main` (polycopiés) :

  | Polycopié | Boîtes | Résultats | Cités d'un autre fichier | Rien après | … en fin de section | Sans amorce |
  |---|---|---|---|---|---|---|
  | mesure | 238 | 79 | 48 | 55 | 21 | 38 |
  | calcul-diff | 185 | 50 | 9 | 79 | 36 | 45 |
  | automatique | 77 | 22 | 1 | 15 | 8 | 7 |

- Taille : environ un tiers de la source (130 000 caractères de JSON pour
  347 000 sur mesure).
- Défauts du prototype, à corriger : titres de section posés par une macro
  (`\def\subsectionname{…}` suivi de `\subsection{\subsectionname}`,
  usage de mesure), cette macro prise pour une reprise ; boîtes dans un
  fichier que l'analyse refuse (repli à prévoir).
- Agents : Albert (`deepseek-v4-flash`) en CI, limité en jetons par minute ;
  Claude Code par la file locale (`LOCAL-QUEUE.md`).

## Critères d'acceptation

1. **Exhaustif** : sur les trois polycopiés, autant de boîtes extraites que
   d'ouvertures d'environnements des familles boîtes du vocabulaire
   (comptées indépendamment) ; un fichier refusé par l'analyse est signalé,
   jamais sauté en silence.
2. **Fidèle** : sur 30 boîtes tirées au hasard (10 par cours), amorce,
   reprise, preuve, section et citations relues contre la source, sans
   écart (liste dans le journal).
3. **Aucun verdict** : l'extraction décrit, ne juge pas ; `verifier` et ses
   trouvailles inchangés (`instantane verifier` : rien ne bouge).
4. **Un contrat** : format JSON versionné (`"schema": 1`, champ
   `extraction`), schéma publié et testé comme celui de `verifier`.
5. **Éprouvé par un agent** : le rôle de relecture, sur un même chapitre de
   mesure, en local puis sur Albert ; chaque rapport comparé au jugement de
   l'auteur (points justes, manqués, à tort) dans le bilan.
6. Temps sous l'alarme de 30 s sur un polycopié entier.

## Stories

- [x] **S7.1** — En tant qu'*agent de relecture*, je veux `ocots-lint
  extraire [périmètre]` : chaque boîte du polycopié avec son empreinte, sa
  famille, sa section (titre résolu), son label, ses citations (combien,
  depuis quels fichiers — l'index de S6), la phrase qui l'amène, sa preuve
  éventuelle et la phrase qui suit l'unité énoncé-preuve, afin de juger P1,
  P3 et P4 sans relire le fichier entier.
- [x] **S7.2** — En tant qu'*agent de relecture*, je veux la carte de chaque
  chapitre et section : introduction de chapitre (`chapterintro`,
  `\minitoc`), texte d'ouverture de section (décor, phrase d'introduction),
  blocs `assumption`, suite des boîtes, ce qui termine la section — afin de
  juger P7, et P4 en fin de section.
- [x] **S7.3** — Contrat de l'extraction : schéma JSON publié
  (`schemas/`), testé, et documenté dans le README (ce qu'elle contient, ce
  qu'elle ne juge pas).
- [x] **S7.4** — Dans `ocourses/agents` : rôle de relecture de jugement
  (P1, P3, P4, P7 sur un chapitre de polycopié, à partir de l'extraction ;
  rapport Bloquant / Important / Mineur, aucune édition). Essai sur un
  chapitre de mesure : en local (file locale), puis sur Albert ; rapports
  comparés au jugement de l'auteur.
- [ ] **S7.5** — Conventions : `methode.md` et P1, P3, P4, P7 renvoient à
  `extraire` pour préparer une passe.
- [ ] **S7.6** — Release `v0.8.0`, relais des conventions, montée des
  cours.

## Journal

- 2026-10-01 — Préparation : règles P1/P3/P4/P7 relues, usages actuels
  (tri, passes, file locale, Albert), prototype d'extraction sur les trois
  polycopiés. Décision 0007 tranchée par l'auteur : A, nouveau rôle en
  local puis sur Albert, polycopié seulement.
- 2026-10-01 — S7.1 : `ocots-lint extraire`. **Critère 1 tenu** : boîtes
  extraites = ouvertures d'environnements boîtes comptées indépendamment
  (commentaires et verbatims retirés), fichier par fichier — mesure 260,
  calcul-diff 213, automatique 77, aucun écart. **Critère 2 tenu** : 30
  boîtes tirées au hasard (graine 7, 10 par cours) relues contre la
  source — amorce, preuve, reprise, ce qui précède et suit, section,
  citations. Écarts trouvés en route et corrigés : l'amorce réduite à la
  dernière phrase perdait la motivation portée par la précédente (→ le
  paragraphe entier ; une ligne de commentaire ne le coupe pas) ; le
  chapitre déclaré dans `main.tex` avant `\input` manquait (→ contexte
  hérité de l'incluant) ; une preuve séparée de son énoncé par un
  `\footnotetext{…}` n'était pas rattachée (calcul-diff, Théorème
  d'inversion locale ; → 7 preuves de plus rattachées sur mesure). Après
  correction, les 30 relues sans écart. **Critère 3 tenu** : `instantane
  verifier`, rien ne bouge. Temps : 2,4 s, 1,9 s, 1,2 s.
- 2026-10-01 — S7.2 : carte des sections. **Exhaustive** : titres de la
  carte = titres comptés indépendamment, fichier par fichier — mesure 88,
  automatique 30, calcul-diff 93 et 1 dans `frontmatter/notations.tex`,
  refusé par l'analyse et signalé. Écarts trouvés en route : les annexes de
  mesure, incluses dans `\begin{appendix}` (→ tout environnement ou groupe
  qui contient des titres ou des `\input` est traversé) ; l'avant-propos de
  calcul-diff, dans un groupe `{\pagestyle{empty} …}` ; un texte en fin de
  conteneur coupé à la fin du fichier (vu par les tests). **Fidèle** : 12
  sections tirées au hasard (4 par cours, graine 11) relues contre la
  source — ouverture, introduction de chapitre, `\minitoc`, contenu, fin.
  Ce que la carte montre : sections finies sur une boîte ou sa preuve,
  sans reprise — mesure 46 sur 63, calcul-diff 48 sur 64, automatique 13 sur
  23 (P4 en compte 73 au corpus) ; chapitres avec introduction — mesure 8
  sur 10, calcul-diff et automatique 0 ; aucun bloc `assumption`.
- 2026-10-01 — S7.3 : schéma `extraire-1.schema.json` (draft 2020-12),
  publié avec le paquet. **Critère 4 tenu** : la sortie d'un petit cours de
  référence (`tests/contrat/extraction/`) est validée contre le schéma et
  comparée à `tests/contrat/extraction.json` ; les extractions réelles de
  mesure, calcul-diff et automatique (`origin/main`) valident sans erreur.
- 2026-10-01 — S7.4 : rôle `judgment-reviewer` (agents#42), essayé sur
  l'annexe B de mesure (15 boîtes, 5 sections), comparaison sur
  mesure#381. **Local (Opus)** : 1 point P1 mineur (résultat cité depuis
  les transparents qui nomme un objet défini seulement dans le texte qui
  précède), juste ; rien d'autre de manqué. **Albert
  (`deepseek-v4-flash`)** : format suivi, rien écrit dans le cours, mais
  0 juste sur 2 — deux P4 à tort sur des exemples en fin de section — et
  le point P1 manqué ; P3 ✅ sur des amorces vides, points sans empreinte.
  Cause : le rôle ne disait pas que P1 et P4 ne portent que sur les
  résultats → agents#43 (règles selon `famille`, P3 « — » sur amorce
  vide, P1 couvre les notations). **Taille** : pour un chapitre,
  l'extraction (28 Ko) pèse autant que la source ; son apport est
  l'exhaustivité et la structure. Aucun signe de gêne chez Albert : pas de
  sortie compacte pour l'instant.

## Bilan

*À écrire en fin de sprint.*
