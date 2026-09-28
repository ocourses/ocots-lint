# Démo — verdicts attendus sur `ocourses/ocots-demo`

Écarts plantés dans le cours de démonstration
([`ocourses/ocots-demo`](https://github.com/ocourses/ocots-demo), commit
initial `417ceee`), et ce que la chaîne doit en faire. Gardé **ici**, pas dans
la démo : un agent qui lit la démo ne doit pas y trouver les réponses.

Sortie de `verifier` avec ocots-lint `v0.4.0` (conventions `v2.3.0`) :
14 trouvailles, toutes plantées.

## Voie mécanique — issues `[nettoyer]`, PR sans modèle

| Fichier | Ligne | Règle | Écart | Attendu |
|---|---|---|---|---|
| `td/td1/td1.tex` | 25 | C4 | `~:` | retiré par `nettoyer` |
| `td/td1/td1.tex` | 37 | C4 | `~:` | retiré par `nettoyer` |
| `poly/mainmatter/suites.tex` | 47 | C4 | `~:` | retiré par `nettoyer` |
| `poly/mainmatter/suites.tex` | 48 | C4 | ` ``oscille'' ` | `\enquote{oscille}` (csquotes chargé par le template) |

## Tri — issue `[conventions]`, rôle `conventions-reviewer`

| Fichier | Ligne | Règle | Écart | Verdict attendu |
|---|---|---|---|---|
| `poly/mainmatter/suites.tex` | 20 | P2 | définition → théorème sans texte | **confirmée** |
| `poly/mainmatter/suites.tex` | 101 | P2 | définition → théorème sans texte | **confirmée** |
| `slides/chapitre1/slides_chapitre_1.tex` | 23 | P2 | deux boîtes sous un même titre | **confirmée**, remède : scinder en deux diapositives (SL4, SL3) |
| `poly/mainmatter/suites.tex` | 54 | P3 | « Nous avons le théorème suivant. » | **confirmée** |
| `poly/mainmatter/suites.tex` | 69 | P3 | phrase finie par une formule hors texte | **faux positif** (limite connue `P3/limites/amorce_en_maths.tex`) → exemption |
| `poly/mainmatter/suites.tex` | 77 | P5 | quatre remarques d'affilée | **exception légitime** : remarques indépendantes et toutes facultatives → exemption (un verdict « confirmée » se défend aussi : noter lequel est rendu) |
| `poly/mainmatter/suites.tex` | 116 | C4 | `théorème~\ref` | **confirmée** (`\cref`) |
| `poly/mainmatter/suites.tex` | 118 | C4 | « sous suite » | **confirmée** (« sous-suite ») |
| `poly/mainmatter/suites.tex` | 32 | C6 | preuve finie par `\[…\]` sans `\qedhere` | **confirmée** |
| `poly/mainmatter/suites.tex` | 114 | C6 | preuve finie par `\[…\]` sans `\qedhere` | **confirmée** |

## Déroulé attendu

1. Lundi 1 (ou `check.yml` à la main) : 1 issue `[conventions]`
   (`poly/mainmatter/suites.tex`) + 1 `[conventions]` (transparents) + 2
   `[nettoyer]` (poly, TD). Vérifier contre
   `./conventions/bin/ocots-lint synchroniser --dry-run`.
2. File : les `[nettoyer]` donnent deux PR Draft
   `ocots-lint/nettoyer/<fichier>` ; le tri promeut le poly en
   `conventions-style` avec une PR d'exemptions (P3 l. 69, P5 l. 77, selon le
   verdict) acceptée par `controle-tri.sh` ; la correction ouvre sa PR.
3. Fusion humaine des PR.
4. Lundi 2 : **aucune issue rouverte** pour les rejets ; seules restent les
   trouvailles non corrigées, s'il y en a.

Écart entre ce tableau et un verdict d'agent : à consigner dans le journal
de S3 (erreur de l'agent, ou attendu à revoir).
