select
    year_path_started,
    region,
    age_group,
    gender,
    has_gender_reported,
    count(*) as student_count
from {{ ref('stg_students') }}
group by 1, 2, 3, 4, 5
