-- Monthly seller concentration starts at seller-month grain.
SELECT month_start,seller_id,SUM(gmv_proxy) AS seller_gmv_proxy
FROM analytics.mart_order_item_grain GROUP BY 1,2;