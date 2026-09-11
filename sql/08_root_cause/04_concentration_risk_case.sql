-- RC4 seller concentration case: seller-level distribution before percentile aggregation.
SELECT metric, value, ci_low, ci_high
FROM analytics.mart_concentration_statistics
WHERE metric IN ('gini','top_1_pct_share','top_5_pct_share','top_10_pct_share','top_20_pct_share');

