with source as (
    select * from {{ ref('insee_population') }}
),

renamed as (
    select
        cast(year as integer)      as year,
        region,
        age_group,
        gender,
        cast(population as integer) as population
    from source
)

select * from renamed