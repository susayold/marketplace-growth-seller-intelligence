CREATE TABLE IF NOT EXISTS marts.mart_seller_monthly AS
SELECT DATE_TRUNC('month', o.order_purchase_timestamp)::date AS month_start, i.seller_id, COUNT(DISTINCT i.order_id) AS orders, COUNT(*) AS items, SUM(i.price) AS gmv_proxy, SUM(i.price) / NULLIF(COUNT(DISTINCT i.order_id),0) AS seller_aov
FROM facts.fct_order_item i INNER JOIN staging.orders o USING(order_id)
GROUP BY 1,2;

