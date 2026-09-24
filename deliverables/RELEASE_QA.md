# Release QA — MarketLens v1.0

## Canonical source contract

| Area | Canonical output | Key result |
|---|---|---|
| Executive monthly KPIs | `tables/mart_marketplace_monthly.csv` | Jul → Aug: GMV -4.6%, orders +2.9%, sellers +1.3%, AOV -7.2%, late delivery +5.9pp |
| Acquisition | `tables/mart_acquisition_channel.csv` | 8,000 MQLs; 842 converted; no `Partner` origin |
| Activation | `tables/activation_summary.csv` | 30D 15.8%; 60D 30.8%; 90D 42.1% |
| Concentration | governed concentration outputs | Seller Gini 0.792; Top 20% share 82.7% |
| Customer experience | `statistics/late_review_effect.csv` | Late n=7,662 / 54.0% low-review; on-time n=88,168 / 9.2% |
| Decisions | `decision_register.csv` | D01–D05 only; D04 is P2 / monthly |

## Automated source checks

- No `Demo*` business tables remain in the semantic model.
- No stale Partner / cohort-ranking / synthetic root-cause claims remain.
- All Power BI file reads use the editable `DataRoot` parameter.
- Activation 30D/60D/90D denominators use observable windows.
- Non-observable activation rates and display counts remain blank.
- Commercial headline Orders/AOV reconcile to canonical marketplace measures.
- Page 4 / Page 5 invalid matrix totals are disabled in the final Desktop state.
- Page 6 root-cause visuals use the governed case/evidence semantics.
- Decision Center contains the five governed decisions.
- `reports/qa/powerbi_reconciliation.csv` is PASS for all required metrics.
- `reports/qa/canonical_final_metrics.json` locks the cross-artifact release
  values.

## Final Desktop and artifact sign-off — 2026-09-24

- Final Power BI source commit:
  `561d9b6867f919708a9aff1fa86119381c225aff`.
- Final PDF publication commit:
  `87de2a32c2ff7561771ee9eebc8cfba307a3bf19`.
- PBIP opened from the final repository state and fully refreshed.
- `DataRoot` resolved to the governed `release_v3_final` source bundle.
- All seven pages were manually reviewed after refresh.
- Page 1 / Page 4 / Page 5 invalid Total rows are absent.
- Page 2 duplicate channel slicer is not visible.
- Page 3 KPI blank artifacts are not visible and retention labels are readable.
- Page 3–6 insight text renders without clipping.
- Page 6 root-cause case charts are readable.
- Page 7 contains exactly five governed decisions and the final decision bubble
  view renders correctly.
- 33 automated tests passed.
- Power BI source contract passed.
- Final release validator passed.
- Fresh seven-page PDF visually reviewed: PASS.
- Final PDF SHA-256:
  `488e30011814bde5eb0749014c63dbeacca448aa0fae6884f0b10a7efc3a5f34`.
- `deliverables/final-market-dashboard.pdf` and
  `dist/assets/final-market-dashboard.pdf` are byte-identical.
- GitHub CI passed for the final PDF publication.
- GitHub Pages deployment passed and renders fresh page previews from the final
  checked-in PDF.

## Reproduction note

The repository deliberately excludes machine-local Power BI `.pbi` cache
files. On another machine, set `DataRoot` to the checked-out
`deliverables/powerbi/source-data/release_v3_final` directory and select
**Refresh all** once.
