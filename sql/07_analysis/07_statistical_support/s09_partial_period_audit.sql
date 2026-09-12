-- Partial-period audit: flag edge and low-volume tails before trend claims.
WITH m AS (SELECT purchase_month,COUNT(*) AS orders FROM analytics.mart_order_experience GROUP BY 1)
SELECT purchase_month,orders,
       CASE WHEN purchase_month=MIN(purchase_month) OVER()
               OR purchase_month=MAX(purchase_month) OVER() THEN 0 ELSE 1 END AS is_complete_month
FROM m ORDER BY purchase_month;