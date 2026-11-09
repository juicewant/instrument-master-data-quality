select
    material_id || '|' || snapshot_date as material_snapshot_key,
    material_id,
    description,
    material_type,
    product_group,
    base_uom,
    weight_kg::numeric(10, 2) as weight_kg,
    snapshot_date::date as snapshot_date
from {{ source('raw', 'materials') }}