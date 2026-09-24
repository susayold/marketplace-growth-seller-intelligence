# MarketLens — Marketplace Growth & Seller Intelligence

[View the live report](https://susayold.github.io/marketplace-growth-seller-intelligence/) · [Download the final Power BI report](deliverables/final-market-dashboard.pdf) · [Open the final Power BI project](deliverables/powerbi/final%20market%20dashboard.pbip)

This portfolio case study evaluates marketplace health across seller acquisition,
activation, retention, commercial concentration, customer experience, root-cause
diagnosis, and a governed action agenda.

## Portfolio navigation

- **Business problem:** determine whether marketplace growth is broad, valuable,
  and operationally healthy—not merely whether orders increased.
- **Data model:** grain-safe marketplace, seller, acquisition, activation,
  retention, commercial, customer-experience, root-cause, and decision outputs.
- **Core findings:** orders and sellers grew into the final complete month while
  GMV, AOV, and seller productivity softened; seller value is concentrated and
  late delivery is strongly associated with low reviews.
- **Technical stack:** SQL-compatible marts, Python statistical validation,
  Power BI PBIP/TMDL, DAX, and a static GitHub Pages release.
- **QA and reconciliation:** see `deliverables/RELEASE_QA.md`,
  `reports/qa/powerbi_reconciliation.csv`, and
  `reports/qa/canonical_final_metrics.json`.
- **Limitations:** GMV is a proxy; the analysis is historical and observational;
  incomplete periods and unobservable cohorts are excluded or flagged.

## Final release contents

- `deliverables/powerbi/` — editable final PBIP source.
- `deliverables/final-market-dashboard.pdf` — final verified seven-page report.
- `dist/assets/final-market-dashboard.pdf` — byte-identical website copy.
- `deliverables/powerbi/source-data/release_v3_final/reports/` — governed
  analytical outputs required to refresh the model.
- GitHub Pages renders fresh page-preview PNGs from the checked-in final PDF
  during deployment.

## Metric governance

The executive monthly source is `mart_marketplace_monthly.csv`. Its latest
complete-month comparison is Jul → Aug 2018: GMV proxy **-4.6%**, orders
**+2.9%**, active sellers **+1.3%**, AOV **-7.2%**, and late delivery
**+5.9 percentage points**.

Customer-experience review effects use `statistics/late_review_effect.csv`;
the decision agenda uses `decision_register.csv`.

## Final Power BI release

The final Power BI source was Desktop-refreshed and visually checked across all
seven pages. The final PDF was published in commit `87de2a3` and has SHA-256:

`488e30011814bde5eb0749014c63dbeacca448aa0fae6884f0b10a7efc3a5f34`

The repository PDF and website PDF are byte-identical. GitHub CI and the Pages
deployment for the final PDF publication both completed successfully.

## Refreshing Power BI

1. Open `deliverables/powerbi/final market dashboard.pbip` in Power BI Desktop.
2. If needed, set the single `DataRoot` parameter to
   `<repository-root>\deliverables\powerbi\source-data\release_v3_final`.
3. Refresh the model and inspect the seven pages.

The raw Olist files are intentionally not committed. The project ships the
small governed analytical release tables needed by the Power BI model.
