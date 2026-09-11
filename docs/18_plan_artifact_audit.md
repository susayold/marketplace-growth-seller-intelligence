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

## Still pending / not fabricated

- powerbi/marketplace_growth_seller_intelligence.pbix: requires an authenticated Power BI Desktop/Web authoring runtime.
- Power BI PDF export, measured slicer/drill-through QA, and PASS values in reports/qa/powerbi_reconciliation.csv remain pending for the same reason.

## Current decision

Do not tag the project as fully complete yet. The non-Power-BI evidence is publishable and the remaining gaps are explicit runtime/artifact gaps, not hidden assumptions. When an authenticated Power BI authoring session is available, build the six pages, run reconciliation, and update this audit.
