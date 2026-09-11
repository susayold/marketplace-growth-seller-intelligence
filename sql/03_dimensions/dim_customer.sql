CREATE TABLE IF NOT EXISTS dimensions.dim_customer AS SELECT DISTINCT customer_id, customer_unique_id, customer_city, customer_state FROM raw.olist_customers;

