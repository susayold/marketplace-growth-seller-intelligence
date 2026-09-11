CREATE OR REPLACE VIEW staging.orders AS SELECT order_id, customer_id, order_status, order_purchase_timestamp, order_delivered_customer_date, order_estimated_delivery_date FROM raw.olist_orders;
CREATE OR REPLACE VIEW staging.order_items AS SELECT order_id, order_item_id, product_id, seller_id, price, freight_value FROM raw.olist_order_items;
CREATE OR REPLACE VIEW staging.order_value AS SELECT order_id, SUM(price) AS gmv_proxy, SUM(freight_value) AS freight_value FROM staging.order_items GROUP BY order_id;
CREATE OR REPLACE VIEW staging.funnel AS SELECT m.mql_id, m.first_contact_date, COALESCE(NULLIF(m.origin, ''), 'unknown') AS origin, d.seller_id, d.won_date FROM raw.mql m LEFT JOIN raw.closed_deals d ON d.mql_id = m.mql_id;

