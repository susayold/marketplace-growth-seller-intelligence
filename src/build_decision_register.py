"""Build decision cards from the reviewed statistical and root-cause evidence."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd


def main() -> None:
    project = Path(os.environ.get("OLIST_PROJECT_DIR", "."))
    stats = project / "reports" / "statistics"
    root = project / "reports"
    acq = pd.read_csv(stats / "acquisition_conversion_global.csv").iloc[0]
    late = pd.read_csv(stats / "late_review_effect.csv")
    late_g = late.loc[late.delivery_group.eq("late")].iloc[0]
    conc = pd.read_csv(stats / "concentration_statistics.csv").set_index("metric")["value"]
    act = pd.read_csv(stats / "activation_summary_extended.csv").iloc[0]
    selected = pd.read_json(root / "root_cause_selection.json", typ="series")
    category = selected.get("selected_category", "selected high-value category")
    cards = [
        {"decision_id": "D01", "problem": "Partial periods can create false executive trend alarms.", "finding": "RC1 confirms the final observed tail is not decision-eligible under the complete-month rule.", "evidence_level": "LEVEL 0 — confirmed measurement issue", "confidence": "HIGH", "target_scope": "all executive marketplace reporting periods", "recommended_action": "Exclude or visibly flag incomplete periods before reporting a trend.", "why_this_action": "The measurement boundary can mimic a commercial collapse; the gate is reversible and low-risk.", "primary_kpi": "period completeness", "guardrail_kpi": "no valid complete period suppressed", "owner_role": "Data / BI", "review_frequency": "daily", "stop_condition": "stop the reporting refresh when completeness metadata is missing or fails threshold", "limitation": "The historical extract does not prove the upstream source's intended end date.", "evidence_strength": 3, "actionability": 3, "scope_size": "all periods", "priority_band": "P1"},
        {"decision_id": "D02", "problem": "Channel volume alone does not identify the best seller-acquisition motion.", "finding": "Origin is associated with conversion (Cramér's V {:.3f}), while M3 retention evidence is inconclusive.".format(float(acq.cramers_v)), "evidence_level": "LEVEL 2 — association", "confidence": "MEDIUM", "target_scope": "actionable origins with sufficient MQL volume", "recommended_action": "Govern channels with a scorecard covering MQL volume, conversion, matched-seller value, activation and M3 retention as a guardrail.", "why_this_action": "It prevents over-optimizing a single funnel rate and keeps unknown/sparse origins out of false rankings.", "primary_kpi": "conversion + downstream GMV per matched seller", "guardrail_kpi": "M3 retention", "owner_role": "Seller Acquisition", "review_frequency": "weekly", "stop_condition": "do not scale a channel when volume is below the sample policy or value/retention evidence is missing", "limitation": "No CAC/ROAS and no causal channel assignment are available.", "evidence_strength": 2, "actionability": 2, "scope_size": "8,000 MQLs", "priority_band": "P1"},
        {"decision_id": "D03", "problem": "Seller time-to-value is slow after conversion.", "finding": "Only {:.1%} of valid linked sellers activate within 30 days; median first sale is {:.0f} days.".format(float(act.activation_rate_le_30d), float(act.median_days_to_first_sale)), "evidence_level": "LEVEL 1 — descriptive timing signal", "confidence": "MEDIUM", "target_scope": "valid linked closed sellers", "recommended_action": "Instrument onboarding checkpoints at 7, 30 and 60 days and test interventions rather than assuming a causal fix.", "why_this_action": "The delay is large enough to monitor; the intervention should be evaluated against retention and downstream value.", "primary_kpi": "30/60-day activation and median days-to-first-sale", "guardrail_kpi": "M3 retention and downstream GMV", "owner_role": "Seller Operations", "review_frequency": "weekly", "stop_condition": "stop or redesign an onboarding change if activation improves while retention/value deteriorates", "limitation": "Seller readiness, category mix and demand are not fully observed.", "evidence_strength": 2, "actionability": 2, "scope_size": "327 valid activation links", "priority_band": "P1"},
        {"decision_id": "D04", "problem": "GMV dependence on a small seller cohort creates concentration risk.", "finding": "The top 20% of positive-GMV sellers account for {:.1%} of seller GMV proxy; Gini is {:.3f}.".format(float(conc["top_20_pct_share"]), float(conc["gini"])), "evidence_level": "LEVEL 1 — descriptive concentration", "confidence": "MEDIUM", "target_scope": "marketplace sellers and high-value categories", "recommended_action": "Monitor top 1/5/10/20% shares and investigate categories where high value combines with weak seller breadth.", "why_this_action": "Concentration is a risk signal, but a universal diversification threshold would be arbitrary.", "primary_kpi": "top 1/5/10/20% seller GMV share", "guardrail_kpi": "active sellers per high-value category", "owner_role": "Commercial Analytics", "review_frequency": "monthly", "stop_condition": "escalate only when concentration rises materially and category breadth is fragile", "limitation": "Seller attribution and historical scope limit current supply-risk inference.", "evidence_strength": 2, "actionability": 2, "scope_size": "R$13.59M GMV proxy", "priority_band": "P2"},
        {"decision_id": "D05", "problem": "Late delivery is associated with materially weaker customer experience.", "finding": "Late orders show a {:.2f}-point lower mean review and a {:.1f}pp higher low-review rate.".format(float(late_g.review_difference_vs_on_time), float(late_g.risk_difference_vs_on_time) * 100), "evidence_level": "LEVEL 2 — association with bootstrap CI", "confidence": "HIGH", "target_scope": "delivered orders with observed reviews; prioritize high-volume segments", "recommended_action": "Prioritize delivery investigations using order volume × delay severity × review penalty, then test operational changes.", "why_this_action": "The effect is large and actionable, but the dataset cannot assign causality to one seller or carrier.", "primary_kpi": "late-delivery rate", "guardrail_kpi": "review score / low-review rate and cost if available", "owner_role": "Customer Experience", "review_frequency": "daily operations; weekly review", "stop_condition": "do not roll out a broad fix when the effect disappears under segment or robustness checks", "limitation": "Observational evidence, review selection and multi-seller orders limit causal attribution.", "evidence_strength": 3, "actionability": 3, "scope_size": "95,830 reviewed delivered orders in adjusted model", "priority_band": "P1"},
    ]
    df = pd.DataFrame(cards)
    root.mkdir(parents=True, exist_ok=True)
    df.to_csv(root / "decision_register.csv", index=False, encoding="utf-8")
    priority = df[["decision_id", "problem", "confidence", "evidence_level", "target_scope", "evidence_strength", "actionability", "scope_size", "priority_band"]].copy()
    priority["matrix_note"] = "position evidence strength vs actionability; scope shown as bubble label, not a fabricated composite score"
    priority.to_csv(root / "decision_priority.csv", index=False, encoding="utf-8")
    print({"decision_cards": len(df), "priority_bands": df.priority_band.value_counts().to_dict()})


if __name__ == "__main__":
    main()
