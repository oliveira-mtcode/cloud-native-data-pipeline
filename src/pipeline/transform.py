from __future__ import annotations

import polars as pl

from .logging_utils import get_logger


logger = get_logger(__name__)


def clean_sales(df: pl.DataFrame) -> pl.DataFrame:
    # Standardize column names
    df = df.rename({c: c.strip().lower() for c in df.columns})
    # Required fields
    required = ["date", "store_id", "product_id", "quantity", "price"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Sales dataset missing required columns: {missing}")

    # Coerce types and handle bad values
    df = df.with_columns([
        pl.col("date").str.strptime(pl.Date, strict=False).alias("date"),
        pl.col("store_id").cast(pl.Utf8),
        pl.col("product_id").cast(pl.Utf8),
        pl.col("quantity").cast(pl.Float64),
        pl.col("price").cast(pl.Float64),
    ])

    # Drop invalid rows
    df = df.filter(
        pl.col("date").is_not_null()
        & pl.col("quantity").is_not_null()
        & pl.col("price").is_not_null()
        & (pl.col("quantity") >= 0)
        & (pl.col("price") >= 0)
    )

    # Compute revenue
    df = df.with_columns((pl.col("quantity") * pl.col("price")).alias("revenue"))
    logger.info("Cleaned sales data: %s rows", df.height)
    return df


def clean_customers(df: pl.DataFrame) -> pl.DataFrame:
    df = df.rename({c: c.strip().lower() for c in df.columns})
    required = ["customer_id", "signup_date"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Customers dataset missing required columns: {missing}")
    df = df.with_columns([
        pl.col("customer_id").cast(pl.Utf8),
        pl.col("signup_date").str.strptime(pl.Date, strict=False).alias("signup_date"),
    ])
    df = df.filter(pl.col("customer_id").is_not_null())
    logger.info("Cleaned customers data: %s rows", df.height)
    return df


