"""Inventory and validate the two source ZIP archives.

This command never copies raw data into Git. Use OLIST_RAW_DIR to point to the
Drive-materialized raw ZIPs and OLIST_PROJECT_DIR for generated artifacts.
"""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import pandas as pd
try:
    from .utils.io import zip_csv_members
    from .utils.logging import configure_logging
except ImportError:
    from utils.io import zip_csv_members
    from utils.logging import configure_logging


def inventory(raw_dir: Path, output: Path) -> pd.DataFrame:
    rows = []
    for path in sorted(raw_dir.glob("*.zip")):
        members = zip_csv_members(path)
        rows.append({"archive": path.name, "bytes": path.stat().st_size, "csv_members": len(members), "members": ";".join(members)})
    result = pd.DataFrame(rows)
    result.to_csv(output, index=False)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", default=os.getenv("OLIST_RAW_DIR", "data/raw"))
    parser.add_argument("--project-dir", default=os.getenv("OLIST_PROJECT_DIR", "."))
    args = parser.parse_args()
    project = Path(args.project_dir)
    logger = configure_logging(project / "reports/qa/pipeline_run.log")
    result = inventory(Path(args.raw_dir), project / "reports/qa/raw_inventory.csv")
    logger.info("input archives=%s rows=%s", len(result), len(result))


if __name__ == "__main__":
    main()
