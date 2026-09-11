from __future__ import annotations

import json
import math
import os
import zipfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from scipy.stats import chi2_contingency, fisher_exact, mannwhitneyu


ROOT = Path(os.environ.get("PROJECT_WORK_ROOT", Path(__file__).resolve().parent))
DOWNLOADS = Path(os.environ.get("OLIST_RAW_DIR", ROOT / "downloads"))
PROJECT = Path(os.environ.get("OLIST_PROJECT_DIR", ROOT / "project"))
TABLES = PROJECT / "reports" / "tables"
QA = PROJECT / "reports" / "qa"
CHARTS = PROJECT / "reports" / "charts"
DOCS = PROJECT / "docs"
SQL = PROJECT / "sql"
SRC = PROJECT / "src"
NOTEBOOKS = PROJECT / "notebooks"
for d in [TABLES, QA, CHARTS, DOCS, SQL, SRC, NOTEBOOKS, PROJECT / "config", PROJECT / "data", PROJECT / "powerbi", PROJECT / "tests", PROJECT / "assets"]:
    d.mkdir(parents=True, exist_ok=True)


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    return df


def load_zip(path: Path) -> dict[str, pd.DataFrame]:
    out = {}
    with zipfile.ZipFile(path) as z:
        for member in z.namelist():
            if member.lower().endswith(".csv"):
                out[Path(member).stem] = clean_columns(pd.read_csv(z.open(member), low_memory=False))
    return out


