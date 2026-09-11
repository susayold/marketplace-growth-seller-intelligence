SELECT cohort_month, age_month, cohort_sellers, retained_sellers, retention_rate
FROM marts.mart_seller_cohort
WHERE eligible_flag=1 ORDER BY cohort_month, age_month;

