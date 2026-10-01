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

- [ ] **S7.1** — En tant qu'*agent de relecture*, je veux `ocots-lint
  extraire [périmètre]` : chaque boîte du polycopié avec son empreinte, sa
  famille, sa section (titre résolu), son label, ses citations (combien,
  depuis quels fichiers — l'index de S6), la phrase qui l'amène, sa preuve
  éventuelle et la phrase qui suit l'unité énoncé-preuve, afin de juger P1,
  P3 et P4 sans relire le fichier entier.
- [ ] **S7.2** — En tant qu'*agent de relecture*, je veux la carte de chaque
  chapitre et section : introduction de chapitre (`chapterintro`,
  `\minitoc`), texte d'ouverture de section (décor, phrase d'introduction),
  blocs `assumption`, suite des boîtes, ce qui termine la section — afin de
  juger P7, et P4 en fin de section.
- [ ] **S7.3** — Contrat de l'extraction : schéma JSON publié
  (`schemas/`), testé, et documenté dans le README (ce qu'elle contient, ce
  qu'elle ne juge pas).
- [ ] **S7.4** — Dans `ocourses/agents` : rôle de relecture de jugement
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

## Bilan

*À écrire en fin de sprint.*
