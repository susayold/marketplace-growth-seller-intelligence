CREATE TABLE IF NOT EXISTS marts.mart_seller_monthly AS
WITH base AS (
    SELECT
        DATE_TRUNC('month', o.order_purchase_timestamp)::date AS month_start,
        i.seller_id,
        i.order_id,
        i.product_id,
        i.price,
        c.customer_unique_id,
        p.product_category_name
    FROM facts.fct_order_item i
    INNER JOIN staging.orders o USING (order_id)
    LEFT JOIN dimensions.dim_customer c USING (customer_id)
    LEFT JOIN dimensions.dim_product p USING (product_id)
),
order_seller_count AS (
    SELECT order_id, COUNT(DISTINCT seller_id) AS seller_count
    FROM base
    GROUP BY order_id
),
review_order AS (
    SELECT order_id, AVG(review_score) AS avg_review_score
    FROM raw.olist_order_reviews
    GROUP BY order_id
)
SELECT
    b.seller_id,
    b.month_start,
    COUNT(DISTINCT b.order_id) AS orders,
    COUNT(*) AS items,
    SUM(b.price) AS gmv_proxy,
    SUM(b.price) / NULLIF(COUNT(DISTINCT b.order_id), 0) AS aov,
    1 AS active_flag,
    COUNT(DISTINCT b.customer_unique_id) AS customer_count,
    COUNT(DISTINCT b.product_category_name) AS category_count,
    AVG(CASE WHEN osc.seller_count = 1 THEN ro.avg_review_score END) AS avg_review_score_proxy,
    COUNT(DISTINCT CASE WHEN osc.seller_count = 1 AND ro.avg_review_score IS NOT NULL THEN b.order_id END) AS review_eligible_orders
FROM base b
INNER JOIN order_seller_count osc USING (order_id)
LEFT JOIN review_order ro USING (order_id)
GROUP BY 1, 2
ORDER BY 1, 2;

