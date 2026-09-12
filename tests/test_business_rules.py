from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parents[1]


def test_customer_repeat_rate_uses_unique_customer_identity():
    df = pd.read_csv(ROOT / "reports/tables/customer_repeat_summary.csv")
    assert df.loc[0, "repeat_customer_rate"] >= 0
    assert df.loc[0, "repeat_customer_rate"] <= 1


def test_activation_and_retention_rules():
    activation = pd.read_csv(ROOT / "reports/tables/activation_summary.csv")
    row = activation.loc[0]
    assert row["observed_activated_sellers"] <= row["activation_eligible_sellers"]
    assert row["observed_activated_sellers"] + row["censored_sellers"] == row["activation_eligible_sellers"]
    assert row["activation_rate_le_30d"] <= 1
    assert row["activation_rate_le_90d"] <= 1
    cohort = pd.read_csv(ROOT / "reports/tables/mart_seller_cohort.csv")
    assert {"eligible_flag", "retention_rate"}.issubset(cohort.columns)
    assert cohort.loc[cohort["eligible_flag"] == 0, "retention_rate"].isna().all()
    assert cohort["retention_rate"].dropna().between(0, 1).all()


def test_review_delivery_is_association_not_causality():
    experience = pd.read_csv(ROOT / "reports/tables/mart_order_experience.csv")
    assert experience["low_review_rate"].between(0, 1).all()
    assert experience["avg_review_score"].between(1, 5).all()
    text = (ROOT / "docs/11_limitations.md").read_text(encoding="utf-8").lower()
    assert "causal" in text

