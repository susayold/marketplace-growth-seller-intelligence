# Data dictionary

| Source/model | Grain | Key fields | Important measures / timestamps |
|---|---|---|---|
| orders | one row per order | `order_id`, `customer_id` | purchase/approval/delivery timestamps, status |
| order_items | one row per order-item | `order_id`, `order_item_id` | `seller_id`, `product_id`, `price`, `freight_value` |
| order_payments | one row per payment record | `order_id`, `payment_sequential` | payment type/value/installments |
| order_reviews | one row per review | `review_id`, `order_id` | score, creation/answer timestamps |
| customers | one row per order-customer mapping | `customer_id` | `customer_unique_id`, geography |
| sellers | one row per seller | `seller_id` | seller geography |
| products | one row per product | `product_id` | category and product attributes |
| marketing qualified leads | one row per MQL | `mql_id` | first contact date, origin |
| closed deals | one row per won lead | `mql_id`, `seller_id` | won date, segment, declared commercial fields |

`customer_id` identifies an order-level mapping; `customer_unique_id` is used for repeat-customer analysis. `price` is the GMV proxy; freight is preserved as a separate customer-paid value component.

