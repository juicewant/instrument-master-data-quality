with materials as (
    select
        *,
        row_number() over (
            partition by snapshot_date, lower(trim(description))
            order by material_id
        ) as dup_rank
    from {{ ref('stg_materials') }}
)

select snapshot_date, material_id as record_id, 'GLOBAL' as region, 'MISSING_UOM' as rule_code
from materials
where base_uom is null or trim(base_uom) = ''

union all

select snapshot_date, material_id, 'GLOBAL', 'INVALID_UOM'
from materials
where base_uom is not null
  and trim(base_uom) <> ''
  and base_uom not in ('EA', 'KG', 'H')

union all

-- services legitimately have no weight, so only physical items are checked
select snapshot_date, material_id, 'GLOBAL', 'MISSING_WEIGHT'
from materials
where material_type in ('INSTRUMENT', 'ACCESSORY', 'SPARE_PART')
  and (weight_kg is null or weight_kg <= 0)

union all

select snapshot_date, material_id, 'GLOBAL', 'DUPLICATE_MATERIAL'
from materials
where dup_rank > 1