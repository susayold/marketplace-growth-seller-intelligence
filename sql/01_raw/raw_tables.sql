CREATE TABLE IF NOT EXISTS raw.olist_orders (
    order_id text PRIMARY KEY,
    customer_id text NOT NULL,
    order_status text NOT NULL,
    order_purchase_timestamp timestamptz,
    order_approved_at timestamptz,
    order_delivered_carrier_date timestamptz,
    order_delivered_customer_date timestamptz,
    order_estimated_delivery_date timestamptz
);
CREATE TABLE IF NOT EXISTS raw.olist_order_items (
    order_id text NOT NULL,
    order_item_id integer NOT NULL,
    product_id text,
    seller_id text,
    shipping_limit_date timestamptz,
    price numeric(14,2),
    freight_value numeric(14,2),
    PRIMARY KEY (order_id, order_item_id)
);
CREATE TABLE IF NOT EXISTS raw.olist_order_payments (order_id text, payment_sequential integer, payment_type text, payment_installments integer, payment_value numeric(14,2));
CREATE TABLE IF NOT EXISTS raw.olist_order_reviews (review_id text, order_id text, review_score integer, review_creation_date timestamptz, review_answer_timestamp timestamptz);
CREATE TABLE IF NOT EXISTS raw.olist_customers (customer_id text PRIMARY KEY, customer_unique_id text, customer_zip_code_prefix integer, customer_city text, customer_state text);
CREATE TABLE IF NOT EXISTS raw.olist_sellers (seller_id text PRIMARY KEY, seller_zip_code_prefix integer, seller_city text, seller_state text);
CREATE TABLE IF NOT EXISTS raw.olist_products (product_id text PRIMARY KEY, product_category_name text, product_name_lenght integer, product_description_lenght integer, product_photos_qty integer, product_weight_g numeric, product_length_cm numeric, product_height_cm numeric, product_width_cm numeric);
CREATE TABLE IF NOT EXISTS raw.olist_geolocation (geolocation_zip_code_prefix integer, geolocation_lat numeric, geolocation_lng numeric, geolocation_city text, geolocation_state text);
CREATE TABLE IF NOT EXISTS raw.mql (mql_id text PRIMARY KEY, first_contact_date date, landing_page_id text, origin text);
CREATE TABLE IF NOT EXISTS raw.closed_deals (mql_id text PRIMARY KEY, seller_id text, sdr_id text, sr_id text, won_date date, business_segment text, lead_type text, lead_behaviour_profile text, has_company text, has_gtin text, average_stock text, business_type text, declared_product_catalog_size numeric, declared_monthly_revenue numeric);

