-- RC5 late-delivery/customer-experience case.
SELECT delivery_group, n_orders, avg_review, low_review_rate,
       low_review_ci_low, low_review_ci_high
FROM analytics.mart_late_review_effect;

