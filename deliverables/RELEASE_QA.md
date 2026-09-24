# Release QA — MarketLens v1.0

## Canonical source contract

| Area | Canonical output | Key result |
|---|---|---|
| Executive monthly KPIs | `tables/mart_marketplace_monthly.csv` | Jul → Aug: orders +2.9%, AOV -7.2% |
| Acquisition | `tables/mart_acquisition_channel.csv` | No `Partner` origin; origins are assessed across conversion and value |
| Activation | `tables/activation_summary.csv` | 30D 15.8%; 60D 30.8%; 90D 42.1% |
| Customer experience | `statistics/late_review_effect.csv` | Late: n=7,662, low-review 54.0%; on-time: n=88,168, low-review 9.2% |
| Decisions | `decision_register.csv` | D01–D05 only; D04 is P2 |

## Automated source checks

- No `Demo*` business tables remain in the semantic model.
- No stale `Partner` claim remains in report or website source.
- Power BI report inputs live under `deliverables/powerbi/source-data/`.
- File reads use the editable `DataRoot` parameter.
- `reports/qa/powerbi_reconciliation.csv` is fully `PASS`.
- `reports/qa/canonical_final_metrics.json` locks the cross-artifact release numbers.

## Portable PBIP contract

The project excludes Power BI's machine-local `.pbi` cache. On another
machine, set `DataRoot` to the local
`deliverables/powerbi/source-data/release_v3_final` folder and refresh.

## Final Desktop and artifact sign-off — 2026-09-24

- Final Power BI source commit:
  `561d9b6867f919708a9aff1fa86119381c225aff`.
- Final PDF publication commit:
  `87de2a32c2ff7561771ee9eebc8cfba307a3bf19`.
- Power BI Desktop refresh completed successfully.
- All seven pages were manually reviewed after refresh.
- Invalid Total rows are absent from Pages 1, 4 and 5.
- Page 3–6 insight copy renders without clipping.
- Page 7 contains the five governed decisions and final decision visual.
- 33 automated tests passed on the final Power BI source revision.
- Power BI source contract passed.
- Final release validator passed.
- Fresh seven-page PDF published and visually reviewed.
- Final PDF SHA-256:
  `488e30011814bde5eb0749014c63dbeacca448aa0fae6884f0b10a7efc3a5f34`.
- `deliverables/final-market-dashboard.pdf` and
  `dist/assets/final-market-dashboard.pdf` are byte-identical.
- GitHub CI for commit `87de2a3` passed.
- GitHub Pages deployment for commit `87de2a3` passed and renders fresh
  preview PNGs from the final website PDF.

## Release status

**FINAL / PASS.**

Further changes should be limited to genuine bug fixes or deliberate future
version work; the v1 portfolio scope is frozen.
