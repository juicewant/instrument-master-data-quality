select s.total_in_scorecard, i.total_issues
from (select sum(failed_records) as total_in_scorecard from {{ ref('fct_dq_scorecard') }}) s
cross join (select count(*) as total_issues from {{ ref('fct_dq_issue') }}) i
where s.total_in_scorecard <> i.total_issues