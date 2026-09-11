from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parents[1]


def test_monthly_mart_dates_are_sorted_and_unique():
    df = pd.read_csv(ROOT / "reports/tables/mart_marketplace_monthly.csv", parse_dates=["purchase_month"])
    assert df["purchase_month"].is_monotonic_increasing
    assert df["purchase_month"].is_unique
    assert df["purchase_month"].notna().all()


def test_profiled_date_ranges_are_valid():
    df = pd.read_csv(ROOT / "reports/qa/raw_inventory.csv")
    dated = df.dropna(subset=["date_min", "date_max"]).copy()
    assert (pd.to_datetime(dated["date_min"]) <= pd.to_datetime(dated["date_max"])).all()

