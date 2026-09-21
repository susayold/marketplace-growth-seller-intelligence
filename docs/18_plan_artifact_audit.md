# Current plan artifact audit

Run date: 2026-09-12

This audit separates explicit user instructions from the attached execution blueprint. The user instruction is authoritative for storage and sequencing: keep data/results/charts remote in Drive and GitHub, and do Power BI last. The blueprint defines the technical scope and acceptance gates.

## Verified complete

- Drive project folder and subfolders exist; raw archives and generated artifacts are remote.
- GitHub repository contains source SQL, Python, notebooks, documentation, charts, PDF, QA evidence, and the Power BI implementation pack.
- Clean rebuild evidence covers 10 raw tables, 1,559,693 loaded rows, 32 SQL files, zero warnings/errors, key tests, fan-out detection, and grain-safe GMV reconciliation.
- Daily and seller-month SQL definitions are present and pass PostgreSQL static parsing; the parameterized Python build script reproduces the published CSVs.
- Analytical tables are present for marketplace monthly, seller lifetime, cohorts, acquisition channel, activation, retention by origin, category, geography, order experience, customer repeat, concentration, growth decomposition, and seller segmentation.
- Derived plan outputs now added: daily marketplace, seller-month, time-to-first-sale, Pareto seller curve, delivery-performance summary, and automated test report.

## Newly completed

- reports/tables/mart_marketplace_daily.csv: 616 daily rows and GMV proxy 13,591,643.70.
- reports/tables/mart_seller_monthly.csv: 16,441 seller-month rows and GMV proxy 13,591,643.70.

## Final release artifacts

- `deliverables/powerbi/final market dashboard.pbip` is the editable Power BI
  project used for the final release.
- `deliverables/final-market-dashboard.pdf` contains seven verified pages, and
  `reports/qa/powerbi_reconciliation.csv` contains measured PASS values.

## Current decision

The Power BI runtime gate is complete. Freeze the analytical, PBIP, PDF, and
website artifacts at the final release tag; keep observational limitations and
the historical reporting boundary explicit.
