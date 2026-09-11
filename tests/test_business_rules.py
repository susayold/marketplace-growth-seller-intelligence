from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def test_core_outputs_exist():
    assert (ROOT / "reports" / "qa" / "fanout_audit.csv").exists()
    assert (ROOT / "reports" / "tables" / "mart_marketplace_monthly.csv").exists()


def test_metric_ranges():
    cohort = pd.read_csv(ROOT / "reports" / "tables" / "mart_seller_cohort.csv")
    assert cohort["retention_rate"].dropna().between(0, 1).all()
    experience = pd.read_csv(ROOT / "reports" / "tables" / "mart_order_experience.csv")
    assert experience["low_review_rate"].between(0, 1).all()

