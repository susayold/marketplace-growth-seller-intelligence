"""Reconcile grain-safe measures and record a machine-readable result."""
from __future__ import annotations
import argparse
from pathlib import Path
import json
import pandas as pd


def reconcile(project: Path) -> dict:
    qa = pd.read_csv(project / "reports/qa/fanout_audit.csv").iloc[0]
    monthly = pd.read_csv(project / "reports/tables/mart_marketplace_monthly.csv")
    naive_key = next(key for key in ("naive_order_item_payment_gmv", "naive_joined_gmv", "naive_gmv") if key in qa)
    result = {"grain_safe_gmv_proxy": float(monthly["gmv_proxy"].sum()), "naive_join_gmv": float(qa[naive_key]), "fanout_difference": float(qa["fanout_difference"]), "fanout_multiple": float(qa["fanout_multiple"]), "passes": bool(float(qa["fanout_difference"]) > 0)}
    (project / "reports/qa/reconciliation_result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", default=".")
    args = parser.parse_args()
    print(json.dumps(reconcile(Path(args.project_dir)), indent=2))


if __name__ == "__main__":
    main()
