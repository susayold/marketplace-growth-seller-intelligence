# Marketplace Growth & Seller Intelligence

Historical Olist case study focused on seller acquisition → activation → retention → commercial value → customer experience.

## Execution status

Non-Power-BI scope is complete and released as a reproducible v1.2 package with seller segmentation and full statistical validation. The only intentionally pending area is the six-page Power BI build and the final SQL ↔ Power BI reconciliation.

## Evidence-backed findings

- GMV proxy: R$ 13,591,644; orders: 98,666; sellers: 3,095.
- Repeat customer rate: 3.1%.
- Top 20% seller GMV proxy share: 82.7%.
- Activation within 90 days among valid closed-seller links: 87.5%.
- M3 seller retention is available by acquisition origin with eligibility-aware denominators.
- Naive item × payment GMV overstates the grain-safe item GMV by R$617,472, or 4.54%.

## Repository map

- src: ingestion, profiling, PostgreSQL loading, mart build, reconciliation, validation and release-manifest entrypoints.
- sql: raw, staging, dimensions, facts, marts, quality audits, analysis modules and exports.
- notebooks: six executable analysis notebooks with embedded tables and figures.
- reports/tables: decision-facing marts, seller segmentation and retention-by-origin outputs.
- reports/qa: statistical tests with confidence intervals, effect sizes, robustness checks and reconciliation evidence.
- reports/charts and assets: visual evidence, architecture, data-model, pipeline and dashboard hero assets.
- tests: raw-schema, key, date, reconciliation, metric and business-rule checks.
- docs: business context, methodology, metric dictionary, root causes, decisions, limitations, interview guide and completion matrix.

## Reproduce

1. Materialize the two raw ZIPs from the Drive workspace folder into a temporary directory; do not commit them.
2. Set OLIST_RAW_DIR to that temporary directory and OLIST_PROJECT_DIR to the repository path.
3. Run python src/ingest.py, python src/profile.py and python src/build_marts.py.
4. Run python -m pytest -q and python src/validate.py.
5. Use python src/build_database.py only after PGHOST, PGPORT, PGDATABASE, PGUSER and PGPASSWORD are configured.
6. Review reports/qa/pipeline_run.log and release_manifest.json.

The SQL files are PostgreSQL-compatible and pass static PostgreSQL parsing. Live database execution is credential-driven; no password is stored in the repository.

## Metric guardrails

GMV is a proxy from order-item price, not platform revenue. Orders use distinct order IDs. Repeat-customer analysis uses customer_unique_id. Retention uses observation eligibility. Late-delivery and review results are associative, not causal. Multi-seller order attribution remains limited.

## Remote storage

Raw ZIPs, tables, charts and reports are stored in the Drive workspace:
https://drive.google.com/drive/folders/1PBOPGZzxiPfTG_0O-b0suxy6cAYVt37G

Code and reviewable artifacts are mirrored in the private GitHub repository:
https://github.com/susayold/marketplace-growth-seller-intelligence

Power BI is deliberately reserved for the final stage.

