# Claims and evidence register

| Claim | Evidence | Strength | Allowed wording | Alternative explanation |
|---|---|---|---|---|
| Partial edge months can distort trend interpretation | `marketplace_health_extended.csv`, robustness register | LEVEL 0 | measurement risk is present; suppress edge claims | seasonality / source cutoff |
| Acquisition origins have different observed conversion | acquisition origin + pairwise FDR outputs | LEVEL 2 | observed conversion differs; test before scaling | mix, intent, lead quality |
| Activation speed aligns with M3 retention | `retention_by_activation_speed.csv` | LEVEL 2 | faster activation is associated with higher observed retention | reverse causality, readiness mix |
| Seller value is concentrated | Gini, Lorenz, top-share bootstrap outputs | LEVEL 1 | seller value is highly concentrated | proxy definition, assortment mix |
| Late delivery aligns with poor reviews | late-review effect + adjusted model | LEVEL 3 | lateness remains associated after observed controls | carrier, route, category confounding |
| Some categories need joint value/breadth/experience review | category and geography extended tables | LEVEL 1 | prioritize category investigation by size and risk | sparse category mix |

The register is deliberately conservative. It separates what the data shows from what a business action should test.

