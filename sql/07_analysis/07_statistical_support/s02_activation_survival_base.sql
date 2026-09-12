-- Activation time-to-event base population.
SELECT seller_id, lead_origin,
       EXTRACT(DAY FROM first_sale_at-won_at)::int AS days_to_first_sale,
       CASE WHEN first_sale_at IS NULL THEN 0 ELSE 1 END AS activation_event,
       EXTRACT(DAY FROM COALESCE(first_sale_at,analysis_end_at)-won_at)::int AS observed_days
FROM analytics.mart_seller_activation WHERE won_at IS NOT NULL;