from __future__ import annotations

import polars as pl

from .logging_utils import get_logger


logger = get_logger(__name__)


def daily_store_sales(df: pl.DataFrame) -> pl.DataFrame:
    # Aggregate daily totals per store
    out = (
        df.group_by(["date", "store_id"]).agg([
            pl.sum("quantity").alias("qty_sum"),
            pl.sum("revenue").alias("rev_sum"),
            pl.count().alias("num_txn"),
        ])
        .sort(["store_id", "date"])
    )
    return out


def customer_features(sales_df: pl.DataFrame, customers_df: pl.DataFrame) -> pl.DataFrame:
    # Optional join on customer_id if present in sales
    if "customer_id" in sales_df.columns:
        s = sales_df.select([
            pl.col("customer_id").cast(pl.Utf8),
            pl.col("revenue"),
            pl.col("date"),
        ]).drop_nulls(["customer_id"]) 
        feats = (
            s.group_by("customer_id").agg([
                pl.count().alias("customer_num_txn"),
                pl.sum("revenue").alias("customer_ltv"),
                pl.mean("revenue").alias("customer_avg_basket"),
                pl.max("date").alias("customer_last_purchase_date"),
            ])
        )
        out = customers_df.join(feats, on="customer_id", how="left")
        # Fill missing engineered fields for customers without transactions
        out = out.with_columns([
            pl.col("customer_num_txn").fill_null(0),
            pl.col("customer_ltv").fill_null(0.0),
            pl.col("customer_avg_basket").fill_null(0.0),
        ])
        return out
    else:
        return customers_df.with_columns([
            pl.lit(0).alias("customer_num_txn"),
            pl.lit(0.0).alias("customer_ltv"),
            pl.lit(0.0).alias("customer_avg_basket"),
        ])


def fill_missing_time_series(df: pl.DataFrame, group_key: str, date_col: str, value_cols: list[str]) -> pl.DataFrame:
    # Create a complete date range per group and forward-fill
    date_min = df.select(pl.min(date_col)).item()
    date_max = df.select(pl.max(date_col)).item()
    all_dates = pl.date_range(low=date_min, high=date_max, eager=True)

    completed = (
        df.join(
            pl.DataFrame({date_col: all_dates}),
            on=date_col,
            how="outer",
        )
        .sort([group_key, date_col])
        .group_by(group_key)
        .agg([
            pl.all().forward_fill(),
        ])
        .explode(pl.exclude(group_key))
        .sort([group_key, date_col])
    )

    # Fill remaining nulls with zeros for numeric value columns
    completed = completed.with_columns([pl.col(c).fill_null(0) for c in value_cols])
    return completed


