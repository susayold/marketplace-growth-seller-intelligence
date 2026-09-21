# Analysis showcase release

Status: **FINAL — PASS_WITH_ASSOCIATIVE_LIMITATIONS**

This analytical release freezes the measurement contract, statistical evidence,
root-cause cases, decision register, chart registry, and remote delivery paths
that underpin the final semantic model and dashboard.

## Acceptance snapshot

- Raw evidence: orders, items, reviews, marketing funnel and linked seller metrics rebuilt.
- Statistical outputs: 29 CSV/JSON files in `reports/statistics/`.
- Charts: 61 registered entries and 66 rendered PNGs; active registry rows have source/method/denominator metadata, with five retained legacy summaries explicitly outside the active registry.
- Root-cause layer: 6 cases, 20 hypotheses, no causal overclaim.
- Decision layer: 5 decision cards with KPI, guardrail, owner, cadence and stop condition.
- QA: verification JSON includes counts, required files, chart count, registry status and warnings.
- Delivery: GitHub and Drive are the authoritative storage locations; working raw data is not retained locally after upload.

The final PBIP, PDF, website, and reconciliation extend this analytical release
without changing the governed measurement contract.

