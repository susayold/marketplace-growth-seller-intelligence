WITH item_month AS (
    SELECT date_trunc('month', o.order_purchase_timestamp)::date AS purchase_month,
           oi.order_id, oi.seller_id, oi.price AS gmv_proxy
    FROM staging.orders o JOIN staging.order_items oi USING (order_id)
)
SELECT purchase_month, SUM(gmv_proxy) AS gmv_proxy, COUNT(DISTINCT order_id) AS orders,
       COUNT(DISTINCT seller_id) AS active_sellers,
       SUM(gmv_proxy) / NULLIF(COUNT(DISTINCT order_id),0) AS aov
FROM item_month GROUP BY 1 ORDER BY 1;

