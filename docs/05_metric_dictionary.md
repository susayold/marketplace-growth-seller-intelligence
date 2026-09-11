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
