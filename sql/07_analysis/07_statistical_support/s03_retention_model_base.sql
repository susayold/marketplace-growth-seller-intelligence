-- M3 retention model population; recent cohorts are censored.
SELECT retained_m3::int AS retained_m3, origin_normalized, cohort_month
FROM analytics.mart_seller_retention_m3
WHERE eligible_m3=1
  AND origin_normalized IN ('organic_search','paid_search','social','direct_traffic','unknown');