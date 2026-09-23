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
            display = row[f"Activated{horizon}DDisplay"].strip()
            if denominator == 0:
                assert display == ""
            else:
                assert int(display) == numerator


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
    rc5 = next(row for row in rows if row["Case"] == "RC5")
    assert rc5["EvidenceStatus"] == "Supported operational association"
    assert "mechanism" not in rc5["EvidenceStatus"].lower()


def test_activation_kpi_deltas_are_suppressed_without_mature_comparison() -> None:
    text = (MODEL / "tables" / "ActivationCohort.tmdl").read_text(encoding="utf-8")
    for name in (
        "Activation Closed Sellers Delta Label",
        "Activation 30D Delta Label",
        "Activation 60D Delta Label",
        "Activation 90D Delta Label",
        "Activation Median Days Delta Label",
    ):
        assert f"measure '{name}' = BLANK ()" in text
    assert "prior cohort" not in text.lower()


def test_page2_has_one_visible_acquisition_channel_slicer() -> None:
    page = REPORT / "pages" / "1a2b3c4d5e6f708192a3" / "visuals"
    visible = []
    for name in ("p2s1", "p2s2"):
        payload = json.loads((page / name / "visual.json").read_text(encoding="utf-8-sig"))
        projection = payload["visual"]["query"]["queryState"]["Values"]["projections"][0]
        if not payload.get("isHidden", False):
            visible.append(projection["queryRef"])
    assert visible == ["AcquisitionChannel.Channel"]


def test_page3_blank_delta_visuals_are_hidden() -> None:
    page = REPORT / "pages" / "2b3c4d5e6f708192a3b4" / "visuals"
    for name in ("p3delta1", "p3delta2", "p3delta3", "p3delta4", "p3delta5"):
        payload = json.loads((page / name / "visual.json").read_text(encoding="utf-8-sig"))
        assert payload.get("isHidden") is True


def test_page3_retention_matrix_has_reader_facing_headers() -> None:
    payload = json.loads(
        (REPORT / "pages" / "2b3c4d5e6f708192a3b4" / "visuals" / "p3v3" / "visual.json").read_text(
            encoding="utf-8-sig"
        )
    )
    values = payload["visual"]["query"]["queryState"]["Values"]["projections"]
    assert [value["displayName"] for value in values] == ["M0", "M1", "M2", "M3"]


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
        properties = payload["visual"]["objects"]
        row_subtotals = properties["general"][0]["properties"]["rowSubtotals"]
        assert row_subtotals["expr"]["Literal"]["Value"] == "false"


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
        "January cohort",
        "Lower activation and weaker R1 retention",
        "Supported business mechanism",
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


def test_report_labels_match_governed_semantics() -> None:
    def visual(page: str, name: str) -> dict:
        return json.loads(
            (REPORT / "pages" / page / "visuals" / name / "visual.json").read_text(
                encoding="utf-8-sig"
            )
        )

    p5_matrix = visual("4d5e6f708192a3b4c5d6", "p5v6")
    p5_rows = p5_matrix["visual"]["query"]["queryState"]["Rows"]["projections"]
    assert p5_rows[0]["displayName"] == "Delivery Status"

    for name in ("p5v1", "p5v2", "p5v4", "p5v5"):
        payload = visual("4d5e6f708192a3b4c5d6", name)
        category = payload["visual"]["query"]["queryState"]["Category"]["projections"][0]
        assert category["queryRef"] == "CustomerExperience.Segment"
        assert category["displayName"] == "Delivery Status"

    p4_top_share = visual("3c4d5e6f708192a3b4c5", "p4k4")
    p4_gini = visual("3c4d5e6f708192a3b4c5", "p4k5")
    top_projection = p4_top_share["visual"]["query"]["queryState"]["Data"]["projections"][0]
    gini_projection = p4_gini["visual"]["query"]["queryState"]["Data"]["projections"][0]
    assert top_projection["queryRef"] == "Snapshot.Top 20% GMV"
    assert gini_projection["queryRef"] == "Snapshot.Seller Gini"

    p6_scatter = visual("5e6f708192a3b4c5d6e7", "p6v1")
    category = p6_scatter["visual"]["query"]["queryState"]["Category"]["projections"][0]
    assert category["queryRef"] == "RootCauseRegister.Case"
    assert category["displayName"] == "Root-Cause Case"
    assert p6_scatter["visual"]["visualType"] == "clusteredBarChart"
    assert [projection["queryRef"] for projection in p6_scatter["visual"]["query"]["queryState"]["Y"]["projections"]] == [
        "RootCauseRegister.SupportedHypotheses",
        "RootCauseRegister.PlausibleHypotheses",
        "RootCauseRegister.RejectedHypotheses",
        "RootCauseRegister.InconclusiveHypotheses",
    ]
    assert "columnFormatting" not in p6_scatter["visual"]["objects"]

    p6_supported = visual("5e6f708192a3b4c5d6e7", "p6v2")
    supported_category = p6_supported["visual"]["query"]["queryState"]["Category"]["projections"][0]
    assert supported_category["queryRef"] == "RootCauseRegister.Case"

    p6_table = visual("5e6f708192a3b4c5d6e7", "p6v3")
    assert "columnFormatting" not in p6_table["visual"]["objects"]

    p7_matrix = visual("6f708192a3b4c5d6e7f8", "p7v1")
    fields = [
        projection["displayName"]
        for role in ("Size", "X", "Y")
        for projection in p7_matrix["visual"]["query"]["queryState"][role]["projections"]
    ]
    assert fields == ["Evidence Strength", "Actionability", "Evidence Strength"]
    for name in ("p7spark1", "p7spark2", "p7spark3", "p7spark4", "p7spark5"):
        spark = visual("6f708192a3b4c5d6e7f8", name)
        projection = spark["visual"]["query"]["queryState"]["Y"]["projections"][0]
        assert projection["displayName"] == "Evidence Strength"

    commercial = (MODEL / "tables" / "CommercialSegment.tmdl").read_text(encoding="utf-8")
    assert "column AOV\n\t\tdataType: double\n\t\tformatString: R$ #,0.0" in commercial
    assert "lineageTag: 34c8fc0d-d9e5-4145-8eb8-e90d46452edb\n\t\tsummarizeBy: average" in commercial
