# MarketLens Website — Page 1 Executive Overview

This branch implements the real-data web version of Page 1 only.

## Data sources

The GitHub Pages workflow copies the following existing project outputs into the deployed site's `data/` directory:

- `mart_marketplace_monthly.csv`
- `mart_category_performance.csv`
- `mart_geography_performance.csv`
- `delivery_performance.csv`
- `seller_concentration.csv`
- `activation_summary.csv`
- `seller_segmentation.csv`
- `statistical_validation.csv`

## Page 1 features

- Real GMV, Orders, Active Sellers, AOV, and Late Delivery KPIs
- Real previous-period KPI deltas
- KPI mini sparklines
- GMV + Orders trend
- Concentration curve anchored to observed seller-share concentration
- Gini calculated from seller-level lifetime GMV
- Real Top 5 categories and states
- Blue sequential matrix heat formatting
- Real 30D / 90D activation and review-gap highlights
- Month, Category, and State controls
- Responsive layout

Pages 2–7 are intentionally left disabled until Page 1 is reviewed and approved.

## Local preview

From repository root, assemble a local preview folder using the same files copied by the deployment workflow, then serve it with a local HTTP server. Opening `website/index.html` directly will not load CSV files reliably because browsers restrict local `file://` fetches.
