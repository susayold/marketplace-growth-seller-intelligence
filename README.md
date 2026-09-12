# Marketplace Growth & Seller Intelligence

Decision-support analysis of marketplace growth, seller activation, retention, concentration and customer experience.

## Current release

The pre-Power-BI showcase is frozen against the analytical consistency release-freeze plan. It has 61 registered charts (66 rendered PNGs including five retained legacy summaries), the original statistical pack plus v3 activation/retention QA artifacts, 6 root-cause cases, 20 hypotheses and 5 decision cards. `reports/qa/analysis_showcase_verification.json` reports every repair gate as `true`; observational limitations remain explicit.

Start with:

- `docs/18_statistical_rigor_upgrade.md` — measurement, uncertainty and model rules
- `docs/19_root_cause_playbook.md` — six evidence-backed investigation cases
- `docs/20_business_decision_layer.md` — KPI/guardrail decision cards
- `docs/21_chart_catalog.md` — chart map and Power BI candidates
- `docs/22_claims_and_evidence_register.md` — allowed wording and boundaries
- `docs/metric_changelog.md` — activation v1 → v2 → canonical v3 changes
- `reports/headline_metrics.json` — single source for headline numbers
- `reports/qa/activation_definition_reconciliation.csv` — 327 vs 380 reconciliation
- `reports/qa/reporting_boundary_register.csv` — raw/analytical/executive boundaries
- `reports/qa/headline_claim_reconciliation.csv` — claim-to-source audit
- `reports/qa/analysis_showcase_verification.json` — acceptance checks
- `docs/23_analytical_release_freeze.md` — freeze decision and Power BI handoff contract

## Rebuild

Set `OLIST_RAW_DIR` to a temporary source directory and `OLIST_PROJECT_DIR` to the project path, then run `make analysis-showcase` or execute the five Python scripts in `src/`. Raw data is an input only and is not committed to the repository.

## Core findings

- Acquisition conversion differs by origin; pairwise comparisons are FDR-adjusted and downstream activation/retention remain guardrails.
- Activation v3 uses exact seller-level first-sale timestamps, eligibility-aware fixed windows and right censoring; 30-day activation is 15.8% over 825 observable sellers and observed activator median is 44.3 days.
- The repaired M3 retention headline model uses origin plus pooled eligible cohort quarter with HC3 robust errors; origin effects remain imprecise and are a guardrail, not a channel-ranking KPI.
- Seller value is concentrated: Gini is approximately 0.792 and the top 20% account for approximately 82.7% of positive-GMV seller value.
- Late delivery is associated with a 44.8 percentage-point higher low-review rate in reviewed delivered orders; an adjusted model retains the association after observed controls.

Power BI is deliberately the next phase after this analytical release gate.

