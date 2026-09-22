from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PB = ROOT / "deliverables" / "powerbi"
SOURCE = PB / "source-data" / "release_v3_final"
REPORT = PB / "final market dashboard.Report" / "definition"
MODEL = PB / "final market dashboard.SemanticModel" / "definition"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def test_activation_uses_mature_observation_windows() -> None:
    rows = read_csv(SOURCE / "reports" / "tables" / "powerbi_activation_cohort.csv")
    expected = {30: (825, 130), 60: (803, 247), 90: (769, 324)}
    for horizon, (expected_observable, expected_activated) in expected.items():
        observable = sum(int(row[f"Observable{horizon}D"] or 0) for row in rows)
        activated = sum(int(row[f"Activated{horizon}D"] or 0) for row in rows)
        assert (observable, activated) == (expected_observable, expected_activated)
        for row in rows:
            denominator = int(row[f"Observable{horizon}D"] or 0)
            numerator = int(row[f"Activated{horizon}D"] or 0)
            rate = row[f"Activation{horizon}Rate"].strip()
            if denominator == 0:
                assert rate == ""
            else:
                assert math.isclose(float(rate), numerator / denominator, rel_tol=1e-9)


def test_root_cause_register_is_evidence_oriented() -> None:
    rows = read_csv(SOURCE / "reports" / "tables" / "powerbi_root_cause_register.csv")
    assert len(rows) == 6
    assert set(rows[0]) == {
        "Case",
        "Driver",
        "EvidenceStatus",
        "HypothesesTested",
        "SupportedHypotheses",
        "PlausibleHypotheses",
        "RejectedHypotheses",
        "InconclusiveHypotheses",
        "Actionability",
        "Owner",
    }
    assert sum(int(row["HypothesesTested"]) for row in rows) == 20
    for row in rows:
        parts = [
            int(row["SupportedHypotheses"]),
            int(row["PlausibleHypotheses"]),
            int(row["RejectedHypotheses"]),
            int(row["InconclusiveHypotheses"]),
        ]
        assert sum(parts) == int(row["HypothesesTested"])


def test_decision_register_keeps_d04_priority_and_cadence() -> None:
    rows = read_csv(SOURCE / "reports" / "tables" / "powerbi_decision_register.csv")
    assert len(rows) == 5
    d04 = next(row for row in rows if "top 1/5/10/20%" in row["Action"])
    assert d04["Priority"] == "P2"
    assert d04["TimeHorizon"] == "monthly"


def test_affected_matrix_totals_are_hidden() -> None:
    for page, visual in [
        ("3c4d5e6f708192a3b4c5", "p4v6"),
        ("4d5e6f708192a3b4c5d6", "p5v6"),
    ]:
        payload = json.loads(
            (REPORT / "pages" / page / "visuals" / visual / "visual.json").read_text(
                encoding="utf-8-sig"
            )
        )
        total = payload["visual"]["objects"]["total"][0]["properties"]["show"]
        assert total["expr"]["Literal"]["Value"] == "false"


def test_forbidden_stale_report_language_is_absent() -> None:
    forbidden = (
        "Partner converts best",
        "Aug is strongest",
        "Best 90D activation",
        "Strategic leads value",
        "Strategic and Growth",
        "P1 commercial action with a 90D horizon",
        "Highest severity and frequency",
        "Driver Impact Ranking",
        "Priority Score",
    )
    paths = list(REPORT.rglob("*.json")) + list(MODEL.rglob("*.tmdl"))
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for phrase in forbidden:
            assert phrase not in text, f"{phrase!r} remains in {path}"


def test_page4_headline_cards_use_canonical_snapshot_measures() -> None:
    for visual, expected_property in [("p4k2", "Orders (K)"), ("p4k3", "Average Order Value")]:
        payload = json.loads(
            (REPORT / "pages" / "3c4d5e6f708192a3b4c5" / "visuals" / visual / "visual.json").read_text(
                encoding="utf-8-sig"
            )
        )
        projection = payload["visual"]["query"]["queryState"]["Data"]["projections"][0]
        measure = projection["field"]["Measure"]
        assert measure["Expression"]["SourceRef"]["Entity"] == "Snapshot"
        assert measure["Property"] == expected_property
