# Root-cause investigation cases

## Case 1 — Marketplace growth
**Trigger:** monthly GMV proxy and order trend.
**Evidence:** total GMV proxy is R$ 13,591,644; latest monthly GMV proxy is R$ 145, with MoM change -100.0%.
**Hypotheses:** order volume, AOV, active seller count, or seller productivity.
**Diagnostic:** use `growth_decomposition.csv`; do not infer causality from decomposition alone.

## Case 2 — High-volume but low-value acquisition
**Trigger:** acquisition origins with large MQL volume and lower downstream seller value.
**Evidence:** compare `mart_acquisition_channel.csv` by MQL denominator, conversion, matched seller count, and GMV per matched seller.
**Recommendation:** use a two-dimensional channel scorecard; avoid optimizing raw lead volume alone.

## Case 3 — Customer experience
**Trigger:** late-delivery rate and review score.
**Evidence:** `mart_order_experience.csv` compares on-time and late delivered orders.
**Recommendation:** prioritize categories/states with material order volume and weak service metrics; treat the relationship as associative.
