# Page 1 real-data load check

Checked on 2026-09-12 with Power BI Desktop 2.157.879.0.

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
| Active Sellers (latest complete month) | 1,278 |
| Average Order Value | R$ 137.75 |
| Late Delivery Rate | 8.11% |
| Seller Gini | 0.7915 |
| Top 20% GMV share | 82.69% |

The latest executive-complete period is August 2018; incomplete edge periods are excluded from the executive trend logic.

## Fixes applied

- Removed the Geo cyclic-reference condition by using the unique measure `Seller Count`.
- Renamed duplicate model measures to `Category GMV Total` and `State GMV Total`.
- Restored the PBIP `themeCollection` declaration so the page renders its visual containers.
- Added the registered `page_background.png` resource and native title cards for the sidebar, header, chart blocks, and KPI labels.
- Corrected the trend combo projection so Orders render as columns and GMV renders as a line on the secondary axis.
- Kept state distribution as a native clustered bar visual for Desktop stability; the supplied reference uses a map, but the underlying Geo data is present and verified.

Note: a PBIP import model can show the `Refresh now` banner on its first open because the CSV-backed import cache is not stored in the text project. After the first refresh, the page renders and the checks above pass.

