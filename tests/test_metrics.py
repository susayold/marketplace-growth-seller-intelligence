from pathlib import Path
import pandas as pd
ROOT = Path(__file__).parents[1]

def test_metric_outputs_are_non_negative_and_bounded():
    monthly = pd.read_csv(ROOT / "reports/tables/mart_marketplace_monthly.csv")
    assert (monthly["orders"] >= 0).all()
    assert (monthly["gmv_proxy"] >= 0).all()
    activation = pd.read_csv(ROOT / "reports/tables/activation_summary.csv")
    assert activation["activation_rate_any_sale"].between(0, 1).all()
    assert activation["activation_within_90d"].between(0, 1).all()

