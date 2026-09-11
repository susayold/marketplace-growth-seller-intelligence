"""Run compact schema, missingness and cardinality profiling on source ZIPs."""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import pandas as pd
try:
    from .utils.io import read_zip_csv, zip_csv_members
except ImportError:
    from utils.io import read_zip_csv, zip_csv_members


def profile_zip(zip_path: Path) -> pd.DataFrame:
    rows = []
    for member in zip_csv_members(zip_path):
        df = read_zip_csv(zip_path, member)
        for column in df.columns:
            rows.append({"archive": zip_path.name, "table": Path(member).stem, "column": column, "rows": len(df), "null_rate": float(df[column].isna().mean()), "distinct": int(df[column].nunique(dropna=True)), "dtype": str(df[column].dtype)})
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", default=os.getenv("OLIST_RAW_DIR", "data/raw"))
    parser.add_argument("--project-dir", default=os.getenv("OLIST_PROJECT_DIR", "."))
    args = parser.parse_args()
    raw_dir, project = Path(args.raw_dir), Path(args.project_dir)
    frames = [profile_zip(path) for path in sorted(raw_dir.glob("*.zip"))]
    pd.concat(frames, ignore_index=True).to_csv(project / "reports/qa/data_profile_summary.csv", index=False)


if __name__ == "__main__":
    main()
