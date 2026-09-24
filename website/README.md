# MarketLens Website — final seven-page portfolio release

The GitHub Pages site is the public presentation layer for the final MarketLens
Power BI case study.

## Live report

https://susayold.github.io/marketplace-growth-seller-intelligence/

The site presents all seven Power BI pages:

1. Executive Overview
2. Seller Acquisition
3. Seller Activation & Retention
4. Commercial Performance
5. Customer Experience & Operations
6. Root Cause & Diagnostic
7. Decision Center

## Artifact contract

- `dist/assets/final-market-dashboard.pdf` is the downloadable final report.
- The GitHub Pages workflow renders fresh `page-1.png` through `page-7.png`
  previews from that checked-in PDF during deployment.

This keeps the live report previews synchronized with the final downloadable PDF.

## Final release

- Final Power BI source commit: `561d9b6867f919708a9aff1fa86119381c225aff`.
- Final PDF publication commit: `87de2a32c2ff7561771ee9eebc8cfba307a3bf19`.
- Final PDF SHA-256:
  `488e30011814bde5eb0749014c63dbeacca448aa0fae6884f0b10a7efc3a5f34`.
- GitHub Pages deployment: PASS.
- Seven live report pages: PASS.

The website is a static portfolio publication layer; governed analytical logic
remains in the repository's SQL/Python outputs and Power BI PBIP model.
