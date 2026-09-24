# Release notes

## v1.1 non-Power-BI completion

- Added reusable ingestion, profiling, validation, reconciliation and export entrypoints.
- Added PostgreSQL schemas for raw, staging, dimensions, facts, marts and quality audits.
- Added six executable notebooks with embedded outputs.
- Added expanded automated tests, CI workflow, release log and portfolio assets.
- Preserved remote-only storage: raw data, tables and charts live in Drive; GitHub stores code, documentation and reviewable small artifacts.

## v1.2 additional analytical coverage

- Added reusable seller segmentation and eligibility-aware retention by acquisition origin.
- Added conversion confidence intervals, Cramer's V, Mann-Whitney plus bootstrap review validation, and eligible M3 retention-by-origin testing.
- Updated the statistical-validation notebook and added detailed QA output.

## Final Power BI release — 2026-09-24

- Final Power BI source commit: `561d9b6867f919708a9aff1fa86119381c225aff`.
- Completed final Desktop refresh and seven-page visual QA.
- Removed invalid matrix totals and stale/duplicated report artifacts.
- Finalized activation/retention, commercial, CX, root-cause and decision-center presentation.
- Published the fresh seven-page PDF in commit `87de2a3`.
- Final PDF SHA-256:
  `488e30011814bde5eb0749014c63dbeacca448aa0fae6884f0b10a7efc3a5f34`.
- Repository and website PDF copies are byte-identical.
- GitHub CI and GitHub Pages deployment passed for the final PDF publication.
- The v1 portfolio scope is frozen except for genuine bug fixes.
