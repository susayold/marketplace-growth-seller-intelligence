-- Demonstrate why joining raw order_items and raw payments before aggregation is unsafe.
-- Expected result: naive item price sum exceeds grain-safe item GMV.
SELECT COUNT(*) AS joined_rows, SUM(oi.price) AS naive_joined_gmv
FROM raw.olist_order_items oi JOIN raw.olist_order_payments p USING (order_id);

