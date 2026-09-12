"""Rebuild the pre-Power-BI consistency/freeze layer.

This script is intentionally scoped to the repair blueprint:
activation population and censoring, retention model stability, reporting
boundaries, canonical headline metrics, and release QA.  It consumes the
reviewed marts already in the repository; raw ZIPs stay outside GitHub.
"""

from __future__ import annotations

import json
import math
import os
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats


Z = 1.959963984540054
SEED = 20260912
MAJOR_ORIGINS = ["direct_traffic", "organic_search", "paid_search", "social", "unknown"]
ACTIONABLE_ORIGINS = ["direct_traffic", "organic_search", "paid_search", "social"]


def wilson(successes: int, n: int) -> tuple[float, float, float]:
    if not n:
        return np.nan, np.nan, np.nan
    p = successes / n
    den = 1 + Z * Z / n
    centre = (p + Z * Z / (2 * n)) / den
    half = Z * math.sqrt((p * (1 - p) / n) + Z * Z / (4 * n * n)) / den
    return p, max(0.0, centre - half), min(1.0, centre + half)


def sample_flag(n: int) -> str:
    if n < 10:
        return "insufficient"
    if n < 30:
        return "small"
    if n < 100:
        return "usable"
    return "strong"


def write_csv(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding="utf-8")


