with latest as (
    select max(snapshot_date) as snapshot_date from {{ ref('fct_dq_issue') }}
),

issues as (
    select i.table_name, i.record_id, i.region, i.rule_code, r.severity_weight
    from {{ ref('fct_dq_issue') }} i
    join latest l on l.snapshot_date = i.snapshot_date
    join {{ ref('dim_rule') }} r on r.rule_code = i.rule_code
),

record_names as (
    select 'customers' as table_name, customer_id as record_id, customer_name as record_name
    from {{ ref('stg_customers') }}
    where snapshot_date = (select snapshot_date from latest)

    union all

    select 'materials', material_id, description
    from {{ ref('stg_materials') }}
    where snapshot_date = (select snapshot_date from latest)

    union all

    select 'installed_base', asset_id, serial_number
    from {{ ref('stg_installed_base') }}
    where snapshot_date = (select snapshot_date from latest)
),

open_requests as (
    select record_id, count(*) as open_requests
    from {{ ref('stg_change_requests') }}
    where status <> 'CLOSED'
    group by 1
)

select
    i.table_name,
    i.record_id,
    n.record_name,
    i.region,
    count(*) as issue_count,
    sum(i.severity_weight) as priority_score,
    string_agg(i.rule_code, ', ' order by i.rule_code) as failed_rules,
    coalesce(o.open_requests, 0) > 0 as has_open_request
from issues i
left join record_names n
    on n.table_name = i.table_name and n.record_id = i.record_id
left join open_requests o
    on o.record_id = i.record_id
group by i.table_name, i.record_id, n.record_name, i.region, o.open_requests
order by priority_score desc, issue_count desc