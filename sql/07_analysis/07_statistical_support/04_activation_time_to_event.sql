-- Activation timing population: linked seller/lead records only.
SELECT
    seller_id,
    lead_origin,
    EXTRACT(DAY FROM first_sale_at - won_at)::int AS days_to_first_sale,
    CASE WHEN first_sale_at IS NOT NULL THEN 1 ELSE 0 END AS activation_event,
    EXTRACT(DAY FROM COALESCE(first_sale_at, analysis_end_at) - won_at)::int AS observed_days
FROM analytics.mart_seller_activation
WHERE won_at IS NOT NULL;
-- Use milestone rates plus a Kaplan–Meier-style curve; do not call it causal.

