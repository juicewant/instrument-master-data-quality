select
    request_id,
    record_type,
    record_id,
    reason,
    region,
    priority,
    created_date::date as created_date,
    resolved_date::date as resolved_date,
    status
from {{ source('raw', 'change_requests') }}