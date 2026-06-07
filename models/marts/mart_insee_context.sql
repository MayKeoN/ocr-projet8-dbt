-- Mart contextuel: jointure étudiants × population INSEE par région, groupe d'âge et genre.
-- Calcule le taux de pénétration (inscriptions pour 100 000 habitants).
-- Limitations connues du LEFT JOIN (résidu NULLs après normalisation):
--   1. Années 2024-2025: données INSEE non encore disponibles
--   2. Région DROM: non couverte par les estimations métropolitaines INSEE
-- Note: Genre 'Non renseigné' contextualisé sur population totale M+F (approche conservative)

with students as (
    select * from {{ ref('mart_demographic_evolution') }}
),

insee as (
    -- Population par genre (M/F) pour jointure sur étudiants au genre connu
    select
        year,
        region,
        age_group,
        gender,
        population
    from {{ ref('stg_insee_population') }}
),

insee_total as (
    -- Population totale M+F par région/âge/année
    -- Utilisée comme dénominateur pour les étudiants au genre non renseigné
    select
        year,
        region,
        age_group,
        sum(population) as population
    from {{ ref('stg_insee_population') }}
    group by 1, 2, 3
),

joined as (
    select
        s.year_path_started,
        s.region,
        s.age_group,
        s.gender,
        s.student_count,
        s.new_student_count,
        s.returning_student_count,
        s.total_students_year,
        s.pct_of_year,
        s.pct_returning,
        -- Pour genre connu: population genrée INSEE
        -- Pour 'Non renseigné': population totale M+F du groupe région/âge/année
        -- Pour 2024/2025 et DROM: NULL (données indisponibles)
        coalesce(i.population, t.population) as regional_population,
        -- Taux d'inscription pour 100 000 habitants dans ce groupe démographique
        round(
            100000.0 * s.student_count / nullif(coalesce(i.population, t.population), 0),
            4
        ) as students_per_100k_inhabitants
    from students as s
    left join insee as i
        on s.year_path_started = i.year
        and s.region = i.region
        and s.age_group = i.age_group
        and s.gender = i.gender
    left join insee_total as t
        on s.year_path_started = t.year
        and s.region = t.region
        and s.age_group = t.age_group
        and s.gender = 'Non renseigné'
)

select * from joined