# Lier projet8_ocr à dbt Cloud (projet P9)

1. Ouvrir [dbt Cloud](https://ph982.us1.dbt.com/) — projet **P9** (voir `dbt_cloud.yml` à la racine Projet 08).
2. **Settings → Project setup** : définir le sous-dossier Git / répertoire de projet sur `projet8_ocr` (ou pousser ce dossier seul vers le repo connecté).
3. **Settings → Environments → Development** : même connexion Snowflake que le profil local `projet8_ocr` (`analytics`, warehouse `compute_wh`).
4. Dans l’IDE Cloud : `dbt seed` puis `dbt build`.
5. Documenter l’URL du job réussi pour le livrable 2.

Profil local déjà configuré dans `~/.dbt/profiles.yml` — ne pas commiter les mots de passe.
