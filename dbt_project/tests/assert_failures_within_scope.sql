select scorecard_key, failed_records, checks_performed
from {{ ref('fct_dq_scorecard') }}
where failed_records > checks_performed