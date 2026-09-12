# Analytical Release Freeze

**Scope:** Final pre-Power-BI consistency repair for the Marketplace Growth & Seller Intelligence showcase.  
**Metric version:** `v3` for activation; pooled-quarter R2 for the retention headline.  
**Release status:** `PASS_WITH_ASSOCIATIVE_LIMITATIONS` once the verification JSON is regenerated from the committed artifacts.

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

## Release rules

1. Do not restore the old `valid_activation_link` headline or use the old 30/60/90 rates.
2. Do not publish origin-specific M3 retention as a definitive ranking while the confidence intervals cross 1.0.
3. Do not use partial or low-volume edge months for executive trend claims.
4. Every decision card must retain its source file, chart ID, root-cause case, owner, guardrail and stop condition.
5. Any source refresh or metric-definition change reopens the freeze and requires the repair scripts, charts, tests and verification JSON to be rerun.

## Power BI handoff

Power BI may begin only after `power_bi_ready=true` in `reports/qa/analysis_showcase_verification.json`. The semantic model must import the frozen definitions above, preserve the boundary fields, and expose population, denominator, censoring and uncertainty metadata alongside every headline measure.

**Verification base commit:** recorded in the release commit history after the final automated run.
