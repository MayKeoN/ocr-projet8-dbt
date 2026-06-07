-- Staging: nettoyage et déduplication des inscriptions OCR Data (2022-2025)
-- RGPD: USER_ID est pseudonymisé. Aucune donnée nominative présente.
-- Données longitudinales conservées: un étudiant peut apparaître sur plusieurs années.

with source as (
    select * from {{ source('ocr_raw', 'students_raw') }}
),

renamed as (
    select
        "USER_ID" as user_id,
        "PATH_CATEGORY_NAME" as path_category_name,
        "AGE_GROUP" as age_group,
        nullif(trim("GENDER"), '') as gender_raw,
        "REGION" as region,
        try_to_number("YEAR_PATH_STARTED") as year_path_started
    from source
),

cleaned as (
    select
        user_id,
        path_category_name,
        age_group,
        coalesce(gender_raw, 'Non renseigné') as gender,  -- Genre: remplace les valeurs vides par 'Non renseigné' (RGPD: pas d'imputation)
        gender_raw is not null as has_gender_reported,
        region,
        year_path_started,
        year_path_started::varchar as year_path_started_str
    from renamed
    where path_category_name = 'Data'
        and year_path_started in (2022, 2023, 2024, 2025)
),

deduped as (
    select
        *,
        -- Déduplication par user_id × année: supprime les vrais doublons (même étudiant, même année)
        -- Un étudiant inscrit sur plusieurs années conserve une ligne par année (données longitudinales)
        row_number() over (
            partition by user_id, year_path_started
            order by user_id
        ) as row_num
    from cleaned
)

select
    user_id,
    path_category_name,
    age_group,
    gender,
    has_gender_reported,
    region,
    year_path_started,
    year_path_started_str
from deduped
where row_num = 1
