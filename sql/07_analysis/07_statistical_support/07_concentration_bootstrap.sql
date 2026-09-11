-- Seller value concentration population. Aggregate to seller before any percentile math.
SELECT seller_id, SUM(gmv_proxy) AS seller_gmv_proxy
FROM analytics.mart_order_item_grain
GROUP BY 1
HAVING SUM(gmv_proxy) > 0;
-- Compute Gini, top 1/5/10/20 shares, Lorenz curve, and deterministic bootstrap CIs downstream.

