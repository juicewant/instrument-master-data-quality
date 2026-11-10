-- Fails the build if any rule misses injected defects or flags clean records (below 95%)
select rule_code, precision_pct, recall_pct
from {{ ref('dq_rule_validation') }}
where coalesce(precision_pct, 0) < 95
   or coalesce(recall_pct, 0) < 95