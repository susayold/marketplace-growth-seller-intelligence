"""PostgreSQL connection, COPY loading and SQL execution helpers."""
from __future__ import annotations
import os
from io import StringIO
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


def copy_dataframe(conn, table: str, frame, columns: list[str]) -> int:
    """COPY a source-shaped DataFrame into a controlled raw table."""
    missing = sorted(set(columns) - set(frame.columns))
    if missing:
        raise ValueError(f"{table}: missing source columns {missing}")
    payload = frame.loc[:, columns].copy()
    payload = payload.astype(object).where(payload.notna(), None)
    buffer = StringIO()
    payload.to_csv(buffer, index=False, header=False, na_rep="\\N")
    buffer.seek(0)
    column_sql = ", ".join(columns)
    statement = f"COPY {table} ({column_sql}) FROM STDIN WITH (FORMAT CSV, NULL '\\N')"
    with conn.cursor() as cur:
        with cur.copy(statement) as copy:
            copy.write(buffer.getvalue())
    return len(payload)

