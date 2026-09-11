# Published mart SQL updates

These definitions complete the plan-specified daily marketplace and seller-month grains.

- `mart_marketplace_daily.sql`: one row per purchase date; GMV proxy is the sum of order-item price. Late rate uses delivered orders as denominator.
- `mart_seller_monthly.sql`: one row per seller and purchase month. Seller review proxy is populated only for single-seller orders to avoid multi-seller attribution bias.

The corresponding CSV exports are in `reports/tables/`, and `reports/qa/missing_marts_build.json` records source row counts and GMV reconciliation.

