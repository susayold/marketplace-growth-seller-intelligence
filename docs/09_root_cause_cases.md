# Root-cause investigation cases

Each case separates trigger, scope, hypotheses, evidence, alternative explanations, conclusion, action and risk. Findings are descriptive/associative unless stated otherwise.

## Case 1 — Marketplace GMV decline

**Problem:** The final observed month shows a sharp GMV proxy decline.

**Trigger metric:** monthly GMV proxy, orders, active sellers and AOV from mart_marketplace_monthly.

**Scope:** the historical dataset boundary; the final month is a partial/low-volume tail and should not be treated as a current operating period.

**Initial hypotheses:**
- order volume fell;
- active-seller coverage fell;
- AOV changed;
- the observed final month is incomplete.

**Evidence:** growth_decomposition.csv decomposes month-over-month change into GMV, orders, active sellers and AOV. The final row is an extreme negative movement because the observed tail contains very little activity relative to the prior month.

**Alternative explanations:** source extract boundary, delayed orders, missing late-arriving records, or an incomplete final calendar month.

**Conclusion:** the data supports a measurement/boundary investigation before a commercial-growth conclusion.

**Recommended action:** exclude partial periods from the weekly operating scorecard, add a freshness/completeness gate, and monitor the four-metric decomposition.

**Risk / limitation:** the historical dataset does not establish the current marketplace trend or a causal driver.

## Case 2 — High-volume but low-value acquisition channel

**Problem:** A channel with many MQLs may not create the most commercial value.

**Trigger metric:** MQL volume, conversion rate, matched sellers and downstream GMV proxy per matched seller.

**Scope:** linked funnel records only; not every lead maps to a marketplace seller.

**Initial hypotheses:**
- raw lead volume is optimized at the expense of conversion quality;
- a channel attracts sellers with lower early value;
- observed differences reflect channel mix or linkage coverage.

**Evidence:** mart_acquisition_channel.csv reports all denominators together. A channel is not ranked on conversion alone; matched seller count and downstream GMV are required.

**Alternative explanations:** small-channel volatility, different seller segments, sales-team routing, or missing spend data.

**Conclusion:** channel performance is multidimensional and cannot be represented by MQL volume alone.

**Recommended action:** use a minimum-volume scorecard with conversion, match rate, activation and downstream GMV; add CAC once spend is available.

**Risk / limitation:** without marketing cost, CAC and ROAS cannot be calculated.

## Case 3 — Customer experience deterioration

**Problem:** Late-delivery orders receive weaker review outcomes.

**Trigger metric:** late-delivery rate, average review score and low-review rate.

**Scope:** delivered orders at order grain; seller attribution is intentionally not assigned for multi-seller orders.

**Initial hypotheses:**
- late delivery harms customer experience;
- late orders differ by category, route, carrier or season;
- review response and selection bias distort the observed association.

**Evidence:** mart_order_experience.csv shows the comparison between late and on-time/early orders; statistical_validation.csv records a strong association test.

**Alternative explanations:** category mix, geography, freight complexity, seller mix, review non-response and unmeasured operational conditions.

**Conclusion:** late delivery is a high-priority diagnostic signal, not proof of a causal effect or a single-seller fault.

**Recommended action:** segment by volume, delay severity, state, category and carrier; then test operational interventions.

**Risk / limitation:** observational evidence and multi-seller orders limit causal and seller-level attribution.

