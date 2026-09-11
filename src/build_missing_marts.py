from pathlib import Path
import os
import pandas as pd


RAW = Path(os.environ.get("OLIST_RAW_DIR", "data/raw"))
OUT = Path(os.environ.get("OLIST_OUTPUT_DIR", "reports/tables"))
OUT.mkdir(parents=True, exist_ok=True)

orders = pd.read_csv(RAW / "olist_orders_dataset.csv", parse_dates=[
    "order_purchase_timestamp", "order_delivered_customer_date",
    "order_estimated_delivery_date"
])
items = pd.read_csv(RAW / "olist_order_items_dataset.csv", parse_dates=["shipping_limit_date"])
customers = pd.read_csv(RAW / "olist_customers_dataset.csv")
reviews = pd.read_csv(RAW / "olist_order_reviews_dataset.csv")
products = pd.read_csv(RAW / "olist_products_dataset.csv")

# The public repository copy is validated against the governed inventory before use.
expected = {
    "orders": 99441,
    "items": 112650,
    "customers": 99441,
    "reviews": 99224,
    "products": 32951,
}
actual = {"orders": len(orders), "items": len(items), "customers": len(customers),
          "reviews": len(reviews), "products": len(products)}
if actual != expected:
    raise RuntimeError(f"raw row-count mismatch: {actual}")

orders["purchase_date"] = orders["order_purchase_timestamp"].dt.normalize()
orders["month"] = orders["order_purchase_timestamp"].dt.to_period("M").astype(str)
orders["delivered_orders_flag"] = orders["order_delivered_customer_date"].notna().astype(int)
orders["late_flag"] = (
    orders["order_delivered_customer_date"].notna()
    & orders["order_estimated_delivery_date"].notna()
    & (orders["order_delivered_customer_date"] > orders["order_estimated_delivery_date"])
).astype(int)

review_order = reviews.groupby("order_id", as_index=False).agg(
    review_score=("review_score", "mean")
)
seller_count = items.groupby("order_id", as_index=False)["seller_id"].nunique()
seller_count = seller_count.rename(columns={"seller_id": "seller_count"})

base = (
    items.merge(orders[["order_id", "customer_id", "purchase_date", "month", "delivered_orders_flag", "late_flag"]],
                on="order_id", how="inner")
          .merge(customers[["customer_id", "customer_unique_id"]], on="customer_id", how="left")
          .merge(products[["product_id", "product_category_name"]], on="product_id", how="left")
)

# Daily marketplace mart: one row per purchase date, item-price GMV proxy.
daily = base.groupby("purchase_date", as_index=False).agg(
    gmv_proxy=("price", "sum"),
    orders=("order_id", "nunique"),
    items=("order_id", "size"),
    active_sellers=("seller_id", "nunique"),
    active_customers=("customer_unique_id", "nunique"),
)
order_daily = orders.groupby("purchase_date", as_index=False).agg(
    delivered_orders=("delivered_orders_flag", "sum"),
    late_orders=("late_flag", "sum"),
)
daily = daily.merge(order_daily, on="purchase_date", how="left")
daily["aov"] = daily["gmv_proxy"] / daily["orders"].where(daily["orders"].ne(0))
daily["late_delivery_rate"] = daily["late_orders"] / daily["delivered_orders"].where(daily["delivered_orders"].ne(0))

review_daily = (
    orders[["order_id", "purchase_date"]]
    .merge(review_order, on="order_id", how="left")
    .groupby("purchase_date", as_index=False)
    .agg(avg_review_score=("review_score", "mean"))
)
daily = daily.merge(review_daily, on="purchase_date", how="left")
daily = daily[["purchase_date", "gmv_proxy", "orders", "items", "active_sellers", "active_customers",
               "aov", "late_orders", "late_delivery_rate", "avg_review_score"]]
daily = daily.sort_values("purchase_date")
daily.to_csv(OUT / "mart_marketplace_daily.csv", index=False, date_format="%Y-%m-%d")

# Seller-month mart. Review scores are attributed only to single-seller orders.
order_seller_counts = seller_count
single_seller_reviews = (
    order_seller_counts[order_seller_counts["seller_count"].eq(1)]
    .merge(items[["order_id", "seller_id"]].drop_duplicates(), on="order_id", how="left")
    .merge(orders[["order_id", "month"]], on="order_id", how="left")
    .merge(review_order, on="order_id", how="left")
)
review_seller_month = single_seller_reviews.groupby(["seller_id", "month"], as_index=False).agg(
    avg_review_score_proxy=("review_score", "mean"),
    review_eligible_orders=("order_id", "nunique"),
)

seller_month = base.groupby(["seller_id", "month"], as_index=False).agg(
    orders=("order_id", "nunique"),
    items=("order_id", "size"),
    gmv_proxy=("price", "sum"),
    customer_count=("customer_unique_id", "nunique"),
    category_count=("product_category_name", lambda x: x.dropna().nunique()),
)
seller_month["aov"] = seller_month["gmv_proxy"] / seller_month["orders"].where(seller_month["orders"].ne(0))
seller_month["active_flag"] = 1
seller_month = seller_month.merge(review_seller_month, on=["seller_id", "month"], how="left")
seller_month = seller_month[["seller_id", "month", "orders", "items", "gmv_proxy", "aov", "active_flag",
                             "customer_count", "category_count", "avg_review_score_proxy", "review_eligible_orders"]]
seller_month = seller_month.sort_values(["seller_id", "month"])
seller_month.to_csv(OUT / "mart_seller_monthly.csv", index=False)

print({"raw_rows": actual, "daily_rows": len(daily), "seller_month_rows": len(seller_month),
       "daily_gmv_proxy": round(float(daily["gmv_proxy"].sum()), 2),
       "seller_month_gmv_proxy": round(float(seller_month["gmv_proxy"].sum()), 2)})

