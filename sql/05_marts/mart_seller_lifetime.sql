CREATE TABLE IF NOT EXISTS marts.mart_seller_lifetime AS
WITH base AS (SELECT seller_id, COUNT(DISTINCT order_id) AS orders, SUM(price) AS gmv_proxy, MIN(order_purchase_timestamp)::date AS first_sale_date, MAX(order_purchase_timestamp)::date AS last_sale_date FROM facts.fct_order_item i INNER JOIN staging.orders o USING(order_id) GROUP BY seller_id), ranked AS (SELECT *, NTILE(5) OVER (ORDER BY gmv_proxy DESC) AS value_quintile, RANK() OVER (ORDER BY gmv_proxy DESC) AS gmv_rank, DENSE_RANK() OVER (ORDER BY orders DESC) AS order_rank FROM base) SELECT * FROM ranked;

