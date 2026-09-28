<!-- LTeX: language=fr-FR -->

# S2 — Registre, garanties, couverture

**Objectif** : chaque vérificateur déclare ce qu'il garantit, et l'outil sait
quelles règles des conventions il couvre.

**Version livrée** : `v0.2.0`.

## Stories (à affiner en début de sprint)

- [ ] **S2.1** — En tant que *mainteneur*, je veux que chaque vérificateur
  porte ses métadonnées (règle, garantie *exact / heuristique / mesure*,
  supports concernés), afin que `--list` et la documentation soient générés
  au lieu d'être recopiés.
- [ ] **S2.2** — En tant que *mainteneur*, je veux que le CI échoue si un
  vérificateur cite une règle absente de la version épinglée des conventions.
- [ ] **S2.3** — En tant que *relecteur*, je veux une commande `couverture`
  qui liste chaque règle des conventions avec son vérificateur et sa garantie,
  ou « non outillée », afin d'interpréter une absence de trouvaille.
- [ ] **S2.4** — En tant qu'*auteur*, je veux exempter une trouvaille dans la
  source (`% ocots-lint: ignore P5 — raison`), afin qu'une règle heuristique
  puisse devenir bloquante sans bruit.
- [ ] **S2.5** — En tant que *mainteneur de CI*, je veux une sortie JSON et
  SARIF, afin d'avoir des annotations dans les PR GitHub.
- [ ] **S2.6** — `nettoyer` porté (avec parité), sur la lecture commune.
- [ ] **S2.7** — Dans `ocots-conventions`, `bin/verifier` et `bin/nettoyer`
  deviennent des relais vers `ocots-lint` (ou sont dépréciés), README mis à
  jour.
- [ ] **S2.8** — Release `v0.2.0`.

## Bilan

*À écrire en fin de sprint.*
