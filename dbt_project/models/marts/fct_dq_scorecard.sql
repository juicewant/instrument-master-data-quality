with scope as (
    select snapshot_date, 'customers' as table_name, 'ALL' as scope_key, region, count(*) as records
    from {{ ref('stg_customers') }}
    group by 1, 4

    union all

    select snapshot_date, 'materials', 'ALL', 'GLOBAL', count(*)
    from {{ ref('stg_materials') }}
    group by 1

    union all

    -- services legitimately have no weight, so the weight rule only covers physical items
    select snapshot_date, 'materials', 'PHYSICAL', 'GLOBAL', count(*)
    from {{ ref('stg_materials') }}
    where material_type in ('INSTRUMENT', 'ACCESSORY', 'SPARE_PART')
    group by 1

    union all

    select a.snapshot_date, 'installed_base', 'ALL', coalesce(c.region, 'UNKNOWN'), count(*)
    from {{ ref('stg_installed_base') }} a
    left join {{ ref('stg_customers') }} c
        on c.snapshot_date = a.snapshot_date
       and c.customer_id = a.customer_id
    group by 1, 4
),

rules as (
    select
        rule_code, table_name, quality_dimension, severity,
        case when rule_code = 'MISSING_WEIGHT' then 'PHYSICAL' else 'ALL' end as scope_key
    from {{ ref('dim_rule') }}
),

failures as (
    select snapshot_date, rule_code, region, count(*) as failed_records
    from {{ ref('fct_dq_issue') }}
    group by 1, 2, 3
)

select
    s.snapshot_date::text || '|' || r.rule_code || '|' || s.region as scorecard_key,
    s.snapshot_date,
    r.rule_code,
    r.table_name,
    r.quality_dimension,
    r.severity,
    s.region,
    s.records as checks_performed,
    coalesce(f.failed_records, 0) as failed_records,
    round(100.0 * (1 - coalesce(f.failed_records, 0)::numeric / s.records), 2) as pass_rate_pct
from rules r
join scope s
    on s.table_name = r.table_name
   and s.scope_key = r.scope_key
left join failures f
    on f.snapshot_date = s.snapshot_date
   and f.rule_code = r.rule_code
   and f.region = s.region