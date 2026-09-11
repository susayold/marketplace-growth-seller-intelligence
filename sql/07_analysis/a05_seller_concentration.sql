WITH ranked AS (
    SELECT
        seller_id,
        gmv_proxy,
        ROW_NUMBER() OVER (ORDER BY gmv_proxy DESC, seller_id) AS seller_row_number,
        RANK() OVER (ORDER BY gmv_proxy DESC) AS gmv_rank,
        DENSE_RANK() OVER (ORDER BY gmv_proxy DESC) AS dense_gmv_rank,
        SUM(gmv_proxy) OVER () AS total_gmv,
        SUM(gmv_proxy) OVER (
            ORDER BY gmv_proxy DESC, seller_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS running_gmv
    FROM marts.mart_seller_lifetime
),
seller_stats AS (
    SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY gmv_proxy) AS median_seller_gmv
    FROM marts.mart_seller_lifetime
),
scored AS (
    SELECT
        ranked.*,
        running_gmv / NULLIF(total_gmv, 0) AS cumulative_share,
        NTILE(5) OVER (ORDER BY gmv_proxy DESC, seller_id) AS quintile
    FROM ranked
)
SELECT
    quintile,
    COUNT(*) AS sellers,
    SUM(gmv_proxy) AS gmv_proxy,
    SUM(gmv_proxy) / MAX(total_gmv) AS share_of_gmv,
    MAX(cumulative_share) AS cumulative_share,
    MAX(seller_stats.median_seller_gmv) AS median_seller_gmv
FROM scored
CROSS JOIN seller_stats
GROUP BY quintile
ORDER BY quintile;

