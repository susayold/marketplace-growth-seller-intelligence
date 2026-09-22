"""Static release gate for the unified MarketLens repository."""

from __future__ import annotations

import csv
import json
import math
import re
import uuid
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PB = ROOT / "deliverables" / "powerbi"
REPORT = PB / "final market dashboard.Report"
MODEL = PB / "final market dashboard.SemanticModel"
SOURCE = PB / "source-data" / "release_v3_final"
RECON = ROOT / "reports" / "qa" / "powerbi_reconciliation.csv"
SOURCE_RECON = SOURCE / "reports" / "qa" / "powerbi_reconciliation.csv"
ACTIVATION_SOURCE = SOURCE / "reports" / "tables" / "powerbi_activation_cohort.csv"
ROOT_CAUSE_SOURCE = SOURCE / "reports" / "tables" / "powerbi_root_cause_register.csv"
DECISION_SOURCE = SOURCE / "reports" / "tables" / "powerbi_decision_register.csv"


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

    for path in MODEL.joinpath("definition").rglob("*.tmdl"):
        text = path.read_text(encoding="utf-8")
        if re.search(r"PBI_ResultType\s*=\s*Exception", text):
            raise AssertionError(
                f"Power Query exception metadata remains in {path.relative_to(ROOT)}"
            )
        for tag in re.findall(r"lineageTag:\s*([^\s]+)", text):
            try:
                uuid.UUID(tag)
            except ValueError as exc:
                raise AssertionError(
                    f"invalid lineageTag {tag} in {path.relative_to(ROOT)}"
                ) from exc

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

    with ACTIVATION_SOURCE.open(newline="", encoding="utf-8-sig") as handle:
        activation_rows = list(csv.DictReader(handle))
    expected_windows = {30: (825, 130), 60: (803, 247), 90: (769, 324)}
    for horizon, (expected_observable, expected_activated) in expected_windows.items():
        observable = sum(int(row[f"Observable{horizon}D"] or 0) for row in activation_rows)
        activated = sum(int(row[f"Activated{horizon}D"] or 0) for row in activation_rows)
        if (observable, activated) != (expected_observable, expected_activated):
            raise AssertionError(
                f"activation {horizon}D denominator mismatch: {observable}/{activated}"
            )
        for row in activation_rows:
            denominator = int(row[f"Observable{horizon}D"] or 0)
            numerator = int(row[f"Activated{horizon}D"] or 0)
            rate = row[f"Activation{horizon}Rate"].strip()
            if denominator == 0 and rate:
                raise AssertionError(f"immature {horizon}D cohort is not blank: {row['Cohort']}")
            if denominator > 0 and not math.isclose(float(rate), numerator / denominator, rel_tol=1e-9):
                raise AssertionError(f"activation {horizon}D rate mismatch: {row['Cohort']}")

    with ROOT_CAUSE_SOURCE.open(newline="", encoding="utf-8-sig") as handle:
        root_headers = set(next(csv.reader(handle)))
    if root_headers & {"Impact", "Severity", "Frequency", "PriorityScore"}:
        raise AssertionError("root-cause source still exposes synthetic scoring fields")

    with DECISION_SOURCE.open(newline="", encoding="utf-8-sig") as handle:
        release_decisions = list(csv.DictReader(handle))
    d04 = next((row for row in release_decisions if "top 1/5/10/20%" in row["Action"]), None)
    if not d04 or d04["Priority"] != "P2" or d04["TimeHorizon"] != "monthly":
        raise AssertionError("D04 priority/cadence does not match the canonical register")

    scan_paths = [REPORT / "definition", MODEL / "definition", SOURCE, ROOT / "dist"]
    forbidden = re.compile(
        r"bi_fact_marketplace_item|Demo[A-Z]|Partner converts best|Aug is strongest|"
        r"Best 90D activation|Strategic leads value|Strategic and Growth|"
        r"P1 commercial action with a 90D horizon|Highest severity and frequency|"
        r"Lowest conversion and longest cycle|Referral is efficient|Slightly Late|"
        r"time horizons|Target Horizon|"
        r"Driver Impact Ranking|Priority Score|PROTOTYPE.*MOCK|CancelRate|"
        r"MedianDeliveryDays|BLOCKED_DESKTOP_NOT_INSTALLED",
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
