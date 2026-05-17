select
    user_id,
    age_group,
    gender,
    has_gender_reported,
    region,
    year_path_started
from {{ ref('stg_students') }}
