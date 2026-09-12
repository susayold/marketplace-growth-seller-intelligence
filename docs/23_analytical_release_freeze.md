# Analytical Release Freeze

**Commit:** `19e6e6496c104be83b62aa1855e13b31d7084eb4` analytical release artifacts  
**Date:** 2026-09-12  
**Verification Status:** `PASS_WITH_ASSOCIATIVE_LIMITATIONS` (`power_bi_ready=true`)  
**Scope:** Final pre-Power-BI consistency repair for the Marketplace Growth & Seller Intelligence showcase.  
**Metric version:** `v3` for activation; pooled-quarter R2 for the retention headline.

## Freeze decision

The analytical layer is frozen for the current extract when every gate below is `PASS`. Power BI is intentionally downstream of this freeze. The freeze does not authorize causal language: the source is observational, and the retention and operational models are associative.

| Gate | Required evidence | Status |
|---|---|---|
| Activation population/event/censoring reconciled | `reports/qa/activation_definition_reconciliation.csv`, `reports/statistics/activation_fixed_window.csv`, `reports/statistics/activation_survival.csv` | PASS |
| Retention separation repaired | `reports/statistics/retention_model_diagnostics.csv`, `retention_model_comparison.csv`, `retention_cohort_outcome_cells.csv` | PASS |
| Reporting boundary reconciled | `reports/qa/reporting_boundary_register.csv`, `period_completeness.csv` | PASS |
| Headline claims reconciled | `reports/qa/headline_claim_reconciliation.csv` | PASS |
| Website uses canonical claims | `reports/qa/website_metric_audit.csv` plus deployed Site review | PASS |
| Chart registry and files aligned | `reports/chart_registry.csv` and `reports/charts/**/*.png` | PASS |
| Automated acceptance | `reports/qa/analysis_showcase_verification.json` and `tests/test_consistency_repair.py` | PASS after final run |

## Frozen headline definitions

- **Activation:** 842 closed sellers, 380 exact post-win matched sellers, 840 activation-eligible sellers, 380 observed activation events and 460 right-censored sellers. Fixed-window rates use observable denominators: 15.8% by day 30 (`130/825`), 30.8% by day 60 (`247/803`) and 42.1% by day 90 (`324/769`). The separate observed-activator median is 44.3 days.
- **Retention:** the headline model is `R2_origin_plus_pooled_cohort`, using origin plus pooled quarter and HC3 robust standard errors. The legacy month-cohort model remains in the diagnostics only because its sparse cells produced separation. Origin contrasts are guardrails, not ranking KPIs.
- **Reporting:** raw order data extend to 2018-11-12, while the executive complete-month boundary is 2018-08-31 under the low-volume/edge-period rule. The tail is not interpreted as a commercial collapse.
- **Concentration and experience:** top 20% seller GMV share is 82.7% with Gini 0.792; late orders have a 44.8 percentage-point higher low-review risk and a 5.9× risk ratio. Both remain descriptive/associative evidence.

## Canonical Activation Definition

The canonical table is `reports/tables/seller_activation_timing.csv` at one row per activation-eligible matched closed seller. Exact first-sale timestamps define `activation_event`; sellers without an event through their observation horizon remain `censored`. Fixed-window rates use observable denominators and Wilson 95% intervals. The observed-activator median (44.3 days) is intentionally separate from survival-estimated cumulative activation.

## Canonical Retention Conclusion

The descriptive R0 output, origin-only R1, pooled-quarter R2 and actionable-origin R3 specifications are retained together. R0–R3 support the same operating conclusion: origin is useful context for conversion governance, but current M3 retention contrasts are imprecise and do not support an origin-specific retention intervention. R2 is the headline adjusted model because the legacy monthly-cohort model had sparse-cell separation.

## Reporting Boundary Contract

Each domain records raw observation, analytical eligibility and executive-complete boundaries separately in `reports/qa/reporting_boundary_register.csv`. Executive trend reporting uses `reports/qa/period_completeness.csv`, excluding edge months and months below the configured 5% interior-volume threshold.

## Frozen Root-Cause Cases

RC1–RC6 remain in `reports/root_cause_evidence.csv`. RC1 is a confirmed reporting-boundary issue for the observed tail; RC2 is an associative acquisition-quality case with retention as a guardrail; RC3 is the canonical v3 activation timing signal; RC4–RC6 retain their existing concentration, delivery and category evidence.

## Frozen Decision Cards

D01–D05 remain in `reports/decision_register.csv`. D03 uses v3 30/60/90-day activation and observed-activator median; D02 uses conversion and downstream value as primary acquisition metrics with M3 retention as guardrail. Every card retains owner, cadence and stop condition.

## Known Limitations

The source is observational, seller readiness and demand are incompletely observed, review selection may be non-random, the GMV measure is a proxy, and the extract does not provide causal channel assignment or CAC/ROAS.

## Deferred Work

- Power BI semantic model and dashboard build.
- Any causal experiment or operational rollout; these require pre-registered guardrails and refreshed source data.

## Release rules

1. Do not restore the old `valid_activation_link` headline or use the old 30/60/90 rates.
2. Do not publish origin-specific M3 retention as a definitive ranking while the confidence intervals cross 1.0.
3. Do not use partial or low-volume edge months for executive trend claims.
4. Every decision card must retain its source file, chart ID, root-cause case, owner, guardrail and stop condition.
5. Any source refresh or metric-definition change reopens the freeze and requires the repair scripts, charts, tests and verification JSON to be rerun.

## Power BI handoff

Power BI may begin only after `power_bi_ready=true` in `reports/qa/analysis_showcase_verification.json`. The semantic model must import the frozen definitions above, preserve the boundary fields, and expose population, denominator, censoring and uncertainty metadata alongside every headline measure.

**Verification base commit:** `19e6e6496c104be83b62aa1855e13b31d7084eb4` (the analytical artifacts validated by the final automated run).
