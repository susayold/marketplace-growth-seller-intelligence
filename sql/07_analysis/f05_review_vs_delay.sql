SELECT is_late, COUNT(DISTINCT order_id) AS orders, AVG(review_score) AS avg_review_score,
       AVG((review_score <= 2)::int) AS low_review_rate
FROM marts.mart_order_experience GROUP BY 1 ORDER BY 1;

