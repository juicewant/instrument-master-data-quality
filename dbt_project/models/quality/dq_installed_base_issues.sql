with assets as (
    select * from {{ ref('stg_installed_base') }}
),

customers as (
    select snapshot_date, customer_id, region
    from {{ ref('stg_customers') }}
),

enriched as (
    select
        a.*,
        c.customer_id as matched_customer_id,
        coalesce(c.region, 'UNKNOWN') as region,
        row_number() over (
            partition by a.snapshot_date, a.serial_number
            order by a.asset_id
        ) as serial_rank
    from assets a
    left join customers c
        on c.snapshot_date = a.snapshot_date
       and c.customer_id = a.customer_id
)

select snapshot_date, asset_id as record_id, region, 'ORPHAN_CUSTOMER' as rule_code
from enriched
where matched_customer_id is null

union all

select snapshot_date, asset_id, region, 'CALIBRATION_BEFORE_INSTALL'
from enriched
where next_calibration_due < install_date

union all

select snapshot_date, asset_id, region, 'DUPLICATE_SERIAL'
from enriched
where serial_rank > 1