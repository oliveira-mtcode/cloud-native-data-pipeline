from __future__ import annotations

import os
from typing import Optional

import polars as pl

from .logging_utils import get_logger


logger = get_logger(__name__)


def read_sales(path: str) -> pl.DataFrame:
    if path.endswith(".csv"):
        df = pl.read_csv(path, try_parse_dates=True, infer_schema_length=10000)
    elif path.endswith(".parquet"):
        df = pl.read_parquet(path)
    else:
        raise ValueError(f"Unsupported file type: {path}")
    logger.info("Read sales data: %s rows, %s cols", df.height, df.width)
    return df


def read_customers(path: str) -> pl.DataFrame:
    if path.endswith(".csv"):
        df = pl.read_csv(path, try_parse_dates=True, infer_schema_length=5000)
    elif path.endswith(".parquet"):
        df = pl.read_parquet(path)
    else:
        raise ValueError(f"Unsupported file type: {path}")
    logger.info("Read customers data: %s rows, %s cols", df.height, df.width)
    return df


def write_df(df: pl.DataFrame, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if path.endswith(".parquet"):
        df.write_parquet(path)
    elif path.endswith(".csv"):
        df.write_csv(path)
    else:
        raise ValueError(f"Unsupported output file type: {path}")
    logger.info("Wrote dataset to %s", path)


