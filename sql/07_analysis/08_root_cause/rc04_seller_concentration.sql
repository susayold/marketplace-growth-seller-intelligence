-- RC4: seller-value concentration evidence.
SELECT metric,value,ci_low,ci_high FROM analytics.mart_concentration_statistics
WHERE metric LIKE 'top_%' OR metric='gini';