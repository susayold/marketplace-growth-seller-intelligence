-- Pairwise acquisition comparison population; apply two-proportion tests + BH/FDR downstream.
WITH g AS (
  SELECT COALESCE(origin_normalized,'unknown') AS origin,
         COUNT(*) AS n, COUNT(*) FILTER (WHERE is_converted) AS converted
  FROM analytics.mart_lead_funnel GROUP BY 1
)
SELECT a.origin AS group_a,b.origin AS group_b,a.n AS n_a,b.n AS n_b,
       a.converted AS converted_a,b.converted AS converted_b
FROM g a JOIN g b ON a.origin < b.origin;