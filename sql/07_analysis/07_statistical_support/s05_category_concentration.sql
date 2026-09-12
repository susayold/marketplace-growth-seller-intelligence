-- Category concentration combines value and seller breadth.
SELECT category,SUM(gmv_proxy) AS gmv_proxy,COUNT(DISTINCT seller_id) AS seller_count
FROM analytics.mart_order_item_grain GROUP BY 1;