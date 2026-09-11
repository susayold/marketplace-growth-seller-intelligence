CREATE TABLE IF NOT EXISTS dimensions.dim_seller AS SELECT DISTINCT seller_id, seller_city, seller_state FROM raw.olist_sellers;

