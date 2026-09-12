-- Customer-state late-minus-on-time review penalty population.
SELECT customer_state,delivery_group,COUNT(*) AS n_orders,AVG(review_score) AS avg_review
FROM analytics.mart_order_experience
WHERE delivery_observed=1 AND review_score IS NOT NULL GROUP BY 1,2;