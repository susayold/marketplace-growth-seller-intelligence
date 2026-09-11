WITH seller_origin AS (
    SELECT seller_id, MIN(origin) AS origin_group
    FROM facts.fct_seller_funnel
    WHERE seller_id IS NOT NULL
    GROUP BY seller_id
),
first_sale AS (
    SELECT seller_id, MIN(month_start) AS cohort_month
    FROM marts.mart_seller_monthly
    GROUP BY seller_id
),
seller_cohort AS (
    SELECT f.seller_id, o.origin_group, f.cohort_month
    FROM first_sale f
    INNER JOIN seller_origin o USING (seller_id)
),
eligible_activity AS (
    SELECT
        c.origin_group,
        c.cohort_month,
        DATE_PART('month', AGE(a.month_start, c.cohort_month))::int AS age_month,
        c.seller_id
    FROM seller_cohort c
    INNER JOIN marts.mart_seller_monthly a USING (seller_id)
),
eligible_denominator AS (
    SELECT
        origin_group,
        age_month,
        COUNT(DISTINCT seller_id) AS cohort_sellers
    FROM seller_cohort c
    CROSS JOIN (SELECT MAX(month_start) AS observed_end FROM marts.mart_seller_monthly) e
    CROSS JOIN LATERAL generate_series(0, 6) AS ages(age_month)
    WHERE c.cohort_month + (ages.age_month * INTERVAL '1 month') <= e.observed_end
    GROUP BY origin_group, age_month
),
retained AS (
    SELECT origin_group, age_month, COUNT(DISTINCT seller_id) AS retained_sellers
    FROM eligible_activity
    GROUP BY origin_group, age_month
)
SELECT
    d.origin_group,
    d.age_month,
    d.cohort_sellers,
    COALESCE(r.retained_sellers, 0) AS retained_sellers,
    COALESCE(r.retained_sellers, 0)::numeric / NULLIF(d.cohort_sellers, 0) AS retention_rate
FROM eligible_denominator d
LEFT JOIN retained r USING (origin_group, age_month)
ORDER BY d.origin_group, d.age_month;
