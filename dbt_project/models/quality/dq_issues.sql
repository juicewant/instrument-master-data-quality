with all_issues as (
    select 'customers' as table_name, snapshot_date, record_id, region, rule_code
    from {{ ref('dq_customer_issues') }}

    union all

    select 'materials', snapshot_date, record_id, region, rule_code
    from {{ ref('dq_material_issues') }}

    union all

    select 'installed_base', snapshot_date, record_id, region, rule_code
    from {{ ref('dq_installed_base_issues') }}
)

select
    snapshot_date::text || '|' || record_id || '|' || rule_code as issue_key,
    snapshot_date,
    table_name,
    record_id,
    region,
    rule_code
from all_issues