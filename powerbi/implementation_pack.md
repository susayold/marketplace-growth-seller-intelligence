# Power BI implementation pack — Marketplace Growth & Seller Intelligence

Status: **ready-to-build upstream model; PBIX not yet generated**.

The SQL pipeline, marts, QA evidence, and the static website preview are complete. This pack is the controlled hand-off for the final Power BI stage. Power BI Desktop is not installed in the current Windows environment, so no fabricated `.pbix`, PDF export, or reconciliation pass is claimed.

## 1. Source contract

Import the governed marts and dimensions from the GitHub repository, or from the matching CSV exports in Drive. Do not build visuals from raw payment/order joins.

Recommended import set:

- `mart_marketplace_monthly`
- `mart_marketplace_daily`
- `mart_seller_monthly`
- `mart_seller_lifetime`
- `mart_acquisition_channel`
- `mart_seller_cohort`
- `mart_order_experience`
- `mart_category_performance`
- `mart_geography_performance`
- `seller_activation`
- `activation_summary`
- `customer_repeat_summary`
- `seller_concentration`

Create `dim_date` in Power BI from the min/max `purchase_month` values. Create a small `dim_seller` from distinct `seller_id` values in `mart_seller_lifetime` and `seller_activation` when a seller slicer is needed. Category, geography, and channel labels can be sourced directly from their marts because the published exports are already aggregated.

The current CSV exports are already aggregated to their documented grains. In Power Query, normalize date fields to Date and numeric fields to Decimal Number/Whole Number. The current exports use `purchase_month`, `cohort_month`, and `first_sale_month`; create first-of-month Date columns named `month_start`, `cohort_month_start`, and `first_sale_month_start` as appropriate. Preserve `is_late` as a numeric 0/1 flag.

## 2. Semantic model

Create a dedicated `Measures` table and hide technical keys from report view. Use single-direction, one-to-many relationships from dimensions into facts/marts:

| From | To | Key |
|---|---|---|
| `dim_date` | `mart_marketplace_monthly` | `month_start` → `month_start` |
| `dim_date` | `mart_marketplace_daily` | `full_date` → `purchase_date` |
| `dim_date` | `mart_category_performance` | `month_start` → `month_start` |
| `dim_date` | `mart_seller_monthly` | `month_start` → `month_start` |
| `dim_date` | `mart_seller_cohort` | `month_start` → `cohort_month` |
| `dim_seller` | `mart_seller_lifetime` | `seller_id` |
| `dim_seller` | `mart_seller_monthly` | `seller_id` |
| `dim_seller` | `seller_activation` | `seller_id` |

`mart_order_experience`, `mart_acquisition_channel`, `activation_summary`, `customer_repeat_summary`, `seller_concentration`, and `mart_geography_performance` are aggregate marts. Keep them disconnected unless a documented conformed key is present; use them for their own scorecards and QA visuals. Do not create many-to-many relationships merely to make a visual populate.

Create `dim_date` as a contiguous calendar covering the observed purchase and funnel periods. Mark it as the date table. Add `Year`, `Month Number`, `Month`, `Year-Month`, and `Quarter` columns; sort `Month` by `Month Number` and `Year-Month` by a numeric year-month key.

## 3. Required report pages

### P1 — Executive Marketplace Health

KPI cards: GMV Proxy, Orders, Active Sellers, Active Customers, AOV, Late Delivery Rate. Add a monthly GMV/Orders combo trend, active seller trend, GMV-per-seller productivity, category contribution, geography view, and a compact alert panel. Slicers: Date, Category, State.

### P2 — Seller Acquisition Funnel

Show MQL → Won → Linked → Activated → M3 Retained, with counts and conversion rates. Add conversion by origin, activation by origin, median sales cycle, days-to-first-sale distribution, business-segment conversion, and an origin scorecard with MQLs, converted sellers, conversion rate, matched sellers, downstream GMV proxy, orders, and GMV per matched seller.

### P3 — Activation & Retention

Show cohort retention heatmap, time-to-first-sale distribution, activation buckets, M1/M3/M6 retention, retention by channel, and seller lifecycle distribution. Keep cohort denominator and cohort size visible in tooltips.

### P4 — Commercial Performance

Show GMV, Orders, AOV, Active Sellers, GMV per Seller, and Orders per Seller. Add growth decomposition, Pareto concentration, top-seller share, category matrix, GMV-vs-retention scatter, and seller-tier comparison.

### P5 — Customer & Operations

Show Late Delivery Rate, average delivery days, average review score, low-review rate, freight ratio, and repeat-customer rate. Add review score vs late-delivery comparison, delivery performance by State/Category, freight-vs-review relationship, review trend, and repeat-customer summary.

### P6 — Diagnostic / Seller 360

Configure a seller drill-through page. Include seller selector, first sale, lead origin, won date, days to first sale, lifetime GMV proxy, orders, active months, GMV trend, category mix, geography, lifecycle stage, and an explicit “data available through” date. Add a back button and keep drill-through filters scoped to `seller_id`.

## 4. Interaction and presentation rules

- Sync Date, Category, State, and Origin slicers only where the underlying grain supports them.
- Add report-page tooltips for definitions, denominator, grain, and source mart.
- Use consistent formats: GMV/AOV as currency with two decimals, counts with thousands separators, rates as percentages with one decimal, days as one decimal.
- Use a restrained palette, clear hierarchy, and whitespace. Reserve red/orange for operational risk (late delivery and low review), not for ordinary category comparisons.
- Disable misleading “Show items with no data” behavior where it creates empty categories.
- Keep a visible “Proxy” label on GMV because the controlled metric is item-price GMV, not payment value.

## 5. Required DAX

The canonical measures are in `powerbi/measures.dax`. Create them in the `Measures` table and validate their filter behavior on every page.

## 6. Reconciliation gate

Before release, export `reports/qa/powerbi_reconciliation.csv` with one row per metric and these columns:

`metric,sql_value,powerbi_value,difference,tolerance,status`

Minimum metrics: GMV Proxy, Orders, Active Sellers, AOV, Conversion Rate, Activation Rate, Late Delivery Rate. `difference = powerbi_value - sql_value`; `status = PASS` when the absolute difference is within tolerance. The current template contains SQL control totals and remains blocked until a real PBIX is opened and evaluated.

Control totals from the verified rebuild:

- GMV Proxy: 13,591,643.70
- Orders: 98,666
- Active Sellers: 3,095
- AOV: 137.754076378894
- Conversion Rate: 0.10525
- Activation Rate: 0.388361045131
- Late Delivery Rate: 0.081116938577

The concentration export uses `top_seller_share` (for example, 0.1) and `gmv_proxy_share` as its control columns.

## 7. Acceptance checklist

1. Refresh succeeds without errors or ambiguous relationships.
2. All six pages render with populated visuals and no unexplained blanks.
3. Cross-filtering and seller drill-through work as specified.
4. The seven reconciliation metrics pass their tolerances.
5. PDF export is readable at 100% zoom and has no clipped titles, labels, or legends.
6. Save the final `.pbix`, PDF export, reconciliation CSV, and a short refresh note to the remote Drive/GitHub locations; remove temporary local copies after upload.

## 8. Current blocker

The environment currently has no Power BI Desktop executable and the Windows computer-use bridge is unavailable. The next execution step is therefore to install/open Power BI Desktop (or provide an enabled Power BI-connected session), then implement this pack and replace the blocked reconciliation template with measured values.



