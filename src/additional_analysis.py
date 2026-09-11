from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZipFile
import os

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, mannwhitneyu


ROOT = Path(os.environ.get("OLIST_PROJECT_DIR", Path(__file__).resolve().parents[1]))
RAW = Path(os.environ.get("OLIST_RAW_DIR", ROOT / "data" / "raw"))
TABLES = ROOT / "reports" / "tables"
QA = ROOT / "reports" / "qa"
TABLES.mkdir(parents=True, exist_ok=True)
QA.mkdir(parents=True, exist_ok=True)


def read_zip(path: Path, filename: str) -> pd.DataFrame:
    with ZipFile(path) as zf:
        member = next(name for name in zf.namelist() if Path(name).name == filename)
        with zf.open(member) as fh:
            return pd.read_csv(fh)


def wilson(successes: int, total: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if total == 0:
        return (np.nan, np.nan)
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    margin = z * np.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return (centre - margin, centre + margin)


def months_between(start: pd.Series, end: pd.Series) -> pd.Series:
    return (end.dt.year - start.dt.year) * 12 + (end.dt.month - start.dt.month)


def main() -> None:
    orders = read_zip(RAW / "brazilian-ecommerce.zip", "olist_orders_dataset.csv")
    items = read_zip(RAW / "brazilian-ecommerce.zip", "olist_order_items_dataset.csv")
    reviews = read_zip(RAW / "brazilian-ecommerce.zip", "olist_order_reviews_dataset.csv")
    mql = read_zip(RAW / "marketing-funnel-olist.zip", "marketing_qualified_leads_olist.csv")
    deals = read_zip(RAW / "marketing-funnel-olist.zip", "closed_deals_olist.csv")

    orders["purchase_ts"] = pd.to_datetime(orders["order_purchase_timestamp"], errors="coerce")
    orders["delivered_ts"] = pd.to_datetime(orders["order_delivered_customer_date"], errors="coerce")
    orders["estimated_ts"] = pd.to_datetime(orders["order_estimated_delivery_date"], errors="coerce")
    items = items.merge(orders[["order_id", "purchase_ts"]], on="order_id", how="inner")
    items["purchase_month"] = items["purchase_ts"].dt.to_period("M").dt.to_timestamp()
    seller_monthly = items.groupby(["seller_id", "purchase_month"], as_index=False).agg(
        gmv_proxy=("price", "sum"), orders=("order_id", "nunique")
    )
    seller_first = items.groupby("seller_id", as_index=False).agg(
        first_sale_date=("purchase_ts", "min"),
        last_sale_date=("purchase_ts", "max"),
        total_gmv_proxy=("price", "sum"),
        total_orders=("order_id", "nunique"),
        active_months=("purchase_month", "nunique"),
    )
    seller_first["days_since_last_sale"] = (
        items["purchase_ts"].max() - seller_first["last_sale_date"]
    ).dt.days
    seller_first["days_since_first_sale"] = (
        seller_first["first_sale_date"] - items["purchase_ts"].min()
    ).dt.days
    seller_first["lifecycle_segment"] = np.select(
        [
            seller_first["days_since_last_sale"] > 90,
            seller_first["days_since_last_sale"] > 60,
            seller_first["days_since_first_sale"] <= 30,
            (seller_first["active_months"] >= 6) & (seller_first["total_orders"] >= 10),
            seller_first["active_months"] >= 3,
        ],
        ["dormant", "at_risk", "new", "established", "growing"],
        default="activated",
    )
    seller_first["value_tier"] = pd.cut(
        seller_first["total_gmv_proxy"].rank(method="first", pct=True),
        bins=[0, 0.2, 0.8, 1.0],
        labels=["long_tail", "core", "high_value"],
        include_lowest=True,
    ).astype(str)
    seller_first.to_csv(TABLES / "seller_segmentation.csv", index=False)

    mql["origin_group"] = mql["origin"].fillna("unknown").replace("", "unknown")
    deals = deals.merge(mql[["mql_id", "origin_group"]], on="mql_id", how="left")
    deals["won_date"] = pd.to_datetime(deals["won_date"], errors="coerce")
    activation = deals.merge(
        seller_first[["seller_id", "first_sale_date"]], on="seller_id", how="left"
    )
    activation["valid_activation_link"] = (
        activation["first_sale_date"].notna()
        & (activation["first_sale_date"] >= activation["won_date"])
    )
    activation = activation[activation["valid_activation_link"]].copy()
    activation["cohort_month"] = activation["first_sale_date"].dt.to_period("M").dt.to_timestamp()
    observed_end = items["purchase_month"].max()
    activity = seller_monthly.merge(
        activation[["seller_id", "origin_group", "cohort_month"]], on="seller_id", how="inner"
    )
    activity["age_month"] = months_between(activity["cohort_month"], activity["purchase_month"])
    retention = []
    for origin in sorted(activation["origin_group"].dropna().unique()):
        origin_cohort = activation.loc[
            activation["origin_group"].eq(origin) & activation["cohort_month"].notna()
        ].drop_duplicates("seller_id")
        for age in range(0, 7):
            eligible_mask = origin_cohort["cohort_month"].apply(
                lambda value: value + pd.DateOffset(months=age) <= observed_end
            )
            eligible_sellers = set(origin_cohort.loc[eligible_mask, "seller_id"])
            group = activity.loc[
                activity["origin_group"].eq(origin)
                & activity["age_month"].eq(age)
                & activity["seller_id"].isin(eligible_sellers)
            ]
            cohort_sellers = len(eligible_sellers)
            retained = group["seller_id"].nunique()
            eligible = int(cohort_sellers > 0)
            retention.append({
                "origin_group": origin,
                "age_month": age,
                "eligible_flag": eligible,
                "cohort_sellers": cohort_sellers,
                "retained_sellers": int(retained),
                "retention_rate": float(retained / cohort_sellers) if eligible else np.nan,
            })
    retention_df = pd.DataFrame(retention).sort_values(["origin_group", "age_month"])
    retention_df.to_csv(TABLES / "retention_by_origin.csv", index=False)

    # Statistical validation: lead conversion, robust review comparison, and M3 retention.
    stats_rows = []
    mql_stats = mql.merge(deals[["mql_id", "seller_id"]], on="mql_id", how="left")
    mql_stats["converted_flag"] = mql_stats["seller_id"].notna().astype(int)
    table = pd.crosstab(mql_stats["origin_group"], mql_stats["converted_flag"])
    chi2, p_value, _, _ = chi2_contingency(table)
    n = int(table.to_numpy().sum())
    cramers_v = float(np.sqrt(chi2 / (n * min(table.shape[0] - 1, table.shape[1] - 1))))
    stats_rows.append({"test": "lead_origin_vs_conversion", "method": "chi_square", "statistic": chi2, "p_value": p_value, "sample_size": n, "effect_size": cramers_v, "metric": "conversion_rate", "ci_low": np.nan, "ci_high": np.nan, "interpretation": "association detected; Cramers V reported; not causal"})
    for origin, group in mql_stats.groupby("origin_group"):
        lo, hi = wilson(int(group["converted_flag"].sum()), len(group))
        stats_rows.append({"test": f"conversion_ci:{origin}", "method": "wilson_95pct", "statistic": np.nan, "p_value": np.nan, "sample_size": len(group), "effect_size": float(group["converted_flag"].mean()), "metric": "conversion_rate", "ci_low": lo, "ci_high": hi, "interpretation": "descriptive interval"})

    experience = orders.loc[orders["order_status"].eq("delivered"), ["order_id", "delivered_ts", "estimated_ts"]].copy()
    experience["is_late"] = (experience["delivered_ts"] > experience["estimated_ts"]).astype(int)
    experience = experience.merge(reviews[["order_id", "review_score"]], on="order_id", how="inner").dropna(subset=["review_score"])
    late = experience.loc[experience["is_late"].eq(1), "review_score"].to_numpy()
    ontime = experience.loc[experience["is_late"].eq(0), "review_score"].to_numpy()
    u_stat, u_p = mannwhitneyu(late, ontime, alternative="two-sided")
    rng = np.random.default_rng(42)
    draws = 1000
    sample_size = min(5000, len(late), len(ontime))
    diffs = np.array([
        late[rng.integers(0, len(late), sample_size)].mean()
        - ontime[rng.integers(0, len(ontime), sample_size)].mean()
        for _ in range(draws)
    ])
    stats_rows.append({"test": "late_delivery_vs_review_score", "method": "mann_whitney_plus_bootstrap_mean_difference", "statistic": u_stat, "p_value": u_p, "sample_size": len(experience), "effect_size": float(late.mean() - ontime.mean()), "metric": "mean_review_score_late_minus_ontime", "ci_low": float(np.quantile(diffs, 0.025)), "ci_high": float(np.quantile(diffs, 0.975)), "n_on_time": len(ontime), "n_late": len(late), "mean_on_time": float(ontime.mean()), "mean_late": float(late.mean()), "median_on_time": float(np.median(ontime)), "median_late": float(np.median(late)), "interpretation": "late orders have different review scores; association only"})

    m3 = retention_df.loc[retention_df["age_month"].eq(3) & retention_df["eligible_flag"].eq(1)].copy()
    m3["origin_for_test"] = np.where(m3["cohort_sellers"] >= 30, m3["origin_group"], "other_sparse")
    ct = pd.DataFrame({
        "retained": m3.groupby("origin_for_test")["retained_sellers"].sum(),
        "not_retained": m3.groupby("origin_for_test").apply(lambda x: x["cohort_sellers"].sum() - x["retained_sellers"].sum(), include_groups=False),
    }).fillna(0)
    if len(ct) >= 2:
        chi3, p3, _, _ = chi2_contingency(ct)
        n3 = int(ct.to_numpy().sum())
        v3 = float(np.sqrt(chi3 / (n3 * min(ct.shape[0] - 1, ct.shape[1] - 1))))
        stats_rows.append({"test": "retention_m3_by_origin", "method": "chi_square", "statistic": chi3, "p_value": p3, "sample_size": n3, "effect_size": v3, "metric": "m3_retention_rate", "ci_low": np.nan, "ci_high": np.nan, "interpretation": "channel differences are associative; only eligible M3 observations"})
        for origin, row in ct.iterrows():
            total = int(row["retained"] + row["not_retained"])
            lo, hi = wilson(int(row["retained"]), total)
            stats_rows.append({"test": f"retention_m3_ci:{origin}", "method": "wilson_95pct", "statistic": np.nan, "p_value": np.nan, "sample_size": total, "effect_size": float(row["retained"] / total) if total else np.nan, "metric": "m3_retention_rate", "ci_low": lo, "ci_high": hi, "interpretation": "eligible M3 descriptive interval"})

    pd.DataFrame(stats_rows).to_csv(QA / "statistical_validation.csv", index=False)
    pd.DataFrame(stats_rows).to_csv(QA / "statistical_validation_detail.csv", index=False)
    summary = {
        "retention_rows": len(retention_df),
        "segmentation_rows": len(seller_first),
        "statistical_rows": len(stats_rows),
        "m3_origins": int(len(m3)),
        "observed_end_month": str(observed_end.date()),
    }
    (QA / "additional_analysis_manifest.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()


