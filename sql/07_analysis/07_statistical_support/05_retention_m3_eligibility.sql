-- M3 retention eligibility. Recent cohorts are censored and excluded from M3.
WITH cohorts AS (
    SELECT seller_id, MIN(month_start) AS cohort_month
    FROM analytics.mart_seller_monthly
    WHERE gmv_proxy > 0
    GROUP BY seller_id
)
SELECT c.cohort_month, COUNT(*) AS eligible_sellers,
       COUNT(*) FILTER (WHERE EXISTS (
           SELECT 1 FROM analytics.mart_seller_monthly m
           WHERE m.seller_id = c.seller_id
             AND m.month_start >= c.cohort_month + INTERVAL '3 months'
             AND m.month_start < c.cohort_month + INTERVAL '4 months'
             AND m.gmv_proxy > 0
       )) AS retained_m3
FROM cohorts c
WHERE c.cohort_month + INTERVAL '3 months' <= (SELECT MAX(month_start) FROM analytics.mart_seller_monthly)
GROUP BY 1;

