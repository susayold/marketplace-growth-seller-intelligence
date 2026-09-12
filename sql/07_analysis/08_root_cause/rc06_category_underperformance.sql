-- RC6: size, breadth and customer-experience segmentation.
SELECT * FROM analytics.mart_category_analysis_extended
WHERE active_sellers>=10 ORDER BY gmv_proxy DESC;