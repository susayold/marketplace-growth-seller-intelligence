WITH cohort_sizes AS (
    SELECT cohort_month,
           MAX(active_sellers) FILTER (WHERE cohort_age = 0) AS cohort_sellers
    FROM marts.mart_seller_cohort
    GROUP BY cohort_month
)
SELECT c.cohort_month,
       c.cohort_age AS age_month,
       s.cohort_sellers,
       c.active_sellers AS retained_sellers,
       c.active_sellers::numeric / NULLIF(s.cohort_sellers, 0) AS retention_rate
FROM marts.mart_seller_cohort c
INNER JOIN cohort_sizes s USING (cohort_month)
ORDER BY c.cohort_month, c.cohort_age;