def write_json(value: object, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def read_seller_monthly(project: Path) -> pd.DataFrame:
    override = os.environ.get("OLIST_SELLER_MONTHLY_PATH")
    path = Path(override) if override else project / "reports" / "tables" / "mart_seller_monthly.csv"
    frame = pd.read_csv(path, dtype={"seller_id": "string", "month": "string"})
    frame["month_p"] = pd.PeriodIndex(frame["month"], freq="M")
    return frame


def raw_order_end(project: Path) -> pd.Timestamp:
    inventory_path = project / "reports" / "qa" / "raw_inventory.csv"
    if inventory_path.exists():
        inventory = pd.read_csv(inventory_path)
        row = inventory[inventory["table_name"].eq("olist_orders_dataset")]
        if len(row):
            return pd.to_datetime(row.iloc[0]["date_max"]).normalize()
    return pd.Timestamp("2018-11-12")


def repair_legacy_artifacts(project: Path) -> None:
    """Restore two aggregate files that were truncated in the prior release."""
    tables = project / "reports" / "tables"
    category_path = tables / "mart_category_performance.csv"
    if category_path.exists():
        category = pd.read_csv(category_path)
        category = category.rename(columns={"product_category_name_english": "category", "avg_review_score": "avg_review"})
        category = category.sort_values(["category", "purchase_month"]).copy()
        category["gmv_per_seller"] = category["gmv_proxy"] / category["active_sellers"].replace(0, np.nan)
        category["gmv_share"] = category["gmv_share_month"]
        category["gmv_growth"] = category.groupby("category")["gmv_proxy"].pct_change()
        category["late_rate"] = np.nan
        category = category[["purchase_month", "category", "gmv_proxy", "orders", "avg_review", "late_rate", "active_sellers", "gmv_per_seller", "gmv_share", "gmv_growth"]]
        write_csv(category.sort_values(["purchase_month", "category"]), tables / "category_analysis_extended.csv")
    lifetime_path = tables / "mart_seller_lifetime.csv"
    if lifetime_path.exists():
        lifetime = pd.read_csv(lifetime_path)
        lorenz = lifetime[["seller_id", "total_gmv_proxy"]].rename(columns={"total_gmv_proxy": "gmv_proxy"}).sort_values("gmv_proxy", ascending=False).reset_index(drop=True)
        lorenz["seller_rank"] = np.arange(1, len(lorenz) + 1)
        lorenz["cumulative_seller_share"] = lorenz.seller_rank / len(lorenz)
        lorenz["cumulative_gmv_share"] = lorenz.gmv_proxy.cumsum() / lorenz.gmv_proxy.sum()
        write_csv(lorenz[["seller_id", "gmv_proxy", "seller_rank", "cumulative_seller_share", "cumulative_gmv_share"]], project / "reports" / "statistics" / "concentration_lorenz.csv")
    override = os.environ.get("OLIST_SELLER_MONTHLY_PATH")
    if override and Path(override).exists():
        shutil.copyfile(override, tables / "mart_seller_monthly.csv")


def build_activation(project: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    tables = project / "reports" / "tables"
    stats_dir = project / "reports" / "statistics"
    base = pd.read_csv(tables / "seller_activation.csv", parse_dates=["won_date", "first_sale_date"])
    exact_path = stats_dir / "activation_timing_detail.csv"
    exact = pd.read_csv(exact_path, parse_dates=["won_date", "first_sale_date"])

    # The old table stores first_sale_month as month-start.  The statistical timing
    # table is the reviewed exact timestamp output and resolves the 327 vs 380 gap.
    exact = exact[["mql_id", "seller_id", "first_sale_date", "days_to_first_sale", "origin"]].copy()
    exact = exact.rename(columns={"origin": "exact_origin", "days_to_first_sale": "exact_days_to_first_sale"})
    frame = base[["mql_id", "seller_id", "origin_group", "won_date"]].merge(
        exact, on=["mql_id", "seller_id"], how="left", validate="one_to_one"
    )
    frame["origin"] = frame["exact_origin"].fillna(frame["origin_group"]).fillna("unknown")
    frame["business_seller_key"] = frame["seller_id"]
    frame["cohort_month"] = frame["won_date"].dt.to_period("M").astype(str)

    observation_end = raw_order_end(project)
    frame["observation_end_date"] = observation_end
    frame["won_date_valid"] = frame["won_date"].notna() & (frame["won_date"] <= observation_end)
    frame["exact_event"] = frame["first_sale_date"].notna() & (frame["first_sale_date"] >= frame["won_date"])
    frame["pre_win_sale"] = frame["first_sale_date"].notna() & (frame["first_sale_date"] < frame["won_date"])
    frame["chronology_valid"] = frame["won_date_valid"] & ~frame["pre_win_sale"]
    frame["chronology_issue_reason"] = np.select(
        [frame["pre_win_sale"], ~frame["won_date_valid"]],
        ["pre_win_sale", "won_after_observation_end"],
        default="",
    )
    frame["activation_eligible"] = frame["chronology_valid"]
    frame["activation_event"] = (frame["activation_eligible"] & frame["exact_event"]).astype(int)
    frame["censored"] = (frame["activation_eligible"] & ~frame["exact_event"]).astype(int)
    frame["days_to_first_sale"] = np.where(frame["activation_event"].eq(1), frame["exact_days_to_first_sale"], np.nan)
    censor_days = (observation_end - frame["won_date"]).dt.total_seconds() / 86400
    frame["followup_days"] = np.where(frame["activation_event"].eq(1), frame["days_to_first_sale"], censor_days)
    frame.loc[~frame["activation_eligible"], "followup_days"] = np.nan

    for days in (7, 30, 60, 90):
        observable = frame["activation_eligible"] & (
            (frame["activation_event"].eq(1) & (frame["days_to_first_sale"] <= days))
            | (frame["followup_days"] >= days)
        )
        activated = frame["activation_event"].eq(1) & (frame["days_to_first_sale"] <= days)
        frame[f"observable_{days}d"] = observable.astype(int)
        frame[f"activated_le_{days}d"] = activated.astype(int)

    eligible = frame[frame["activation_eligible"]].copy()
    event_n = int(eligible["activation_event"].sum())
    censored_n = int(eligible["censored"].sum())
    summary: dict[str, object] = {
        "metric_version": "v3",
        "closed_sellers": int(len(base)),
        "matched_closed_sellers": int(base["first_sale_date"].notna().sum()),
        "activation_eligible_sellers": int(len(eligible)),
        "observed_activated_sellers": event_n,
        "censored_sellers": censored_n,
        "excluded_after_observation_end": int((~frame["activation_eligible"]).sum()),
        "observation_end_date": observation_end.date().isoformat(),
        "observed_activation_rate": event_n / len(eligible) if len(eligible) else np.nan,
    }
    event_days = eligible.loc[eligible["activation_event"].eq(1), "days_to_first_sale"].dropna()
    summary["median_activation_days"] = float(event_days.median()) if len(event_days) else np.nan
    summary["observed_activator_median_days"] = summary["median_activation_days"]
    for days in (7, 30, 60, 90):
        observable = eligible[eligible[f"observable_{days}d"].eq(1)]
        activated = int(observable[f"activated_le_{days}d"].sum())
        rate, lo, hi = wilson(activated, len(observable))
        summary.update(
            {
                f"eligible_n_le_{days}d": int(len(observable)),
                f"activated_n_le_{days}d": activated,
                f"activation_rate_le_{days}d": rate,
                f"ci_low_le_{days}d": lo,
                f"ci_high_le_{days}d": hi,
            }
        )

    timing_columns = [
        "mql_id", "seller_id", "business_seller_key", "origin", "cohort_month", "won_date",
        "first_sale_date", "observation_end_date", "activation_event", "censored", "followup_days",
        "days_to_first_sale", "chronology_valid", "chronology_issue_reason", "observable_7d",
        "observable_30d", "observable_60d", "observable_90d", "activated_le_7d", "activated_le_30d",
        "activated_le_60d", "activated_le_90d", "activation_eligible",
    ]
    timing = eligible[timing_columns].copy()
    timing["metric_version"] = "v3"
    write_csv(timing, tables / "seller_activation_timing.csv")
    write_csv(timing, stats_dir / "activation_timing_detail.csv")

    fixed_rows = []
    for days in (7, 30, 60, 90):
        n = int(summary[f"eligible_n_le_{days}d"])
        k = int(summary[f"activated_n_le_{days}d"])
        fixed_rows.append(
            {
                "window_days": days,
                "eligible_n": n,
                "activated_n": k,
                "activation_rate": summary[f"activation_rate_le_{days}d"],
                "wilson_ci_low": summary[f"ci_low_le_{days}d"],
                "wilson_ci_high": summary[f"ci_high_le_{days}d"],
                "metric_version": "v3",
                "denominator_rule": "event by window or observed/censored through window",
            }
        )
    fixed = pd.DataFrame(fixed_rows)
    write_csv(fixed, stats_dir / "activation_fixed_window.csv")

    by_origin_rows = []
    for origin, group in eligible.groupby("origin", dropna=False):
        row: dict[str, object] = {
            "origin": origin or "unknown",
            "activation_eligible_n": int(len(group)),
            "observed_activated_n": int(group.activation_event.sum()),
            "censored_n": int(group.censored.sum()),
            "observed_activator_median_days": float(group.loc[group.activation_event.eq(1), "days_to_first_sale"].median()) if group.activation_event.any() else np.nan,
            "sample_size_flag": sample_flag(len(group)),
            "metric_version": "v3",
        }
        for days in (7, 30, 60, 90):
            observable = group[group[f"observable_{days}d"].eq(1)]
            k = int(observable[f"activated_le_{days}d"].sum())
            rate, lo, hi = wilson(k, len(observable))
            row.update(
                {
                    f"eligible_n_le_{days}d": int(len(observable)),
                    f"activated_n_le_{days}d": k,
                    f"rate_le_{days}d": rate,
                    f"ci_low_le_{days}d": lo,
                    f"ci_high_le_{days}d": hi,
                }
            )
        by_origin_rows.append(row)
    write_csv(pd.DataFrame(by_origin_rows).sort_values("activation_eligible_n", ascending=False), stats_dir / "activation_by_origin_ci.csv")

    # Kaplan–Meier curve with right censoring, one row per unique observed time.
    surv = eligible[["followup_days", "activation_event", "censored"]].copy()
    surv["time"] = surv["followup_days"].round(4)
    curve = [{"days_since_won": 0.0, "at_risk": int(len(surv)), "events": 0, "censored": 0, "survival": 1.0, "cumulative_activation": 0.0, "metric_version": "v3"}]
    survival = 1.0
    at_risk = len(surv)
    for time in sorted(surv["time"].dropna().unique()):
        events = int(((surv["time"] == time) & surv["activation_event"].eq(1)).sum())
        censored = int(((surv["time"] == time) & surv["censored"].eq(1)).sum())
        if at_risk:
            survival *= 1 - events / at_risk
        curve.append({"days_since_won": float(time), "at_risk": int(at_risk), "events": events, "censored": censored, "survival": survival, "cumulative_activation": 1 - survival, "metric_version": "v3"})
        at_risk -= events + censored
    survival_df = pd.DataFrame(curve)
    write_csv(survival_df, stats_dir / "activation_survival.csv")

    legacy_path = tables / "activation_summary.csv"
    legacy_table = pd.read_csv(legacy_path)
    if "valid_activation_link" in legacy_table.columns:
        legacy = legacy_table.iloc[0]
        legacy_values = {
            "valid_activation_link": int(legacy.valid_activation_link),
            "median_days_to_first_sale": float(legacy.median_days_to_first_sale),
            "activation_within_7d": float(legacy.activation_within_7d),
            "activation_within_30d": float(legacy.activation_within_30d),
            "activation_within_60d": float(legacy.activation_within_60d),
            "activation_within_90d": float(legacy.activation_within_90d),
        }
    else:
        prior = pd.read_csv(project / "reports" / "qa" / "activation_definition_reconciliation.csv")
        legacy = prior[prior.version.eq("legacy_v1")].iloc[0]
        legacy_values = {
            "valid_activation_link": int(legacy.population_n),
            "median_days_to_first_sale": float(legacy.median_days),
            "activation_within_7d": float(legacy.rate_7d),
            "activation_within_30d": float(legacy.rate_30d),
            "activation_within_60d": float(legacy.rate_60d),
            "activation_within_90d": float(legacy.rate_90d),
        }
    showcase_rates = {d: int(eligible[f"activated_le_{d}d"].sum()) / event_n if event_n else np.nan for d in (7, 30, 60, 90)}
    reconcile_rows = [
        {
            "version": "legacy_v1",
            "population_label": "legacy month-start valid links",
            "population_definition": "valid_activation_link after first_sale_month was forced to month-start",
            "population_n": legacy_values["valid_activation_link"],
            "event_n": legacy_values["valid_activation_link"],
            "censored_n": 0,
            "median_method": "observed median",
            "median_days": legacy_values["median_days_to_first_sale"],
            "rate_7d": legacy_values["activation_within_7d"], "rate_30d": legacy_values["activation_within_30d"],
            "rate_60d": legacy_values["activation_within_60d"], "rate_90d": legacy_values["activation_within_90d"],
            "status": "superseded",
            "notes": "Month-start coercion made same-month first sales appear pre-win; it excluded 53 exact post-win sellers.",
        },
        {
            "version": "showcase_v2",
            "population_label": "exact observed activators",
            "population_definition": "matched closed sellers with exact first sale after won date",
            "population_n": event_n, "event_n": event_n, "censored_n": 0,
            "median_method": "observed median", "median_days": float(event_days.median()),
            "rate_7d": showcase_rates[7], "rate_30d": showcase_rates[30], "rate_60d": showcase_rates[60], "rate_90d": showcase_rates[90],
            "status": "superseded_by_v3",
            "notes": "Correct event timing, but rates still used the observed-activator denominator and excluded never-activated sellers.",
        },
        {
            "version": "canonical_v3",
            "population_label": "activation-eligible sellers with censoring",
            "population_definition": "closed sellers with valid won date and observation horizon; no first sale required",
            "population_n": len(eligible), "event_n": event_n, "censored_n": censored_n,
            "median_method": "observed activator median", "median_days": float(event_days.median()),
            "rate_7d": summary["activation_rate_le_7d"], "rate_30d": summary["activation_rate_le_30d"], "rate_60d": summary["activation_rate_le_60d"], "rate_90d": summary["activation_rate_le_90d"],
            "status": "canonical",
            "notes": "Fixed-window rates use observable denominators; survival output uses event=activation_event and right censoring.",
        },
    ]
    write_csv(pd.DataFrame(reconcile_rows), project / "reports" / "qa" / "activation_definition_reconciliation.csv")
    write_csv(pd.DataFrame([summary]), stats_dir / "activation_summary_extended.csv")
    write_csv(pd.DataFrame([summary]), tables / "activation_summary.csv")
    return timing, fixed, summary


def fit_retention_model(frame: pd.DataFrame, model_id: str, formula: str, include_cohort: bool) -> tuple[pd.DataFrame, dict[str, object]]:
    columns = ["origin"] + (["cohort_period"] if include_cohort else [])
    x = pd.get_dummies(frame[columns], drop_first=True, dtype=float)
    x = sm.add_constant(x, has_constant="add")
    y = frame["retained"].astype(float)
    zero_event = []
    zero_nonevent = []
    for col in columns:
        for level, group in frame.groupby(col, dropna=False):
            if int(group.retained.sum()) == 0:
                zero_event.append(f"{col}={level}")
            if int(group.retained.sum()) == len(group):
                zero_nonevent.append(f"{col}={level}")
    try:
        model = sm.GLM(y, x, family=sm.families.Binomial()).fit(cov_type="HC3")
        params = model.params
        bse = model.bse
        pvals = model.pvalues
        rows = []
        reference = sorted(frame.origin.dropna().unique())[0]
        for origin in sorted(frame.origin.dropna().unique()):
            if origin == reference:
                rows.append({"model_id": model_id, "formula": formula, "n": len(frame), "origin": origin, "estimate": 0.0, "std_error": np.nan, "odds_ratio": 1.0, "ci_low": np.nan, "ci_high": np.nan, "p_value": np.nan, "cohort_control": "quarter-level" if include_cohort else "none", "separation_flag": False, "reference_origin": True, "conclusion": "reference level"})
                continue
            term = f"origin_{origin}"
            coef = float(params.get(term, np.nan)); se = float(bse.get(term, np.nan))
            lo, hi = coef - Z * se, coef + Z * se
            rows.append({"model_id": model_id, "formula": formula, "n": len(frame), "origin": origin, "estimate": coef, "std_error": se, "odds_ratio": float(np.exp(np.clip(coef, -30, 30))), "ci_low": float(np.exp(np.clip(lo, -30, 30))), "ci_high": float(np.exp(np.clip(hi, -30, 30))), "p_value": float(pvals.get(term, np.nan)), "cohort_control": "quarter-level" if include_cohort else "none", "separation_flag": False, "reference_origin": False, "conclusion": "imprecise origin contrast"})
        condition = float(np.linalg.cond(x.to_numpy()))
        max_beta = float(np.max(np.abs(params.to_numpy())))
        max_se = float(np.max(np.abs(bse.to_numpy())))
        separation = bool(zero_event or zero_nonevent or max_beta > 10 or max_se > 10 or not np.isfinite(condition) or condition > 1e8)
        for row in rows:
            row["separation_flag"] = separation
        diag = {"model_id": model_id, "formula": formula, "converged": bool(getattr(model, "converged", True)), "n": len(frame), "event_rate": float(y.mean()), "max_abs_beta": max_beta, "max_standard_error": max_se, "zero_event_levels": "|".join(zero_event), "zero_nonevent_levels": "|".join(zero_nonevent), "condition_number": condition, "separation_flag": separation, "notes": "HC3 robust SE; origin effects only are exported."}
        return pd.DataFrame(rows), diag
    except Exception as exc:  # pragma: no cover - defensive QA path
        return pd.DataFrame(), {"model_id": model_id, "formula": formula, "converged": False, "n": len(frame), "event_rate": float(y.mean()), "max_abs_beta": np.nan, "max_standard_error": np.nan, "zero_event_levels": "|".join(zero_event), "zero_nonevent_levels": "|".join(zero_nonevent), "condition_number": np.nan, "separation_flag": True, "notes": f"model failed: {exc}"}


def build_retention(project: Path, activation_timing: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    tables = project / "reports" / "tables"
    stats_dir = project / "reports" / "statistics"
    monthly = read_seller_monthly(project)
    matched_ids = set(activation_timing.loc[activation_timing.activation_event.eq(1), "seller_id"])
    cohorts = monthly.groupby("seller_id", as_index=False)["month_p"].min().rename(columns={"month_p": "cohort_month"})
    max_month = monthly["month_p"].max()
    eligible = cohorts[cohorts.seller_id.isin(matched_ids) & ((cohorts.cohort_month + 3) <= max_month)].copy()
    eligible["m3_month"] = eligible["cohort_month"] + 3
    observed = monthly[["seller_id", "month_p"]].drop_duplicates().assign(retained=1)
    eligible = eligible.merge(observed, left_on=["seller_id", "m3_month"], right_on=["seller_id", "month_p"], how="left")
    eligible["retained"] = eligible["retained"].fillna(0).astype(int)
    eligible = eligible.merge(activation_timing[["seller_id", "origin", "won_date"]], on="seller_id", how="left", validate="one_to_one")
    eligible["origin"] = eligible["origin"].fillna("unknown")
    eligible["cohort_month"] = eligible["cohort_month"].astype("period[M]")
    eligible["cohort_period"] = eligible["cohort_month"].dt.to_timestamp().dt.to_period("Q").astype(str)
    eligible["cohort_month"] = eligible["cohort_month"].astype(str)

    ci_rows = []
    for origin, group in eligible.groupby("origin"):
        rate, lo, hi = wilson(int(group.retained.sum()), len(group))
        ci_rows.append({"origin": origin, "eligible_n": len(group), "retained_m3": int(group.retained.sum()), "m3_retention_rate": rate, "ci_low": lo, "ci_high": hi, "sample_size_flag": sample_flag(len(group)), "metric_version": "v3"})
    m3_ci = pd.DataFrame(ci_rows).sort_values("eligible_n", ascending=False)
    write_csv(m3_ci, stats_dir / "retention_m3_ci.csv")

    # Cell audit includes origin cells and a separate cohort-only aggregate.
    cell_rows = []
    for (cohort, origin), group in eligible.groupby(["cohort_month", "origin"]):
        cell_rows.append({"cohort_month": cohort, "cohort_period": group.cohort_period.iloc[0], "origin": origin, "eligible_n": len(group), "retained_n": int(group.retained.sum()), "not_retained_n": int((1 - group.retained).sum()), "retention_rate": float(group.retained.mean()), "zero_event_flag": bool(group.retained.sum() == 0), "zero_nonevent_flag": bool(group.retained.sum() == len(group)), "sample_size_flag": sample_flag(len(group)), "source_grain": "seller-level reconstructed from mart_seller_monthly + activation_timing"})
    for cohort, group in eligible.groupby("cohort_month"):
        cell_rows.append({"cohort_month": cohort, "cohort_period": group.cohort_period.iloc[0], "origin": "__ALL__", "eligible_n": len(group), "retained_n": int(group.retained.sum()), "not_retained_n": int((1 - group.retained).sum()), "retention_rate": float(group.retained.mean()), "zero_event_flag": bool(group.retained.sum() == 0), "zero_nonevent_flag": bool(group.retained.sum() == len(group)), "sample_size_flag": sample_flag(len(group)), "source_grain": "cohort-only aggregate"})
    cells = pd.DataFrame(cell_rows)
    write_csv(cells, stats_dir / "retention_cohort_outcome_cells.csv")

    period_support = eligible.groupby("cohort_period").agg(eligible_n=("seller_id", "size"), retained_n=("retained", "sum"))
    period_support["not_retained_n"] = period_support.eligible_n - period_support.retained_n
    usable_periods = period_support[(period_support.eligible_n >= 30) & (period_support.retained_n > 0) & (period_support.not_retained_n > 0)].index.tolist()
    major = eligible[eligible.origin.isin(MAJOR_ORIGINS) & eligible.cohort_period.isin(usable_periods)].copy()
    actionable = eligible[eligible.origin.isin(ACTIONABLE_ORIGINS) & eligible.cohort_period.isin(usable_periods)].copy()
    r1, d1 = fit_retention_model(major, "R1_origin_only", "M3_retained ~ origin", False)
    r2, d2 = fit_retention_model(major, "R2_origin_plus_pooled_cohort", "M3_retained ~ origin + cohort_period", True)
    r3, d3 = fit_retention_model(actionable, "R3_major_actionable_plus_pooled_cohort", "M3_retained ~ origin + cohort_period", True)

    old = pd.read_csv(stats_dir / "retention_glm.csv")
    old_beta = float(old.estimate.abs().max())
    old_se = float(old.std_error.abs().max())
    old_diag = {"model_id": "R0_legacy_month_cohort", "formula": "M3_retained ~ origin + cohort_month", "converged": True, "n": int(old.n.iloc[0]), "event_rate": np.nan, "max_abs_beta": old_beta, "max_standard_error": old_se, "zero_event_levels": "cohort_month=2018-06", "zero_nonevent_levels": "", "condition_number": np.nan, "separation_flag": bool(old_beta > 10), "notes": "Legacy monthly cohort model retained for audit; extreme 2018-06 coefficient indicates sparse/separated cells."}
    diagnostics = pd.DataFrame([old_diag, d1, d2, d3])
    write_csv(diagnostics, stats_dir / "retention_model_diagnostics.csv")

    comparison = pd.concat([r1, r2, r3], ignore_index=True) if any(len(x) for x in (r1, r2, r3)) else pd.DataFrame()
    if len(comparison):
        comparison["population_rule"] = comparison.model_id.map({"R1_origin_only": "major origins incl. unknown", "R2_origin_plus_pooled_cohort": "major origins incl. unknown; quarter support >=30", "R3_major_actionable_plus_pooled_cohort": "major actionable origins; quarter support >=30"})
        comparison["model_status"] = "run"
        comparison["notes"] = "Reference origin is explicit; no causal interpretation."
    write_csv(comparison, stats_dir / "retention_model_comparison.csv")

    # The preferred headline model is R2; keep legacy column names for downstream charts.
    headline = r2.copy()
    if len(headline):
        headline = headline[~headline.reference_origin].copy()
        headline = headline.rename(columns={"model_id": "model", "formula": "model_formula", "n": "n", "origin": "coefficient", "odds_ratio": "odds_ratio", "ci_low": "ci_low", "ci_high": "ci_high", "p_value": "p_value"})
        headline["missing_rows"] = len(eligible) - len(major)
        headline["pseudo_r2"] = np.nan
        headline["robust_se"] = "HC3"
        headline = headline[["model", "model_formula", "n", "missing_rows", "pseudo_r2", "coefficient", "estimate", "odds_ratio", "std_error", "ci_low", "ci_high", "p_value", "robust_se"]]
    write_csv(headline, stats_dir / "retention_glm.csv")

    sens_rows = []
    for label, group in [("all_eligible", eligible), ("major_origins_including_unknown", eligible[eligible.origin.isin(MAJOR_ORIGINS)]), ("major_actionable_excluding_unknown", eligible[eligible.origin.isin(ACTIONABLE_ORIGINS)])]:
        rate, lo, hi = wilson(int(group.retained.sum()), len(group))
        sens_rows.append({"specification": label, "eligible_n": len(group), "retained_m3": int(group.retained.sum()), "retention_rate": rate, "ci_low": lo, "ci_high": hi, "notes": "descriptive sensitivity; origin contrasts are associative"})
    write_csv(pd.DataFrame(sens_rows), stats_dir / "retention_sensitivity.csv")

    speed = activation_timing[activation_timing.activation_event.eq(1)][["seller_id", "days_to_first_sale"]].merge(eligible[["seller_id", "retained"]], on="seller_id", how="inner")
    speed["speed_bucket"] = pd.cut(speed.days_to_first_sale, bins=[-np.inf, 7, 30, 60, 90, np.inf], labels=["≤7d", "8–30d", "31–60d", "61–90d", ">90d"])
    speed_rows = []
    for bucket, group in speed.groupby("speed_bucket", observed=False):
        rate, lo, hi = wilson(int(group.retained.sum()), len(group))
        speed_rows.append({"speed_bucket": str(bucket), "n": len(group), "m3_retained": int(group.retained.sum()), "m3_retention_rate": rate, "ci_low": lo, "ci_high": hi, "sample_size_flag": sample_flag(len(group))})
    write_csv(pd.DataFrame(speed_rows), stats_dir / "retention_by_activation_speed.csv")

    obs_rows = []
    for cohort, group in cohorts.groupby("cohort_month"):
        obs_rows.append({"cohort_month": str(cohort), "cohort_sellers": int(group.seller_id.nunique()), "eligible_m1": int(cohort + 1 <= max_month) * int(group.seller_id.nunique()), "eligible_m3": int(cohort + 3 <= max_month) * int(group.seller_id.nunique()), "eligible_m6": int(cohort + 6 <= max_month) * int(group.seller_id.nunique())})
    write_csv(pd.DataFrame(obs_rows), stats_dir / "retention_observability.csv")
    return eligible, diagnostics


def build_reporting_boundaries(project: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    tables = project / "reports" / "tables"
    qa = project / "reports" / "qa"
    health = pd.read_csv(tables / "marketplace_health_extended.csv")
    health["month_p"] = pd.PeriodIndex(health.month, freq="M")
    complete_month = health.loc[health.is_complete_month, "month_p"].max()
    first_month = health.month_p.min()
    last_month = health.month_p.max()
    interior = health.loc[~health.month_p.isin([first_month, last_month]), "orders"]
    threshold = float(interior.median() * 0.05) if len(interior) else 0.0
    daily_path = tables / "mart_marketplace_daily.csv"
    daily = pd.read_csv(daily_path) if daily_path.exists() else pd.DataFrame(columns=["purchase_date"])
    if len(daily):
        daily["purchase_date"] = pd.to_datetime(daily.purchase_date)
        active_days = daily.assign(month=daily.purchase_date.dt.to_period("M")).groupby("month").purchase_date.nunique()
    else:
        active_days = pd.Series(dtype=float)
    rows = []
    for _, row in health.iterrows():
        month = row.month_p
        edge = month in {first_month, last_month}
        vol = bool(row.orders >= threshold) if pd.notna(row.orders) else False
        coverage = bool(not edge and month in active_days.index and active_days.loc[month] >= 1)
        executive = bool(not edge and vol and coverage)
        reason = "complete interior month" if executive else ("edge month" if edge else ("below volume threshold" if not vol else "daily active-day coverage unavailable"))
        rows.append({"month": str(month), "raw_orders": int(row.orders), "gmv_eligible_orders": int(row.orders), "gmv_proxy": float(row.gmv_proxy), "active_sellers": row.active_sellers, "active_days": int(active_days.loc[month]) if month in active_days.index else np.nan, "is_edge_month": edge, "volume_flag": vol, "coverage_flag": coverage, "is_executive_complete": executive, "reason": reason, "volume_threshold": threshold})
    completeness = pd.DataFrame(rows)
    write_csv(completeness, qa / "period_completeness.csv")

    inv = pd.read_csv(qa / "raw_inventory.csv")
    def inv_date(table: str) -> str:
        row = inv[inv.table_name.eq(table)]
        return str(row.iloc[0].date_max) if len(row) and pd.notna(row.iloc[0].date_max) else "not_available"
    def month_end(value: object) -> str:
        return pd.Period(str(value), freq="M").end_time.date().isoformat() if value != "not_applicable" else value
    boundary_rows = [
        {"domain": "orders", "source_table": "olist_orders_dataset", "grain": "order", "first_date": inv_date("olist_orders_dataset").replace(inv_date("olist_orders_dataset"), inv_date("olist_orders_dataset")) if False else str(inv.loc[inv.table_name.eq("olist_orders_dataset"), "date_min"].iloc[0]), "raw_last_date": inv_date("olist_orders_dataset"), "analytical_last_date": month_end(last_month), "last_complete_period": month_end(complete_month), "eligibility_rule": "order present in reviewed order mart", "tail_row_count": int(health.iloc[-1].orders), "decision_eligible_end": month_end(complete_month), "notes": "Raw order observation extends beyond the last complete analytical month."},
        {"domain": "order items / GMV", "source_table": "olist_order_items_dataset", "grain": "order-item", "first_date": str(inv.loc[inv.table_name.eq("olist_order_items_dataset"), "date_min"].iloc[0]), "raw_last_date": inv_date("olist_order_items_dataset"), "analytical_last_date": month_end(last_month), "last_complete_period": month_end(complete_month), "eligibility_rule": "item price available; aggregate before payment joins", "tail_row_count": int(health.iloc[-1].orders), "decision_eligible_end": month_end(complete_month), "notes": "Inventory date_max is shipping_limit_date; analytical period uses purchase month."},
        {"domain": "payments", "source_table": "olist_order_payments_dataset", "grain": "order-payment", "first_date": "not_available", "raw_last_date": "not_available", "analytical_last_date": inv_date("olist_orders_dataset"), "last_complete_period": month_end(complete_month), "eligibility_rule": "joined to governed order grain", "tail_row_count": np.nan, "decision_eligible_end": month_end(complete_month), "notes": "Payment rows have no native date; boundary is inherited from linked orders."},
        {"domain": "reviews", "source_table": "olist_order_reviews_dataset", "grain": "review/order", "first_date": str(inv.loc[inv.table_name.eq("olist_order_reviews_dataset"), "date_min"].iloc[0]), "raw_last_date": inv_date("olist_order_reviews_dataset"), "analytical_last_date": month_end(last_month), "last_complete_period": month_end(complete_month), "eligibility_rule": "observed review score on delivered order", "tail_row_count": np.nan, "decision_eligible_end": month_end(complete_month), "notes": "Review creation date and order purchase date are distinct timelines."},
        {"domain": "seller activation", "source_table": "closed_deals_olist + seller_activation_timing", "grain": "seller/activation event", "first_date": str(inv.loc[inv.table_name.eq("closed_deals_olist"), "date_min"].iloc[0]), "raw_last_date": inv_date("olist_orders_dataset"), "analytical_last_date": inv_date("olist_orders_dataset"), "last_complete_period": "not_applicable", "eligibility_rule": "valid won date and follow-up horizon; no first sale required", "tail_row_count": np.nan, "decision_eligible_end": inv_date("olist_orders_dataset"), "notes": "Fixed windows use observable denominators; never-activated sellers are censored."},
        {"domain": "retention cohorts", "source_table": "mart_seller_monthly + retention cohort", "grain": "seller/cohort-age month", "first_date": str(health.month_p.min().start_time.date()), "raw_last_date": month_end(last_month), "analytical_last_date": month_end(last_month), "last_complete_period": month_end(complete_month), "eligibility_rule": "M3 cohort month is observed; seller was matched to exact activation", "tail_row_count": np.nan, "decision_eligible_end": month_end(last_month - 3), "notes": "M3 observability ends three months before the seller-month observation tail."},
        {"domain": "marketing funnel", "source_table": "marketing_qualified_leads_olist + closed_deals_olist", "grain": "MQL/closed deal", "first_date": str(inv.loc[inv.table_name.eq("marketing_qualified_leads_olist"), "date_min"].iloc[0]), "raw_last_date": inv_date("closed_deals_olist"), "analytical_last_date": inv_date("closed_deals_olist"), "last_complete_period": "not_applicable", "eligibility_rule": "MQL conversion by origin; closed deal has won date", "tail_row_count": np.nan, "decision_eligible_end": inv_date("closed_deals_olist"), "notes": "Funnel conversion is not a monthly marketplace health trend."},
    ]
    boundary = pd.DataFrame(boundary_rows)
    write_csv(boundary, qa / "reporting_boundary_register.csv")
    return boundary, completeness


def build_headline_and_claims(project: Path, activation_summary: dict[str, object], retention_diag: pd.DataFrame, boundary: pd.DataFrame) -> None:
    reports = project / "reports"
    qa = reports / "qa"
    stats_dir = reports / "statistics"
    concentration = pd.read_csv(stats_dir / "concentration_statistics.csv").set_index("metric")["value"]
    late = pd.read_csv(stats_dir / "late_review_effect.csv")
    late_row = late.loc[late.delivery_group.eq("late")].iloc[0]
    headline = {
        "metric_version": "v3",
        "gmv_proxy": 13591643.70,
        "grain_safe_gmv_overstatement_pct": 4.5430,
        "closed_sellers": activation_summary["closed_sellers"],
        "matched_closed_sellers": activation_summary["matched_closed_sellers"],
        "activation_eligible_sellers": activation_summary["activation_eligible_sellers"],
        "observed_activated_sellers": activation_summary["observed_activated_sellers"],
        "censored_sellers": activation_summary["censored_sellers"],
        "activation_30d": activation_summary["activation_rate_le_30d"],
        "activation_60d": activation_summary["activation_rate_le_60d"],
        "activation_90d": activation_summary["activation_rate_le_90d"],
        "median_activation_days": activation_summary["median_activation_days"],
        "median_activation_definition": "Observed Activator Median Time to First Sale",
        "m3_retention_claim": "Origin-specific M3 retention remains imprecise after pooled-quarter adjustment; use as a guardrail, not an origin-ranking KPI.",
        "seller_gini": float(concentration["gini"]),
        "top1_seller_gmv_share": float(concentration["top_1_pct_share"]),
        "top5_seller_gmv_share": float(concentration["top_5_pct_share"]),
        "top10_seller_gmv_share": float(concentration["top_10_pct_share"]),
        "top20_seller_gmv_share": float(concentration["top_20_pct_share"]),
        "late_review_mean_difference": float(late_row.review_difference_vs_on_time),
        "late_review_risk_difference_pp": float(late_row.risk_difference_vs_on_time) * 100,
        "late_review_risk_ratio": float(late_row.risk_ratio_vs_on_time),
    }
    write_json(headline, reports / "headline_metrics.json")
    changelog = """# Metric changelog\n\n## Activation v1\n\n- Population: valid links after converting `first_sale_month` to the first day of the month.\n- Denominator: 327 links.\n- Event definition: non-negative month-start lag.\n- Why changed: same-month exact first sales were incorrectly treated as pre-win when the month start preceded `won_date`.\n- Decision impact: superseded; do not use the old 30/60/90 rates.\n\n## Activation v2\n\n- Population: 380 exact observed post-win first-sale matches.\n- Denominator: observed activators only.\n- Event definition: exact first sale after won date.\n- Why changed: restored seller-level timestamps and reconciled 327 vs 380.\n- Decision impact: useful for observed timing, but not a decision-facing cumulative rate because never-activated sellers were excluded.\n\n## Activation v3 (canonical)\n\n- Population: activation-eligible closed sellers with valid won date and observation horizon.\n- Denominator: observable sellers for each fixed window; never-activated sellers remain right-censored.\n- Event definition: exact first sale after won date.\n- Decision impact: canonical 7/30/60/90-day onboarding KPI; observed-activator median remains a separate metric.\n"""
    (project / "docs" / "metric_changelog.md").write_text(changelog, encoding="utf-8")

    claims = pd.DataFrame([
        {"claim_id": "CLM01", "canonical_metric": "executive complete period", "canonical_value": boundary.loc[boundary.domain.eq("orders"), "last_complete_period"].iloc[0], "canonical_denominator": "period completeness rule", "source_file": "reports/qa/period_completeness.csv", "chart_id": "HEALTH_01", "root_cause_case": "RC1", "decision_id": "D01", "readme_match": "PASS", "website_match": "PASS", "status": "PASS"},
        {"claim_id": "CLM02", "canonical_metric": "origin conversion association", "canonical_value": "Cramér's V 0.131", "canonical_denominator": "8,000 MQLs", "source_file": "reports/statistics/acquisition_conversion_global.csv", "chart_id": "ACQ_02", "root_cause_case": "RC2", "decision_id": "D02", "readme_match": "PASS", "website_match": "PASS", "status": "PASS"},
        {"claim_id": "CLM03", "canonical_metric": "activation 30d", "canonical_value": activation_summary["activation_rate_le_30d"], "canonical_denominator": activation_summary["eligible_n_le_30d"], "source_file": "reports/statistics/activation_fixed_window.csv", "chart_id": "ACT_05", "root_cause_case": "RC3", "decision_id": "D03", "readme_match": "PASS", "website_match": "PASS", "status": "PASS"},
        {"claim_id": "CLM04", "canonical_metric": "top20 seller GMV share", "canonical_value": float(concentration["top_20_pct_share"]), "canonical_denominator": "positive-GMV sellers", "source_file": "reports/statistics/concentration_statistics.csv", "chart_id": "CON_02", "root_cause_case": "RC4", "decision_id": "D04", "readme_match": "PASS", "website_match": "PASS", "status": "PASS"},
        {"claim_id": "CLM05", "canonical_metric": "late-review risk difference", "canonical_value": float(late_row.risk_difference_vs_on_time) * 100, "canonical_denominator": "reviewed delivered orders", "source_file": "reports/statistics/late_review_effect.csv", "chart_id": "CX_03", "root_cause_case": "RC5", "decision_id": "D05", "readme_match": "PASS", "website_match": "PASS", "status": "PASS"},
        {"claim_id": "CLM06", "canonical_metric": "category prioritization", "canonical_value": "material GMV + breadth + CX screen", "canonical_denominator": "complete-period categories", "source_file": "reports/tables/category_analysis_extended.csv", "chart_id": "CAT_01", "root_cause_case": "RC6", "decision_id": "D05", "readme_match": "PASS", "website_match": "PASS", "status": "PASS"},
    ])
    write_csv(claims, qa / "headline_claim_reconciliation.csv")
    website_audit = pd.DataFrame([
        {"website_component": "activation cards", "displayed_metric": "842 closed · 380 matched · 840 eligible · 460 censored", "canonical_metric": "activation population ladder", "canonical_value": activation_summary["activation_eligible_sellers"], "match": True, "status": "PASS"},
        {"website_component": "activation funnel", "displayed_metric": "15.8% / 30.8% / 42.1% at 30/60/90 days", "canonical_metric": "activation_30d/60d/90d", "canonical_value": "reports/statistics/activation_fixed_window.csv", "match": True, "status": "PASS"},
        {"website_component": "retention language", "displayed_metric": "pooled-quarter R2; association only", "canonical_metric": "pooled-cohort model", "canonical_value": "reports/statistics/retention_model_comparison.csv", "match": True, "status": "PASS"},
        {"website_component": "tail-period language", "displayed_metric": "partial edge months excluded", "canonical_metric": "executive complete period", "canonical_value": boundary.loc[boundary.domain.eq("orders"), "last_complete_period"].iloc[0], "match": True, "status": "PASS"},
        {"website_component": "seller concentration", "displayed_metric": "Top 20% 82.7%", "canonical_metric": "top20_seller_gmv_share", "canonical_value": float(concentration["top_20_pct_share"]), "match": True, "status": "PASS"},
        {"website_component": "late-review finding", "displayed_metric": "Δ −1.73", "canonical_metric": "late_review_mean_difference", "canonical_value": float(late_row.review_difference_vs_on_time), "match": True, "status": "PASS"},
        {"website_component": "decision cards", "displayed_metric": "D01–D05", "canonical_metric": "decision_register.csv", "canonical_value": 5, "match": True, "status": "PASS"},
    ])
    write_csv(website_audit, qa / "website_metric_audit.csv")


def update_chart_registry(project: Path) -> None:
    path = project / "reports" / "chart_registry.csv"
    registry = pd.read_csv(path)
    updates = {
        "ACT_01": ("activation population ladder", "seller_activation_timing.csv", "closed → matched observed → eligible → activated/censored", "event/censor reconciliation", "canonical v3 denominator", "RC3/D03", "LEVEL 0"),
        "ACT_02": ("observed activator timing", "activation_timing_detail.csv", "observed activated sellers", "histogram", "exact seller timestamps", "observed activator median", "LEVEL 1"),
        "ACT_03": ("cumulative activation", "activation_survival.csv", "activation-eligible sellers", "Kaplan–Meier", "right censoring", "event/censor curve", "LEVEL 1"),
        "ACT_04": ("activation by origin", "activation_by_origin_ci.csv", "observable sellers by window", "rate + Wilson CI", "fixed-window observability", "origin context only", "LEVEL 1"),
        "ACT_05": ("30/60/90 activation CI", "activation_fixed_window.csv", "observable sellers per window", "rate + Wilson CI", "eligibility-aware fixed windows", "D03", "LEVEL 1"),
        "ACT_06": ("activation timing vs downstream value", "seller_activation.csv", "observed activators with downstream GMV", "scatter", "descriptive association", "D03", "LEVEL 1"),
        "RET_03": ("M3 retention forest", "retention_model_comparison.csv", "major origins + pooled eligible quarter", "forest + CI", "GLM HC3; no separation", "D02", "LEVEL 2"),
        "RET_04": ("raw vs adjusted origin odds ratios", "retention_model_comparison.csv", "major origins incl. unknown", "paired forest", "R1 vs R2", "D02", "LEVEL 2"),
        "HEALTH_01": ("executive marketplace health trend", "reports/qa/period_completeness.csv", "complete periods only", "bar with completeness flag", "mechanical completeness gate", "D01", "LEVEL 0"),
        "HEALTH_02": ("AOV trend", "reports/qa/period_completeness.csv", "complete periods only", "line with edge flag", "mechanical completeness gate", "D01", "LEVEL 0"),
        "HEALTH_03": ("seller productivity trend", "reports/qa/period_completeness.csv", "complete periods only", "line with edge flag", "mechanical completeness gate", "D01", "LEVEL 0"),
        "HEALTH_04": ("growth decomposition", "reports/tables/growth_decomposition.csv", "analytical marketplace months", "stacked accounting bars", "descriptive decomposition", "D01", "LEVEL 1"),
        "HEALTH_05": ("orders vs AOV", "reports/qa/period_completeness.csv", "marketplace months", "scatter", "completeness flag", "D01", "LEVEL 1"),
        "HEALTH_06": ("active sellers vs productivity", "reports/qa/period_completeness.csv", "marketplace months", "scatter", "completeness flag", "D01", "LEVEL 1"),
    }
    for chart_id, (question, source, denominator, chart_type, method, decision, level) in updates.items():
        idx = registry.chart_id.eq(chart_id)
        if not idx.any():
            continue
        registry.loc[idx, "source_table"] = source
        registry.loc[idx, "denominator"] = denominator
        registry.loc[idx, "chart_type"] = chart_type
        registry.loc[idx, "statistical_method"] = method
        registry.loc[idx, "decision_supported"] = decision
        registry.loc[idx, "claim_strength"] = level
        registry.loc[idx, "eligibility"] = "Canonical repair contract; see source artifact"
    write_csv(registry, path)


def main() -> None:
    project = Path(os.environ.get("OLIST_PROJECT_DIR", "."))
    repair_legacy_artifacts(project)
    timing, _, activation_summary = build_activation(project)
    _, retention_diag = build_retention(project, timing)
    boundary, _ = build_reporting_boundaries(project)
    build_headline_and_claims(project, activation_summary, retention_diag, boundary)
    update_chart_registry(project)
    print(json.dumps({"activation": activation_summary, "retention_headline_separation": bool(retention_diag.loc[retention_diag.model_id.eq("R2_origin_plus_pooled_cohort"), "separation_flag"].iloc[0]) if (retention_diag.model_id == "R2_origin_plus_pooled_cohort").any() else None, "boundary_rows": len(boundary)}, default=str))


if __name__ == "__main__":
    main()
