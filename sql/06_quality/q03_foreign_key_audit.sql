SELECT COUNT(*) AS orphan_items, COUNT(*)=0 AS passes FROM raw.olist_order_items i LEFT JOIN raw.olist_orders o USING(order_id) WHERE o.order_id IS NULL;
SELECT COUNT(*) AS orphan_payments, COUNT(*)=0 AS passes FROM raw.olist_order_payments p LEFT JOIN raw.olist_orders o USING(order_id) WHERE o.order_id IS NULL;

