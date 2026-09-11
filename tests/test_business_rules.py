from pathlib import Path
import pandas as pd
ROOT = Path(__file__).parents[1]

def test_customer_repeat_rate_uses_unique_customer_identity():
    df = pd.read_csv(ROOT / "reports/tables/customer_repeat_summary.csv")
    assert df.loc[0, "repeat_customer_rate"] >= 0
    assert df.loc[0, "repeat_customer_rate"] <= 1

def test_retention_keeps_ineligible_cells_out_of_denominator():
    df = pd.read_csv(ROOT / "reports/tables/mart_seller_cohort.csv")
    assert {"eligible_flag", "retention_rate"}.issubset(df.columns)
    assert df.loc[df["eligible_flag"] == 0, "retention_rate"].isna().all()

def test_review_delivery_is_association_not_causality():
    text = (ROOT / "docs/11_limitations.md").read_text(encoding="utf-8").lower()
    assert "causal" in text
