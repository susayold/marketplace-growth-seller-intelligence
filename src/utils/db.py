"""PostgreSQL connection and SQL execution helpers.

The credentials are environment-driven; no secrets are committed.
"""
from __future__ import annotations
import os
from pathlib import Path
from typing import Iterable


def connection_kwargs() -> dict[str, str | int]:
    return {
        "host": os.getenv("PGHOST", "127.0.0.1"),
        "port": int(os.getenv("PGPORT", "5432")),
        "dbname": os.getenv("PGDATABASE", "marketplace_growth"),
        "user": os.getenv("PGUSER", "postgres"),
        "password": os.getenv("PGPASSWORD", ""),
    }


def connect():
    try:
        import psycopg
    except ImportError as exc:
        raise RuntimeError("Install psycopg[binary] to use PostgreSQL execution") from exc
    return psycopg.connect(**connection_kwargs())


def run_sql_files(paths: Iterable[Path]) -> None:
    with connect() as conn:
        with conn.cursor() as cur:
            for path in paths:
                cur.execute(path.read_text(encoding="utf-8"))
        conn.commit()

