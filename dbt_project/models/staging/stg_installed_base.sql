select
    asset_id || '|' || snapshot_date as asset_snapshot_key,
    asset_id,
    serial_number,
    material_id,
    customer_id,
    install_date::date as install_date,
    warranty_end_date::date as warranty_end_date,
    last_calibration_date::date as last_calibration_date,
    next_calibration_due::date as next_calibration_due,
    snapshot_date::date as snapshot_date
from {{ source('raw', 'installed_base') }}