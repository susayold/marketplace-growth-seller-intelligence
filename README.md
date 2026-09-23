# MarketLens — Marketplace Growth & Seller Intelligence

[View the live report](https://susayold.github.io/marketplace-growth-seller-intelligence/) · [Download the prior PDF export](deliverables/final-market-dashboard.pdf) · [Open the updated Power BI project](deliverables/powerbi/final%20market%20dashboard.pbip)

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

- `deliverables/powerbi/` — editable PBIP source.
- `deliverables/final-market-dashboard.pdf` — prior exported seven-page report;
  re-export is pending from the updated PBIP.
- `deliverables/powerbi/source-data/release_v3_final/reports/` — small governed
  analytical outputs required to refresh the model.
- `scripts/build-powerbi-canonical-inputs.ps1` — reproducibly builds the
  display-shaped Power BI tables from the analytical release.
- `scripts/build-pdf-from-pbi-snapshots.py` — packages the verified Power BI
  canvas snapshots into the seven-page PDF and synchronized web previews.

## Metric governance

The executive monthly source is `mart_marketplace_monthly.csv`. Its latest
complete-month comparison is Jul → Aug 2018: GMV proxy **-4.6%**, orders
**+2.9%**, active sellers **+1.3%**, AOV **-7.2%**, and late delivery
**+5.9 percentage points**. The website, Power BI model and release QA are
expected to use this source only.

Customer-experience review effects use `statistics/late_review_effect.csv`;
the decision agenda uses `decision_register.csv`. These are intentionally
separate, governed release outputs rather than demo inputs.

## Refreshing Power BI

1. Open `deliverables/powerbi/final market dashboard.pbip` in Power BI Desktop.
2. In Power Query, change the single `DataRoot` parameter only if the repository
   is located somewhere other than the value saved in the project.
3. Refresh the model, check the seven pages, save the PBIP, then export a new
   PDF. Synchronize website previews and the release manifest only after that
   export.

The raw Olist files are intentionally not committed. The project ships the
small analytical release tables needed by the Power BI model.
