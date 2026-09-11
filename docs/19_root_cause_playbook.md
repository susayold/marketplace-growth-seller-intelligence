# Root-cause playbook

Root-cause language is governed by evidence status. `supported` means the data is consistent with the hypothesis; `inconclusive` means the evidence is not decision-grade; `rejected` means the tested pattern does not support the hypothesis. No case is labeled causal from this observational source alone.

| Case | Question | Evidence status | Action | Monitoring |
|---|---|---|---|---|
| RC1 false GMV collapse | Is the apparent decline a partial-period artifact? | supported measurement risk | suppress partial-edge executive claims | complete-month GMV, orders, data freshness |
| RC2 acquisition quality gap | Which origins deserve channel experiments? | supported association, not causal | run origin-level experiments with downstream guardrails | conversion, 30-day activation, GMV/seller |
| RC3 activation bottleneck | Does slower first sale align with weaker retention? | supported descriptive gradient | test onboarding milestones at 7/30/60/90 days | activation rate, time-to-first-sale, M3 retention |
| RC4 seller concentration risk | Is value dependent on a narrow seller base? | supported concentration | monitor breadth and protect top sellers | Gini, top-share, active-seller breadth |
| RC5 late delivery/customer experience | Is lateness associated with poor reviews? | strong associative evidence | investigate carrier/category/state pathways | late rate, low-review rate, penalty, refunds/cost |
| RC6 category underperformance | Which categories combine value, breadth and experience risk? | supported segmentation | prioritize category deep dives where size × risk intersects | category GMV, seller breadth, late rate, reviews |

Each case has a matching SQL query under `sql/08_root_cause/` and evidence rows in `reports/root_cause_evidence.csv` and `reports/root_cause_hypothesis_matrix.csv`.

## Operating pattern

1. Define the metric tree and eligible population.
2. Separate measurement risk from business performance.
3. Test descriptive patterns with uncertainty and sample flags.
4. Record alternative explanations before recommending action.
5. Run an experiment or targeted operational investigation.
6. Keep primary KPI, guardrail, owner, cadence and stop condition in the decision register.

