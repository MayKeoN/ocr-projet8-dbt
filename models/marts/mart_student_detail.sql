-- Mart détail: une ligne par étudiant par année d'inscription (données longitudinales)
-- RGPD: données pseudonymisées — USER_ID est un identifiant technique,
-- aucune donnée nominative, aucune adresse, aucun contact présent.
-- Livrable 1 OCR: ce modèle est la source du fichier CSV exporté.

select
    user_id,
    age_group,
    gender,
    has_gender_reported,
    region,
    year_path_started,
    -- Longitudinal flag: is this student's first year or a return?
    min(year_path_started) over (partition by user_id) as first_year,
    -- TRUE si l'étudiant était déjà inscrit une année précédente
    case 
        when year_path_started = min(year_path_started) over (partition by user_id) 
        then false else true 
    end as is_returning_student
from {{ ref('stg_students') }}