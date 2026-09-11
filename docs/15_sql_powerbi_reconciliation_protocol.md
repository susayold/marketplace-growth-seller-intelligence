# SQL to Power BI reconciliation protocol

This is the final-stage checklist, intentionally left executable after the Power BI model is built.

1. Load only dimension/fact/mart tables with documented grain.
2. Bind every KPI to the metric dictionary; never rebuild GMV from payment joins.
3. Reconcile total GMV proxy, orders, active sellers, AOV, repeat rate, activation and late-delivery rate against the CSV marts.
4. Export one row per metric with SQL value, Power BI value, absolute difference, relative difference, tolerance and pass/fail.
5. Validate all six pages, slicers, cohort eligibility, drill-through and tooltips.
6. Save the reconciliation CSV under reports/qa/powerbi_reconciliation.csv and upload it to Drive only after the PBIX is available.

