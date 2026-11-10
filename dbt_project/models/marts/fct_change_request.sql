with as_of as (
    select max(snapshot_date) as as_of_date from {{ ref('stg_customers') }}
)

select
    cr.request_id,
    cr.record_type,
    cr.record_id,
    cr.reason as rule_code,
    cr.region,
    cr.priority,
    cr.status,
    cr.created_date,
    cr.resolved_date,
    cr.status = 'CLOSED' as is_closed,
    -- SLA targets are an assumption for this project: High 7 days, Medium 14, Low 21
    case cr.priority when 'HIGH' then 7 when 'MEDIUM' then 14 else 21 end as sla_days,
    coalesce(cr.resolved_date, a.as_of_date) - cr.created_date as age_days,
    (coalesce(cr.resolved_date, a.as_of_date) - cr.created_date)
        <= case cr.priority when 'HIGH' then 7 when 'MEDIUM' then 14 else 21 end as within_sla
from {{ ref('stg_change_requests') }} cr
cross join as_of a