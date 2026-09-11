WITH m AS (
    SELECT
        month_start,
        gmv_proxy,
        orders,
        active_sellers,
        aov,
        ROW_NUMBER() OVER (ORDER BY month_start) AS month_sequence,
        LAG(gmv_proxy) OVER (ORDER BY month_start) AS prior_gmv,
        LEAD(gmv_proxy) OVER (ORDER BY month_start) AS next_gmv,
        LAG(orders) OVER (ORDER BY month_start) AS prior_orders,
        LAG(active_sellers) OVER (ORDER BY month_start) AS prior_sellers,
        AVG(aov) OVER (ORDER BY month_start ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS aov_3m_avg
    FROM marts.mart_marketplace_monthly
)
SELECT
    month_sequence,
    month_start,
    gmv_proxy,
    prior_gmv,
    next_gmv,
    gmv_proxy - prior_gmv AS gmv_change,
    orders - prior_orders AS order_change,
    active_sellers - prior_sellers AS seller_change,
    aov - LAG(aov) OVER (ORDER BY month_start) AS aov_change,
    aov_3m_avg
FROM m
ORDER BY month_start;

