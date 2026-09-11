SELECT origin, COUNT(*) AS mqls, SUM(converted_flag) AS conversions, AVG(converted_flag::numeric) AS conversion_rate, AVG(CASE WHEN seller_id IS NOT NULL THEN 1.0 ELSE 0 END) AS seller_match_rate FROM facts.fct_seller_funnel GROUP BY origin HAVING COUNT(*) >= 10 ORDER BY conversion_rate DESC;

