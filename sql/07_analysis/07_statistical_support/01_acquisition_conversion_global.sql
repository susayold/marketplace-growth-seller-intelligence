-- Global acquisition conversion with an explicit denominator.
-- Expected source grain: one row per qualified lead in mart_lead_funnel.
SELECT
    COUNT(*) AS mqls,
    COUNT(*) FILTER (WHERE is_converted) AS converted_leads,
    COUNT(*) FILTER (WHERE is_converted)::numeric / NULLIF(COUNT(*), 0) AS conversion_rate
FROM analytics.mart_lead_funnel
WHERE lead_created_at IS NOT NULL;

