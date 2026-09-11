# Analysis showcase release

Status: **PASS_WITH_ASSOCIATIVE_LIMITATIONS**

This is the pre-Power-BI analytical release required by the new showcase plan. It freezes the measurement contract, statistical evidence, root-cause cases, decision register, chart registry and remote delivery paths before any semantic-model/dashboard build.

## Acceptance snapshot

- Raw evidence: orders, items, reviews, marketing funnel and linked seller metrics rebuilt.
- Statistical outputs: 29 CSV/JSON files in `reports/statistics/`.
- Charts: 61 PNGs; 92 registry rows; all chart files have source/method/denominator metadata.
- Root-cause layer: 6 cases, 20 hypotheses, no causal overclaim.
- Decision layer: 5 decision cards with KPI, guardrail, owner, cadence and stop condition.
- QA: verification JSON includes counts, required files, chart count, registry status and warnings.
- Delivery: GitHub and Drive are the authoritative storage locations; working raw data is not retained locally after upload.

Power BI is intentionally the next phase, not part of this pre-build gate.

