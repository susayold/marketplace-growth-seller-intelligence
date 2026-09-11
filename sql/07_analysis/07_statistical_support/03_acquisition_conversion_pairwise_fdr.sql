-- Pairwise two-proportion comparisons are materialized by the Python build.
-- This SQL preserves the comparison population for audit/reproduction.
WITH grouped AS (
    SELECT COALESCE(origin_normalized, 'unknown') AS origin,
           COUNT(*) AS n,
           COUNT(*) FILTER (WHERE is_converted) AS converted
    FROM analytics.mart_lead_funnel
    GROUP BY 1
)
SELECT a.origin AS group_a, b.origin AS group_b,
       a.n AS n_a, b.n AS n_b, a.converted AS converted_a, b.converted AS converted_b,
       a.converted::numeric / NULLIF(a.n, 0) AS rate_a,
       b.converted::numeric / NULLIF(b.n, 0) AS rate_b
FROM grouped a
JOIN grouped b ON a.origin < b.origin;
-- Apply two-proportion z-tests and Benjamini–Hochberg FDR correction downstream.

