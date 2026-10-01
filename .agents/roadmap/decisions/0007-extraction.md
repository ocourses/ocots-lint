<!-- LTeX: language=fr-FR -->

# 0007 — Règles de jugement : un inventaire à lire, pas des signaux

**Date** : 2026-10-01 — **État** : acceptée

## Contexte

P1 (hypothèses d'un résultat cité de loin), P3 (amorce *motivée*), P4
(reprise qui exploite le résultat) et P7 (ouverture de chapitre et de
section) demandent un jugement : aucun outil ne les tranche. Aujourd'hui,
elles ne sont vues que **par hasard** — l'agent de tri y pense en lisant un
fichier pour une autre trouvaille (étape 6 de `conventions-reviewer`) — ou
lors d'une passe menée avec l'auteur, qui relit les fichiers entiers.

Mesuré le 2026-10-01 sur `main`, prototype d'extraction (polycopiés) :

| Polycopié | Boîtes | Résultats | Cités d'un autre fichier (P1) | Rien après la boîte | … en fin de section (P4) | Sans amorce |
|---|---|---|---|---|---|---|
| mesure | 238 | 79 | 48 | 55 | 21 | 38 |
| calcul-diff | 185 | 50 | 9 | 79 | 36 | 45 |
| automatique | 77 | 22 | 1 | 15 | 8 | 7 |

- **Le critère de P1 est observable** : « cité de loin » = un label cité
  ailleurs, ce que l'index de S6 donne déjà ; seul « se suffit-il à
  lui-même ? » reste à juger.
- **L'inventaire tient en un tiers de la source** (JSON du prototype :
  130 000 caractères pour 347 000 sur mesure), et il est **exhaustif** :
  une liste de boîtes ne s'en saute aucune.
- **Les agents de la CI tournent sur Albert** (`deepseek-v4-flash`), avec
  une limite de jetons par minute déjà atteinte (429, `ARCHITECTURE.md`
  d'`agents`) : un matériau court et structuré y compte plus que pour un
  grand modèle qui relit le fichier.

## Options

| | A. Inventaire à lire | B. Signaux en issues | C. Inventaire + verdicts conservés |
|---|---|---|---|
| Produit | `ocots-lint extraire` : JSON par boîte et par section | nouveaux vérificateurs `signal` (P1, P4) | A, et un fichier de verdicts par empreinte de boîte |
| Qui juge | un agent, ou l'auteur | l'agent de tri, trouvaille par trouvaille | un agent ; seules les boîtes modifiées sont rejugées |
| Trace dans les sources | aucune | une exemption par cas correct (~70 sur le poly de mesure) | aucune |
| Coût | un nouveau format (schéma versionné) | les mécanismes existants | A + un format de verdicts à maintenir |

## Recommandation

**A.** Il n'invente pas de verdict et ne charge pas les sources ; B
transformerait chaque bon résultat cité en exemption à écrire. C est la
suite naturelle de A, une fois A éprouvé par un agent.

## Décision

**A**, acceptée par l'auteur le 2026-10-01, avec :

- **un nouveau rôle** dans `ocourses/agents` (relecture de jugement, rapport
  sans édition), essayé sur un chapitre de mesure **d'abord en local**
  (Claude Code, file locale), **puis sur Albert** en CI, et comparé au
  jugement de l'auteur ;
- **le polycopié seulement** : TD et examens au backlog.

C (verdicts conservés) passe au backlog, avec son critère d'entrée : une
seconde passe sur un chapitre déjà relu, où rejuger tout coûte.
