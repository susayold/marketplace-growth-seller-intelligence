# Data quality report

## Reporting Boundary Contract

The project distinguishes three boundaries:

- **Raw observation boundary:** latest source date physically present.
- **Analytical eligibility boundary:** latest point where a specific metric can be validly computed.
- **Executive reporting boundary:** latest complete period allowed in headline trend reporting.

The mechanical period rule excludes the first and final observed health months, requires at least 5% of the median interior-month order volume, and requires active-day coverage in the daily mart. The detailed register is `reports/qa/reporting_boundary_register.csv`; the period-level result is `reports/qa/period_completeness.csv`. Executive trend charts must either exclude incomplete periods or show them as a separate flagged style.

## Scope
The source is the anonymized Olist Brazilian E-Commerce Public Dataset plus the Olist Marketing Funnel dataset. The intended facts are order, order-item, seller, customer, review, payment, and lead grain.

## Checks
- Orders duplicate key rows: 0.
- Sellers duplicate key rows: 0.
- Negative item prices: 0.
- Review scores outside 1–5: 0.
- Closed deals linked to a seller with a negative first-sale lag: 53; these are retained in QA but excluded from valid activation-window rates.
- Naive order-item × payment join overstates GMV by R$ 617,472 (104.5% of grain-safe GMV).

## Material risks
1. **High — fan-out**: payments and order-items are both one-to-many; all marketplace KPIs use pre-aggregated/order-item grain-safe paths.
2. **Medium — funnel linkage**: only 842 closed deals are available and seller-to-transaction linkage is incomplete.
3. **Medium — retention censoring**: cohorts without enough observation time have null retention, not zero.
4. **Medium — seller attribution**: multi-seller orders make delivery/review attribution risky; operations analysis stays at order level.

## Remediation
Keep the fan-out audit as a regression test, enforce key/foreign-key tests, preserve raw statuses, and reconcile SQL/BI outputs before release.
