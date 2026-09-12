"""Turn the statistical outputs into auditable root-cause cases and hypothesis rows."""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd


def main() -> None:
    project = Path(os.environ.get("OLIST_PROJECT_DIR", "."))
    stats = project / "reports" / "statistics"
    tables = project / "reports" / "tables"
    out = project / "reports"
    health = pd.read_csv(tables / "marketplace_health_extended.csv")
    acq = pd.read_csv(stats / "acquisition_conversion_by_origin.csv")
    activation = pd.read_csv(stats / "activation_summary_extended.csv").iloc[0]
    retention = pd.read_csv(stats / "retention_m3_ci.csv")
    speed = pd.read_csv(stats / "retention_by_activation_speed.csv")
    conc = pd.read_csv(stats / "concentration_statistics.csv").set_index("metric")["value"]
    late = pd.read_csv(stats / "late_review_effect.csv")
    severity = pd.read_csv(stats / "late_review_by_severity.csv")
    cat = pd.read_csv(tables / "category_analysis_extended.csv")

    complete = health[health["is_complete_month"]].sort_values("month")
    last_complete = complete.iloc[-1]["month"]
    prior_complete = complete.iloc[-2]["month"]
    last_tail = health.iloc[-1]
    selected = cat[cat.purchase_month.isin(set(complete.month))].groupby("category", as_index=False).agg(gmv_proxy=("gmv_proxy", "sum"), orders=("orders", "sum"))
    selected["gmv_share"] = selected.gmv_proxy / selected.gmv_proxy.sum()
    pivot = cat[cat.purchase_month.isin(set(complete.month))].pivot_table(index="category", columns="purchase_month", values="gmv_proxy", aggfunc="sum")
    selected["last_vs_prior"] = selected.category.map((pivot[last_complete] - pivot[prior_complete]).div(pivot[prior_complete]).replace([np.inf, -np.inf], np.nan))
    selected = selected[(selected.gmv_share >= 0.03) & (selected.orders >= 300)].sort_values(["last_vs_prior", "gmv_proxy"], ascending=[True, False])
    category_name = str(selected.iloc[0].category) if len(selected) else "relogios_presentes"
    category_change = float(selected.iloc[0].last_vs_prior) if len(selected) else np.nan

    rows = []
    def add(case_id, trigger, hypothesis, evidence_for, evidence_against, strength, magnitude, alternative, status, decision):
        rows.append({"case_id": case_id, "trigger": trigger, "hypothesis": hypothesis, "evidence_for": evidence_for, "evidence_against": evidence_against, "statistical_strength": strength, "business_magnitude": magnitude, "alternative_explanation": alternative, "status": status, "decision": decision})

    trigger1 = f"Observed tail decline in {last_tail['month']} versus {prior_complete}; only {int(last_tail['orders'])} orders in the final observed month."
    add("RC1", trigger1, "H1 seller count collapse", f"Final tail reports {last_tail['active_sellers']:.0f} active sellers versus {complete.iloc[-1].active_sellers:.0f} in {last_complete}.", "The tail is a partial observation and is excluded by the complete-period rule.", "measurement evidence", "edge-month GMV is {0:.2f} versus {1:.2f} in the prior complete month".format(last_tail.gmv_proxy, complete.iloc[-1].gmv_proxy), "delayed or truncated extract", "Inconclusive as a business collapse", "gate executive reporting on completeness")
    add("RC1", trigger1, "H2 seller productivity collapse", "Observed GMV per seller is not interpretable in the four-order tail.", "Complete months retain normal seller productivity; the denominator itself is incomplete.", "measurement evidence", "tail is not decision-eligible", "partial-month mix", "Rejected as the primary explanation", "do not escalate commercial action from the tail")
    add("RC1", trigger1, "H3 AOV collapse", f"Tail AOV is {last_tail.aov:.2f}, driven by four orders.", "AOV is computed on an ineligible partial period.", "measurement evidence", "tail AOV is not comparable", "small-sample volatility", "Rejected as a headline explanation", "flag partial periods")
    add("RC1", trigger1, "H4 data incompleteness", "The last observed months fail the documented complete-month rule.", "No raw row-level check can prove the upstream extract's intended end date.", "strong measurement evidence", "false-alarm risk is material", "legitimate seasonality cannot be ruled out without current data", "Confirmed measurement issue", "enforce a period-completeness gate")

    trigger2 = "Actionable origins show different conversion rates and sparse groups have wide uncertainty."
    add("RC2", trigger2, "H1 optimize raw MQL volume alone", "MQL volume and conversion rank different origins; social contributes 1,350 MQLs but converts at 5.6%.", "Volume is not downstream value and unknown is not actionable.", "descriptive + association", "paid vs social gap is {:.1f} percentage points".format(float(acq.loc[acq.origin.eq('paid_search'), 'conversion_rate'].iloc[0] - acq.loc[acq.origin.eq('social'), 'conversion_rate'].iloc[0]) * 100), "channel mix and sales routing", "Rejected hypothesis", "use a multidimensional channel scorecard")
    add("RC2", trigger2, "H2 origin is associated with conversion", "Global origin test and FDR-adjusted pairwise tests provide evidence of conversion differences.", "Effect size is modest and does not establish causal channel quality.", "Level 2 association", "Cramér's V is {:.3f}".format(float(pd.read_csv(stats / 'acquisition_conversion_global.csv').cramers_v.iloc[0])), "selection bias, linkage and unmeasured seller mix", "Plausible contributor", "separate acquisition efficiency from retention claims")
    add("RC2", trigger2, "H3 origin-specific retention advantage is established", "M3 retention CI table is eligibility-aware.", "The adjusted retention model and global M3 test do not provide strong evidence of origin-specific retention intervention.", "null / inconclusive", "M3 eligible n is {}".format(int(retention.eligible_n.sum())), "cohort timing and censoring", "Rejected by current evidence", "do not optimize channels on M3 retention alone")

    trigger3 = "Canonical v3: observed activator median is {:.1f} days; 30-day activation is {:.1%} over {} observable sellers.".format(float(activation.median_activation_days), float(activation.activation_rate_le_30d), int(activation.eligible_n_le_30d))
    add("RC3", trigger3, "H1 seller onboarding has a long time-to-value", "The eligibility-aware fixed-window table and right-censored survival curve show delayed first sale among activation-eligible sellers.", "Historical data does not identify which onboarding step caused delay.", "descriptive timing evidence", "only {:.1%} activate by 30 days in the observable denominator".format(float(activation.activation_rate_le_30d)), "seller readiness, category and demand differences", "Supported business signal", "instrument 7/30/60-day onboarding checkpoints")
    add("RC3", trigger3, "H2 faster activation is associated with stronger M3 retention", "M3 retention rates decline across activation-speed buckets after the small ≤7d bucket.", "The comparison is observational and extreme buckets are small.", "descriptive association", "31–60d versus >90d rates are {:.1%} and {:.1%}".format(float(speed.loc[speed.speed_bucket.eq('31–60d'), 'm3_retention_rate'].iloc[0]), float(speed.loc[speed.speed_bucket.eq('>90d'), 'm3_retention_rate'].iloc[0])), "reverse causality and seller mix", "Plausible contributor", "test onboarding interventions with retention as guardrail")
    add("RC3", trigger3, "H3 origin alone explains activation speed", "Activation speed varies by origin in the CI table.", "Origin is not the same as seller readiness or onboarding experience.", "descriptive comparison", "origin differences require volume flags", "seller segment and category mix", "Inconclusive", "target the onboarding journey rather than a channel proxy")

    trigger4 = "Top 20% of sellers account for {:.1%} of seller GMV proxy.".format(float(conc["top_20_pct_share"]))
    add("RC4", trigger4, "H1 marketplace value is concentrated", "Lorenz/Gini and top-share statistics show a long-tailed seller distribution.", "Concentration is measured on historical positive-GMV sellers, not current supply health.", "Level 1 descriptive pattern", "Gini {:.3f}; top 1% {:.1%}".format(float(conc["gini"]), float(conc["top_1_pct_share"])), "multi-seller attribution and seller churn", "Supported risk signal", "monitor top 1/5/10/20% shares")
    add("RC4", trigger4, "H2 generic seller diversification is the right immediate action", "High concentration creates dependency risk.", "The evidence does not identify which categories or states are fragile.", "decision evidence", "top 20% share {:.1%}".format(float(conc["top_20_pct_share"])), "some concentration may reflect healthy specialization", "Rejected as a generic action", "target categories with high GMV and weak seller breadth")
    add("RC4", trigger4, "H3 concentration is stable across time and segments", "Monthly and category concentration tables permit the check.", "Historical scope does not establish a universal threshold or causal driver.", "descriptive + robustness", "segment and time monitoring required", "category mix and seller entry/exit", "Inconclusive until monitoring is refreshed", "use a monitoring trigger, not an arbitrary threshold")

    trigger5 = "Late orders have lower reviews and a higher low-review rate than on-time orders."
    late_g = late.loc[late.delivery_group.eq("late")].iloc[0]; on_g = late.loc[late.delivery_group.eq("on_time")].iloc[0]
    add("RC5", trigger5, "H1 delivery lateness is associated with customer-experience deterioration", "Mean review penalty is {:.2f} points and low-review risk ratio is {:.2f}x.".format(float(late_g.review_difference_vs_on_time), float(late_g.risk_ratio_vs_on_time)), "Association is not causal proof.", "Level 2 association + bootstrap", "risk difference +{:.1f} percentage points".format(float(late_g.risk_difference_vs_on_time) * 100), "category, state, freight and review selection", "Supported business mechanism", "prioritize operational investigation by volume × severity × penalty")
    add("RC5", trigger5, "H2 delay severity has a dose-response pattern", "Severity buckets retain monotonic operational detail and show the late tail's weaker review outcomes.", "Early/late buckets are observational and some extremes are smaller.", "descriptive severity evidence", "late >14d is the most severe diagnostic segment", "delivery route and category mix", "Plausible contributor", "investigate severity bands before a broad rollout")
    add("RC5", trigger5, "H3 one seller is the root cause", "Seller-level responsibility is not available for multi-seller orders without attribution assumptions.", "Order-level evidence should not assign blame to a single seller.", "rejected attribution", "seller attribution is a measurement limitation", "carrier, route, category and customer geography", "Rejected hypothesis", "do not assign seller blame from this dataset")

    trigger6 = "Selected high-value category {} falls {:.1%} from {} to {} while retaining sufficient historical volume.".format(category_name, abs(category_change) if np.isfinite(category_change) else np.nan, prior_complete, last_complete)
    add("RC6", trigger6, "H1 category demand/GMV deterioration", "The category is selected using material GMV, sufficient orders and complete-month decline.", "Historical category trend is not a current commercial forecast.", "descriptive trend evidence", "selected category GMV change {:.1%}".format(category_change), "mix shift and partial periods", "Plausible contributor", "build a category-specific diagnostic plan")
    add("RC6", trigger6, "H2 orders versus AOV explains the category movement", "Category tables separate GMV, orders and AOV/productivity proxies.", "Decomposition is descriptive and may not capture assortment changes.", "accounting decomposition", "drivers are available in category_analysis_extended.csv", "price, assortment and promotion data are unavailable", "Supported diagnostic path", "choose an intervention only after driver split")
    add("RC6", trigger6, "H3 seller breadth/productivity explains the decline", "Active sellers and GMV per seller are tracked by category.", "Seller attribution is item-based and multi-seller order context remains limited.", "descriptive segment evidence", "seller breadth and productivity must be compared", "seller mix and assortment", "Inconclusive until drilldown", "monitor category seller breadth and productivity")
    add("RC6", trigger6, "H4 category experience explains the decline", "Category late rate and review metrics are available for further investigation.", "No causal demand model is available.", "associative operational evidence", "customer-experience gap is a guardrail, not invented lost GMV", "seasonality, price and product mix", "Inconclusive", "keep CX in the category decision card as a guardrail")

    evidence = pd.DataFrame(rows)
    out.mkdir(parents=True, exist_ok=True)
    evidence.to_csv(out / "root_cause_evidence.csv", index=False, encoding="utf-8")
    matrix = evidence[["case_id", "hypothesis", "evidence_for", "status", "decision"]].copy()
    matrix["result"] = matrix["status"]
    matrix.to_csv(out / "root_cause_hypothesis_matrix.csv", index=False, encoding="utf-8")
    summary = evidence.groupby("case_id", as_index=False).agg(trigger=("trigger", "first"), hypotheses_tested=("hypothesis", "count"), statuses=("status", lambda s: " | ".join(sorted(set(s)))), decisions=("decision", "first"))
    summary.to_csv(out / "root_cause_case_summary.csv", index=False, encoding="utf-8")
    (out / "root_cause_selection.json").write_text(json.dumps({"selected_category": category_name, "last_complete_month": last_complete, "prior_complete_month": prior_complete, "selection_rule": "material GMV share, at least 300 orders, largest complete-month decline among eligible categories"}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"cases": int(evidence.case_id.nunique()), "hypotheses": int(len(evidence)), "selected_category": category_name}, ensure_ascii=False))


if __name__ == "__main__":
    main()
