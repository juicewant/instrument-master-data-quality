Checks Performed = SUM(fct_dq_scorecard[checks_performed])

Failed Checks = SUM(fct_dq_scorecard[failed_records])

Pass Rate % = DIVIDE([Checks Performed] - [Failed Checks], [Checks Performed])

Issues per 1000 Checks = DIVIDE([Failed Checks], [Checks Performed]) * 1000

Latest Snapshot = CALCULATE(MAX(fct_dq_scorecard[snapshot_date]), ALL(fct_dq_scorecard))

First Snapshot = CALCULATE(MIN(fct_dq_scorecard[snapshot_date]), ALL(fct_dq_scorecard))

Latest Pass Rate % =
VAR snap = [Latest Snapshot]
RETURN
    CALCULATE([Pass Rate %], fct_dq_scorecard[snapshot_date] = snap)

First Pass Rate % =
VAR snap = [First Snapshot]
RETURN
    CALCULATE([Pass Rate %], fct_dq_scorecard[snapshot_date] = snap)

Pass Rate Change (pts) = ([Latest Pass Rate %] - [First Pass Rate %]) * 100

Latest Issues =
VAR snap = [Latest Snapshot]
RETURN
    CALCULATE(COUNTROWS(fct_dq_issue), fct_dq_issue[snapshot_date] = snap)

First Issues =
VAR snap = [First Snapshot]
RETURN
    CALCULATE(COUNTROWS(fct_dq_issue), fct_dq_issue[snapshot_date] = snap)

Issue Reduction % = DIVIDE([First Issues] - [Latest Issues], [First Issues])

Latest High Severity Issues =
CALCULATE([Latest Issues], dim_rule[severity] = "High")

Requests = COUNTROWS(fct_change_request)

Closed Requests = CALCULATE([Requests], fct_change_request[is_closed] = TRUE())

Open Requests = [Requests] - [Closed Requests]

Avg Resolution Days =
CALCULATE(AVERAGE(fct_change_request[age_days]), fct_change_request[is_closed] = TRUE())

Avg Age of Open Requests =
CALCULATE(AVERAGE(fct_change_request[age_days]), fct_change_request[is_closed] = FALSE())

SLA Compliance % =
DIVIDE(
    CALCULATE([Requests], fct_change_request[is_closed] = TRUE(), fct_change_request[within_sla] = TRUE()),
    [Closed Requests]
)

Records Needing Action =
CALCULATE(COUNTROWS(dq_worklist), dq_worklist[has_open_request] = FALSE())