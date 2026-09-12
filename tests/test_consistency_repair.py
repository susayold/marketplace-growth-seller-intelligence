import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).parents[1]


def test_activation_population_reconciliation():
    d = pd.read_csv(ROOT / "reports" / "tables" / "seller_activation_timing.csv")
    assert len(d) == 840
    assert d.activation_event.sum() == 380
    assert d.censored.sum() == 460
    assert d.activation_event.sum() + d.censored.sum() == len(d)


def test_activation_fixed_window_observability():
    d = pd.read_csv(ROOT / "reports" / "statistics" / "activation_fixed_window.csv")
    assert d.window_days.tolist() == [7, 30, 60, 90]
    assert d.eligible_n.tolist() == sorted(d.eligible_n.tolist(), reverse=True)
    assert (d.activated_n <= d.eligible_n).all()
    assert (d.activation_rate >= 0).all() and (d.activation_rate <= 1).all()


def test_activation_metric_version():
    d = pd.read_csv(ROOT / "reports" / "statistics" / "activation_summary_extended.csv").iloc[0]
    assert d.metric_version == "v3"
    assert d.observed_activated_sellers == 380


def test_retention_cell_support():
    cells = pd.read_csv(ROOT / "reports" / "statistics" / "retention_cohort_outcome_cells.csv")
    pooled = cells[cells.origin == "__ALL__"]
    assert len(pooled) > 0
    assert (pooled.eligible_n == pooled.retained_n + pooled.not_retained_n).all()
    assert (pooled.sample_size_flag != "insufficient").any()


def test_retention_headline_no_separation():
    d = pd.read_csv(ROOT / "reports" / "statistics" / "retention_model_diagnostics.csv")
    headline = d[d.model_id == "R2_origin_plus_pooled_cohort"]
    assert len(headline) == 1
    assert bool(headline.separation_flag.iloc[0]) is False


def test_retention_model_population_reconciliation():
    d = pd.read_csv(ROOT / "reports" / "statistics" / "retention_model_comparison.csv")
    assert set(d.model_id) >= {"R1_origin_only", "R2_origin_plus_pooled_cohort", "R3_major_actionable_plus_pooled_cohort"}
    assert d[d.model_id == "R2_origin_plus_pooled_cohort"].n.iloc[0] == 265


def test_reporting_boundary_contract():
    d = pd.read_csv(ROOT / "reports" / "qa" / "reporting_boundary_register.csv")
    orders = d[d.domain == "orders"].iloc[0]
    assert pd.Timestamp(orders.last_complete_period) <= pd.Timestamp(orders.analytical_last_date)
    assert pd.Timestamp(orders.analytical_last_date) <= pd.Timestamp(orders.raw_last_date)


def test_complete_period_subset():
    d = pd.read_csv(ROOT / "reports" / "qa" / "period_completeness.csv")
    complete = d[d.is_executive_complete]
    assert (~complete.is_edge_month).all()
    assert complete.volume_flag.all()
    assert complete.coverage_flag.all()


def test_headline_metric_consistency():
    summary = pd.read_csv(ROOT / "reports" / "statistics" / "activation_summary_extended.csv").iloc[0]
    headline = json.loads((ROOT / "reports" / "headline_metrics.json").read_text(encoding="utf-8"))
    assert headline["metric_version"] == "v3"
    assert np.isclose(headline["activation_30d"], summary.activation_rate_le_30d)
    assert np.isclose(headline["activation_60d"], summary.activation_rate_le_60d)
    assert np.isclose(headline["activation_90d"], summary.activation_rate_le_90d)


def test_claim_reconciliation():
    d = pd.read_csv(ROOT / "reports" / "qa" / "headline_claim_reconciliation.csv")
    assert len(d) >= 6
    assert (d.status == "PASS").all()
