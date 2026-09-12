# Page 1 real-data load check

Checked on 2026-09-13 with Power BI Desktop 2.157.879.0.

## Source

The PBIP reads the frozen release at:

`C:\Users\sangk\Documents\Codex\2026-09-12\che\outputs\Marketplace_Growth_Seller_Intelligence_Page1\data\release_v3_final`

The report uses the release tables under `reports\tables` and the QA period file under `reports\qa`.

## Verified after refresh

| Table / metric | Result |
|---|---:|
| Monthly rows | 24 |
| Category rows | 1,283 |
| CategoryTop5 rows | 5 |
| StateTop5 rows | 5 |
| Geo rows | 23 |
| SellerLifetime rows | 3,095 |
| Highlights rows | 5 |
| GMV Proxy | R$ 13,591,643.70 |
| Orders | 98,666 |
| Active Sellers (Page 1 All-period default) | 3,095 |
| Monthly active_sellers (latest complete month, reference only) | 1,278 |
| Average Order Value | R$ 137.75 |
| Late Delivery Rate | 8.11% |
| Seller Gini | 0.7915 |
| Top 20% GMV share | 82.69% |

The latest executive-complete period is August 2018; incomplete edge periods are excluded from the executive trend logic.

The distinction above is intentional: the Page 1 KPI uses `DISTINCTCOUNT ( bi_fact_marketplace_item[seller_id] )` over the default All-period context, while 1,278 is the source mart's latest-month active-seller snapshot. They answer different questions and must not be mixed.

## Fixes applied

- Removed the Geo cyclic-reference condition by using the unique measure `Seller Count`.
- Renamed duplicate model measures to `Category GMV Total` and `State GMV Total`.
- Restored the PBIP `themeCollection` declaration so the page renders its visual containers.
- Added the registered `page_background.png` resource and native title cards for the sidebar, header, chart blocks, and KPI labels.
- Corrected the trend combo projection so Orders render as columns and GMV renders as a line on the secondary axis.
- Set the Page 1 Active Sellers measure to the governed all-period distinct seller count so the default KPI reconciles to 3,095 rather than the latest-month snapshot of 1,278.
- Added native trend measures that suppress the unmatched blank dimension member caused by incomplete edge months.
- Kept state distribution as a source-backed map image fallback in `v021` because the native map visual was unavailable in the current Desktop configuration; the underlying Geo data is present and verified.

Note: a PBIP import model can show the `Refresh now` banner on its first open because the CSV-backed import cache is not stored in the text project. After the first refresh, the page renders and the checks above pass.

