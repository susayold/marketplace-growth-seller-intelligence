# Power BI — final stage only

The Power BI semantic model and six-page layout are specified in the execution plan, metric dictionary and SQL-to-Power BI reconciliation protocol.

Required pages:
1. Executive Marketplace Health
2. Seller Acquisition Funnel
3. Seller Activation & Retention
4. Commercial Performance
5. Customer & Operations
6. Diagnostic / Seller 360

The PBIX, dashboard PDF and reports/qa/powerbi_reconciliation.csv remain intentionally pending because the user requested Power BI last. All upstream marts, charts, notebook evidence, SQL metric definitions, diagrams and QA artifacts are ready for that final stage.



## Build pack

The remote hand-off pack is now available at [`powerbi/implementation_pack.md`](implementation_pack.md) with the canonical DAX in [`powerbi/measures.dax`](measures.dax). The reconciliation template is at [`reports/qa/powerbi_reconciliation.csv`](../reports/qa/powerbi_reconciliation.csv).

The actual PBIX, PDF export, and measured reconciliation remain pending until Power BI Desktop is available. The template intentionally uses `BLOCKED_DESKTOP_NOT_INSTALLED`; it must be replaced with measured Power BI values and `PASS`/`FAIL` statuses after the six-page report is built and validated.
