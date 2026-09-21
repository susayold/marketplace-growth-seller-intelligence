"""Static release gate for the unified MarketLens repository."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PB = ROOT / "deliverables" / "powerbi"
REPORT = PB / "final market dashboard.Report"
MODEL = PB / "final market dashboard.SemanticModel"
SOURCE = PB / "source-data" / "release_v3_final"
RECON = ROOT / "reports" / "qa" / "powerbi_reconciliation.csv"
SOURCE_RECON = SOURCE / "reports" / "qa" / "powerbi_reconciliation.csv"


def require(path: Path) -> None:
    if not path.exists():
        raise AssertionError(f"missing required path: {path.relative_to(ROOT)}")


def main() -> None:
    required = [
        ROOT / "README.md",
        ROOT / "dist" / "index.html",
        ROOT / "dist" / "assets" / "final-market-dashboard.pdf",
        PB / "final market dashboard.pbip",
        MODEL / "definition" / "expressions.tmdl",
        SOURCE / "reports" / "tables" / "mart_marketplace_monthly.csv",
        SOURCE / "reports" / "tables" / "mart_acquisition_channel.csv",
        SOURCE / "reports" / "tables" / "powerbi_activation_cohort.csv",
        SOURCE / "reports" / "tables" / "powerbi_commercial_segment.csv",
        SOURCE / "reports" / "tables" / "powerbi_customer_experience.csv",
        SOURCE / "reports" / "tables" / "powerbi_decision_register.csv",
        SOURCE / "reports" / "tables" / "powerbi_retention_cohort.csv",
        SOURCE / "reports" / "tables" / "powerbi_root_cause_register.csv",
        RECON,
        SOURCE_RECON,
    ]
    for path in required:
        require(path)

    pbip = json.loads((PB / "final market dashboard.pbip").read_text(encoding="utf-8"))
    if pbip.get("version") != "1.0":
        raise AssertionError("unexpected PBIP version")

    definition_json = list(REPORT.joinpath("definition").rglob("*.json"))
    for path in definition_json:
        json.loads(path.read_text(encoding="utf-8"))
    pages = list(REPORT.joinpath("definition", "pages").glob("*/page.json"))
    if len(pages) != 7:
        raise AssertionError(f"expected 7 PBIR pages, found {len(pages)}")

    expression = (MODEL / "definition" / "expressions.tmdl").read_text(encoding="utf-8")
    if "expression DataRoot" not in expression:
        raise AssertionError("DataRoot parameter is missing")

    with RECON.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise AssertionError("reconciliation is empty")
    for row in rows:
        if row["status"] != "PASS":
            raise AssertionError(f"reconciliation row is not PASS: {row['metric']}")
        if abs(float(row["difference"])) > float(row["tolerance"]):
            raise AssertionError(f"reconciliation exceeds tolerance: {row['metric']}")
    if RECON.read_bytes() != SOURCE_RECON.read_bytes():
        raise AssertionError("root and PBIP source-bundle reconciliation files differ")

    decision_path = SOURCE / "reports" / "tables" / "powerbi_decision_register.csv"
    with decision_path.open(newline="", encoding="utf-8-sig") as handle:
        decision_rows = list(csv.DictReader(handle))
    if len(decision_rows) != 5:
        raise AssertionError(f"expected five governed decisions, found {len(decision_rows)}")
    if any(int(row["Effort"]) <= 0 for row in decision_rows):
        raise AssertionError("decision matrix actionability values must be positive")
    if {int(row["ExpectedImpact"]) for row in decision_rows} - {2, 3}:
        raise AssertionError("decision matrix evidence-strength values are outside the governed scale")

    scan_paths = [REPORT / "definition", MODEL / "definition", SOURCE, ROOT / "dist"]
    forbidden = re.compile(
        r"bi_fact_marketplace_item|Demo[A-Z]|Partner converts best|"
        r"PROTOTYPE.*MOCK|CancelRate|MedianDeliveryDays|BLOCKED_DESKTOP_NOT_INSTALLED",
        re.IGNORECASE,
    )
    for base in scan_paths:
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".json", ".tmdl", ".html", ".js"}:
                if forbidden.search(path.read_text(encoding="utf-8", errors="ignore")):
                    raise AssertionError(f"forbidden legacy text in {path.relative_to(ROOT)}")

    if (ROOT / "dist" / "data.js").exists():
        raise AssertionError("stale dist/data.js must not be shipped")
    previews = list((ROOT / "dist" / "assets" / "dashboard").glob("page-*.png"))
    if len(previews) != 7:
        raise AssertionError(f"expected 7 synchronized dashboard previews, found {len(previews)}")

    print(
        f"final_release_ok pages={len(pages)} json={len(definition_json)} "
        f"reconciliation_rows={len(rows)} previews={len(previews)}"
    )


if __name__ == "__main__":
    main()
