-- RC6 category case: combine commercial size, seller breadth and experience risk.
SELECT category, gmv_proxy, active_sellers, top_10_seller_share, late_rate, avg_review
FROM analytics.mart_category_analysis_extended
WHERE active_sellers >= 10
ORDER BY gmv_proxy DESC;

