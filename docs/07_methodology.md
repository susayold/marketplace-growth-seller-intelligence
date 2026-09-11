# Methodology

1. Read source CSVs directly from their ZIP files.
2. Normalize column names and parse timestamps.
3. Profile nulls, distinctness, candidate keys, domains, and date ranges.
4. Demonstrate fan-out risk before calculating metrics.
5. Build pandas/SQL-shaped marts at documented grain.
6. Validate with chi-square association checks and descriptive distributions.
7. Generate decision-facing charts with explicit units, denominators, and caveats.

The production target remains PostgreSQL + Power BI. This v1 execution used DuckDB/pandas-compatible transformations because PostgreSQL and Power BI were not available in the current desktop runtime; the repo contains the SQL and semantic-model specifications for the next runtime.
