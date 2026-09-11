CREATE TABLE IF NOT EXISTS marts.mart_marketplace_monthly AS
WITH monthly AS (
 SELECT DATE_TRUNC('month', order_purchase_timestamp)::date AS month_start, COUNT(DISTINCT order_id) AS orders, SUM(price) AS gmv_proxy, COUNT(DISTINCT seller_id) AS active_sellers
 FROM facts.fct_order_item i INNER JOIN staging.orders o USING(order_id) GROUP BY 1
), lagged AS (
 SELECT *, LAG(gmv_proxy) OVER (ORDER BY month_start) AS prior_gmv, LAG(orders) OVER (ORDER BY month_start) AS prior_orders FROM monthly
)
SELECT *, gmv_proxy - prior_gmv AS gmv_change, CASE WHEN prior_gmv > 0 THEN gmv_proxy / prior_gmv - 1 END AS gmv_mom_pct, CASE WHEN prior_orders > 0 THEN orders::numeric / prior_orders - 1 END AS orders_mom_pct, gmv_proxy / NULLIF(orders,0) AS aov FROM lagged;


