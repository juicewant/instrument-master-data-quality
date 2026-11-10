with customers as (
    select * from {{ ref('stg_customers') }}
),

countries as (
    select * from {{ ref('ref_countries') }}
),

-- Map whatever was typed (ISO2, ISO3 or a country name) to the reference country.
-- Used only inside the rules: the data itself is never repaired.
normalized as (
    select
        c.*,
        r.iso2 as country_iso2,
        r.expected_currency,
        r.postal_regex,
        regexp_replace(
            regexp_replace(lower(c.customer_name), '[^a-z0-9]', '', 'g'),
            '(ltd|limited|inc|llc|plc|group|gmbh)+$', ''
        ) as name_key
    from customers c
    left join countries r
        on upper(c.country_code) in (r.iso2, r.iso3, upper(r.country_name))
),

ranked as (
    select
        *,
        row_number() over (
            partition by snapshot_date, name_key, country_iso2, city
            order by customer_id
        ) as dup_rank
    from normalized
)

select snapshot_date, customer_id as record_id, region, 'MISSING_TAX_ID' as rule_code
from ranked
where tax_id is null or trim(tax_id) = ''

union all

select snapshot_date, customer_id, region, 'INVALID_EMAIL'
from ranked
where email is null
   or email !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

union all

select snapshot_date, customer_id, region, 'COUNTRY_FORMAT'
from ranked
where country_code is null or country_code !~ '^[A-Z]{2}$'

union all

select snapshot_date, customer_id, region, 'INVALID_POSTAL_CODE'
from ranked
where postal_regex is not null
  and (postal_code is null or postal_code !~ postal_regex)

union all

select snapshot_date, customer_id, region, 'CURRENCY_MISMATCH'
from ranked
where expected_currency is not null and currency <> expected_currency

union all

select snapshot_date, customer_id, region, 'PAYMENT_TERMS_FORMAT'
from ranked
where payment_terms is null
   or payment_terms not in ('NET30', 'NET45', 'NET60', 'PREPAY')

union all

select snapshot_date, customer_id, region, 'DUPLICATE_CUSTOMER'
from ranked
where dup_rank > 1