def parse_dates(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    df = df.copy()
    for c in columns:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    return df


def safe_pct(n, d):
    return float(n / d) if d else np.nan


def write_csv(df: pd.DataFrame, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def pct(x):
    return "n/a" if pd.isna(x) else f"{x:.1%}"


def money(x):
    return "n/a" if pd.isna(x) else f"R$ {x:,.0f}"


def compute() -> dict:
    ecom = load_zip(DOWNLOADS / "brazilian-ecommerce.zip")
    funnel = load_zip(DOWNLOADS / "marketing-funnel-olist.zip")
    customers = ecom["olist_customers_dataset"]
    geolocation = ecom["olist_geolocation_dataset"]
    items = ecom["olist_order_items_dataset"]
    orders = ecom["olist_orders_dataset"]
    payments = ecom["olist_order_payments_dataset"]
    reviews = ecom["olist_order_reviews_dataset"]
    products = ecom["olist_products_dataset"]
    sellers = ecom["olist_sellers_dataset"]
    translation = ecom["product_category_name_translation"]
    mql = funnel["marketing_qualified_leads_olist"]
    closed = funnel["closed_deals_olist"]

    orders = parse_dates(orders, [c for c in orders.columns if c.endswith("timestamp")])
    orders = parse_dates(orders, ["order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"])
    items = parse_dates(items, ["shipping_limit_date"])
    reviews = parse_dates(reviews, ["review_creation_date", "review_answer_timestamp"])
    mql = parse_dates(mql, ["first_contact_date"])
    closed = parse_dates(closed, ["won_date"])

    # Inventory and profiling
    key_map = {
        "olist_orders_dataset": "order_id",
        "olist_order_items_dataset": "order_id + order_item_id",
        "olist_order_payments_dataset": "order_id + payment_sequential",
        "olist_order_reviews_dataset": "review_id",
        "olist_customers_dataset": "customer_id",
        "olist_products_dataset": "product_id",
        "olist_sellers_dataset": "seller_id",
        "olist_geolocation_dataset": "zip_code_prefix + geolocation_lat + geolocation_lng",
        "product_category_name_translation": "product_category_name",
        "marketing_qualified_leads_olist": "mql_id",
        "closed_deals_olist": "mql_id",
    }
    inventory = []
    profiles = []
    all_tables = {**ecom, **funnel}
    for name, df in all_tables.items():
        key = key_map.get(name)
        duplicate_count = int(df.duplicated(subset=[c.strip() for c in key.split("+")]).sum()) if key and all(c.strip() in df.columns for c in key.split("+")) else int(df.duplicated().sum())
        dt_cols = [c for c in df.columns if "date" in c or "timestamp" in c]
        date_values = pd.Series(dtype="datetime64[ns]")
        for c in dt_cols:
            date_values = pd.concat([date_values, pd.to_datetime(df[c], errors="coerce")], ignore_index=True)
        inventory.append({
            "table_name": name, "row_count": len(df), "column_count": len(df.columns),
            "candidate_key": key, "duplicate_key_count": duplicate_count,
            "date_min": date_values.min() if not date_values.empty else pd.NaT,
            "date_max": date_values.max() if not date_values.empty else pd.NaT,
            "file_size_mb": np.nan,
        })
        for c in df.columns:
            s = df[c]
            profiles.append({
                "table_name": name, "column_name": c, "dtype": str(s.dtype),
                "row_count": len(s), "null_count": int(s.isna().sum()),
                "null_pct": safe_pct(int(s.isna().sum()), len(s)),
                "distinct_count": int(s.nunique(dropna=True)),
                "min_value": str(s.min()) if not s.dropna().empty and pd.api.types.is_numeric_dtype(s) else "",
                "max_value": str(s.max()) if not s.dropna().empty and pd.api.types.is_numeric_dtype(s) else "",
            })
    write_csv(pd.DataFrame(inventory), QA / "raw_inventory.csv")
    write_csv(pd.DataFrame(profiles), QA / "data_profile_summary.csv")

    # Normalize core facts.
    customers2 = customers[["customer_id", "customer_unique_id", "customer_city", "customer_state", "customer_zip_code_prefix"]].copy()
    orders2 = orders.merge(customers2, on="customer_id", how="left", validate="one_to_one")
    orders2["purchase_date"] = orders2["order_purchase_timestamp"].dt.date
    orders2["purchase_month"] = orders2["order_purchase_timestamp"].dt.to_period("M").astype(str)
    orders2["is_delivered"] = (orders2["order_status"] == "delivered").astype(int)
    orders2["is_canceled"] = orders2["order_status"].isin(["canceled", "unavailable"]).astype(int)
    orders2["delivery_days"] = (orders2["order_delivered_customer_date"] - orders2["order_purchase_timestamp"]).dt.total_seconds() / 86400
    orders2["delivery_delay_days"] = (orders2["order_delivered_customer_date"] - orders2["order_estimated_delivery_date"]).dt.total_seconds() / 86400
    orders2["is_late"] = ((orders2["is_delivered"] == 1) & (orders2["delivery_delay_days"] > 0)).astype(int)
    payment_agg = payments.groupby("order_id", as_index=False).agg(payment_value_total=("payment_value", "sum"), payment_count=("payment_sequential", "nunique"))
    review_agg = reviews.groupby("order_id", as_index=False).agg(review_score=("review_score", "mean"), review_count=("review_id", "nunique"))
    orders2 = orders2.merge(payment_agg, on="order_id", how="left").merge(review_agg, on="order_id", how="left")
    items2 = items.merge(orders2[["order_id", "purchase_month", "customer_unique_id", "order_status", "is_delivered", "is_late", "review_score", "customer_state"]], on="order_id", how="left", validate="many_to_one")
    items2["gmv_proxy"] = items2["price"]
    items2["customer_paid_item_value"] = items2["price"] + items2["freight_value"]
    items2 = items2.merge(products[[c for c in products.columns if c in ["product_id", "product_category_name"]]], on="product_id", how="left", validate="many_to_one")
    items2 = items2.merge(translation, on="product_category_name", how="left")
    items2["product_category_name_english"] = items2["product_category_name_english"].fillna(items2["product_category_name"]).fillna("unknown")

    # Fan-out audit: naive item x payment join vs grain-safe totals.
    safe_gmv = float(items2["gmv_proxy"].sum())
    fanout = items[["order_id", "order_item_id", "price"]].merge(payments[["order_id", "payment_sequential", "payment_value"]], on="order_id", how="inner")
    naive_gmv = float(fanout["price"].sum())
    fanout_audit = pd.DataFrame([{
        "raw_order_count": orders["order_id"].nunique(),
        "joined_row_count": len(fanout),
        "grain_safe_item_gmv": safe_gmv,
        "naive_joined_gmv": naive_gmv,
        "fanout_difference": naive_gmv - safe_gmv,
        "fanout_multiple": safe_pct(naive_gmv, safe_gmv),
    }])
    write_csv(fanout_audit, QA / "fanout_audit.csv")

    # Marketplace monthly mart.
    monthly = items2.groupby("purchase_month", as_index=False).agg(
        gmv_proxy=("gmv_proxy", "sum"), customer_paid_value=("customer_paid_item_value", "sum"),
        orders=("order_id", "nunique"), active_sellers=("seller_id", "nunique"),
        active_customers=("customer_unique_id", "nunique"), items=("order_item_id", "count"),
    )
    late = orders2.groupby("purchase_month", as_index=False).agg(delivered_orders=("is_delivered", "sum"), late_orders=("is_late", "sum"), avg_review_score=("review_score", "mean"))
    monthly = monthly.merge(late, on="purchase_month", how="left")
    monthly["aov"] = monthly["gmv_proxy"] / monthly["orders"].replace(0, np.nan)
    monthly["seller_productivity"] = monthly["gmv_proxy"] / monthly["active_sellers"].replace(0, np.nan)
    monthly["late_delivery_rate"] = monthly["late_orders"] / monthly["delivered_orders"].replace(0, np.nan)
    monthly["low_review_rate"] = orders2.groupby("purchase_month")["review_score"].apply(lambda x: (x <= 2).mean()).reindex(monthly["purchase_month"]).to_numpy()
    monthly = monthly.sort_values("purchase_month")
    for c in ["gmv_proxy", "orders", "aov", "active_sellers"]:
        monthly[f"{c}_mom_pct"] = monthly[c].pct_change()
    write_csv(monthly, TABLES / "mart_marketplace_monthly.csv")

    prev = monthly.shift(1)
    growth = monthly[["purchase_month", "gmv_proxy", "orders", "aov", "active_sellers", "seller_productivity"]].copy()
    growth["volume_effect"] = (growth["orders"] - prev["orders"]) * prev["aov"]
    growth["aov_effect"] = growth["orders"] * (growth["aov"] - prev["aov"])
    growth["seller_count_effect"] = (growth["active_sellers"] - prev["active_sellers"]) * prev["seller_productivity"]
    growth["productivity_effect"] = growth["active_sellers"] * (growth["seller_productivity"] - prev["seller_productivity"])
    write_csv(growth, TABLES / "growth_decomposition.csv")

    # Seller marts.
    seller_monthly = items2.groupby(["seller_id", "purchase_month"], as_index=False).agg(
        gmv_proxy=("gmv_proxy", "sum"), customer_paid_value=("customer_paid_item_value", "sum"),
        orders=("order_id", "nunique"), items=("order_item_id", "count"), products=("product_id", "nunique"),
        avg_review_score=("review_score", "mean"), late_orders=("is_late", "sum"),
    )
    seller_monthly["active_flag"] = 1
    firsts = seller_monthly.groupby("seller_id", as_index=False).agg(first_sale_month=("purchase_month", "min"), last_sale_month=("purchase_month", "max"))
    seller_lifetime = seller_monthly.groupby("seller_id", as_index=False).agg(
        total_gmv_proxy=("gmv_proxy", "sum"), total_orders=("orders", "sum"), total_items=("items", "sum"), active_months=("purchase_month", "nunique"),
        avg_review_score=("avg_review_score", "mean"),
    ).merge(firsts, on="seller_id", how="left")
    seller_lifetime["avg_order_value"] = seller_lifetime["total_gmv_proxy"] / seller_lifetime["total_orders"].replace(0, np.nan)
    seller_lifetime["seller_rank"] = seller_lifetime["total_gmv_proxy"].rank(method="first", ascending=False).astype(int)
    seller_lifetime["seller_share"] = seller_lifetime["total_gmv_proxy"] / seller_lifetime["total_gmv_proxy"].sum()
    seller_lifetime = seller_lifetime.sort_values("total_gmv_proxy", ascending=False).reset_index(drop=True)
    seller_lifetime["cumulative_gmv_share"] = seller_lifetime["seller_share"].cumsum()
    seller_lifetime["cumulative_seller_share"] = (np.arange(len(seller_lifetime)) + 1) / len(seller_lifetime)
    write_csv(seller_monthly, TABLES / "mart_seller_monthly.csv")
    write_csv(seller_lifetime, TABLES / "mart_seller_lifetime.csv")

    # Funnel and activation.
    mql_first = mql.sort_values("first_contact_date").drop_duplicates("mql_id", keep="first")
    funnel2 = mql_first.merge(closed, on="mql_id", how="left", indicator=True)
    funnel2["converted_flag"] = (funnel2["_merge"] == "both").astype(int)
    funnel2["origin_group"] = funnel2["origin"].fillna("unknown").replace({"": "unknown"})
    write_csv(funnel2.drop(columns=["_merge"]), TABLES / "mart_seller_funnel.csv")
    funnel_by_origin = funnel2.groupby("origin_group", dropna=False, as_index=False).agg(
        mqls=("mql_id", "nunique"), converted_sellers=("converted_flag", "sum"),
    )
    funnel_by_origin["conversion_rate"] = funnel_by_origin["converted_sellers"] / funnel_by_origin["mqls"].replace(0, np.nan)
    seller_lifetime2 = seller_lifetime[["seller_id", "first_sale_month", "total_gmv_proxy", "total_orders", "active_months"]].copy()
    funnel_by_origin = funnel_by_origin.merge(
        funnel2.loc[funnel2["converted_flag"] == 1, ["origin_group", "seller_id"]].merge(seller_lifetime2, on="seller_id", how="left").groupby("origin_group", as_index=False).agg(
            matched_sellers=("seller_id", "nunique"), downstream_gmv_proxy=("total_gmv_proxy", "sum"), downstream_orders=("total_orders", "sum"),
        ), on="origin_group", how="left"
    )
    funnel_by_origin["gmv_per_matched_seller"] = funnel_by_origin["downstream_gmv_proxy"] / funnel_by_origin["matched_sellers"].replace(0, np.nan)
    write_csv(funnel_by_origin, TABLES / "mart_acquisition_channel.csv")

    closed2 = funnel2.loc[funnel2["converted_flag"] == 1, ["mql_id", "seller_id", "origin_group", "won_date", "business_segment", "lead_type"]].merge(seller_lifetime2, on="seller_id", how="left")
    closed2["first_sale_date"] = pd.to_datetime(closed2["first_sale_month"] + "-01", errors="coerce")
    closed2["days_to_first_sale"] = (closed2["first_sale_date"] - closed2["won_date"].dt.normalize()).dt.days
    closed2["valid_activation_link"] = ((closed2["days_to_first_sale"] >= 0) & closed2["days_to_first_sale"].notna()).astype(int)
    closed2["activated_7d"] = ((closed2["valid_activation_link"] == 1) & (closed2["days_to_first_sale"] <= 7)).astype(int)
    closed2["activated_30d"] = ((closed2["valid_activation_link"] == 1) & (closed2["days_to_first_sale"] <= 30)).astype(int)
    closed2["activated_60d"] = ((closed2["valid_activation_link"] == 1) & (closed2["days_to_first_sale"] <= 60)).astype(int)
    closed2["activated_90d"] = ((closed2["valid_activation_link"] == 1) & (closed2["days_to_first_sale"] <= 90)).astype(int)
    write_csv(closed2, TABLES / "seller_activation.csv")
    activation_summary = pd.DataFrame([{
        "closed_sellers": len(closed2), "matched_to_sales": int(closed2["first_sale_month"].notna().sum()),
        "valid_activation_link": int(closed2["valid_activation_link"].sum()),
        "activation_rate_any_sale": safe_pct(int(closed2["valid_activation_link"].sum()), len(closed2)),
        "activation_within_7d": safe_pct(int(closed2["activated_7d"].sum()), int(closed2["valid_activation_link"].sum())),
        "activation_within_30d": safe_pct(int(closed2["activated_30d"].sum()), int(closed2["valid_activation_link"].sum())),
        "activation_within_60d": safe_pct(int(closed2["activated_60d"].sum()), int(closed2["valid_activation_link"].sum())),
        "activation_within_90d": safe_pct(int(closed2["activated_90d"].sum()), int(closed2["valid_activation_link"].sum())),
        "median_days_to_first_sale": float(closed2.loc[closed2["valid_activation_link"] == 1, "days_to_first_sale"].median()),
    }])
    write_csv(activation_summary, TABLES / "activation_summary.csv")

    # Seller cohorts and retention (observation eligibility is explicit).
    seller_monthly["cohort_month"] = seller_monthly.groupby("seller_id")["purchase_month"].transform("min")
    sdate = pd.to_datetime(seller_monthly["purchase_month"] + "-01")
    cdate = pd.to_datetime(seller_monthly["cohort_month"] + "-01")
    seller_monthly["age_month"] = (sdate.dt.year - cdate.dt.year) * 12 + (sdate.dt.month - cdate.dt.month)
    max_month = pd.to_datetime(seller_monthly["purchase_month"] + "-01").max()
    cohort_sizes = seller_monthly.groupby("cohort_month")["seller_id"].nunique().rename("cohort_sellers")
    retention_rows = []
    for cohort, g in seller_monthly.groupby("cohort_month"):
        cohort_date = pd.Timestamp(cohort + "-01")
        for age in range(0, 7):
            month = cohort_date + pd.DateOffset(months=age)
            eligible = int(max_month >= month)
            sellers_in_cohort = g["seller_id"].unique()
            retained = int(g.loc[g["age_month"] == age, "seller_id"].nunique()) if eligible else np.nan
            retention_rows.append({"cohort_month": cohort, "age_month": age, "eligible_flag": eligible, "cohort_sellers": int(len(sellers_in_cohort)), "retained_sellers": retained, "retention_rate": safe_pct(retained, len(sellers_in_cohort)) if eligible else np.nan})
    cohort = pd.DataFrame(retention_rows)
    write_csv(cohort, TABLES / "mart_seller_cohort.csv")

    # Category, geography, repeat customer, and experience marts.
    category = items2.groupby(["purchase_month", "product_category_name_english"], as_index=False).agg(
        gmv_proxy=("gmv_proxy", "sum"), orders=("order_id", "nunique"), active_sellers=("seller_id", "nunique"), avg_review_score=("review_score", "mean"),
    )
    category["gmv_share_month"] = category["gmv_proxy"] / category.groupby("purchase_month")["gmv_proxy"].transform("sum")
    write_csv(category, TABLES / "mart_category_performance.csv")
    seller_geo = items2.merge(sellers, on="seller_id", how="left", validate="many_to_one").groupby("seller_state", as_index=False).agg(gmv_proxy=("gmv_proxy", "sum"), orders=("order_id", "nunique"), active_sellers=("seller_id", "nunique"))
    seller_geo["gmv_share"] = seller_geo["gmv_proxy"] / seller_geo["gmv_proxy"].sum()
    write_csv(seller_geo.sort_values("gmv_proxy", ascending=False), TABLES / "mart_geography_performance.csv")
    cust_orders = orders2.groupby("customer_unique_id", as_index=False).agg(order_count=("order_id", "nunique"), first_order=("order_purchase_timestamp", "min"), last_order=("order_purchase_timestamp", "max"))
    repeat_summary = pd.DataFrame([{"unique_customers": len(cust_orders), "repeat_customers": int((cust_orders["order_count"] > 1).sum()), "repeat_customer_rate": safe_pct(int((cust_orders["order_count"] > 1).sum()), len(cust_orders)), "max_orders_per_customer": int(cust_orders["order_count"].max())}])
    write_csv(cust_orders, TABLES / "customer_order_frequency.csv")
    write_csv(repeat_summary, TABLES / "customer_repeat_summary.csv")
    experience = orders2.loc[orders2["is_delivered"] == 1].copy()
    experience["low_review_flag"] = (experience["review_score"] <= 2).astype(int)
    experience_summary = experience.groupby("is_late", dropna=False, as_index=False).agg(orders=("order_id", "nunique"), avg_review_score=("review_score", "mean"), low_review_rate=("low_review_flag", "mean"), avg_delay_days=("delivery_delay_days", "mean"))
    write_csv(experience_summary, TABLES / "mart_order_experience.csv")

    concentration = []
    total_gmv = seller_lifetime["total_gmv_proxy"].sum()
    for p in [0.01, 0.05, 0.10, 0.20]:
        n = max(1, math.ceil(len(seller_lifetime) * p))
        concentration.append({"top_seller_share": p, "top_seller_count": n, "gmv_proxy_share": seller_lifetime.head(n)["total_gmv_proxy"].sum() / total_gmv})
    concentration = pd.DataFrame(concentration)
    write_csv(concentration, TABLES / "seller_concentration.csv")

    # Statistical validation.
    stats_rows = []
    ct = pd.crosstab(funnel2["origin_group"], funnel2["converted_flag"])
    chi2, pval, dof, _ = chi2_contingency(ct) if ct.shape[0] > 1 and ct.shape[1] > 1 else (np.nan, np.nan, np.nan, None)
    stats_rows.append({"test": "lead_origin_vs_conversion", "statistic": chi2, "p_value": pval, "sample_size": len(funnel2), "interpretation": "association detected; not causal" if pval < 0.05 else "no statistically detectable association at alpha=0.05"})
    ct2 = pd.crosstab(experience["is_late"], experience["low_review_flag"])
    chi2, pval, dof, _ = chi2_contingency(ct2) if ct2.shape[0] > 1 and ct2.shape[1] > 1 else (np.nan, np.nan, np.nan, None)
    stats_rows.append({"test": "late_delivery_vs_low_review", "statistic": chi2, "p_value": pval, "sample_size": len(experience), "interpretation": "association detected; direction requires operational investigation" if pval < 0.05 else "no statistically detectable association at alpha=0.05"})
    valid_days = closed2.loc[closed2["valid_activation_link"] == 1, "days_to_first_sale"].dropna()
    stats_rows.append({"test": "activation_days_distribution", "statistic": valid_days.median() if not valid_days.empty else np.nan, "p_value": np.nan, "sample_size": len(valid_days), "interpretation": "median days to first sale; descriptive, not causal"})
    write_csv(pd.DataFrame(stats_rows), QA / "statistical_validation.csv")

    # Charts.
    plt.style.use("seaborn-v0_8-whitegrid")
    blue, gold, orange, charcoal = "#1f4e79", "#c69214", "#d95f02", "#263238"
    fig, ax1 = plt.subplots(figsize=(12, 5))
    ax1.plot(monthly["purchase_month"], monthly["gmv_proxy"], marker="o", color=blue, label="GMV proxy")
    ax1.set_ylabel("GMV proxy (R$)", color=blue); ax1.tick_params(axis="x", rotation=60)
    ax2 = ax1.twinx(); ax2.plot(monthly["purchase_month"], monthly["orders"], color=gold, marker="s", label="Orders"); ax2.set_ylabel("Orders", color=gold)
    fig.suptitle("Marketplace health: GMV proxy and orders by purchase month"); fig.tight_layout(); fig.savefig(CHARTS / "01_marketplace_health.png", dpi=180); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    funnel_plot = funnel_by_origin.sort_values("mqls", ascending=False).head(8)
    ax.barh(funnel_plot["origin_group"].astype(str), funnel_plot["mqls"], color=blue, label="MQLs")
    ax2 = ax.twiny(); ax2.plot(funnel_plot["conversion_rate"] * 100, funnel_plot["origin_group"].astype(str), "o", color=orange); ax2.set_xlabel("Conversion rate (%)")
    ax.set_xlabel("MQL count"); ax.set_title("Seller acquisition: volume vs conversion by origin"); fig.tight_layout(); fig.savefig(CHARTS / "02_acquisition_funnel.png", dpi=180); plt.close(fig)

    matrix = cohort.pivot(index="cohort_month", columns="age_month", values="retention_rate")
    fig, ax = plt.subplots(figsize=(9, 7)); im = ax.imshow(matrix, aspect="auto", cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(range(len(matrix.columns)), [f"M{x}" for x in matrix.columns]); ax.set_yticks(range(len(matrix.index)), matrix.index); ax.set_title("Seller retention cohort matrix (eligible cohorts only)")
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            v = matrix.iloc[i, j]
            if pd.notna(v): ax.text(j, i, f"{v:.0%}", ha="center", va="center", fontsize=8, color=charcoal)
    fig.colorbar(im, ax=ax, format=lambda x, pos: f"{x:.0%}"); fig.tight_layout(); fig.savefig(CHARTS / "03_retention_cohort.png", dpi=180); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5)); ax.plot(seller_lifetime["cumulative_seller_share"], seller_lifetime["cumulative_gmv_share"], color=blue); ax.plot([0, 1], [0, 1], "--", color="gray"); ax.set_xlabel("Cumulative share of sellers"); ax.set_ylabel("Cumulative share of GMV proxy"); ax.set_title("Seller concentration / Pareto curve"); fig.tight_layout(); fig.savefig(CHARTS / "04_seller_concentration.png", dpi=180); plt.close(fig)

    exp_plot = experience_summary.copy(); exp_plot["late_label"] = exp_plot["is_late"].map({0: "On time", 1: "Late"})
    fig, ax = plt.subplots(figsize=(7, 5)); ax.bar(exp_plot["late_label"], exp_plot["avg_review_score"], color=[gold, orange]); ax.set_ylim(0, 5); ax.set_ylabel("Average review score"); ax.set_title("Customer experience: review score by delivery timeliness"); fig.tight_layout(); fig.savefig(CHARTS / "05_late_delivery_reviews.png", dpi=180); plt.close(fig)

    # Executive PDF.
    first_month, last_month = monthly.iloc[0], monthly.iloc[-1]
    top_category = category.groupby("product_category_name_english", as_index=False)["gmv_proxy"].sum().sort_values("gmv_proxy", ascending=False).iloc[0]
    top_channel = funnel_by_origin.sort_values("conversion_rate", ascending=False).iloc[0]
    top20 = concentration.loc[concentration["top_seller_share"] == 0.2, "gmv_proxy_share"].iloc[0]
    with PdfPages(PROJECT / "reports" / "executive_summary.pdf") as pdf:
        fig = plt.figure(figsize=(11, 8.5)); fig.text(0.07, 0.92, "Marketplace Growth & Seller Intelligence", fontsize=20, weight="bold", color=blue); fig.text(0.07, 0.875, "Historical Olist case study | GMV is a proxy, not platform revenue", fontsize=11, color=charcoal)
        body = [
            f"Period: {monthly['purchase_month'].min()} to {monthly['purchase_month'].max()} | Orders: {int(monthly['orders'].sum()):,} | Sellers: {len(seller_lifetime):,}",
            f"GMV proxy: {money(monthly['gmv_proxy'].sum())}; latest month vs previous: {pct(monthly.iloc[-1]['gmv_proxy_mom_pct'])}.",
            f"Largest category by GMV proxy: {top_category['product_category_name_english']} ({money(top_category['gmv_proxy'])}).",
            f"Top 20% of sellers contributed {top20:.1%} of GMV proxy; concentration should be monitored.",
            f"Highest observed channel conversion: {top_channel['origin_group']} at {top_channel['conversion_rate']:.1%} on {int(top_channel['mqls']):,} MQLs.",
            "Recommendations are associative and historical; investigate operational mechanisms before claiming causality.",
        ]
        y = 0.78
        for line in body: fig.text(0.08, y, "• " + line, fontsize=12); y -= 0.06
        pdf.savefig(fig); plt.close(fig)
        for chart in ["01_marketplace_health.png", "02_acquisition_funnel.png", "03_retention_cohort.png", "04_seller_concentration.png", "05_late_delivery_reviews.png"]:
            img = plt.imread(CHARTS / chart); fig, ax = plt.subplots(figsize=(11, 8.5)); ax.imshow(img); ax.axis("off"); pdf.savefig(fig); plt.close(fig)

    # Data dictionary and quality reports.
    dup_orders = int(orders["order_id"].duplicated().sum())
    dup_sellers = int(sellers["seller_id"].duplicated().sum())
    negative_price = int((items["price"] < 0).sum())
    review_out = int((~reviews["review_score"].between(1, 5)).sum())
    negative_activation = int((closed2["days_to_first_sale"] < 0).sum())
    quality = f"""# Data quality report\n\n## Scope\nThe source is the anonymized Olist Brazilian E-Commerce Public Dataset plus the Olist Marketing Funnel dataset. The intended facts are order, order-item, seller, customer, review, payment, and lead grain.\n\n## Checks\n- Orders duplicate key rows: {dup_orders:,}.\n- Sellers duplicate key rows: {dup_sellers:,}.\n- Negative item prices: {negative_price:,}.\n- Review scores outside 1–5: {review_out:,}.\n- Closed deals linked to a seller with a negative first-sale lag: {negative_activation:,}; these are retained in QA but excluded from valid activation-window rates.\n- Naive order-item × payment join overstates GMV by {money(fanout_audit.iloc[0]['fanout_difference'])} ({fanout_audit.iloc[0]['fanout_multiple']:.1%} of grain-safe GMV).\n\n## Material risks\n1. **High — fan-out**: payments and order-items are both one-to-many; all marketplace KPIs use pre-aggregated/order-item grain-safe paths.\n2. **Medium — funnel linkage**: only 842 closed deals are available and seller-to-transaction linkage is incomplete.\n3. **Medium — retention censoring**: cohorts without enough observation time have null retention, not zero.\n4. **Medium — seller attribution**: multi-seller orders make delivery/review attribution risky; operations analysis stays at order level.\n\n## Remediation\nKeep the fan-out audit as a regression test, enforce key/foreign-key tests, preserve raw statuses, and reconcile SQL/BI outputs before release.\n"""
    (DOCS / "06_data_quality_report.md").write_text(quality, encoding="utf-8")

    metrics = f"""# Metric dictionary\n\n| Metric | Definition | Grain / caveat |\n|---|---|---|\n| GMV proxy | Sum of `order_item.price` | Order-item; not platform revenue or profit.\n| Customer-paid item value | `price + freight_value` | Order-item; freight shown separately from GMV proxy.\n| Orders | Distinct `order_id` | Never count rows after item joins.\n| Active sellers | Distinct sellers with at least one item in period | Seller-month.\n| AOV | GMV proxy / distinct orders | Period-level.\n| Activation | Closed seller with first sale on/after won date | Negative lags excluded from valid activation rates.\n| Retention | Seller active in cohort-age month / cohort sellers | Only eligible observation windows are reported.\n| Late delivery rate | Delivered orders with delivered date after estimated date / delivered orders | Order-level; no direct seller causality.\n| Low review rate | Reviews with score <= 2 / reviewed orders | Review score is an experience signal, not causal proof.\n\nKey outputs: total GMV proxy {money(monthly['gmv_proxy'].sum())}, {int(monthly['orders'].sum()):,} orders, {len(seller_lifetime):,} sellers, repeat-customer rate {repeat_summary.iloc[0]['repeat_customer_rate']:.1%}.\n"""
    (DOCS / "05_metric_dictionary.md").write_text(metrics, encoding="utf-8")
    (DOCS / "02_data_sources.md").write_text("""# Data sources\n\n- `brazilian-ecommerce.zip`: 9 CSVs from Olist's Brazilian E-Commerce Public Dataset.\n- `marketing-funnel-olist.zip`: MQL and closed-deal CSVs from Olist's Marketing Funnel dataset.\n- License/source note: Kaggle pages identify the datasets as Olist releases under CC BY-NC-SA 4.0.\n- Historical boundary: the project is a historical anonymized case study, not a description of current Brazilian e-commerce.\n\nSource files are stored in the project Drive folder under `01_raw_data`; raw data is not committed to GitHub.\n""", encoding="utf-8")
    (DOCS / "04_data_model.md").write_text("""# Data model\n\nCore grain-safe model:\n\n- `fct_order`: one row per order.\n- `fct_order_item`: one row per order-item.\n- `fct_payment`: one row per payment record.\n- `fct_seller_funnel`: one row per marketing-qualified lead.\n- `dim_customer`, `dim_seller`, `dim_product`, `dim_channel`, `dim_date`.\n- Marts: marketplace-month, seller-month, seller-lifetime, cohort, acquisition-channel, order-experience, category-performance.\n\nThe critical design decision is to aggregate payments and reviews before joining to order-grain facts and to calculate GMV from order-item grain.\n""", encoding="utf-8")
    (DOCS / "07_methodology.md").write_text("""# Methodology\n\n1. Read source CSVs directly from their ZIP files.\n2. Normalize column names and parse timestamps.\n3. Profile nulls, distinctness, candidate keys, domains, and date ranges.\n4. Demonstrate fan-out risk before calculating metrics.\n5. Build pandas/SQL-shaped marts at documented grain.\n6. Validate with chi-square association checks and descriptive distributions.\n7. Generate decision-facing charts with explicit units, denominators, and caveats.\n\nThe production target remains PostgreSQL + Power BI. This v1 execution used DuckDB/pandas-compatible transformations because PostgreSQL and Power BI were not available in the current desktop runtime; the repo contains the SQL and semantic-model specifications for the next runtime.\n""", encoding="utf-8")
    (DOCS / "08_analysis_log.md").write_text("""# Analysis log\n\n- Inventory: measured rows, columns, candidate keys, dates, and nulls.\n- Grain audit: quantified order-item × payment fan-out.\n- Marketplace health: monthly GMV proxy, orders, active sellers, AOV, and operating quality.\n- Acquisition: MQL volume, conversion, and downstream matched seller value by origin.\n- Activation: time-to-first-sale and 7/30/60/90-day windows.\n- Retention: cohort-age matrix with eligibility censoring.\n- Commercial: seller lifetime value proxy and concentration.\n- Operations: late delivery vs review association at order grain.\n- Statistical validation: association tests only; no causal claims.\n""", encoding="utf-8")
    (DOCS / "09_root_cause_cases.md").write_text(f"""# Root-cause investigation cases\n\n## Case 1 — Marketplace growth\n**Trigger:** monthly GMV proxy and order trend.\n**Evidence:** total GMV proxy is {money(monthly['gmv_proxy'].sum())}; latest monthly GMV proxy is {money(last_month['gmv_proxy'])}, with MoM change {pct(last_month['gmv_proxy_mom_pct'])}.\n**Hypotheses:** order volume, AOV, active seller count, or seller productivity.\n**Diagnostic:** use `growth_decomposition.csv`; do not infer causality from decomposition alone.\n\n## Case 2 — High-volume but low-value acquisition\n**Trigger:** acquisition origins with large MQL volume and lower downstream seller value.\n**Evidence:** compare `mart_acquisition_channel.csv` by MQL denominator, conversion, matched seller count, and GMV per matched seller.\n**Recommendation:** use a two-dimensional channel scorecard; avoid optimizing raw lead volume alone.\n\n## Case 3 — Customer experience\n**Trigger:** late-delivery rate and review score.\n**Evidence:** `mart_order_experience.csv` compares on-time and late delivered orders.\n**Recommendation:** prioritize categories/states with material order volume and weak service metrics; treat the relationship as associative.\n""", encoding="utf-8")
    recs = [
        "Use grain-safe monthly GMV proxy, orders, active sellers, and AOV as the operating scorecard; reconcile every refresh.",
        "Evaluate acquisition origins on conversion and downstream seller value together, with minimum-volume thresholds.",
        "Instrument onboarding around first-sale milestones and monitor 7/30/60/90-day activation by origin and segment.",
        "Monitor seller concentration and build a diversification plan when a small seller cohort dominates GMV proxy.",
        "Prioritize late-delivery investigations using order volume, delay severity, and review outcomes; do not assign causality to one seller in multi-seller orders.",
    ]
    (DOCS / "10_executive_decisions.md").write_text("# Executive decisions\n\n" + "\n".join(f"{i+1}. {x}" for i, x in enumerate(recs)) + "\n\nAll recommendations are historical and associative; confirm with current operating data before action.\n", encoding="utf-8")
    (DOCS / "11_limitations.md").write_text("""# Limitations\n\n- Historical anonymized dataset; no current-market claims.\n- GMV proxy only; platform revenue, margin, CAC, and ROAS are unavailable.\n- Olist marketing funnel is sampled; not every lead links to a marketplace seller.\n- Observational associations are not causal effects.\n- Multi-seller orders complicate seller-level delivery/review attribution.\n- Recent retention cohorts are censored; ineligible M6 cells are null.\n- Geography uses postcode/state approximations.\n""", encoding="utf-8")
    (DOCS / "12_interview_guide.md").write_text("""# Interview guide\n\n**Problem:** understand which seller acquisition sources create sustainable marketplace value.\n\n**Data challenge:** orders, items, payments, reviews, sellers, customers, and leads have different grains.\n\n**Solution:** build a reconciled star-schema-shaped model, explicit metrics, QA tests, and decision visuals.\n\n**Key learning:** grain control and metric definitions mattered more than adding machine learning.\n""", encoding="utf-8")
    (DOCS / "01_business_context.md").write_text("""# Business context\n\nManagement needs to understand marketplace growth across seller acquisition, activation, retention, commercial value, and customer experience. The decision is where to focus onboarding, channel quality, seller portfolio monitoring, and operational investigation.\n\nAudience: marketplace growth, seller operations, commercial, and BI stakeholders.\n""", encoding="utf-8")

    # SQL skeletons and reproducibility assets.
    sql_files = {
        "06_quality/q01_fanout_audit.sql": """-- Demonstrate why joining raw order_items and raw payments before aggregation is unsafe.\n-- Expected result: naive item price sum exceeds grain-safe item GMV.\nSELECT COUNT(*) AS joined_rows, SUM(oi.price) AS naive_joined_gmv\nFROM raw.order_items oi JOIN raw.order_payments p USING (order_id);\n""",
        "07_analysis/a01_monthly_marketplace_kpis.sql": """WITH item_month AS (\n    SELECT date_trunc('month', o.order_purchase_timestamp)::date AS purchase_month,\n           oi.order_id, oi.seller_id, oi.price AS gmv_proxy\n    FROM stg.orders o JOIN stg.order_items oi USING (order_id)\n)\nSELECT purchase_month, SUM(gmv_proxy) AS gmv_proxy, COUNT(DISTINCT order_id) AS orders,\n       COUNT(DISTINCT seller_id) AS active_sellers,\n       SUM(gmv_proxy) / NULLIF(COUNT(DISTINCT order_id),0) AS aov\nFROM item_month GROUP BY 1 ORDER BY 1;\n""",
        "07_analysis/b02_conversion_by_origin.sql": """SELECT origin_group, COUNT(DISTINCT mql_id) AS mqls,\n       COUNT(DISTINCT seller_id) FILTER (WHERE converted_flag=1) AS converted_sellers,\n       COUNT(DISTINCT seller_id) FILTER (WHERE converted_flag=1)::numeric / NULLIF(COUNT(DISTINCT mql_id),0) AS conversion_rate\nFROM mart.seller_funnel GROUP BY 1 ORDER BY mqls DESC;\n""",
        "07_analysis/d02_monthly_retention.sql": """SELECT cohort_month, age_month, cohort_sellers, retained_sellers, retention_rate\nFROM mart.seller_cohort\nWHERE eligible_flag=1 ORDER BY cohort_month, age_month;\n""",
        "07_analysis/f05_review_vs_delay.sql": """SELECT is_late, COUNT(DISTINCT order_id) AS orders, AVG(review_score) AS avg_review_score,\n       AVG((review_score <= 2)::int) AS low_review_rate\nFROM mart.order_experience GROUP BY 1 ORDER BY 1;\n""",
    }
    for rel, content in sql_files.items():
        p = SQL / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, encoding="utf-8")
    (SRC / "build_marts.py").write_text("""# Reproducible v1 build entrypoint.\n# The full reference implementation is in work/build_project.py during this run.\n# In the GitHub release, replace this wrapper with the packaged pipeline from the Drive code folder.\n\nfrom pathlib import Path\n\n\ndef main():\n    raise SystemExit('Run the documented pipeline with the Olist ZIP files from Drive.')\n\n\nif __name__ == '__main__':\n    main()\n""", encoding="utf-8")
    (PROJECT / "config" / "settings.yaml").write_text("""project_name: marketplace-growth-seller-intelligence\nraw_sources:\n  ecommerce_zip: brazilian-ecommerce.zip\n  funnel_zip: marketing-funnel-olist.zip\nmetric_policy:\n  gmv_proxy: order_item.price\n  active_seller: seller with at least one order-item in period\n  retention: seller active in eligible cohort-age month\n""", encoding="utf-8")
    (PROJECT / "requirements.txt").write_text("pandas\nnumpy\nmatplotlib\nscipy\nduckdb\nnbformat\npytest\n", encoding="utf-8")
    (PROJECT / "data" / "README.md").write_text("""# Data\n\nRaw ZIPs are stored in the project Drive folder because the user requested no raw data/output retention on local disk and GitHub is not the right place for large raw archives.\n\nSee `docs/02_data_sources.md` for provenance and `config/settings.yaml` for expected names.\n""", encoding="utf-8")
    (PROJECT / "powerbi" / "README.md").write_text("""# Power BI semantic model plan\n\nThe six-page Power BI design is defined in the plan and metric dictionary.\n\nRecommended pages: Executive Marketplace Health; Seller Acquisition Funnel; Seller Activation & Retention; Commercial Performance; Customer & Operations; Root Cause / Decisions.\n\nMeasures should bind to the CSV marts in `reports/tables` and reconcile to `mart_marketplace_monthly.csv`, `mart_seller_cohort.csv`, `seller_concentration.csv`, and `mart_order_experience.csv`. A `.pbix` binary is not generated in this runtime because Power BI Desktop is unavailable.\n""", encoding="utf-8")
    (PROJECT / "README.md").write_text(f"""# Marketplace Growth & Seller Intelligence\n\nHistorical Olist case study focused on seller acquisition → activation → retention → commercial value → customer experience.\n\n## v1 execution status\n\n- Raw ZIPs downloaded from the official Olist Kaggle dataset pages and stored in Drive.\n- Inventory, profiling, fan-out audit, marts, cohort retention, seller concentration, operations analysis, charts, executive PDF, and QA outputs generated.\n- SQL templates and Power BI semantic-model plan included.\n- PostgreSQL/Power BI execution is pending because those runtimes are not installed in the current desktop session.\n\n## Core evidence\n\n- GMV proxy: {money(monthly['gmv_proxy'].sum())}; orders: {int(monthly['orders'].sum()):,}; sellers: {len(seller_lifetime):,}.\n- Repeat customer rate: {repeat_summary.iloc[0]['repeat_customer_rate']:.1%}.\n- Top 20% seller GMV share: {top20:.1%}.\n- Activation within 90 days among valid closed-seller links: {activation_summary.iloc[0]['activation_within_90d']:.1%}.\n\n## Metric guardrails\n\nGMV is a proxy from order-item price, not platform revenue. The project preserves observation eligibility for retention and treats association as non-causal.\n\n## Remote storage\n\nRaw data and all chart/report/table artifacts are stored in the Drive folder `marketplace-growth-seller-intelligence`; code and documentation are mirrored in GitHub.\n""", encoding="utf-8")
    # Minimal notebook with reproducible instructions.
    nb = {"cells":[{"cell_type":"markdown","metadata":{},"source":["# Data profiling\n","\n","This notebook documents the v1 profiling path; execute the pipeline script with the two source ZIPs from Drive.\n"]},{"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":["from pathlib import Path\n","print('Use the Drive raw ZIPs and run the reproducible build script.')\n"]}],"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python"}},"nbformat":4,"nbformat_minor":5}
    (NOTEBOOKS / "01_data_profiling.ipynb").write_text(json.dumps(nb, indent=2), encoding="utf-8")
    # QA README and manifest.
    (QA / "README.md").write_text("""# QA outputs\n\n`raw_inventory.csv`, `data_profile_summary.csv`, `fanout_audit.csv`, and `statistical_validation.csv` are generated from the Olist ZIPs.\n""", encoding="utf-8")
    manifest = []
    for p in PROJECT.rglob("*"):
        if p.is_file(): manifest.append({"path": str(p.relative_to(PROJECT)).replace("\\", "/"), "bytes": p.stat().st_size})
    (PROJECT / "release_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"monthly": monthly, "seller_lifetime": seller_lifetime, "funnel": funnel_by_origin, "cohort": cohort, "concentration": concentration, "quality": fanout_audit, "project": PROJECT}


if __name__ == "__main__":
    result = compute()
    print(json.dumps({"project": str(result["project"]), "files": len(list(result["project"].rglob('*'))), "months": len(result["monthly"]), "sellers": len(result["seller_lifetime"])}, default=str))
