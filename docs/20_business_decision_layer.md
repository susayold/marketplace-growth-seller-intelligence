# Business decision layer

The decision register converts evidence into bounded operating actions. Priority is based on evidence strength, actionability and scope; it is not an invented ROI score.

| ID | Priority | Decision | Primary KPI | Guardrail | Owner / cadence |
|---|---|---|---|---|---|
| D01 | P1 | publish complete-period measurement contract | complete-month coverage | data freshness / missingness | analytics, weekly |
| D02 | P1 | test acquisition journeys by origin | conversion + matched-seller value | 30-day activation and M3 retention | growth, weekly |
| D03 | P1 | improve seller onboarding milestones | activation by day 30 | M3 retention and seller quality | seller growth, weekly |
| D04 | P2 | manage seller concentration risk | top-share / Gini | active-seller breadth and service level | marketplace, monthly |
| D05 | P1 | investigate late-delivery pathways | late-delivery rate | low-review rate, cost and refunds | operations, weekly |

## Decision boundaries

- Do not scale a channel from conversion alone; require downstream value and retention guardrails.
- Do not call activation speed causal; use it to define an onboarding test.
- Do not treat concentration as a mandate for indiscriminate seller diversification; pair breadth with service quality and category economics.
- Do not interpret the late-review association as a causal uplift estimate until carrier, route and category confounding is addressed.
- Stop or escalate when a KPI improves while its guardrail breaches the threshold agreed by the owner.

The machine-readable source is `reports/decision_register.csv`; chart-ready decision views are under `reports/charts/10_decision_layer/`.

## Canonical metric policy

D01 consumes the reporting-boundary register and period-completeness table. D02 uses the repaired pooled-quarter retention comparison as a guardrail. D03 uses activation v3 fixed-window rates and keeps the observed activator median separate from cumulative activation. D04 and D05 remain on their existing concentration and late-review evidence unless the headline reconciliation changes their inputs.

