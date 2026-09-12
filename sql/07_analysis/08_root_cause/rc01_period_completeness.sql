-- RC1: distinguish business movement from source-boundary movement.
SELECT * FROM analytics.mart_marketplace_health_extended
WHERE is_complete_month=1 ORDER BY month_start;