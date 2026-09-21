# Power BI — final release

Status: **PASS**. The editable PBIP, seven-page PDF, governed source bundle,
and SQL-to-Power BI reconciliation are included in this release.

## Delivered artifacts

- `../deliverables/powerbi/final market dashboard.pbip` — editable Power BI
  Project.
- `../deliverables/final-market-dashboard.pdf` — verified seven-page export.
- `../deliverables/powerbi/source-data/release_v3_final/` — governed analytical
  inputs required for refresh.
- `../reports/qa/powerbi_reconciliation.csv` — final reconciliation, all rows
  `PASS`.

The report uses canonical analytical outputs rather than raw payment/order-item
joins or demo tables. The model has seven pages: Executive Overview, Seller
Acquisition, Seller Activation & Retention, Commercial Performance, Customer
Experience & Operations, Root Cause & Diagnostic, and Decision Center.

## Refresh

Open the PBIP from the repository root. The `DataRoot` Power Query parameter
already points to the governed source bundle in this checkout. When cloning to
another machine, change only that parameter to the local
`deliverables/powerbi/source-data/release_v3_final` path, then refresh.

Power BI Desktop was opened against the release, the model refresh completed,
all governed partitions returned `Ready`, and all seven pages were captured and
visually checked. A fresh local refresh may show incomplete tables once; select
**Refresh now** and continue.
