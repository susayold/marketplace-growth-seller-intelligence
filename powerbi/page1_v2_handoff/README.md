# Marketplace Growth & Seller Intelligence — Page 1 V2 handoff

This package contains the editable Power BI Project (PBIP), semantic-model TMDL/DAX, report definition, governed release data, and the detailed implementation status.

## Open

1. Open `powerbi/Marketplace_Growth_Seller_Intelligence_Page1_V2/Marketplace_Growth_Seller_Intelligence_Page1_V2.pbip` in Power BI Desktop.
2. On first open, click `Refresh now` once and wait for the import to finish.
3. Use `PowerBI_Page1_V2_HANDOFF_REPORT.md` as the continuation checklist.

## Important

- The report definition and semantic model are editable text files. The `.tmdl` files contain the source Power Query and DAX measures.
- The PBIP currently uses the local absolute data path recorded in the detailed report. Update `File.Contents(...)` paths when moving the project to another machine.
- Main quantitative visuals are native Power BI visuals backed by model fields. The state map is the documented source-backed fallback image.
- This is Page 1 only. Page 2 has not been started.

