# Data model

Core grain-safe model:

- `fct_order`: one row per order.
- `fct_order_item`: one row per order-item.
- `fct_payment`: one row per payment record.
- `fct_seller_funnel`: one row per marketing-qualified lead.
- `dim_customer`, `dim_seller`, `dim_product`, `dim_channel`, `dim_date`.
- Marts: marketplace-month, seller-month, seller-lifetime, cohort, acquisition-channel, order-experience, category-performance.

The critical design decision is to aggregate payments and reviews before joining to order-grain facts and to calculate GMV from order-item grain.
