# Statistical rigor upgrade

## Purpose

This release upgrades the marketplace analysis from descriptive dashboarding to a decision-support evidence layer. The source is the reviewed Olist Brazilian E-Commerce + Marketing Funnel extract. The evidence remains observational: a strong association is not a causal estimate.

## Measurement rules

- Every rate states its denominator and eligibility population.
- The first and last observed calendar months, plus low-volume tails, are flagged as partial. Executive trend claims use complete interior months only.
- Sample flags are deterministic: `insufficient` (<10), `small` (10–29), `usable` (30–99), `strong` (>=100).
- Proportions use Wilson 95% intervals. Means, medians, differences, Gini and concentration summaries use deterministic bootstrap 95% intervals.
- M3 retention excludes sellers/cohorts that cannot yet be observed at month 3. Current linked M3 eligible population is 281 sellers.

## Inference rules

- Acquisition origin pairwise tests use two-proportion comparisons with Benjamini–Hochberg FDR correction.
- Adjusted models are binomial GLMs with HC3 robust standard errors.
- The retention model is restricted to major origins to avoid sparse/separation-driven headline claims; sparse origins remain in the descriptive output.
- The low-review model controls for delay, category, customer state, log order value, freight ratio and purchase month, but is explicitly associative.
- Every claim is paired with an alternative explanation and a decision boundary in `reports/claims_and_evidence_register.csv`.

## Consistency repair contract

- Activation v3 is the canonical definition: exact first-sale timestamps, activation-eligible population, explicit censoring and observable fixed-window denominators. The reconciliation is in `reports/qa/activation_definition_reconciliation.csv`.
- Retention R2 is `M3_retained ~ origin + cohort_period`, where `cohort_period` is the defensible quarter-level pool with at least 30 eligible sellers and both outcomes. The cell audit, model comparison and separation diagnostics are in `reports/statistics/retention_cohort_outcome_cells.csv`, `retention_model_comparison.csv` and `retention_model_diagnostics.csv`.
- The raw/analytical/executive reporting-boundary contract is in `reports/qa/reporting_boundary_register.csv` and `reports/qa/period_completeness.csv`.
- `reports/headline_metrics.json` is the single source for recruiter-facing headline values. Downstream charts, root-cause cases, decision cards, README and website must reconcile to it.

## Results

- 99,441 orders, 112,650 order items and 99,224 reviews were loaded at governed grains.
- Acquisition is heterogeneous: unknown is 16.65% converted, paid search 12.30%, organic search 11.80%, and social 5.56%.
- M3 retention is eligible-aware and wide by origin; origin-specific retention is not strong causal evidence.
- Seller value is concentrated: Gini 0.792; top 1% 26.1%, top 5% 53.3%, top 10% 67.6%, top 20% 82.7% of positive-GMV seller value.
- Late delivery is associated with a 44.8 percentage-point higher low-review rate; risk ratio is about 5.9 in the reviewed delivered population.

## Inspectable outputs

See `reports/statistics/`, `reports/root_cause_evidence.csv`, `reports/decision_register.csv`, `reports/robustness_register.csv`, `reports/multiple_testing_register.csv`, and `reports/qa/analysis_showcase_verification.json`.

