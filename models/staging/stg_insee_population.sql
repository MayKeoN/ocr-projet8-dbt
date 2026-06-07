-- Staging: nettoyage de la seed INSEE (estimations de population par région/âge/genre)
-- Source: INSEE, séries par région, sexe et âge quinquennal — données 2022-2023
-- Cast des colonnes numériques depuis varchar (format seed CSV)

with source as (
    select * from {{ ref('insee_population') }}
),

renamed as (
    select
        cast(year as integer)      as year,  -- Cast year et population depuis varchar (format brut seed CSV)
        region,
        age_group,
        gender,
        cast(population as integer) as population
    from source
)

select * from renamed