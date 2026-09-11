CREATE TABLE IF NOT EXISTS dimensions.dim_date AS
WITH bounds AS (SELECT MIN(order_purchase_timestamp)::date AS min_date, MAX(order_purchase_timestamp)::date AS max_date FROM raw.olist_orders), series AS (SELECT generate_series(min_date, max_date, INTERVAL '1 day')::date AS date_day FROM bounds)
SELECT date_day, EXTRACT(YEAR FROM date_day)::int AS year, EXTRACT(QUARTER FROM date_day)::int AS quarter, EXTRACT(MONTH FROM date_day)::int AS month, DATE_TRUNC('month', date_day)::date AS month_start, EXTRACT(DOW FROM date_day)::int AS day_of_week FROM series;

