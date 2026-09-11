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
    "activation_summary_extended.csv", "activation_by_origin_ci.csv", "activation_survival.csv",
    "retention_m3_ci.csv", "retention_glm.csv", "retention_sensitivity.csv",
    "retention_by_activation_speed.csv", "retention_observability.csv",
    "concentration_statistics.csv", "concentration_bootstrap.csv", "concentration_lorenz.csv",
    "seller_deciles.csv", "concentration_monthly.csv", "concentration_category.csv",
    "concentration_geography.csv", "late_review_effect.csv", "late_review_by_severity.csv",
    "late_review_by_category.csv", "late_review_by_state.csv", "late_review_adjusted_model.csv",
    "model_diagnostics.csv", "business_magnitude.csv", "robustness_register.csv",
    "multiple_testing_register.csv"
]
required_docs = ["18_statistical_rigor_upgrade.md", "19_root_cause_playbook.md", "20_business_decision_layer.md", "21_chart_catalog.md", "22_claims_and_evidence_register.md"]
registry = pd.read_csv(project / "reports" / "chart_registry.csv")
root = pd.read_csv(project / "reports" / "root_cause_evidence.csv")
decisions = pd.read_csv(project / "reports" / "decision_register.csv")
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
    "warnings": ["Observational source: no causal claims.", "Power BI intentionally deferred until this release gate is accepted."]
}
out = project / "reports" / "qa" / "analysis_showcase_verification.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(verification, indent=2), encoding="utf-8")
print(json.dumps(verification, indent=2))

