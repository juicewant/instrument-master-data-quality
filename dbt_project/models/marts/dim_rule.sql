select
    rule_code,
    table_name,
    quality_dimension,
    severity,
    case severity when 'High' then 3 when 'Medium' then 2 else 1 end as severity_weight,
    description
from {{ ref('dq_rules') }}