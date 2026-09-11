# Plan completion matrix

Last verified after the non-Power-BI build pass.

| Plan area | Evidence | Status |
|---|---|---|
| Business case/questions | docs/01_business_context.md, README | Complete |
| Raw inventory/profiling | reports/qa/raw_inventory.csv, reports/qa/data_profile_summary.csv | Complete |
| Grain/fan-out audit | reports/qa/fanout_audit.csv, sql/06_quality/q01_fanout_audit.sql | Complete |
| Raw/staging/dimensions/facts | sql/01_raw through sql/04_facts, src/build_database.py | Complete as PostgreSQL-compatible definitions; execution requires configured PG credentials |
| Metric dictionary | docs/05_metric_dictionary.md | Complete |
| Marketplace/seller/customer/operations marts | reports/tables, sql/05_marts | Complete |
| Statistical validation | reports/qa/statistical_validation.csv, notebooks/06_statistical_validation.ipynb | Complete; association only, not causality |
| Root causes/decisions | docs/09_root_cause_cases.md, docs/10_executive_decisions.md | Complete |
| Reproducibility/logging/testing | src, tests, .github/workflows/ci.yml, reports/qa/pipeline_run.log | Complete |
| Career packaging | docs/12_interview_guide.md, docs/13_cv_bullets.md | Complete except Power BI bullet finalization |
| Power BI semantic model/pages/reconciliation | powerbi/README.md | Pending by user instruction; intentionally last |

