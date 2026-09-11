-- Root-cause metric tree used by the evidence register.
SELECT 'growth' AS branch, 'GMV proxy' AS metric, 'orders × average item value' AS definition
UNION ALL SELECT 'acquisition', 'conversion rate', 'converted MQLs / MQLs'
UNION ALL SELECT 'activation', '30-day activation', 'activated sellers by day 30 / valid linked sellers'
UNION ALL SELECT 'retention', 'M3 retention', 'retained at month 3 / M3-eligible sellers'
UNION ALL SELECT 'experience', 'low-review rate', 'reviews <= 2 / reviewed delivered orders';

