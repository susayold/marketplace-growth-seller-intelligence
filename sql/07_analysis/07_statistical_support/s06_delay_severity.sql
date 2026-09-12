-- Mutually exclusive delay severity buckets for customer-experience analysis.
SELECT CASE WHEN delay_days<=0 THEN 'on_time' WHEN delay_days<=3 THEN 'early_late'
            WHEN delay_days<=7 THEN 'moderate_late' ELSE 'severe_late' END AS delay_severity,
       COUNT(*) AS n_orders,AVG(review_score) AS avg_review,
       AVG((review_score<=2)::int) AS low_review_rate
FROM analytics.mart_order_experience
WHERE delivery_observed=1 AND review_score IS NOT NULL GROUP BY 1;