# Power BI — final release

Status: **FINAL — DESKTOP REFRESH AND VISUAL QA PASSED**.

The editable PBIP source, governed analytical input bundle, seven-page PDF and
deployed website represent the same final MarketLens release.

## Delivered artifacts

- `../deliverables/powerbi/final market dashboard.pbip` — editable final Power
  BI Project.
- `../deliverables/final-market-dashboard.pdf` — final verified seven-page
  export.
- `../deliverables/powerbi/source-data/release_v3_final/` — governed
  analytical inputs required for refresh.
- `../reports/qa/powerbi_reconciliation.csv` — SQL-to-Power BI reconciliation;
  every required metric is `PASS`.

The model contains seven pages: Executive Overview, Seller Acquisition, Seller
Activation & Retention, Commercial Performance, Customer Experience &
Operations, Root Cause & Diagnostic, and Decision Center.

## Final verification

- Final source commit:
  `561d9b6867f919708a9aff1fa86119381c225aff`.
- Final PDF publication commit:
  `87de2a32c2ff7561771ee9eebc8cfba307a3bf19`.
- Final PDF SHA-256:
  `488e30011814bde5eb0749014c63dbeacca448aa0fae6884f0b10a7efc3a5f34`.
- Full Power BI Desktop refresh: PASS.
- Seven-page visual inspection: PASS.
- 33 automated tests: PASS.
- Power BI source contract: PASS.
- Final release validator: PASS.
- GitHub CI and GitHub Pages deployment: PASS.

## Refresh

Open the PBIP from the repository root. If the repository is cloned or
extracted to another location, set the single `DataRoot` Power Query parameter
to:

`<repository-root>\deliverables\powerbi\source-data\release_v3_final`

Then select **Refresh all** and save the PBIP. No credentials, gateway or
per-query path edits are required.
