# Interview guide

## Three-minute story

**Problem:** Marketplace leadership needed to understand which seller acquisition sources created sustainable commercial value, where sellers failed to activate, and whether growth was concentrated or durable.

**Data:** I combined the Olist Brazilian E-Commerce Public Dataset with the Olist Marketing Funnel dataset, covering orders, items, payments, reviews, customers, sellers, products and leads.

**Challenge:** The hardest issue was grain mismatch. Items and payments are both one-to-many under an order, so a naive join inflates GMV. Seller attribution is also limited in multi-seller orders, and recent seller cohorts are right-censored.

**Solution:** I created a PostgreSQL-compatible raw/staging/dimension/fact/mart design, a Python ZIP-backed pipeline, explicit metric definitions, fan-out and reconciliation tests, and six executable analysis notebooks. I calculated GMV proxy from order-item price, counted orders distinctly, used customer_unique_id for repeat behavior, and kept retention eligibility visible.

**Analysis:** I evaluated marketplace health, lead conversion, time-to-first-sale, cohort retention, seller concentration, category/geography performance, repeat customers and delivery/review association.

**Output:** The non-Power-BI package includes decision marts, charts, executive summary, root-cause cases, five operating recommendations, diagrams, QA artifacts and a final-stage dashboard specification. Power BI is intentionally the last implementation stage.

**Key learning:** Metric definitions and grain control mattered more than adding a predictive model.

## Questions to rehearse

1. Why is GMV called a proxy?
2. How did you prove the payment/order-item fan-out?
3. Why count orders with distinct order_id?
4. Why use customer_unique_id rather than customer_id?
5. How did you define an active seller?
6. What is the activation denominator?
7. Why are recent retention cells blank rather than zero?
8. What does 87.5% activation within 90 days actually mean?
9. Why can conversion rate alone mislead channel decisions?
10. How did you handle unmatched funnel sellers?
11. Why is seller attribution risky for multi-seller orders?
12. What does the late-delivery/review result prove?
13. Which alternative explanations did you consider?
14. What are the top five operating decisions?
15. Which KPI would you monitor weekly?
16. What would you validate before acting on the historical findings?
17. How would you productionize the raw ZIP ingestion?
18. How would you reconcile Power BI to SQL?
19. What additional data is needed for CAC or ROAS?
20. What would make the analysis causal rather than associative?

