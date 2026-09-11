from pathlib import Path
import pandas as pd
ROOT = Path(__file__).parents[1]

def test_fanout_is_detected_and_grain_safe_value_is_preserved():
    df = pd.read_csv(ROOT / "reports/qa/fanout_audit.csv")
    row = df.iloc[0]
    assert row["fanout_difference"] > 0
    assert row["fanout_multiple"] > 1
    assert row["grain_safe_item_gmv"] > 0
