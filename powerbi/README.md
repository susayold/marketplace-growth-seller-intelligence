# Power BI — final release

Status: **FINAL — DESKTOP REFRESH, VISUAL QA AND PDF PUBLICATION PASSED**.

The editable PBIP, governed source bundle, seven-page PDF and deployed website
correspond to the final verified analytical release.

## Delivered artifacts

- `../deliverables/powerbi/final market dashboard.pbip` — editable final Power BI Project.
- `../deliverables/final-market-dashboard.pdf` — final verified seven-page export.
- `../dist/assets/final-market-dashboard.pdf` — byte-identical website copy.
- `../deliverables/powerbi/source-data/release_v3_final/` — governed analytical
  inputs required for refresh.
- `../reports/qa/powerbi_reconciliation.csv` — final reconciliation, all rows
  `PASS`.

## Final sign-off

- Final Power BI source commit: `561d9b6867f919708a9aff1fa86119381c225aff`.
- Final PDF publication commit: `87de2a32c2ff7561771ee9eebc8cfba307a3bf19`.
- Final PDF SHA-256:
  `488e30011814bde5eb0749014c63dbeacca448aa0fae6884f0b10a7efc3a5f34`.
- Power BI Desktop refresh: PASS.
- Seven-page visual review: PASS.
- Automated QA / release validator: PASS.
- GitHub CI: PASS.
- GitHub Pages deployment: PASS.

## Refresh

Open the PBIP from the repository root. When cloning or extracting elsewhere,
set `DataRoot` to:

`<repository-root>\deliverables\powerbi\source-data\release_v3_final`

Then select **Refresh all**. The project deliberately excludes Power BI's
machine-local `.pbi` cache so stale local values are not distributed.
