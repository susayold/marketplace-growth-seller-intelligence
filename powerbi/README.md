# Power BI — final release

Status: **READY FOR FINAL DESKTOP REFRESH**. The editable PBIP and governed
source bundle include the latest semantic and report-definition fixes. The
checked-in PDF predates those fixes and must be re-exported after Desktop
validation.

## Delivered artifacts

- `../deliverables/powerbi/final market dashboard.pbip` — editable Power BI
  Project.
- `../deliverables/final-market-dashboard.pdf` — prior seven-page export;
  **pending re-export** from the updated PBIP.
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
already points to the governed source bundle in this checkout. When cloning or
extracting elsewhere, set it to the concrete local path
`<repository-root>\deliverables\powerbi\source-data\release_v3_final`, then
select **Refresh all** and save the PBIP.

Before a new release, verify all seven pages in Power BI Desktop, export a
fresh seven-page PDF, and only then synchronize website previews and the
release manifest. A fresh local refresh may show incomplete tables once; select
**Refresh now** and continue.
