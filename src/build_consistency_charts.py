"""Regenerate only the charts affected by the analytical consistency repair."""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT = Path(os.environ.get("OLIST_PROJECT_DIR", "."))
CHARTS = PROJECT / "reports" / "charts"
NAVY, BLUE, TEAL, GOLD, RED, GREY = "#10243e", "#2d77c7", "#1d9a8a", "#e3a43b", "#c84b5a", "#6d7a89"


def save(fig: plt.Figure, relative: str, title: str, subtitle: str = "") -> None:
    ax = fig.axes[0]
    ax.set_title(title, loc="left", color=NAVY, fontweight="bold", pad=14)
    if subtitle:
        ax.text(0, 1.01, subtitle, transform=ax.transAxes, ha="left", va="bottom", fontsize=8, color=GREY)
    fig.tight_layout(rect=[0, 0.04, 1, 1])
    path = CHARTS / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main() -> None:
    reports = PROJECT / "reports"
    stats = reports / "statistics"
    tables = reports / "tables"

    summary = pd.read_csv(stats / "activation_summary_extended.csv").iloc[0]
    timing = pd.read_csv(tables / "seller_activation_timing.csv", parse_dates=["won_date", "first_sale_date"])
    fixed = pd.read_csv(stats / "activation_fixed_window.csv")
    by_origin = pd.read_csv(stats / "activation_by_origin_ci.csv")
    base = pd.read_csv(tables / "seller_activation.csv")

    fig, ax = plt.subplots(figsize=(8, 4.8))
    stages = ["closed", "matched\nobserved", "eligible", "activated", "censored"]
    values = [summary.closed_sellers, summary.matched_closed_sellers, summary.activation_eligible_sellers, summary.observed_activated_sellers, summary.censored_sellers]
    bars = ax.bar(stages, values, color=[NAVY, BLUE, TEAL, GOLD, RED])
    ax.set_ylabel("Sellers")
    ax.bar_label(bars, fmt="%.0f", padding=4)
    save(fig, "03_activation/act_01_explicit_denominator_funnel.png", "Activation v3 population ladder", "Exact first-sale events are separated from right-censored eligible sellers.")

    events = timing[timing.activation_event.eq(1)]
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.hist(events.days_to_first_sale, bins=20, color=BLUE, edgecolor="white")
    ax.axvline(events.days_to_first_sale.median(), color=RED, linestyle="--", label=f"median {events.days_to_first_sale.median():.1f}d")
    ax.set_xlabel("Days from won date to exact first sale")
    ax.set_ylabel("Observed activated sellers")
    ax.legend(frameon=False)
    save(fig, "03_activation/act_02_time_to_first_sale_distribution.png", "Observed activator time to first sale", "Timing among 380 observed post-win activators; separate from cumulative activation.")

    surv = pd.read_csv(stats / "activation_survival.csv")
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.step(surv.days_since_won, surv.cumulative_activation, where="post", color=TEAL)
    ax.set_xlabel("Days since won")
    ax.set_ylabel("Cumulative activation")
    ax.set_ylim(0, 1)
    save(fig, "03_activation/act_03_cumulative_activation_curve.png", "Cumulative activation with right censoring", "Kaplan–Meier style event/censor output; v3 observable follow-up contract.")

    fig, ax = plt.subplots(figsize=(8, 4.8))
    plot_origin = by_origin.sort_values("activation_eligible_n", ascending=True)
    ax.barh(plot_origin.origin, plot_origin.rate_le_30d, color=BLUE)
    ax.set_xlabel("30-day activation rate")
    ax.set_xlim(0, max(.3, float(plot_origin.rate_le_30d.max()) * 1.25))
    for i, row in plot_origin.reset_index(drop=True).iterrows():
        ax.text(row.rate_le_30d + .005, i, f"n={int(row.eligible_n_le_30d)}", va="center", fontsize=8)
    save(fig, "03_activation/act_04_activation_speed_by_origin.png", "30-day activation by origin", "Rates use observable denominators; origin remains descriptive context, not causal lift.")

    fig, ax = plt.subplots(figsize=(8, 4.8))
    x = fixed.window_days.to_numpy(); y = fixed.activation_rate.to_numpy(); lo = y - fixed.wilson_ci_low.to_numpy(); hi = fixed.wilson_ci_high.to_numpy() - y
    ax.errorbar(x, y, yerr=[lo, hi], fmt="o-", color=TEAL, capsize=4)
    ax.set_xlabel("Activation window (days)"); ax.set_ylabel("Activation rate"); ax.set_xticks(x); ax.set_ylim(0, 1)
    for xx, yy, nn in zip(x, y, fixed.eligible_n): ax.annotate(f"{yy:.1%}\n(n={int(nn)})", (xx, yy), textcoords="offset points", xytext=(0, 10), ha="center", fontsize=8)
    save(fig, "03_activation/act_05_30_60_90_activation_ci.png", "Eligibility-aware activation windows", "Denominator: event by window or observed/censored through window; Wilson 95% CI.")

    fig, ax = plt.subplots(figsize=(8, 4.8))
    scatter = events.merge(base[["seller_id", "total_gmv_proxy"]], on="seller_id", how="left")
    ax.scatter(scatter.days_to_first_sale, scatter.total_gmv_proxy, s=18, alpha=.55, color=GOLD)
    ax.set_xlabel("Days to exact first sale"); ax.set_ylabel("Downstream GMV proxy (R$)")
    save(fig, "03_activation/act_06_activation_time_vs_downstream_gmv.png", "Activation timing vs downstream value", "Observed association among exact activators; not a causal estimate.")

    comparison = pd.read_csv(stats / "retention_model_comparison.csv")
    r2 = comparison[(comparison.model_id == "R2_origin_plus_pooled_cohort") & (~comparison.reference_origin)].copy()
    r1 = comparison[(comparison.model_id == "R1_origin_only") & (~comparison.reference_origin)].copy()
    fig, ax = plt.subplots(figsize=(8, 4.8))
    r2 = r2.sort_values("odds_ratio")
    ypos = np.arange(len(r2)); ax.errorbar(r2.odds_ratio, ypos, xerr=[r2.odds_ratio-r2.ci_low, r2.ci_high-r2.odds_ratio], fmt="o", color=TEAL, capsize=4)
    ax.axvline(1, color=GREY, linestyle="--"); ax.set_yticks(ypos, r2.origin); ax.set_xlabel("Odds ratio for M3 retention"); ax.set_xscale("log")
    save(fig, "04_retention/ret_03_m3_retention_forest.png", "M3 retention: adjusted origin effects", "Headline model: origin + pooled eligible quarter; HC3 robust SE; no separation flag.")

    fig, ax = plt.subplots(figsize=(8, 4.8))
    for frame, label, color in [(r1, "R1 origin only", BLUE), (r2, "R2 + pooled quarter", TEAL)]:
        s = frame.set_index("origin").reindex(r2.origin)
        ax.plot(s.odds_ratio, ypos, "o", color=color, label=label)
    ax.axvline(1, color=GREY, linestyle="--"); ax.set_yticks(ypos, r2.origin); ax.set_xlabel("Odds ratio for M3 retention"); ax.set_xscale("log"); ax.legend(frameon=False)
    save(fig, "04_retention/ret_04_raw_vs_adjusted_or.png", "Raw vs adjusted M3 retention odds ratios", "Only origin effects shown; adjusted specification controls pooled eligible cohort quarter.")

    complete = pd.read_csv(reports / "qa" / "period_completeness.csv")
    fig, ax = plt.subplots(figsize=(8, 4.8))
    colors = [TEAL if x else RED for x in complete.is_executive_complete]
    ax.bar(complete.month, complete.gmv_proxy / 1e6, color=colors)
    ax.set_ylabel("GMV proxy (R$ millions)"); ax.tick_params(axis="x", rotation=70)
    save(fig, "01_marketplace_health/health_01_gmv_orders_active_sellers.png", "Executive trend with completeness gate", "Green = executive-complete; red = edge/below-threshold period excluded from headline trend.")

    health = pd.read_csv(tables / "marketplace_health_extended.csv")
    for metric, title, rel, ylabel in [("aov", "AOV trend with incomplete periods flagged", "01_marketplace_health/health_02_aov_trend.png", "AOV (R$)"), ("seller_productivity", "Seller productivity trend with incomplete periods flagged", "01_marketplace_health/health_03_seller_productivity_trend.png", "GMV proxy / active seller")]:
        fig, ax = plt.subplots(figsize=(8, 4.8)); ax.plot(health.month, health[metric], color=BLUE, marker="o", linewidth=1.5)
        bad = health[~health.is_complete_month]; ax.scatter(bad.month, bad[metric], color=RED, zorder=3, label="incomplete")
        ax.set_ylabel(ylabel); ax.tick_params(axis="x", rotation=70); ax.legend(frameon=False)
        save(fig, rel, title, "Executive reporting excludes incomplete edge periods.")

    growth = pd.read_csv(tables / "growth_decomposition.csv")
    fig, ax = plt.subplots(figsize=(8, 4.8)); x = np.arange(len(growth)); bottom = np.zeros(len(growth))
    for col, color in [("volume_effect", BLUE), ("aov_effect", GOLD), ("seller_count_effect", TEAL), ("productivity_effect", RED)]:
        vals = growth[col].fillna(0).to_numpy(); ax.bar(x, vals, bottom=bottom, color=color, label=col.replace("_", " ")); bottom += vals
    ax.set_xticks(x, growth.purchase_month, rotation=70); ax.set_ylabel("GMV decomposition effect"); ax.legend(frameon=False, fontsize=8)
    save(fig, "01_marketplace_health/health_04_growth_decomposition.png", "Growth decomposition on analytical months", "Descriptive accounting decomposition; incomplete edge periods remain visually identifiable in the source register.")

    fig, ax = plt.subplots(figsize=(7, 5)); ax.scatter(health.orders, health.aov, c=[TEAL if x else RED for x in health.is_complete_month], alpha=.8); ax.set_xlabel("Orders"); ax.set_ylabel("AOV (R$)")
    save(fig, "01_marketplace_health/health_05_orders_vs_aov_matrix.png", "Orders vs AOV", "Green points are executive-complete periods; red points are excluded/incomplete periods.")
    fig, ax = plt.subplots(figsize=(7, 5)); ax.scatter(health.active_sellers, health.seller_productivity, c=[TEAL if x else RED for x in health.is_complete_month], alpha=.8); ax.set_xlabel("Active sellers"); ax.set_ylabel("Seller productivity")
    save(fig, "01_marketplace_health/health_06_active_sellers_vs_productivity_matrix.png", "Active sellers vs seller productivity", "Green points are executive-complete periods; red points are excluded/incomplete periods.")

    print({"regenerated_activation_charts": 6, "regenerated_retention_charts": 2, "regenerated_health_charts": 6})


if __name__ == "__main__":
    main()
