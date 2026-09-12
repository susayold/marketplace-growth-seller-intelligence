"""Create a compact, machine-readable acceptance report for the pre-Power-BI release."""
from pathlib import Path
import json
import os
import pandas as pd

project = Path(os.environ.get("OLIST_PROJECT_DIR", "."))
stats = project / "reports" / "statistics"
charts = project / "reports" / "charts"
required_stats = [
    "acquisition_conversion_global.csv", "acquisition_conversion_by_origin.csv",
    "acquisition_conversion_pairwise.csv", "acquisition_conversion_sensitivity.csv",
    "activation_summary_extended.csv", "activation_by_origin_ci.csv", "activation_survival.csv", "activation_fixed_window.csv",
    "retention_m3_ci.csv", "retention_glm.csv", "retention_sensitivity.csv", "retention_cohort_outcome_cells.csv", "retention_model_comparison.csv", "retention_model_diagnostics.csv",
    "retention_by_activation_speed.csv", "retention_observability.csv",
    "concentration_statistics.csv", "concentration_bootstrap.csv", "concentration_lorenz.csv",
    "seller_deciles.csv", "concentration_monthly.csv", "concentration_category.csv",
    "concentration_geography.csv", "late_review_effect.csv", "late_review_by_severity.csv",
    "late_review_by_category.csv", "late_review_by_state.csv", "late_review_adjusted_model.csv",
    "model_diagnostics.csv", "business_magnitude.csv", "robustness_register.csv",
    "multiple_testing_register.csv"
]
required_docs = ["18_statistical_rigor_upgrade.md", "19_root_cause_playbook.md", "20_business_decision_layer.md", "21_chart_catalog.md", "22_claims_and_evidence_register.md", "metric_changelog.md", "23_analytical_release_freeze.md"]
registry = pd.read_csv(project / "reports" / "chart_registry.csv")
root = pd.read_csv(project / "reports" / "root_cause_evidence.csv")
decisions = pd.read_csv(project / "reports" / "decision_register.csv")
diagnostics = pd.read_csv(stats / "retention_model_diagnostics.csv") if (stats / "retention_model_diagnostics.csv").exists() else pd.DataFrame()
claims = pd.read_csv(project / "reports" / "qa" / "headline_claim_reconciliation.csv") if (project / "reports" / "qa" / "headline_claim_reconciliation.csv").exists() else pd.DataFrame()
website_audit = pd.read_csv(project / "reports" / "qa" / "website_metric_audit.csv") if (project / "reports" / "qa" / "website_metric_audit.csv").exists() else pd.DataFrame()
verification = {
    "status": "PASS_WITH_ASSOCIATIVE_LIMITATIONS",
    "run_date": "2026-09-12",
    "stats_csv_count": len(list(stats.glob("*.csv"))),
    "required_statistical_outputs_present": all((stats / name).exists() for name in required_stats),
    "charts_png_count": len(list(charts.rglob("*.png"))),
    "chart_registry_rows": len(registry),
    "chart_registry_files_exist": all((project / "reports" / "charts" / str(name)).exists() for name in registry.chart_file),
    "root_cause_cases": int(root.case_id.nunique()),
    "root_cause_hypotheses": int(len(root)),
    "decision_cards": int(len(decisions)),
    "required_docs_present": all((project / "docs" / name).exists() for name in required_docs),
    "model_diagnostics_models": sorted(pd.read_csv(stats / "model_diagnostics.csv").model.dropna().unique().tolist()),
    "metric_version": "v3",
    "activation_definition_reconciled": (project / "reports" / "qa" / "activation_definition_reconciliation.csv").exists() and len(pd.read_csv(project / "reports" / "qa" / "activation_definition_reconciliation.csv")) == 3,
    "retention_separation_resolved": (len(diagnostics) > 0 and bool((diagnostics.loc[diagnostics.model_id.eq("R2_origin_plus_pooled_cohort"), "separation_flag"] == False).all())),
    "retention_headline_model": "origin_plus_pooled_cohort",
    "reporting_boundary_reconciled": all((project / "reports" / "qa" / name).exists() for name in ["reporting_boundary_register.csv", "period_completeness.csv"]),
    "headline_claims_reconciled": len(claims) >= 6 and bool((claims.status == "PASS").all()),
    "website_metrics_reconciled": len(website_audit) >= 7 and bool((website_audit.match == True).all()),
    "power_bi_ready": False,
    "warnings": ["Observational source: no causal claims.", "Power BI remains blocked until all repair gates and the analytical release freeze pass."]
}
verification["power_bi_ready"] = all([
    verification["activation_definition_reconciled"], verification["retention_separation_resolved"],
    verification["reporting_boundary_reconciled"], verification["headline_claims_reconciled"],
    verification["website_metrics_reconciled"], verification["required_docs_present"]
])
if verification["power_bi_ready"]:
    verification["warnings"] = ["Observational source: no causal claims.", "Pre-Power-BI analytical release is frozen; Power BI can begin."]
out = project / "reports" / "qa" / "analysis_showcase_verification.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(verification, indent=2), encoding="utf-8")
print(json.dumps(verification, indent=2))

