# Chart catalog

The release contains 61 registered chart entries and 66 rendered PNGs spanning the required decision-support domains. Five retained legacy summary PNGs are intentionally outside the active registry; `reports/chart_registry.csv` is the source of truth for active chart IDs, questions, denominators, methods, claim strength, Power BI candidacy and README candidacy.

| Folder | Domain | PNGs | Registry rows |
|---|---|---:|---:|
| 00_measurement_trust | measurement trust | 5 | 5 |
| 01_marketplace_health | marketplace health | 6 | 6 |
| 02_acquisition | acquisition | 6 | 24 |
| 03_activation | activation | 6 | 6 |
| 04_retention | retention | 6 | 6 |
| 05_seller_value_concentration | concentration | 6 | 15 |
| 06_category_geography | category + geography | 12 | 12 |
| 07_customer_experience | customer experience | 10 | 10 |
| 08_root_cause_cases | case mapping | 0 | 0 |
| 09_statistical_evidence | statistical evidence | 0 | 0 |
| 10_decision_layer | decision layer | 4 | 8 |

The two zero-PNG folders are intentionally represented by the root-cause and statistical tables/registers; the same evidence is visualized in the domain folders and decision layer. This avoids duplicating identical images while preserving traceability.

README candidates are the strongest measurement, acquisition, activation, retention, concentration, customer-experience and decision views. Power BI candidates are restricted to decision-support charts marked `powerbi_candidate=yes`.

