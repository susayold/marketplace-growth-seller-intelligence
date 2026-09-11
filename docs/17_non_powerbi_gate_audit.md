# Non-Power-BI completion audit

Audit scope: every plan phase that can be completed before Power BI.

| Requirement | Current evidence | Result |
|---|---|---|
| Source inventory and profiling | reports/qa/raw_inventory.csv, reports/qa/data_profile_summary.csv | Verified |
| Grain and fan-out control | reports/qa/fanout_audit.csv, sql/06_quality/q01_fanout_audit.sql, tests/test_reconciliation.py | Verified |
| Raw ingestion | src/build_database.py loads all 10 governed raw tables from the two ZIP archives through PostgreSQL COPY | Implemented |
| Staging, dimensions and facts | sql/02_staging through sql/04_facts | Implemented |
| Analytical marts | reports/tables and sql/05_marts | Verified |
| Seller funnel, activation, retention and segmentation | mart_acquisition_channel, activation_summary, mart_seller_cohort, seller_activation, seller concentration outputs | Verified |
| Customer and operations analytics | customer_repeat_summary, mart_order_experience, category/geography outputs | Verified |
| Statistical validation | reports/qa/statistical_validation.csv and notebooks/06_statistical_validation.ipynb | Verified; associative only |
| Root causes and decisions | docs/09_root_cause_cases.md and docs/10_executive_decisions.md | Verified |
| SQL portfolio coverage | 31 PostgreSQL-parsed SQL files; real joins, CTEs, CASE, windows, percentile, cohort, funnel and reconciliation logic | Verified |
| Python portfolio coverage | reusable ingestion, COPY loader, config/env handling, validation, logging, tests, exports and asset generation | Verified |
| Reproducibility and QA | Makefile, CI workflow, six executed notebooks, nine tests, pipeline log, release manifest | Verified |
| Remote-only artifact storage | raw archives and all data/chart/report artifacts in Drive; code and reviewable artifacts in GitHub | Verified |
| Power BI | PBIX, six pages and SQL-to-Power BI reconciliation | Deliberately deferred to final stage |

The PostgreSQL command is credential-driven through PGHOST, PGPORT, PGDATABASE, PGUSER and PGPASSWORD. No credential is stored in the repository. Power BI is the only plan area intentionally left for the final stage.

