# Metric dictionary

| Metric | Definition | Grain / caveat |
|---|---|---|
| GMV proxy | Sum of `order_item.price` | Order-item; not platform revenue or profit.
| Customer-paid item value | `price + freight_value` | Order-item; freight shown separately from GMV proxy.
| Orders | Distinct `order_id` | Never count rows after item joins.
| Active sellers | Distinct sellers with at least one item in period | Seller-month.
| AOV | GMV proxy / distinct orders | Period-level.
| Activation | Closed seller with first sale on/after won date | Negative lags excluded from valid activation rates.
| Retention | Seller active in cohort-age month / cohort sellers | Only eligible observation windows are reported.
| Late delivery rate | Delivered orders with delivered date after estimated date / delivered orders | Order-level; no direct seller causality.
| Low review rate | Reviews with score <= 2 / reviewed orders | Review score is an experience signal, not causal proof.

Key outputs: total GMV proxy R$ 13,591,644, 98,666 orders, 3,095 sellers, repeat-customer rate 3.1%.

## Canonical activation v3

- **Closed seller:** seller in the 842-row closed/won population.
- **Matched closed seller:** closed seller with an observed exact first-sale match (380 sellers); this is a linkage observation, not the activation denominator.
- **Activation-eligible seller:** closed seller with a valid won date and observation horizon; first sale is not required. Two rows are excluded because `won_date` is after the raw order observation boundary.
- **Observed activated seller:** activation-eligible seller with an exact first sale on or after `won_date` (380 sellers).
- **Censored seller:** activation-eligible seller without an observed event before the observation end (460 sellers).
- **7/30/60/90-day activation:** event count divided by sellers observable through the relevant window, with Wilson 95% CI in `reports/statistics/activation_fixed_window.csv`.
- **Observed Activator Median Time:** median exact `days_to_first_sale` among the 380 observed activators (44.3 days). This is not the survival-estimated median.

The canonical population ladder and event/censor fields are in `reports/tables/seller_activation_timing.csv`. Never use the legacy `valid_activation_link` label as a headline metric.
