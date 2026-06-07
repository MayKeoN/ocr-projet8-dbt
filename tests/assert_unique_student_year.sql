-- Test: each user_id + year_path_started combination must be unique
-- A student can appear multiple times across years (longitudinal data)
-- but never twice in the same year.

select
    user_id,
    year_path_started,
    count(*) as n
from {{ ref('stg_students') }}
group by user_id, year_path_started
having count(*) > 1