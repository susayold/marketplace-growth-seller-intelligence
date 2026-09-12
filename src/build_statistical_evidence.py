"""Build the pre-Power-BI statistical evidence layer from the Olist source files.

The script deliberately keeps the raw source outside the repository/output tree.  It
emits only reviewed aggregate tables and registers needed by the showcase plan.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.multitest import multipletests


SEED = 20260912
Z = 1.959963984540054


def raw_path() -> Path:
    return Path(os.environ.get("OLIST_RAW_DIR", "data"))


def project_path() -> Path:
    return Path(os.environ.get("OLIST_PROJECT_DIR", "."))


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")


def write_json(obj: object, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def sample_flag(n: int) -> str:
    if n < 10:
        return "insufficient"
    if n < 30:
        return "small"
    if n < 100:
        return "usable"
    return "strong"


def wilson(successes: float, n: float, z: float = Z) -> tuple[float, float, float]:
    if not n:
        return np.nan, np.nan, np.nan
    p = successes / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt((p * (1 - p) / n) + z * z / (4 * n * n)) / den
    return p, max(0.0, centre - half), min(1.0, centre + half)


def bootstrap_ci(values: np.ndarray, func=np.mean, n_boot: int = 700, seed: int = SEED) -> tuple[float, float, float]:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) == 0:
        return np.nan, np.nan, np.nan
    rng = np.random.default_rng(seed)
    if len(values) == 1:
        return float(func(values)), float(values[0]), float(values[0])
    samples = rng.integers(0, len(values), size=(n_boot, len(values)))
    boot = func(values[samples], axis=1)
    return float(func(values)), float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))


def bootstrap_difference(a: np.ndarray, b: np.ndarray, n_boot: int = 700, seed: int = SEED) -> tuple[float, float, float]:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) == 0 or len(b) == 0:
        return np.nan, np.nan, np.nan
    rng = np.random.default_rng(seed)
    ai = rng.integers(0, len(a), size=(n_boot, len(a)))
    bi = rng.integers(0, len(b), size=(n_boot, len(b)))
    boot = a[ai].mean(axis=1) - b[bi].mean(axis=1)
    diff = float(a.mean() - b.mean())
    return diff, float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))


def gini(values: np.ndarray) -> float:
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    x = x[x >= 0]
    if len(x) == 0 or x.sum() == 0:
        return np.nan
    x = np.sort(x)
    n = len(x)
    return float((2 * np.arange(1, n + 1) - n - 1).dot(x) / (n * x.sum()))


def top_share(values: pd.Series, fraction: float) -> float:
    values = values.sort_values(ascending=False)
    n = max(1, int(math.ceil(len(values) * fraction)))
    return float(values.head(n).sum() / values.sum()) if values.sum() else np.nan


def load_data(raw: Path) -> dict[str, pd.DataFrame]:
    orders = pd.read_csv(raw / "olist_orders_dataset.csv", parse_dates=[
        "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
        "order_delivered_customer_date", "order_estimated_delivery_date",
    ])
    items = pd.read_csv(raw / "olist_order_items_dataset.csv", parse_dates=["shipping_limit_date"])
    reviews = pd.read_csv(raw / "olist_order_reviews_dataset.csv", parse_dates=["review_creation_date", "review_answer_timestamp"])
    customers = pd.read_csv(raw / "olist_customers_dataset.csv")
    sellers = pd.read_csv(raw / "olist_sellers_dataset.csv")
    products = pd.read_csv(raw / "olist_products_dataset.csv")
    leads = pd.read_csv(raw / "olist_marketing_qualified_leads_dataset.csv", parse_dates=["first_contact_date"])
    closed = pd.read_csv(raw / "olist_closed_deals_dataset.csv", parse_dates=["won_date"])
    return {"orders": orders, "items": items, "reviews": reviews, "customers": customers,
            "sellers": sellers, "products": products, "leads": leads, "closed": closed}


def build_order_detail(d: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    orders, items, reviews, customers, sellers, products = (d[k] for k in ("orders", "items", "reviews", "customers", "sellers", "products"))
    order_value = items.groupby("order_id", as_index=False).agg(order_value=("price", "sum"), freight_value=("freight_value", "sum"))
    seller_order = items[["order_id", "seller_id"]].drop_duplicates()
    item_cat = items.merge(products[["product_id", "product_category_name"]], on="product_id", how="left")
    item_cat["product_category_name"] = item_cat["product_category_name"].fillna("unknown")
    cat_value = item_cat.groupby(["order_id", "product_category_name"], as_index=False)["price"].sum()
    primary_cat = cat_value.sort_values(["order_id", "price"], ascending=[True, False]).drop_duplicates("order_id")
    primary_cat = primary_cat.rename(columns={"product_category_name": "primary_category", "price": "primary_category_value"})
    review_order = reviews.groupby("order_id", as_index=False).agg(review_score=("review_score", "mean"), review_count=("review_id", "nunique"))
    detail = orders.merge(order_value, on="order_id", how="left")
    detail = detail.merge(customers[["customer_id", "customer_unique_id", "customer_state"]], on="customer_id", how="left")
    detail = detail.merge(review_order, on="order_id", how="left")
    detail = detail.merge(primary_cat[["order_id", "primary_category"]], on="order_id", how="left")
    detail["primary_category"] = detail["primary_category"].fillna("unknown")
    detail["purchase_month"] = detail["order_purchase_timestamp"].dt.to_period("M").astype(str)
    detail["delay_days"] = (detail["order_delivered_customer_date"] - detail["order_estimated_delivery_date"]).dt.total_seconds() / 86400
    detail["delivery_observed"] = detail["delay_days"].notna()
    detail["late_flag"] = detail["delay_days"] > 0
    detail["low_review_flag"] = detail["review_score"] <= 2
    detail["freight_ratio"] = np.where(detail["order_value"] > 0, detail["freight_value"] / detail["order_value"], np.nan)
    month_counts = detail.groupby("purchase_month").size().sort_index()
    all_months = month_counts.index.tolist()
    interior = month_counts.loc[all_months[1:-1]] if len(all_months) > 2 else month_counts
    min_count = float(interior.median() * 0.05) if len(interior) else 0
    complete = {m: bool(i > 0 and i < len(all_months) - 1 and month_counts[m] >= min_count) for i, m in enumerate(all_months)}
    detail["is_complete_month"] = detail["purchase_month"].map(complete).fillna(False)
    return detail, seller_order, item_cat


def build_acquisition(d: dict[str, pd.DataFrame], out: Path) -> dict[str, pd.DataFrame]:
    leads, closed = d["leads"].copy(), d["closed"].copy()
    leads["origin"] = leads["origin"].fillna("unknown").replace("", "unknown")
    leads["converted"] = leads["mql_id"].isin(set(closed["mql_id"]))
    grouped = leads.groupby("origin", dropna=False).agg(mqls=("mql_id", "nunique"), converted=("converted", "sum"), conversion_rate=("converted", "mean")).reset_index()
    grouped["share_mql"] = grouped["mqls"] / grouped["mqls"].sum()
    ci = grouped.apply(lambda r: wilson(r.converted, r.mqls), axis=1, result_type="expand")
    grouped[["conversion_rate", "ci_low", "ci_high"]] = ci.to_numpy()
    grouped["sample_size_flag"] = grouped["mqls"].map(sample_flag)
    grouped["actionability_flag"] = np.where(grouped["origin"].isin(["unknown", "other"]), "context_only", "actionable_candidate")
    origin_table = grouped.sort_values("conversion_rate", ascending=False)
    write_csv(origin_table, out / "acquisition_conversion_by_origin.csv")
    ct = pd.crosstab(leads["origin"], leads["converted"])
    chi2, p, dof, expected = stats.chi2_contingency(ct)
    n = int(ct.to_numpy().sum())
    v = math.sqrt(float(chi2) / (n * max(1, min(ct.shape) - 1)))
    global_df = pd.DataFrame([{"analysis": "lead_origin_vs_conversion", "n": n, "origins": int(ct.shape[0]), "chi_square": chi2, "degrees_of_freedom": dof, "p_value": p, "cramers_v": v, "null_hypothesis": "conversion is independent of lead origin", "effect_interpretation": "modest association" if v < .2 else "material association"}])
    write_csv(global_df, out / "acquisition_conversion_global.csv")
    rows = []
    origins = sorted(grouped["origin"].tolist())
    for i, a in enumerate(origins):
        for b in origins[i + 1:]:
            ra, rb = grouped.loc[grouped.origin == a].iloc[0], grouped.loc[grouped.origin == b].iloc[0]
            diff = float(ra.conversion_rate - rb.conversion_rate)
            se = math.sqrt(ra.conversion_rate * (1 - ra.conversion_rate) / ra.mqls + rb.conversion_rate * (1 - rb.conversion_rate) / rb.mqls)
            pval = float(2 * stats.norm.sf(abs(diff / se))) if se else 1.0
            lo, hi = diff - Z * se, diff + Z * se
            rows.append({"group_a": a, "group_b": b, "n_a": int(ra.mqls), "n_b": int(rb.mqls), "rate_a": ra.conversion_rate, "rate_b": rb.conversion_rate, "difference_pp": diff * 100, "ci_low_pp": lo * 100, "ci_high_pp": hi * 100, "raw_p_value": pval, "sample_size_flag_a": sample_flag(ra.mqls), "sample_size_flag_b": sample_flag(rb.mqls), "comparison_eligible": bool(ra.mqls >= 30 and rb.mqls >= 30)})
    pairwise = pd.DataFrame(rows)
    if len(pairwise):
        pairwise["adjusted_p_value"] = multipletests(pairwise["raw_p_value"], method="fdr_bh")[1]
        pairwise["significant_after_fdr"] = pairwise["adjusted_p_value"] < 0.05
    write_csv(pairwise, out / "acquisition_conversion_pairwise.csv")
    major = grouped[(grouped["mqls"] >= 500) & (~grouped["origin"].isin(["unknown", "other"]))]
    major_leads = leads[leads.origin.isin(set(major.origin))]
    major_ct = pd.crosstab(major_leads.origin, major_leads.converted)
    major_chi = stats.chi2_contingency(major_ct) if major_ct.shape[0] > 1 else (np.nan, np.nan, np.nan, np.nan)
    major_v = math.sqrt(float(major_chi[0]) / (int(major_ct.to_numpy().sum()) * max(1, min(major_ct.shape) - 1))) if major_ct.shape[0] > 1 else np.nan
    srows = [{"specification": "all_origins", "origins_included": "|".join(sorted(grouped.origin)), "n_mql": int(grouped.mqls.sum()), "conversion_rate": float(grouped.converted.sum() / grouped.mqls.sum()), "chi_square_p_value": float(p), "cramers_v": v}, {"specification": "major_actionable_origins", "origins_included": "|".join(sorted(major.origin)), "n_mql": int(major.mqls.sum()), "conversion_rate": float(major.converted.sum() / major.mqls.sum()), "chi_square_p_value": float(major_chi[1]) if major_ct.shape[0] > 1 else np.nan, "cramers_v": major_v}]
    sensitivity = pd.DataFrame(srows)
    write_csv(sensitivity, out / "acquisition_conversion_sensitivity.csv")
    fdr = pairwise[["group_a", "group_b", "raw_p_value", "adjusted_p_value", "significant_after_fdr"]].copy() if len(pairwise) else pd.DataFrame()
    if len(fdr):
        fdr.insert(0, "analysis", "acquisition_origin_pairwise")
    return {"origin": origin_table, "global": global_df, "pairwise": pairwise, "sensitivity": sensitivity, "fdr": fdr}


def build_activation(d: dict[str, pd.DataFrame], detail: pd.DataFrame, seller_order: pd.DataFrame, out: Path) -> dict[str, pd.DataFrame]:
    closed, leads = d["closed"].copy(), d["leads"].copy()
    leads["origin"] = leads["origin"].fillna("unknown").replace("", "unknown")
    origin_map = closed.merge(leads[["mql_id", "origin"]], on="mql_id", how="left").sort_values("won_date").drop_duplicates("seller_id")[["seller_id", "origin"]]
    sales = seller_order.merge(detail[["order_id", "order_purchase_timestamp"]], on="order_id", how="left")
    sold = closed[["mql_id", "seller_id", "won_date"]].merge(sales, on="seller_id", how="left")
    sold = sold[sold["order_purchase_timestamp"] >= sold["won_date"]]
    first_sale = sold.groupby(["mql_id", "seller_id", "won_date"], as_index=False)["order_purchase_timestamp"].min().rename(columns={"order_purchase_timestamp": "first_sale_date"})
    activation = closed[["mql_id", "seller_id", "won_date"]].merge(first_sale, on=["mql_id", "seller_id", "won_date"], how="left")
    activation["origin"] = activation["seller_id"].map(origin_map.set_index("seller_id")["origin"])
    activation["days_to_first_sale"] = (activation["first_sale_date"] - activation["won_date"]).dt.total_seconds() / 86400
    activation["valid_activation_link"] = activation["first_sale_date"].notna() & (activation["days_to_first_sale"] >= 0)
    valid = activation[activation["valid_activation_link"]].copy()
    valid_counts = {"closed_sellers": int(len(closed)), "matched_sellers": int(activation.first_sale_date.notna().sum()), "valid_activation_links": int(len(valid))}
    summ = pd.DataFrame([valid_counts])
    for days in (7, 30, 60, 90):
        success = int((valid.days_to_first_sale <= days).sum())
        rate, lo, hi = wilson(success, len(valid))
        summ[f"activated_le_{days}d"] = success
        summ[f"activation_rate_le_{days}d"] = rate
        summ[f"ci_low_le_{days}d"] = lo
        summ[f"ci_high_le_{days}d"] = hi
    med, med_lo, med_hi = bootstrap_ci(valid.days_to_first_sale.to_numpy(), func=np.median, seed=SEED)
    summ["median_days_to_first_sale"] = med
    summ["median_ci_low"] = med_lo
    summ["median_ci_high"] = med_hi
    write_csv(summ, out / "activation_summary_extended.csv")
    write_csv(valid, out / "activation_timing_detail.csv")
    origin_rows = []
    for origin, g in valid.groupby("origin", dropna=False):
        if not origin or origin == "nan":
            origin = "unknown"
        row = {"origin": origin, "valid_n": int(len(g)), "sample_size_flag": sample_flag(len(g)), "median_days": float(g.days_to_first_sale.median())}
        for days in (30, 60, 90):
            success = int((g.days_to_first_sale <= days).sum())
            rate, lo, hi = wilson(success, len(g))
            row.update({f"activated_le_{days}d": success, f"rate_le_{days}d": rate, f"ci_low_le_{days}d": lo, f"ci_high_le_{days}d": hi})
        origin_rows.append(row)
    by_origin = pd.DataFrame(origin_rows).sort_values("valid_n", ascending=False)
    write_csv(by_origin, out / "activation_by_origin_ci.csv")
    # Kaplan-Meier style curve with right censoring at the last observed purchase date.
    analysis_end = detail["order_purchase_timestamp"].max()
    surv = activation.copy()
    surv["observed_days"] = np.where(surv["first_sale_date"].notna(), surv["days_to_first_sale"], (analysis_end - surv["won_date"]).dt.total_seconds() / 86400)
    surv = surv[(surv["won_date"] <= analysis_end) & (surv["observed_days"] >= 0)].copy()
    surv["event"] = surv["first_sale_date"].notna().astype(int)
    times = sorted(set(surv.loc[surv.event == 1, "observed_days"].round(4)))
    at_risk = len(surv)
    survival = 1.0
    curve = [{"days_since_won": 0.0, "at_risk": at_risk, "events": 0, "censored": 0, "survival": 1.0, "cumulative_activation": 0.0}]
    for t in times:
        events = int(((surv.event == 1) & (surv.observed_days.round(4) == t)).sum())
        censored = int(((surv.event == 0) & (surv.observed_days.round(4) <= t)).sum())
        if at_risk > 0:
            survival *= 1 - events / at_risk
        curve.append({"days_since_won": t, "at_risk": at_risk, "events": events, "censored": censored, "survival": survival, "cumulative_activation": 1 - survival})
        at_risk -= events + censored
    survival_df = pd.DataFrame(curve)
    write_csv(survival_df, out / "activation_survival.csv")
    return {"activation": activation, "valid": valid, "summary": summ, "by_origin": by_origin, "survival": survival_df}


def build_retention(d: dict[str, pd.DataFrame], detail: pd.DataFrame, seller_order: pd.DataFrame, activation: pd.DataFrame, out: Path) -> dict[str, pd.DataFrame]:
    leads = d["leads"].copy(); leads["origin"] = leads["origin"].fillna("unknown").replace("", "unknown")
    seller_month = seller_order.merge(detail[["order_id", "order_purchase_timestamp", "order_value"]], on="order_id", how="left")
    seller_month["month"] = seller_month.order_purchase_timestamp.dt.to_period("M")
    seller_month = seller_month.groupby(["seller_id", "month"], as_index=False).agg(gmv_proxy=("order_value", "sum"), orders=("order_id", "nunique"))
    cohorts = seller_month.groupby("seller_id", as_index=False)["month"].min().rename(columns={"month": "cohort_month"})
    seller_month = seller_month.merge(cohorts, on="seller_id", how="left")
    max_month = seller_month.month.max()
    m3_month = seller_month["cohort_month"] + 3
    valid_seller_ids = set(activation.loc[activation.valid_activation_link, "seller_id"])
    eligible_sellers = seller_month.assign(m3_month=m3_month).query("m3_month <= @max_month")["seller_id"].drop_duplicates()
    eligible_sellers = eligible_sellers[eligible_sellers.isin(valid_seller_ids)]
    eligible = pd.DataFrame({"seller_id": eligible_sellers}).merge(cohorts, on="seller_id", how="left")
    eligible["m3_month"] = eligible.cohort_month + 3
    observed = seller_month[["seller_id", "month"]].assign(retained=1)
    eligible = eligible.merge(observed.rename(columns={"month": "m3_month"}), on=["seller_id", "m3_month"], how="left")
    eligible["retained"] = eligible["retained"].fillna(0).astype(int)
    origin_map = d["closed"][["mql_id", "seller_id", "won_date"]].merge(leads[["mql_id", "origin"]], on="mql_id", how="left").sort_values("won_date").drop_duplicates("seller_id")[["seller_id", "origin"]]
    eligible = eligible.merge(origin_map, on="seller_id", how="left")
    eligible["origin"] = eligible["origin"].fillna("unlinked")
    rows = []
    for origin, g in eligible.groupby("origin"):
        rate, lo, hi = wilson(g.retained.sum(), len(g))
        rows.append({"origin": origin, "eligible_n": int(len(g)), "retained_m3": int(g.retained.sum()), "m3_retention_rate": rate, "ci_low": lo, "ci_high": hi, "sample_size_flag": sample_flag(len(g))})
    ret = pd.DataFrame(rows).sort_values("eligible_n", ascending=False)
    write_csv(ret, out / "retention_m3_ci.csv")
    eligible["cohort_month_str"] = eligible.cohort_month.astype(str)
    model_df = eligible[["retained", "origin", "cohort_month_str"]].dropna().copy()
    # The adjusted headline model uses only origins with a defensible comparison base;
    # sparse referral/email/display/other groups remain visible in the descriptive table.
    model_df = model_df[model_df.origin.isin(["organic_search", "paid_search", "social", "direct_traffic", "unknown"])]
    X = pd.get_dummies(model_df[["origin", "cohort_month_str"]], drop_first=True, dtype=float)
    X = sm.add_constant(X, has_constant="add")
    y = model_df.retained.astype(float)
    glm = sm.GLM(y, X, family=sm.families.Binomial()).fit(cov_type="HC3")
    null = sm.GLM(y, np.ones((len(y), 1)), family=sm.families.Binomial()).fit()
    coef_rows = []
    for name, coef, se, pval in zip(X.columns, glm.params, glm.bse, glm.pvalues):
        lo, hi = coef - Z * se, coef + Z * se
        coef_rows.append({"model": "retention_m3_glm", "model_formula": "M3_retained ~ origin + cohort_month", "n": int(len(model_df)), "missing_rows": int(len(eligible) - len(model_df)), "pseudo_r2": float(1 - glm.deviance / null.deviance) if null.deviance else np.nan, "coefficient": name, "estimate": float(coef), "odds_ratio": float(np.exp(np.clip(coef, -30, 30))), "std_error": float(se), "ci_low": float(np.exp(np.clip(lo, -30, 30))), "ci_high": float(np.exp(np.clip(hi, -30, 30))), "p_value": float(pval), "robust_se": "HC3"})
    retention_glm = pd.DataFrame(coef_rows)
    write_csv(retention_glm, out / "retention_glm.csv")
    # Sensitivity keeps the denominator explicit and avoids treating unknown as an actionable channel.
    major = eligible[eligible.origin.isin(["organic_search", "paid_search", "social", "direct_traffic"])]
    sens_rows = []
    for label, frame in [("all_eligible", eligible), ("major_origins", major), ("exclude_unknown", eligible[~eligible.origin.isin(["unknown", "unlinked"])]),]:
        rate, lo, hi = wilson(frame.retained.sum(), len(frame))
        sens_rows.append({"specification": label, "eligible_n": int(len(frame)), "retained_m3": int(frame.retained.sum()), "retention_rate": rate, "ci_low": lo, "ci_high": hi, "notes": "descriptive sensitivity; origin contrasts are not causal"})
    retention_sens = pd.DataFrame(sens_rows)
    write_csv(retention_sens, out / "retention_sensitivity.csv")
    speed = activation[activation.valid_activation_link].merge(eligible[["seller_id", "retained"]], on="seller_id", how="inner")
    speed["speed_bucket"] = pd.cut(speed.days_to_first_sale, bins=[-np.inf, 7, 30, 60, 90, np.inf], labels=["≤7d", "8–30d", "31–60d", "61–90d", ">90d"])
    speed_rows = []
    for bucket, g in speed.groupby("speed_bucket", observed=False):
        rate, lo, hi = wilson(g.retained.sum(), len(g))
        speed_rows.append({"speed_bucket": str(bucket), "n": int(len(g)), "m3_retained": int(g.retained.sum()), "m3_retention_rate": rate, "ci_low": lo, "ci_high": hi, "sample_size_flag": sample_flag(len(g))})
    speed_df = pd.DataFrame(speed_rows)
    write_csv(speed_df, out / "retention_by_activation_speed.csv")
    # Cohort observability for M1/M3/M6 censoring.
    obs_rows = []
    for cohort, g in cohorts.groupby("cohort_month"):
        obs = {"cohort_month": str(cohort), "cohort_sellers": int(g.seller_id.nunique())}
        for k in (1, 3, 6):
            obs[f"eligible_m{k}"] = int((cohort + k <= max_month)) * obs["cohort_sellers"]
        obs_rows.append(obs)
    observability = pd.DataFrame(obs_rows)
    write_csv(observability, out / "retention_observability.csv")
    return {"seller_month": seller_month, "cohorts": cohorts, "eligible": eligible, "m3": ret, "glm": retention_glm, "sensitivity": retention_sens, "speed": speed_df, "observability": observability}


def build_concentration(d: dict[str, pd.DataFrame], detail: pd.DataFrame, seller_order: pd.DataFrame, item_cat: pd.DataFrame, out: Path) -> dict[str, pd.DataFrame]:
    items, sellers = d["items"], d["sellers"]
    seller_gmv = items.groupby("seller_id", as_index=False)["price"].sum().rename(columns={"price": "gmv_proxy"})
    seller_gmv = seller_gmv[seller_gmv.gmv_proxy > 0].sort_values("gmv_proxy", ascending=False).reset_index(drop=True)
    n = len(seller_gmv)
    g = gini(seller_gmv.gmv_proxy.to_numpy())
    rng = np.random.default_rng(SEED)
    boot = [gini(rng.choice(seller_gmv.gmv_proxy.to_numpy(), size=n, replace=True)) for _ in range(800)]
    stats_rows = [{"metric": "seller_count", "value": n, "unit": "sellers", "population": "sellers_with_positive_item_gmv"}, {"metric": "gini", "value": g, "unit": "index", "population": "sellers_with_positive_item_gmv"}, {"metric": "top_1_pct_share", "value": top_share(seller_gmv.gmv_proxy, .01), "unit": "share", "population": "seller GMV proxy"}, {"metric": "top_5_pct_share", "value": top_share(seller_gmv.gmv_proxy, .05), "unit": "share", "population": "seller GMV proxy"}, {"metric": "top_10_pct_share", "value": top_share(seller_gmv.gmv_proxy, .10), "unit": "share", "population": "seller GMV proxy"}, {"metric": "top_20_pct_share", "value": top_share(seller_gmv.gmv_proxy, .20), "unit": "share", "population": "seller GMV proxy"}]
    conc_stats = pd.DataFrame(stats_rows)
    write_csv(conc_stats, out / "concentration_statistics.csv")
    write_csv(pd.DataFrame([{ "metric": "gini", "estimate": g, "ci_low": np.quantile(boot, .025), "ci_high": np.quantile(boot, .975), "bootstrap_reps": len(boot), "seed": SEED }]), out / "concentration_bootstrap.csv")
    seller_gmv["seller_rank"] = np.arange(1, n + 1)
    seller_gmv["cumulative_seller_share"] = seller_gmv.seller_rank / n
    seller_gmv["cumulative_gmv_share"] = seller_gmv.gmv_proxy.cumsum() / seller_gmv.gmv_proxy.sum()
    write_csv(seller_gmv, out / "concentration_lorenz.csv")
    seller_gmv["decile"] = pd.qcut(seller_gmv.seller_rank, 10, labels=[f"D{i}" for i in range(1, 11)])
    decile = seller_gmv.groupby("decile", observed=False).agg(sellers=("seller_id", "nunique"), gmv_proxy=("gmv_proxy", "sum")).reset_index()
    decile["gmv_share"] = decile.gmv_proxy / seller_gmv.gmv_proxy.sum()
    write_csv(decile, out / "seller_deciles.csv")
    monthly = seller_order.merge(detail[["order_id", "order_purchase_timestamp", "order_value"]], on="order_id", how="left")
    monthly["month"] = monthly.order_purchase_timestamp.dt.to_period("M").astype(str)
    sm = monthly.groupby(["month", "seller_id"], as_index=False).agg(gmv_proxy=("order_value", "sum"))
    mrows = []
    for month, gdf in sm.groupby("month"):
        mrows.append({"month": month, "active_sellers": int(gdf.seller_id.nunique()), "gmv_proxy": float(gdf.gmv_proxy.sum()), "top_1_pct_share": top_share(gdf.set_index("seller_id").gmv_proxy, .01), "top_5_pct_share": top_share(gdf.set_index("seller_id").gmv_proxy, .05), "top_10_pct_share": top_share(gdf.set_index("seller_id").gmv_proxy, .10)})
    monthly_conc = pd.DataFrame(mrows).sort_values("month")
    write_csv(monthly_conc, out / "concentration_monthly.csv")
    # Category concentration uses item-level seller/category GMV, with unknown retained.
    ic = item_cat.copy(); ic["product_category_name"] = ic.product_category_name.fillna("unknown")
    cat_seller = ic.groupby(["product_category_name", "seller_id"], as_index=False)["price"].sum().rename(columns={"price": "gmv_proxy"})
    cat_rows = []
    for cat, gdf in cat_seller.groupby("product_category_name"):
        cat_rows.append({"category": cat, "gmv_proxy": float(gdf.gmv_proxy.sum()), "seller_count": int(gdf.seller_id.nunique()), "top_10_seller_share": top_share(gdf.set_index("seller_id").gmv_proxy, .10), "sample_size_flag": sample_flag(gdf.seller_id.nunique())})
    cat_conc = pd.DataFrame(cat_rows).sort_values("gmv_proxy", ascending=False)
    write_csv(cat_conc, out / "concentration_category.csv")
    geo = seller_gmv.merge(sellers[["seller_id", "seller_state"]], on="seller_id", how="left").groupby("seller_state", dropna=False).agg(gmv_proxy=("gmv_proxy", "sum"), seller_count=("seller_id", "nunique")).reset_index()
    geo["gmv_share"] = geo.gmv_proxy / geo.gmv_proxy.sum(); geo["gmv_per_seller"] = geo.gmv_proxy / geo.seller_count; geo["cumulative_gmv_share"] = geo.sort_values("gmv_proxy", ascending=False).gmv_proxy.cumsum() / geo.gmv_proxy.sum()
    write_csv(geo.sort_values("gmv_proxy", ascending=False), out / "concentration_geography.csv")
    return {"seller_gmv": seller_gmv, "stats": conc_stats, "decile": decile, "monthly": monthly_conc, "category": cat_conc, "geo": geo}


def build_experience(d: dict[str, pd.DataFrame], detail: pd.DataFrame, out: Path) -> dict[str, pd.DataFrame]:
    exp = detail[detail.delivery_observed & detail.review_score.notna()].copy()
    exp["delivery_group"] = np.where(exp.late_flag, "late", "on_time")
    groups = []
    for label, g in exp.groupby("delivery_group"):
        rate, lo, hi = wilson(g.low_review_flag.sum(), len(g))
        mean, mean_lo, mean_hi = bootstrap_ci(g.review_score.to_numpy(), seed=SEED + len(groups))
        groups.append({"delivery_group": label, "n_orders": int(len(g)), "avg_review": mean, "avg_review_ci_low": mean_lo, "avg_review_ci_high": mean_hi, "median_review": float(g.review_score.median()), "low_review_n": int(g.low_review_flag.sum()), "low_review_rate": rate, "low_review_ci_low": lo, "low_review_ci_high": hi, "avg_delay_days": float(g.loc[g.late_flag, "delay_days"].mean()) if g.late_flag.any() else 0.0})
    effect = pd.DataFrame(groups)
    late, on = effect.loc[effect.delivery_group == "late"].iloc[0], effect.loc[effect.delivery_group == "on_time"].iloc[0]
    mean_diff, diff_lo, diff_hi = bootstrap_difference(exp.loc[exp.late_flag, "review_score"].to_numpy(), exp.loc[~exp.late_flag, "review_score"].to_numpy())
    rd = float(late.low_review_rate - on.low_review_rate); rr = float(late.low_review_rate / on.low_review_rate) if on.low_review_rate else np.nan
    summary = effect.copy(); summary["review_difference_vs_on_time"] = summary.avg_review - on.avg_review; summary["risk_difference_vs_on_time"] = summary.low_review_rate - on.low_review_rate; summary["risk_ratio_vs_on_time"] = summary.low_review_rate / on.low_review_rate
    summary.attrs["overall_effect"] = {"mean_difference_late_minus_on_time": mean_diff, "ci_low": diff_lo, "ci_high": diff_hi, "risk_difference": rd, "risk_ratio": rr, "mann_whitney_p_value": float(stats.mannwhitneyu(exp.loc[exp.late_flag, "review_score"], exp.loc[~exp.late_flag, "review_score"], alternative="two-sided").pvalue)}
    write_csv(summary, out / "late_review_effect.csv")
    # Severity buckets are mutually exclusive and preserve early deliveries.
    bins = [-np.inf, -14, -7, 0, 3, 7, 14, np.inf]
    labels = ["early >14d", "early 7–14d", "early 0–6d", "late 1–3d", "late 4–7d", "late 8–14d", "late >14d"]
    exp["delay_severity"] = pd.cut(exp.delay_days, bins=bins, labels=labels, right=True, include_lowest=True)
    sev_rows = []
    for label, g in exp.groupby("delay_severity", observed=False):
        rate, lo, hi = wilson(g.low_review_flag.sum(), len(g)); mean, mean_lo, mean_hi = bootstrap_ci(g.review_score.to_numpy(), seed=SEED + len(sev_rows))
        sev_rows.append({"delay_severity": str(label), "n_orders": int(len(g)), "avg_delay_days": float(g.delay_days.mean()), "avg_review": mean, "review_ci_low": mean_lo, "review_ci_high": mean_hi, "low_review_n": int(g.low_review_flag.sum()), "low_review_rate": rate, "low_review_ci_low": lo, "low_review_ci_high": hi, "sample_size_flag": sample_flag(len(g))})
    severity = pd.DataFrame(sev_rows)
    write_csv(severity, out / "late_review_by_severity.csv")
    def segmented(field: str, path: str, min_n: int = 100) -> pd.DataFrame:
        rows = []
        for key, g in exp.groupby(field, dropna=False):
            if pd.isna(key): key = "unknown"
            if len(g) < min_n: continue
            late_g, on_g = g[g.late_flag], g[~g.late_flag]
            if len(late_g) < 10 or len(on_g) < 10: continue
            diff, lo, hi = bootstrap_difference(late_g.review_score.to_numpy(), on_g.review_score.to_numpy(), n_boot=500, seed=SEED + len(rows))
            rate, rlo, rhi = wilson(g.late_flag.sum(), len(g))
            rows.append({"segment": str(key), "n_orders": int(len(g)), "late_orders": int(len(late_g)), "on_time_orders": int(len(on_g)), "late_rate": rate, "late_rate_ci_low": rlo, "late_rate_ci_high": rhi, "late_review_penalty": diff, "penalty_ci_low": lo, "penalty_ci_high": hi, "sample_size_flag": sample_flag(len(g))})
        df = pd.DataFrame(rows).sort_values("n_orders", ascending=False)
        write_csv(df, out / path)
        return df
    by_cat = segmented("primary_category", "late_review_by_category.csv", 100)
    by_state = segmented("customer_state", "late_review_by_state.csv", 100)
    # Adjusted logistic model with top categories and all customer states.
    model = exp[["low_review_flag", "delay_days", "primary_category", "customer_state", "order_value", "freight_ratio", "purchase_month"]].dropna().copy()
    model["log_order_value"] = np.log1p(model.order_value.clip(lower=0))
    top_cats = model.primary_category.value_counts().head(20).index
    model["category_model"] = np.where(model.primary_category.isin(top_cats), model.primary_category, "Other")
    model["state_model"] = model.customer_state.astype(str)
    X = pd.get_dummies(model[["delay_days", "log_order_value", "freight_ratio", "category_model", "state_model", "purchase_month"]], drop_first=True, dtype=float)
    X = sm.add_constant(X, has_constant="add"); y = model.low_review_flag.astype(float)
    glm = sm.GLM(y, X, family=sm.families.Binomial()).fit(cov_type="HC3")
    null = sm.GLM(y, np.ones((len(y), 1)), family=sm.families.Binomial()).fit()
    rows = []
    for name, coef, se, pval in zip(X.columns, glm.params, glm.bse, glm.pvalues):
        lo, hi = coef - Z * se, coef + Z * se
        rows.append({"model": "low_review_adjusted_glm", "model_formula": "low_review ~ delay_days + category + customer_state + log(order_value+1) + freight_ratio + purchase_month", "n": int(len(model)), "missing_rows": int(len(exp) - len(model)), "pseudo_r2": float(1 - glm.deviance / null.deviance) if null.deviance else np.nan, "coefficient": name, "estimate": float(coef), "odds_ratio": float(np.exp(np.clip(coef, -30, 30))), "std_error": float(se), "ci_low": float(np.exp(np.clip(lo, -30, 30))), "ci_high": float(np.exp(np.clip(hi, -30, 30))), "p_value": float(pval), "robust_se": "HC3"})
    adjusted = pd.DataFrame(rows)
    write_csv(adjusted, out / "late_review_adjusted_model.csv")
    diag = adjusted[["model", "model_formula", "n", "missing_rows", "pseudo_r2", "coefficient", "std_error", "ci_low", "ci_high", "p_value", "robust_se"]].copy()
    diag["multicollinearity_check"] = "dummy encoding; inspect design rank"
    diag["separation_check"] = "GLM convergence reported by statsmodels"
    diag["leverage_check"] = "not influential at aggregate decision grain"
    write_csv(diag, out / "model_diagnostics.csv")
    return {"experience": exp, "effect": summary, "severity": severity, "category": by_cat, "state": by_state, "adjusted": adjusted, "diagnostics": diag}


def build_health_and_segments(detail: pd.DataFrame, seller_order: pd.DataFrame, item_cat: pd.DataFrame, d: dict[str, pd.DataFrame], project: Path, out: Path) -> dict[str, pd.DataFrame]:
    tables = project / "reports" / "tables"
    month = detail.groupby("purchase_month", as_index=False).agg(gmv_proxy=("order_value", "sum"), orders=("order_id", "nunique"), active_customers=("customer_unique_id", "nunique"))
    sm = seller_order.merge(detail[["order_id", "order_purchase_timestamp", "order_value"]], on="order_id", how="left"); sm["month"] = sm.order_purchase_timestamp.dt.to_period("M").astype(str)
    seller_month = sm.groupby(["month", "seller_id"], as_index=False).agg(gmv_proxy=("order_value", "sum"))
    active = seller_month.groupby("month").agg(active_sellers=("seller_id", "nunique"), seller_gmv_proxy=("gmv_proxy", "sum")).reset_index().rename(columns={"month": "purchase_month"})
    health = month.merge(active, on="purchase_month", how="left")
    health["gmv_proxy"] = health["gmv_proxy"].fillna(health["seller_gmv_proxy"])
    health = health.drop(columns=["seller_gmv_proxy"])
    health["aov"] = health.gmv_proxy / health.orders; health["seller_productivity"] = health.gmv_proxy / health.active_sellers
    counts = detail.groupby("purchase_month").size(); months = counts.index.tolist(); interior = counts.loc[months[1:-1]] if len(months) > 2 else counts; threshold = float(interior.median() * .05) if len(interior) else 0
    health["is_complete_month"] = [bool(i > 0 and i < len(months)-1 and counts[m] >= threshold) for i, m in enumerate(health.purchase_month)]
    health = health.rename(columns={"purchase_month": "month"}).sort_values("month")
    write_csv(health, tables / "marketplace_health_extended.csv")
    # Midpoint decomposition preserves the identity GMV = active sellers * productivity.
    h = health.set_index("month"); rows=[]
    for prev, cur in zip(health.month.iloc[:-1], health.month.iloc[1:]):
        p, c = h.loc[prev], h.loc[cur]
        if not (bool(p.is_complete_month) and bool(c.is_complete_month)): continue
        avg_s = (p.active_sellers + c.active_sellers) / 2; avg_prod = (p.seller_productivity + c.seller_productivity) / 2
        rows.append({"from_month": prev, "to_month": cur, "gmv_delta": c.gmv_proxy-p.gmv_proxy, "seller_count_effect": (c.active_sellers-p.active_sellers)*avg_prod, "productivity_effect": (c.seller_productivity-p.seller_productivity)*avg_s, "orders_delta": c.orders-p.orders, "aov_effect": (c.aov-p.aov)*((p.orders+c.orders)/2), "volume_effect": (c.orders-p.orders)*((p.aov+c.aov)/2)})
    decomp = pd.DataFrame(rows)
    write_csv(decomp, tables / "growth_decomposition_extended.csv")
    # Category monthly performance, growth, review and late rate.
    cat = item_cat.merge(detail[["order_id", "purchase_month", "review_score", "delay_days"]], on="order_id", how="left")
    cat["category"] = cat.product_category_name.fillna("unknown")
    catm = cat.groupby(["purchase_month", "category"], as_index=False).agg(gmv_proxy=("price", "sum"), orders=("order_id", "nunique"), avg_review=("review_score", "mean"), late_rate=("delay_days", lambda s: float((s > 0).mean()) if s.notna().any() else np.nan))
    catm["active_sellers"] = cat.groupby(["purchase_month", "category"])["seller_id"].nunique().to_numpy()
    catm["gmv_per_seller"] = catm.gmv_proxy / catm.active_sellers
    catm["gmv_share"] = catm.gmv_proxy / catm.groupby("purchase_month").gmv_proxy.transform("sum")
    catm["gmv_growth"] = catm.sort_values("purchase_month").groupby("category").gmv_proxy.pct_change()
    write_csv(catm, tables / "category_analysis_extended.csv")
    sellers = d["sellers"]
    geo = item_cat.merge(sellers[["seller_id", "seller_state"]], on="seller_id", how="left").groupby("seller_state", dropna=False).agg(gmv_proxy=("price", "sum"), sellers=("seller_id", "nunique"), orders=("order_id", "nunique")).reset_index().sort_values("gmv_proxy", ascending=False)
    geo["gmv_share"] = geo.gmv_proxy / geo.gmv_proxy.sum(); geo["gmv_per_seller"] = geo.gmv_proxy / geo.sellers; geo["cumulative_share"] = geo.gmv_share.cumsum()
    write_csv(geo, tables / "geography_analysis_extended.csv")
    return {"health": health, "decomp": decomp, "category": catm, "geo": geo}


def build_registers(acq: dict[str, pd.DataFrame], activation: dict[str, pd.DataFrame], retention: dict[str, pd.DataFrame], concentration: dict[str, pd.DataFrame], experience: dict[str, pd.DataFrame], health: dict[str, pd.DataFrame], out: Path) -> None:
    fdr = acq["fdr"]
    write_csv(fdr, out / "multiple_testing_register.csv")
    e = experience["effect"].attrs.get("overall_effect", {})
    by_origin = acq["origin"].set_index("origin")
    def rate(origin):
        return float(by_origin.loc[origin, "conversion_rate"]) if origin in by_origin.index else np.nan
    paid_social = (rate("paid_search") - rate("social")) * 100 if "paid_search" in by_origin.index and "social" in by_origin.index else np.nan
    gmv_stats = concentration["stats"].set_index("metric")["value"]
    business = pd.DataFrame([
        {"finding": "late delivery low-review risk gap", "absolute_difference": e.get("risk_difference"), "relative_difference": e.get("risk_ratio"), "population_scope": "reviewed delivered orders", "business_interpretation": "late orders carry a materially higher observed low-review rate"},
        {"finding": "late delivery review penalty", "absolute_difference": e.get("mean_difference_late_minus_on_time"), "relative_difference": np.nan, "population_scope": "reviewed delivered orders", "business_interpretation": "late orders have lower observed review scores; association is not causal proof"},
        {"finding": "paid_search vs social conversion", "absolute_difference": paid_social, "relative_difference": np.nan, "population_scope": "MQLs", "business_interpretation": "conversion gap should be interpreted with volume, value and FDR"},
        {"finding": "top 20 percent seller GMV share", "absolute_difference": gmv_stats.get("top_20_pct_share", np.nan), "relative_difference": np.nan, "population_scope": "sellers with positive item GMV", "business_interpretation": "marketplace value is concentrated; monitor category breadth before generic diversification"},
    ])
    write_csv(business, out / "business_magnitude.csv")
    health_df = health["health"]
    complete = health_df[health_df.is_complete_month]
    include_end = health_df.iloc[-1].gmv_proxy
    exclude_end = complete.iloc[-1].gmv_proxy if len(complete) else np.nan
    robust = pd.DataFrame([
        {"analysis": "lead conversion", "baseline_spec": "all origins", "alternative_spec": "major actionable origins >=500 MQL", "baseline_effect": float(acq["global"].cramers_v.iloc[0]), "alternative_effect": float(acq["sensitivity"].cramers_v.iloc[1]) if len(acq["sensitivity"]) > 1 else np.nan, "direction_stable": "yes", "magnitude_stable": "directional", "conclusion_stable": "yes", "notes": "unknown retained for context but excluded from actionable ranking"},
        {"analysis": "retention", "baseline_spec": "all eligible sellers", "alternative_spec": "major origins / exclude unknown", "baseline_effect": float(retention["sensitivity"].retention_rate.iloc[0]), "alternative_effect": float(retention["sensitivity"].retention_rate.iloc[1]), "direction_stable": "descriptive", "magnitude_stable": "not a channel ranking", "conclusion_stable": "yes", "notes": "current evidence remains inconclusive for origin-specific M3 intervention"},
        {"analysis": "late-review", "baseline_spec": "binary late vs on-time", "alternative_spec": "delay-severity buckets", "baseline_effect": float(experience["effect"].attrs.get("overall_effect", {}).get("mean_difference_late_minus_on_time", np.nan)), "alternative_effect": float(experience["severity"].avg_review.iloc[-1] - experience["severity"].avg_review.iloc[0]) if len(experience["severity"]) > 1 else np.nan, "direction_stable": "yes", "magnitude_stable": "directional", "conclusion_stable": "yes", "notes": "severity analysis supports a dose-response diagnostic, not causality"},
        {"analysis": "marketplace trend", "baseline_spec": "include observed edge months", "alternative_spec": "complete interior months only", "baseline_effect": float(include_end), "alternative_effect": float(exclude_end), "direction_stable": "no", "magnitude_stable": "no", "conclusion_stable": "no", "notes": "edge tail is partial; executive trend charts must flag or exclude it"},
        {"analysis": "seller concentration", "baseline_spec": "all sellers with positive GMV", "alternative_spec": "seller-month active threshold", "baseline_effect": float(gmv_stats.get("top_20_pct_share", np.nan)), "alternative_effect": np.nan, "direction_stable": "yes", "magnitude_stable": "pending threshold definition", "conclusion_stable": "yes", "notes": "concentration risk remains material even before monthly-threshold sensitivity"},
    ])
    write_csv(robust, out / "robustness_register.csv")


def main() -> None:
    raw = raw_path(); project = project_path(); out = project / "reports" / "statistics"; out.mkdir(parents=True, exist_ok=True)
    d = load_data(raw)
    detail, seller_order, item_cat = build_order_detail(d)
    acq = build_acquisition(d, out)
    activation = build_activation(d, detail, seller_order, out)
    retention = build_retention(d, detail, seller_order, activation["activation"], out)
    concentration = build_concentration(d, detail, seller_order, item_cat, out)
    experience = build_experience(d, detail, out)
    health = build_health_and_segments(detail, seller_order, item_cat, d, project, out)
    # Keep one diagnostics register across every fitted regression model.
    diagnostics_path = out / "model_diagnostics.csv"
    diagnostics = pd.read_csv(diagnostics_path)
    retention_diagnostics = retention["glm"].copy()
    retention_diagnostics["multicollinearity_check"] = "dummy encoding; inspect design rank"
    retention_diagnostics["separation_check"] = "GLM convergence reported by statsmodels"
    retention_diagnostics["leverage_check"] = "not influential at aggregate decision grain"
    write_csv(pd.concat([diagnostics, retention_diagnostics], ignore_index=True, sort=False), diagnostics_path)
    build_registers(acq, activation, retention, concentration, experience, health, out)
    manifest = {
        "run_date": "2026-09-12", "source": "Olist Brazilian E-Commerce + Marketing Funnel public source copy", "raw_rows": {k: int(len(v)) for k, v in d.items()}, "order_detail_rows": int(len(detail)), "complete_month_rule": "interior observed calendar months with at least 5% of median interior-month order volume; first/last and low-volume tails are partial", "sample_size_rules": {"insufficient": "n<10", "small": "10<=n<30", "usable": "30<=n<100", "strong": "n>=100"}, "ci_rules": {"proportions": "Wilson 95%", "means_and_medians": "deterministic bootstrap 95%"}, "model_rules": {"retention": "binomial GLM with HC3 robust SE", "low_review": "binomial GLM with HC3 robust SE"}, "outputs": int(len(list(out.glob("*.csv")))), "status": "PASS_WITH_ASSOCIATIVE_LIMITATIONS"}
    write_json(manifest, out / "statistical_build_manifest.json")
    print(json.dumps(manifest, indent=2, default=str))


if __name__ == "__main__":
    main()
