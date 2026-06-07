with students as (
    select * from {{ ref('mart_demographic_evolution') }}
),

insee as (
    select
        year,
        region,
        age_group,
        gender,
        population
    from {{ ref('stg_insee_population') }}
),

joined as (
    select
        s.year_path_started,
        s.region,
        s.age_group,
        s.gender,
        s.student_count,
        s.total_students_year,
        s.pct_of_year,
        i.population as regional_population,
        round(
            100000.0 * s.student_count / nullif(i.population, 0),
            4
        ) as students_per_100k_inhabitants
    from students as s
    left join insee as i
        on s.year_path_started = i.year
        and s.region = i.region
        and s.age_group = i.age_group
        and s.gender = i.gender
)

select * from joined