-- Complete-case associative model for low review.
SELECT low_review_flag, delay_days, category, customer_state,
       LN(1 + order_value) AS log_order_value, freight_ratio, purchase_month
FROM analytics.mart_order_experience
WHERE delivery_observed = 1 AND review_score IS NOT NULL
  AND delay_days IS NOT NULL AND order_value IS NOT NULL
  AND freight_ratio IS NOT NULL AND category IS NOT NULL
  AND customer_state IS NOT NULL AND purchase_month IS NOT NULL;
-- Fit binomial GLM with HC3 robust SE; inspect diagnostics and do not infer causality.

