select
    customer_id || '|' || snapshot_date as customer_snapshot_key,
    customer_id,
    customer_name,
    country_code,
    region,
    city,
    postal_code,
    tax_id,
    email,
    industry,
    payment_terms,
    currency,
    sales_org,
    status,
    created_date::date as created_date,
    snapshot_date::date as snapshot_date
from {{ source('raw', 'customers') }}