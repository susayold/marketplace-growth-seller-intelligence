-- Origin-level conversion. Keep sparse origins visible and attach sample flags.
SELECT
    COALESCE(origin_normalized, 'unknown') AS origin,
    COUNT(*) AS mqls,
    COUNT(*) FILTER (WHERE is_converted) AS converted_leads,
    COUNT(*) FILTER (WHERE is_converted)::numeric / NULLIF(COUNT(*), 0) AS conversion_rate,
    CASE WHEN COUNT(*) < 10 THEN 'insufficient'
         WHEN COUNT(*) < 30 THEN 'small'
         WHEN COUNT(*) < 100 THEN 'usable' ELSE 'strong' END AS sample_size_flag
FROM analytics.mart_lead_funnel
GROUP BY 1
ORDER BY mqls DESC;

