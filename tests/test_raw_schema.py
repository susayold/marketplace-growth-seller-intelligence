from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parents[1]

def test_raw_inventory_has_both_archives():
    df = pd.read_csv(ROOT / "reports/qa/raw_inventory.csv")
    assert {"olist_orders_dataset", "marketing_qualified_leads_olist"}.issubset(set(df["table_name"]))

def test_profile_has_required_columns():
    df = pd.read_csv(ROOT / "reports/qa/data_profile_summary.csv")
    assert {"table_name", "column_name", "dtype", "row_count", "null_pct", "distinct_count"}.issubset(df.columns)
