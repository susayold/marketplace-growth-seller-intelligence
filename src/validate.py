"""Automated release checks over generated QA and mart outputs."""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd


def run_checks(project: Path) -> list[str]:
    errors: list[str] = []
    qa = project / "reports/qa"
    fanout = pd.read_csv(qa / "fanout_audit.csv")
    if fanout.empty or fanout.iloc[0]["fanout_difference"] <= 0:
        errors.append("fan-out audit did not demonstrate the expected risk")
    monthly = pd.read_csv(project / "reports/tables/mart_marketplace_monthly.csv")
    if (monthly["orders"] < 0).any() or (monthly["gmv_proxy"] < 0).any():
        errors.append("monthly mart contains negative measures")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", default=".")
    args = parser.parse_args()
    errors = run_checks(Path(args.project_dir))
    if errors:
        raise SystemExit("; ".join(errors))
    print("validation passed")


if __name__ == "__main__":
    main()

