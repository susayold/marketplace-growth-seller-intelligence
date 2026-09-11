CREATE TABLE IF NOT EXISTS dimensions.dim_channel AS SELECT DISTINCT COALESCE(NULLIF(origin, ''), 'unknown') AS origin FROM raw.mql;

