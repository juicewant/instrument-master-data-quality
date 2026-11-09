select
    snapshot_date::date as snapshot_date,
    table_name,
    record_id,
    defect_type
from {{ source('raw', 'ground_truth_defects') }}