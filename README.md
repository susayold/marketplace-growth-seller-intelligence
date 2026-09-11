# Marketplace Growth & Seller Intelligence

Historical Olist case study focused on seller acquisition → activation → retention → commercial value → customer experience.

## v1 execution status

- Raw ZIPs downloaded from the official Olist Kaggle dataset pages and stored in Drive.
- Inventory, profiling, fan-out audit, marts, cohort retention, seller concentration, operations analysis, charts, executive PDF, and QA outputs generated.
- SQL templates and Power BI semantic-model plan included.
- PostgreSQL/Power BI execution is pending because those runtimes are not installed in the current desktop session.

## Core evidence

- GMV proxy: R$ 13,591,644; orders: 98,666; sellers: 3,095.
- Repeat customer rate: 3.1%.
- Top 20% seller GMV share: 82.7%.
- Activation within 90 days among valid closed-seller links: 87.5%.

## Metric guardrails

GMV is a proxy from order-item price, not platform revenue. The project preserves observation eligibility for retention and treats association as non-causal.

## Remote storage

Raw data and all chart/report/table artifacts are stored in the Drive folder `marketplace-growth-seller-intelligence`; code and documentation are mirrored in GitHub.
## Reproduce v1

1. Download the two raw ZIPs from the project Drive folder into a local temporary data/raw/ directory.
2. Create an environment and install requirements.txt.
3. Set OLIST_RAW_DIR to the raw ZIP directory and OLIST_PROJECT_DIR to the checkout root.
4. Run python src/build_project.py, then python -m pytest -q.

The pipeline reads ZIP members directly, writes grain-safe marts/charts/QA outputs, and does not require extracting raw CSVs into the repository. Raw archives are intentionally kept in Drive rather than GitHub.

Drive workspace: https://drive.google.com/drive/folders/1PBOPGZzxiPfTG_0O-b0suxy6cAYVt37G
