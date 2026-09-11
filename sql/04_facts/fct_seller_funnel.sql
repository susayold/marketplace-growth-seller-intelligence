CREATE TABLE IF NOT EXISTS facts.fct_seller_funnel AS SELECT m.mql_id, m.first_contact_date, m.origin, d.seller_id, d.won_date, CASE WHEN d.seller_id IS NOT NULL THEN 1 ELSE 0 END AS converted_flag FROM raw.mql m LEFT JOIN raw.closed_deals d USING (mql_id);

