# projet8_ocr — Pipeline dbt (Mission OCR Projet 8)

Analyse de l'évolution du profil sociodémographique des étudiants Data OpenClassrooms (2022-2025).

## Prérequis

- Profil Snowflake : [profiles.yml](profiles.yml) (copier vers `~/.dbt/profiles.yml` ou `set DBT_PROFILES_DIR` sur ce dossier)
- dbt-fusion : `dbtf --version`

## GitHub / Snowflake

1. Cloner ce dépôt (ou connecter à dbt Cloud).
2. Configurer `~/.dbt/profiles.yml` depuis `profiles.yml.example`.
3. `dbtf seed` puis `dbtf build` — les données mission sont dans `seeds/students_raw.csv`.

## Commandes

```powershell
cd "c:\Users\Jeanne\Documents\OCR\Projet 08\projet8_ocr"
dbtf debug
dbtf seed
dbtf run
dbtf test
dbtf docs generate
```

## Structure

| Couche | Modèles | Schéma Snowflake (suffixe) |
|--------|---------|----------------------------|
| Seed | `students_raw` | `_raw` |
| Staging | `stg_students` | `_staging` |
| Intermediate | `int_students_by_year_region` | `_staging` |
| Marts | `mart_demographic_evolution`, `mart_student_detail` | `_analytics` |

## Export CSV livrable

Requête sur `mart_student_detail` ou `mart_demographic_evolution` dans Snowflake, ou :

```powershell
dbtf show --select mart_student_detail --limit 5000
```

## dbt Cloud

Voir [DBT_CLOUD_LINK.md](DBT_CLOUD_LINK.md) à la racine de Projet 08.
