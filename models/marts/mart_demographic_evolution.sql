-- Mart analytique: évolution sociodémographique par année, région, âge et genre.
-- Inclut le taux de rétention (nouveaux vs étudiants de retour) par groupe.
with base as (
    select * from {{ ref('int_students_by_year_region') }}
),

year_totals as (
    -- Total enrollments per year, used to compute demographic share
    select
        year_path_started,
        sum(student_count) as total_students_year
    from base
    group by 1
),

enriched as (
    select
        b.year_path_started,
        b.region,
        b.age_group,
        b.gender,
        b.has_gender_reported,
        b.student_count,
        b.new_student_count,
        b.returning_student_count,
        y.total_students_year,
        -- Share of this demographic group within the year
        round(100.0 * b.student_count / nullif(y.total_students_year, 0), 2) as pct_of_year,
        -- Retention rate: share of this group that are returning students
        round(100.0 * b.returning_student_count / nullif(b.student_count, 0), 2) as pct_returning
    from base as b
    inner join year_totals as y
        on b.year_path_started = y.year_path_started
)

select * from enriched