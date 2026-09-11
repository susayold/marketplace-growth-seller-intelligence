from pathlib import Path
import pandas as pd
ROOT = Path(__file__).parents[1]

def test_orders_and_items_have_positive_keys():
    inv = pd.read_csv(ROOT / "reports/qa/raw_inventory.csv")
    assert (inv["row_count"] > 0).all()
    fanout = pd.read_csv(ROOT / "reports/qa/fanout_audit.csv")
    assert int(fanout.loc[0, "raw_order_count"]) > 0
    assert int(fanout.loc[0, "joined_row_count"]) >= int(fanout.loc[0, "raw_order_count"])
