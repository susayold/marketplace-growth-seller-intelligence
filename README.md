# Marketplace Growth & Seller Intelligence

Decision-support analysis of marketplace growth, seller activation, retention, concentration and customer experience.

## Current release

The pre-Power-BI statistical showcase is complete with 61 charts, 29 statistical outputs, 6 root-cause cases, 20 hypotheses and 5 decision cards. The evidence status is `PASS_WITH_ASSOCIATIVE_LIMITATIONS`: observational results are suitable for prioritization and experiment design, not causal attribution.

Start with:

- `docs/18_statistical_rigor_upgrade.md` — measurement, uncertainty and model rules
- `docs/19_root_cause_playbook.md` — six evidence-backed investigation cases
- `docs/20_business_decision_layer.md` — KPI/guardrail decision cards
- `docs/21_chart_catalog.md` — chart map and Power BI candidates
- `docs/22_claims_and_evidence_register.md` — allowed wording and boundaries
- `reports/qa/analysis_showcase_verification.json` — acceptance checks

## Rebuild

Set `OLIST_RAW_DIR` to a temporary source directory and `OLIST_PROJECT_DIR` to the project path, then run `make analysis-showcase` or execute the five Python scripts in `src/`. Raw data is an input only and is not committed to the repository.

## Core findings

- Acquisition conversion differs by origin; pairwise comparisons are FDR-adjusted and downstream activation/retention remain guardrails.
- Activation speed is descriptively associated with M3 retention; it is a testable onboarding mechanism, not a causal conclusion.
- Seller value is concentrated: Gini is approximately 0.792 and the top 20% account for approximately 82.7% of positive-GMV seller value.
- Late delivery is associated with a 44.8 percentage-point higher low-review rate in reviewed delivered orders; an adjusted model retains the association after observed controls.

Power BI is deliberately the next phase after this analytical release gate.

