CREATE TABLE IF NOT EXISTS facts.fct_order_item AS SELECT i.*, DATE_TRUNC('month', o.order_purchase_timestamp)::date AS purchase_month FROM staging.order_items i INNER JOIN staging.orders o USING (order_id);

