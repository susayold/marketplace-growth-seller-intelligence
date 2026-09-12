# Metric changelog

## Activation v1

- Population: valid links after converting `first_sale_month` to the first day of the month.
- Denominator: 327 links.
- Event definition: non-negative month-start lag.
- Why changed: same-month exact first sales were incorrectly treated as pre-win when the month start preceded `won_date`.
- Decision impact: superseded; do not use the old 30/60/90 rates.

## Activation v2

- Population: 380 exact observed post-win first-sale matches.
- Denominator: observed activators only.
- Event definition: exact first sale after won date.
- Why changed: restored seller-level timestamps and reconciled 327 vs 380.
- Decision impact: useful for observed timing, but not a decision-facing cumulative rate because never-activated sellers were excluded.

## Activation v3 (canonical)

- Population: activation-eligible closed sellers with valid won date and observation horizon.
- Denominator: observable sellers for each fixed window; never-activated sellers remain right-censored.
- Event definition: exact first sale after won date.
- Decision impact: canonical 7/30/60/90-day onboarding KPI; observed-activator median remains a separate metric.
