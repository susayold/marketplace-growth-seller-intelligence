# Release notes

## v1.1 non-Power-BI completion

- Added reusable ingestion, profiling, validation, reconciliation and export entrypoints.
- Added PostgreSQL schemas for raw, staging, dimensions, facts, marts and quality audits.
- Added six executable notebooks with embedded outputs.
- Added expanded automated tests, CI workflow, release log and portfolio assets.
- Preserved remote-only storage: raw data, tables and charts live in Drive; GitHub stores code, documentation and reviewable small artifacts.

Power BI remains intentionally last.


## v1.2 additional analytical coverage

- Added reusable seller segmentation and eligibility-aware retention by acquisition origin.
- Added conversion confidence intervals, Cramers V, Mann-Whitney plus bootstrap review validation, and eligible M3 retention-by-origin testing.
- Updated the statistical-validation notebook and added detailed QA output.


## Release update — 2026-09-12

Added and verified the daily marketplace and seller-month marts from row-level source, added a parameterized build script and provenance QA, updated the Power BI pack to consume the new grains, and refreshed the plan audit. Power BI remains the final pending runtime gate.
