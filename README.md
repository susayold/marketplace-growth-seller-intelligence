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
- **Reproduction:** follow the refresh steps below; change only `DataRoot` when
  cloning to another machine, then refresh the PBIP model.

## Final release contents

- `deliverables/powerbi/` — editable final PBIP source.
- `deliverables/final-market-dashboard.pdf` — final verified seven-page report.
- `deliverables/powerbi/source-data/release_v3_final/reports/` — governed
  analytical outputs required to refresh the model.
- `scripts/build-powerbi-canonical-inputs.ps1` — reproducibly builds the
  display-shaped Power BI tables from the analytical release.
- `dist/assets/final-market-dashboard.pdf` — byte-identical website download.
- GitHub Pages renders the seven web preview images from that checked-in PDF
  during deployment.

## Metric governance

The executive monthly source is `mart_marketplace_monthly.csv`. Its latest
complete-month comparison is Jul → Aug 2018: GMV proxy **-4.6%**, orders
**+2.9%**, active sellers **+1.3%**, AOV **-7.2%**, and late delivery
**+5.9 percentage points**. The website, Power BI model and release QA use this
governed source.

Customer-experience review effects use `statistics/late_review_effect.csv`;
the decision agenda uses `decision_register.csv`. These are intentionally
separate governed release outputs rather than demo inputs.

## Final publication

- Final Power BI source commit: `561d9b6867f919708a9aff1fa86119381c225aff`.
- Final PDF publication commit: `87de2a32c2ff7561771ee9eebc8cfba307a3bf19`.
- Final PDF SHA-256:
  `488e30011814bde5eb0749014c63dbeacca448aa0fae6884f0b10a7efc3a5f34`.
- Seven-page Desktop visual QA: PASS.
- Automated QA / source contract / release validator: PASS.
- GitHub CI: PASS.
- GitHub Pages deployment: PASS.

## Refreshing Power BI

1. Open `deliverables/powerbi/final market dashboard.pbip` in Power BI Desktop.
2. If required, set the single `DataRoot` parameter to
   `<repository-root>\deliverables\powerbi\source-data\release_v3_final`.
3. Select **Refresh all**, inspect the seven pages, and save the PBIP.

The raw Olist files are intentionally not committed. The project ships the
small governed analytical release tables required by the Power BI model.
