CREATE TABLE IF NOT EXISTS marts.mart_marketplace_daily AS
WITH item_base AS (
    SELECT
        DATE_TRUNC('day', o.order_purchase_timestamp)::date AS purchase_date,
        i.order_id,
        i.seller_id,
        i.price
    FROM facts.fct_order_item i
    INNER JOIN staging.orders o USING (order_id)
),
item_day AS (
    SELECT
        purchase_date,
        SUM(price) AS gmv_proxy,
        COUNT(DISTINCT order_id) AS orders,
        COUNT(*) AS items,
        COUNT(DISTINCT seller_id) AS active_sellers
    FROM item_base
    GROUP BY 1
),
item_orders AS (
    SELECT DISTINCT
        b.order_id,
        b.purchase_date,
        o.customer_id,
        o.order_delivered_customer_date,
        o.order_estimated_delivery_date
    FROM item_base b
    INNER JOIN staging.orders o USING (order_id)
),
review_order AS (
    SELECT order_id, AVG(review_score) AS avg_review_score
    FROM raw.olist_order_reviews
    GROUP BY order_id
),
order_day AS (
    SELECT
        io.purchase_date,
        COUNT(DISTINCT c.customer_unique_id) AS active_customers,
        COUNT(DISTINCT CASE WHEN io.order_delivered_customer_date IS NOT NULL THEN io.order_id END) AS delivered_orders,
        COUNT(DISTINCT CASE
            WHEN io.order_delivered_customer_date IS NOT NULL
             AND io.order_estimated_delivery_date IS NOT NULL
             AND io.order_delivered_customer_date > io.order_estimated_delivery_date
            THEN io.order_id END) AS late_orders,
        AVG(ro.avg_review_score) AS avg_review_score
    FROM item_orders io
    LEFT JOIN dimensions.dim_customer c USING (customer_id)
    LEFT JOIN review_order ro USING (order_id)
    GROUP BY 1
)
SELECT
    d.purchase_date AS date,
    d.gmv_proxy,
    d.orders,
    d.items,
    d.active_sellers,
    od.active_customers,
    d.gmv_proxy / NULLIF(d.orders, 0) AS aov,
    od.late_orders,
    od.delivered_orders,
    od.late_orders::numeric / NULLIF(od.delivered_orders, 0) AS late_delivery_rate,
    od.avg_review_score
FROM item_day d
INNER JOIN order_day od USING (purchase_date)
ORDER BY 1;

