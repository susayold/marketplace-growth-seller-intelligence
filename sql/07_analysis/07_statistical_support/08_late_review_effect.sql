-- Delivery/review effect population with mutually exclusive timing groups.
SELECT delivery_group,
       COUNT(*) AS reviewed_delivered_orders,
       AVG(review_score) AS avg_review,
       AVG((review_score <= 2)::int) AS low_review_rate
FROM analytics.mart_order_experience
WHERE delivery_observed = 1 AND review_score IS NOT NULL
GROUP BY 1;
-- Report Wilson intervals, mean/median bootstrap intervals, risk difference and risk ratio.

