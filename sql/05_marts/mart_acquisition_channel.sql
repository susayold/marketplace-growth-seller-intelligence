CREATE TABLE IF NOT EXISTS marts.mart_acquisition_channel AS SELECT origin, COUNT(*) AS mqls, COUNT(*) FILTER (WHERE converted_flag=1) AS converted_leads, AVG(converted_flag::numeric) AS lead_conversion_rate, COUNT(DISTINCT seller_id) AS matched_sellers FROM facts.fct_seller_funnel GROUP BY origin HAVING COUNT(*) > 0;

