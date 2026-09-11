SELECT 'raw.orders.order_id' AS key_name, COUNT(*) AS rows, COUNT(DISTINCT order_id) AS distinct_keys, COUNT(*) = COUNT(DISTINCT order_id) AS passes FROM raw.olist_orders;
SELECT 'raw.order_items.order_id_order_item_id' AS key_name, COUNT(*) AS rows, COUNT(DISTINCT (order_id, order_item_id)) AS distinct_keys, COUNT(*) = COUNT(DISTINCT (order_id, order_item_id)) AS passes FROM raw.olist_order_items;

