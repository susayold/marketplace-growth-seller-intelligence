"""Date utilities used by staging and marts."""
from __future__ import annotations
import pandas as pd


def to_datetime(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", utc=True)


def month_start(series: pd.Series) -> pd.Series:
    return to_datetime(series).dt.to_period("M").dt.to_timestamp()

