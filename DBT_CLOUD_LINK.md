# Lier projet8_ocr à dbt Cloud

1. Ouvrir [dbt Cloud](https://ph982.us1.dbt.com/) — projet **projet8_ocr** (ID `70506183139824`, voir `dbt_cloud.yml` à la racine Projet 08).
2. **Settings → Project setup** : connecter le dépôt `MayKeoN/ocr-projet8-dbt` (racine = contenu de ce dossier).
3. **Settings → Environments → Development** : même connexion Snowflake que le profil local `projet8_ocr` (`analytics`, warehouse `compute_wh`).
4. Dans l'IDE Cloud :
   - **OCR** (racine du repo) : `dbt seed` puis `dbt build`
   - **Tutorial** : `cd dbt_fundamentals && dbt build`
5. Documenter l'URL du job réussi pour le livrable 2.

Profil local : copier `profiles.yml.example` vers `~/.dbt/profiles.yml` — ne pas commiter les mots de passe.
