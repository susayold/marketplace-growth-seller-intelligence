# Page 1 portfolio case-study content notes

This page intentionally presents the executive dashboard first, then explains the reasoning underneath it.

## Source-backed headline metrics
- GMV proxy: R$13.59M (sum of order-item price; not platform revenue)
- Orders: 98,666 distinct order IDs
- Active sellers: 3,095
- Late delivery rate: ~8.1%
- Top 20% seller share: ~82.7% of GMV proxy
- Late vs on-time review gap: ~-1.73 points (association only)
- Activation v3: 30D 15.8%, 60D 30.8%, 90D 42.1%
- Observed activator median time: 44.3 days

## Narrative rules
- Treat the dataset as historical and anonymized.
- GMV proxy is not platform revenue, margin, or profit.
- Do not claim causality from observational delivery/review evidence.
- Preserve activation eligibility and censoring logic.
- Preserve the executive reporting boundary and exclude partial edge periods from trend interpretation.

## Portfolio objective
The page should demonstrate the full chain:

raw data -> grain-safe mart -> governed metric -> evidence -> business decision -> limitation
