"""Input/output helpers for ZIP-backed source data and CSV artifacts."""
from __future__ import annotations
from pathlib import Path
from zipfile import ZipFile
import pandas as pd


def zip_csv_members(zip_path: Path) -> list[str]:
    with ZipFile(zip_path) as zf:
        return [n for n in zf.namelist() if n.lower().endswith(".csv")]


def read_zip_csv(zip_path: Path, member: str) -> pd.DataFrame:
    with ZipFile(zip_path) as zf, zf.open(member) as fh:
        return pd.read_csv(fh)


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)

