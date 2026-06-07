-- Intermédiaire: agrégation des étudiants par année × région × âge × genre
-- Calcule les effectifs totaux, nouveaux et de retour par groupe démographique
-- Utilisé comme base par mart_demographic_evolution

with base as (
    select
        *,
        min(year_path_started) over (partition by user_id) as first_year
    from {{ ref('stg_students') }}
),

aggregated as (
    select
        year_path_started,
        region,
        age_group,
        gender,
        has_gender_reported,
        count(*) as student_count,  -- Total enrollments for this demographic group in this year
        count(case when year_path_started = first_year then 1 end) as new_student_count,  -- New students: first time appearing in the dataset
        count(case when year_path_started > first_year then 1 end) as returning_student_count  -- Returning students: enrolled in a previous year as well
    from base
    group by 1, 2, 3, 4, 5
)

select * from aggregated