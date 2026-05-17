# Publier sur GitHub

Le dépôt local est prêt (`git` initialisé, commit sur `main`).

## Étape 1 — Connexion GitHub (une fois)

```powershell
gh auth login
```

Choisir : GitHub.com → HTTPS → Login with browser.

## Étape 2 — Créer le dépôt et pousser

```powershell
cd "c:\Users\Jeanne\Documents\OCR\Projet 08\projet8_ocr"
powershell -ExecutionPolicy Bypass -File .\scripts\push_to_github.ps1
```

Dépôt par défaut : **`ocr-projet8-dbt`** (privé). Autre nom :

```powershell
.\scripts\push_to_github.ps1 -RepoName "mon-nom-repo" -Visibility public
```

## Importer dans Snowflake / dbt Cloud

1. **dbt Cloud** : Settings → Git → connecter le repo → sous-dossier racine = `/` (racine du repo).
2. **Snowflake** : les données sont chargées via `dbtf seed` (fichier `seeds/students_raw.csv` dans le repo).
3. Copier [profiles.yml.example](profiles.yml.example) vers `~/.dbt/profiles.yml` et renseigner les secrets (jamais dans Git).

## Fichiers exclus du dépôt (`.gitignore`)

- `target/`, `logs/`, `profiles.yml`, credentials
