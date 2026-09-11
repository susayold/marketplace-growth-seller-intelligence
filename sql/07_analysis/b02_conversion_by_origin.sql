SELECT origin_group, COUNT(DISTINCT mql_id) AS mqls,
       COUNT(DISTINCT seller_id) FILTER (WHERE converted_flag=1) AS converted_sellers,
       COUNT(DISTINCT seller_id) FILTER (WHERE converted_flag=1)::numeric / NULLIF(COUNT(DISTINCT mql_id),0) AS conversion_rate
FROM facts.fct_seller_funnel GROUP BY 1 ORDER BY mqls DESC;

