# Analysis log

| Date | Question | Metric | Query / notebook | Finding | Interpretation | Decision | Open question |
|---|---|---|---|---|---|---|---|
| 2026-09-12 | Can marketplace GMV be trusted after joins? | GMV proxy | sql/06_quality/q01_fanout_audit.sql; notebooks/01_data_profiling.ipynb | Naive item × payment join is 4.54% above grain-safe GMV | One-to-many fan-out is material | Aggregate at item/order grain before joins | Reconcile against a governed production source |
| 2026-09-12 | What drives monthly growth? | GMV proxy, orders, active sellers, AOV | sql/07_analysis/a02_growth_decomposition.sql; notebooks/02_marketplace_health.ipynb | Growth should be decomposed into volume, seller base and AOV | Decomposition is descriptive | Track the four-metric scorecard | Current-market performance is not represented |
| 2026-09-12 | Which acquisition origins create value? | conversion rate, matched sellers, downstream GMV | notebooks/03_seller_funnel.ipynb | Channel quality differs by denominator and downstream value | Volume-only ranking is incomplete | Use a two-dimensional channel scorecard | Need campaign cost for CAC/ROAS |
| 2026-09-12 | Do sellers retain? | eligibility-aware cohort retention | sql/07_analysis/d02_monthly_retention.sql; notebooks/04_seller_retention.ipynb | Recent cohort-age cells are censored | Missing observation is not churn | Compare only eligible ages | Need longer follow-up windows |
| 2026-09-12 | Does late delivery relate to reviews? | late delivery rate, low review rate | sql/07_analysis/f05_review_vs_delay.sql; notebooks/05_operations_analysis.ipynb | Late orders have materially weaker review outcomes | Association, not causality | Prioritize operational investigation | Need carrier, route and seller-level service data |
| 2026-09-12 | Are observed differences statistically notable? | chi-square statistic and p-value | notebooks/06_statistical_validation.ipynb | Lead origin/conversion and late delivery/low review associations are detected | Evidence supports diagnostics | Design follow-up experiments | Need controls and pre-registered causal design |

