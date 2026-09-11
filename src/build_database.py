"""Load PostgreSQL schemas and models using environment-driven credentials.

The command is intentionally separate from the ZIP-backed Python pipeline:
SQL DDL and queries are reviewable, while raw archives remain in Drive.
"""
from __future__ import annotations
import argparse
from pathlib import Path
try:
    from .utils.db import run_sql_files
except ImportError:
    from utils.db import run_sql_files


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", default=".")
    args = parser.parse_args()
    project = Path(args.project_dir)
    files = [project / "sql/00_admin/00_schemas.sql"]
    files += sorted((project / "sql/01_raw").glob("*.sql"))
    files += sorted((project / "sql/02_staging").glob("*.sql"))
    files += sorted((project / "sql/03_dimensions").glob("*.sql"))
    files += sorted((project / "sql/04_facts").glob("*.sql"))
    run_sql_files(files)
    print(f"loaded {len(files)} SQL files")


if __name__ == "__main__":
    main()
