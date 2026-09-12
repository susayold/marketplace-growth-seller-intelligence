# Interview guide — Marketplace Growth & Seller Intelligence

## Five-minute showcase

### Minute 0–1 — Can I trust the number?
Start with grain and denominator. The analysis uses 99,441 orders, 112,650 order items and 99,224 reviews. GMV is aggregated at order-item grain before payment joins; partial edge months are flagged before trend claims. Delivery/review metrics use reviewed delivered orders, while M3 retention excludes right-censored cohorts.

### Minute 1–2 — What pattern is visible?
Acquisition conversion differs by origin: paid search is 12.30%, organic search 11.80% and social 5.56% in the observed funnel. Pairwise comparisons retain effect sizes, intervals and Benjamini–Hochberg FDR context.

### Minute 2–3 — What does the statistical evidence support?
Activation is a time-to-event process. Faster activation buckets show higher observed M3 retention, but the pattern is treated as an onboarding hypothesis, not causal proof. The adjusted retention GLM is cohort-aware and restricted to major origins to avoid sparse headline claims.

### Minute 3–4 — Where is the marketplace fragile?
Seller value is concentrated: Gini is approximately 0.792; the top 1%, 5%, 10% and 20% account for approximately 26.1%, 53.3%, 67.6% and 82.7% of positive-GMV seller value. This supports monitoring breadth and top-seller resilience, not indiscriminate diversification.

### Minute 4–5 — What should the business do?
Late delivery is associated with a 44.8 percentage-point higher low-review rate, with a risk ratio of about 5.9. Investigate category, state, route and carrier pathways. The decision register turns this and the other cases into five cards with primary KPI, guardrail, owner, cadence and stop condition.

## Questions to expect

- **Why is this not causal?** The data is observational and may contain selection, mix, reverse-causality and unmeasured operational confounding. Adjusted models improve comparability but do not create randomization.
- **Why keep unknown acquisition origin?** It is part of the observed denominator and can reveal attribution problems, but it is not automatically an actionable channel.
- **Why not rank every segment?** Minimum sample flags, eligibility and uncertainty prevent small groups from driving decisions.
- **What would you do next?** Freeze the measurement contract, run acquisition and onboarding experiments with downstream guardrails, and launch a delivery pathway investigation. Power BI comes after this analytical gate.

## Remote artifacts

The production scripts, statistical outputs, chart registry, root-cause evidence and decision register are in the repository and mirrored to Drive. No raw or staging data is retained locally.
