select
    issue_key,
    snapshot_date,
    rule_code,
    table_name,
    record_id,
    region
from {{ ref('dq_issues') }}