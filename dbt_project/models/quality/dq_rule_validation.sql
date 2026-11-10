with detected as (
    select snapshot_date, table_name, record_id, rule_code as defect_type
    from {{ ref('dq_issues') }}
),

truth as (
    select snapshot_date, table_name, record_id, defect_type
    from {{ ref('stg_ground_truth_defects') }}
),

compared as (
    select
        coalesce(d.defect_type, t.defect_type) as rule_code,
        d.record_id is not null as was_detected,
        t.record_id is not null as was_injected
    from detected d
    full outer join truth t
        on t.snapshot_date = d.snapshot_date
       and t.table_name = d.table_name
       and t.record_id = d.record_id
       and t.defect_type = d.defect_type
),

counts as (
    select
        rule_code,
        count(*) filter (where was_detected and was_injected) as true_positives,
        count(*) filter (where was_detected and not was_injected) as false_positives,
        count(*) filter (where not was_detected and was_injected) as false_negatives
    from compared
    group by 1
)

select
    rule_code,
    true_positives,
    false_positives,
    false_negatives,
    round(100.0 * true_positives / nullif(true_positives + false_positives, 0), 1) as precision_pct,
    round(100.0 * true_positives / nullif(true_positives + false_negatives, 0), 1) as recall_pct
from counts
order by rule_code