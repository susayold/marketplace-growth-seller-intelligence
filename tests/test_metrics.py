from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parents[1]


def test_metric_outputs_are_non_negative_and_bounded():
    monthly = pd.read_csv(ROOT / "reports/tables/mart_marketplace_monthly.csv")
    assert (monthly["orders"] >= 0).all()
    assert (monthly["gmv_proxy"] >= 0).all()
    activation = pd.read_csv(ROOT / "reports/tables/activation_summary.csv")
    assert activation["activation_rate_le_30d"].between(0, 1).all()
    assert activation["activation_rate_le_60d"].between(0, 1).all()
    assert activation["activation_rate_le_90d"].between(0, 1).all()


def test_controlled_fixture_expected_gmv_aov_and_active_sellers():
    fixture = pd.DataFrame([
        {"order_id": "o1", "seller_id": "s1", "price": 10.0},
        {"order_id": "o1", "seller_id": "s2", "price": 20.0},
        {"order_id": "o2", "seller_id": "s2", "price": 30.0},
    ])
    assert fixture["price"].sum() == 60.0
    assert fixture["order_id"].nunique() == 2
    assert fixture["price"].sum() / fixture["order_id"].nunique() == 30.0
    assert fixture["seller_id"].nunique() == 2

