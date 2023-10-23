from __future__ import annotations

import os
from datetime import date

import polars as pl

from .config import paths, modeling
from .features import customer_features, daily_store_sales
from .ingest import read_customers, read_sales, write_df
from .logging_utils import configure_logging, get_logger
from .model import forecast, train_baseline
from .transform import clean_customers, clean_sales


logger = get_logger(__name__)


def run_local_pipeline(
    sales_path: str,
    customers_path: str,
    output_dir: str | None = None,
):
    configure_logging()
    output_dir = output_dir or paths.data_processed_dir
    os.makedirs(output_dir, exist_ok=True)

    # Ingest
    raw_sales = read_sales(sales_path)
    raw_customers = read_customers(customers_path)

    # Transform
    sales = clean_sales(raw_sales)
    customers = clean_customers(raw_customers)

    # Feature engineering
    daily = daily_store_sales(sales)
    cust_feats = customer_features(sales, customers)

    # Persist processed datasets
    write_df(daily, os.path.join(output_dir, "daily_store_sales.parquet"))
    write_df(cust_feats, os.path.join(output_dir, "customer_features.parquet"))
    # Also write CSVs for interoperability (e.g., Ruby report service)
    write_df(daily, os.path.join(output_dir, "daily_store_sales.csv"))
    write_df(cust_feats, os.path.join(output_dir, "customer_features.csv"))

    # Modeling and forecasting
    artifacts = train_baseline(daily)
    horizon = modeling.forecast_horizon_days
    fcst = forecast(artifacts, daily, horizon)
    write_df(fcst, os.path.join(output_dir, "forecast.parquet"))
    write_df(fcst, os.path.join(output_dir, "forecast.csv"))
    logger.info("Pipeline completed. Outputs saved to %s", output_dir)


if __name__ == "__main__":
    # Defaults for local run
    sales_file = os.path.join(paths.data_raw_dir, "sales.csv")
    customers_file = os.path.join(paths.data_raw_dir, "customers.csv")
    run_local_pipeline(sales_file, customers_file, paths.data_processed_dir)


