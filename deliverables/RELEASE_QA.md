# Release QA — MarketLens v1.0

## Canonical source contract

| Area | Canonical output | Key result |
|---|---|---|
| Executive monthly KPIs | `tables/mart_marketplace_monthly.csv` | Jul → Aug: orders +2.9%, AOV -7.2% |
| Acquisition | `tables/mart_acquisition_channel.csv` | No `Partner` origin; actionable origins are assessed across conversion and value |
| Activation | `tables/activation_summary.csv` | 30D 15.8%; 60D 30.8%; 90D 42.1% |
| Customer experience | `statistics/late_review_effect.csv` | Late: n=7,662, low-review 54.0%; on-time: n=88,168, low-review 9.2% |
| Decisions | `decision_register.csv` | D01–D05 only; D04 is P2 |

## Automated source checks

- No `Demo*` business tables remain in the semantic model.
- No `Partner` claim remains in report or website source.
- All reports inputs live under `deliverables/powerbi/source-data/`.
- All file reads use the editable `DataRoot` Power Query parameter.
- `reports/qa/powerbi_reconciliation.csv` contains the final SQL-to-Power BI
  reconciliation; every required metric is `PASS` within tolerance.
- `reports/qa/canonical_final_metrics.json` locks the cross-artifact release
  numbers used by the analytical repo, Power BI, PDF, and website.

## Desktop sign-off and opening the PBIP

The project deliberately excludes Power BI's machine-local `.pbi` cache. This
keeps the deliverable portable and prevents stale demo values from travelling
with the project. On the first open, Power BI Desktop can show **Some tables
have incomplete or no data**. Select **Refresh now** once; the model reads the
governed CSV bundle in `deliverables/powerbi/source-data/release_v3_final`.

The `DataRoot` parameter already points to that bundle in this repository. No
credentials, gateway, or query editing are required.

After the first refresh, use Desktop to inspect the seven rendered pages and
export a new PDF before publishing a binary release.

## Prior verified sign-off — 2026-09-21

- PBIP opened from the repository and full model refresh completed successfully.
- All governed model partitions report `Ready` after refresh.
- DAX smoke test: 24 monthly rows, 10 acquisition rows, 12 activation rows,
  3 commercial rows, 2 customer-experience rows, 5 decision rows, 23 retention
  rows and 6 root-cause rows; all 3 commercial growth values are populated.
- All seven Power BI pages captured successfully with no bridge failures.
- PDF pages 1–7 were rendered and visually checked after the final snapshot
  refresh; website preview PNGs and the PDF use the same verified snapshots.
- Static checks passed: no legacy Demo/Partner/mock/CX field references and no
  malformed report-definition JSON.

## Pending final Desktop sign-off — updated PBIP

- The PBIP source now contains display-safe activation numerators, refreshed
  evidence wording and report-label fixes, and corrected visual field bindings.
- Automated source contracts, report-definition validation, and the Python test
  suite pass for those changes.
- Refresh the PBIP in Desktop, inspect all seven pages, save, and export a new
  PDF before representing the existing PDF or website previews as current.
