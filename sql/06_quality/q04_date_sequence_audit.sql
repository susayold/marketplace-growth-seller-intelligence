SELECT COUNT(*) AS invalid_sequences, COUNT(*)=0 AS passes FROM raw.olist_orders WHERE order_delivered_customer_date IS NOT NULL AND order_estimated_delivery_date IS NOT NULL AND order_delivered_customer_date < order_purchase_timestamp;

