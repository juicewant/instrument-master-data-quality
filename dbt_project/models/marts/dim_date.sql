with bounds as (
    select min(d) as start_date, max(d) as end_date
    from (
        select snapshot_date as d from {{ ref('stg_customers') }}
        union all
        select created_date from {{ ref('stg_change_requests') }}
        union all
        select resolved_date from {{ ref('stg_change_requests') }}
    ) all_dates
)

select
    d::date as date_day,
    extract(year from d)::int as year,
    extract(month from d)::int as month,
    to_char(d, 'YYYY-MM') as year_month,
    trim(to_char(d, 'Month')) as month_name,
    to_char(d, 'Dy') as day_name,
    d::date = (date_trunc('month', d) + interval '1 month - 1 day')::date as is_month_end
from bounds,
     generate_series(bounds.start_date, bounds.end_date, interval '1 day') as d