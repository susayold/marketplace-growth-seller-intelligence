# SQL to Power BI reconciliation protocol

This is the final-stage checklist used to validate the released PBIP model. The
completed evidence is recorded in `reports/qa/powerbi_reconciliation.csv`.

1. Load only dimension/fact/mart tables with documented grain.
2. Bind every KPI to the metric dictionary; never rebuild GMV from payment joins.
3. Reconcile total GMV proxy, orders, active sellers, AOV, repeat rate, activation and late-delivery rate against the CSV marts.
4. Export one row per metric with SQL value, Power BI value, absolute difference, relative difference, tolerance and pass/fail.
5. Validate all seven pages, slicers, cohort eligibility, drill-through and tooltips.
6. Save the reconciliation CSV under reports/qa/powerbi_reconciliation.csv with measured PBIP values; the final release has completed this gate.

