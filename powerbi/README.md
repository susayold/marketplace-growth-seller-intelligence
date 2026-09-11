# Power BI semantic model plan

The six-page Power BI design is defined in the plan and metric dictionary.

Recommended pages: Executive Marketplace Health; Seller Acquisition Funnel; Seller Activation & Retention; Commercial Performance; Customer & Operations; Root Cause / Decisions.

Measures should bind to the CSV marts in `reports/tables` and reconcile to `mart_marketplace_monthly.csv`, `mart_seller_cohort.csv`, `seller_concentration.csv`, and `mart_order_experience.csv`. A `.pbix` binary is not generated in this runtime because Power BI Desktop is unavailable.
