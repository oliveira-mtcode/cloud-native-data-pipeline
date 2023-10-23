import os
import polars as pl

from src.pipeline.orchestrate import run_local_pipeline
from src.pipeline.config import paths


def test_e2e_local(tmp_path):
    # Prepare small sample data
    raw_dir = tmp_path / "data" / "raw"
    proc_dir = tmp_path / "data" / "processed"
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(proc_dir, exist_ok=True)

    sales = pl.DataFrame({
        "date": ["2024-01-01", "2024-01-02"],
        "store_id": ["s1", "s1"],
        "product_id": ["p1", "p2"],
        "quantity": [1, 2],
        "price": [10.0, 12.0],
    })
    customers = pl.DataFrame({
        "customer_id": ["c1", "c2"],
        "signup_date": ["2024-01-01", "2024-01-02"],
    })
    sales_path = raw_dir / "sales.csv"
    cust_path = raw_dir / "customers.csv"
    sales.write_csv(str(sales_path))
    customers.write_csv(str(cust_path))

    run_local_pipeline(str(sales_path), str(cust_path), str(proc_dir))

    assert (proc_dir / "daily_store_sales.parquet").exists()
    assert (proc_dir / "customer_features.parquet").exists()
    assert (proc_dir / "forecast.parquet").exists()


