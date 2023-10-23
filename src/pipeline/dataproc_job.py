from __future__ import annotations

import os
import tempfile

from .config import gcp, paths
from .gcp_utils import gcs_download, gcs_upload
from .logging_utils import configure_logging, get_logger
from .orchestrate import run_local_pipeline


logger = get_logger(__name__)


def main():
    configure_logging()
    # Expect GCS paths via env
    sales_blob = os.getenv("GCS_SALES_BLOB", "raw/sales.csv")
    customers_blob = os.getenv("GCS_CUSTOMERS_BLOB", "raw/customers.csv")

    if not gcp.bucket_raw or not gcp.bucket_processed:
        raise RuntimeError("GCS buckets not configured")

    with tempfile.TemporaryDirectory() as tmp:
        local_sales = os.path.join(tmp, "sales.csv")
        local_customers = os.path.join(tmp, "customers.csv")
        out_dir = os.path.join(tmp, "processed")

        gcs_download(gcp.bucket_raw, sales_blob, local_sales)
        gcs_download(gcp.bucket_raw, customers_blob, local_customers)

        run_local_pipeline(local_sales, local_customers, out_dir)

        # Upload outputs
        for fname in ["daily_store_sales.parquet", "customer_features.parquet", "forecast.parquet"]:
            src = os.path.join(out_dir, fname)
            dst = f"processed/{fname}"
            gcs_upload(gcp.bucket_processed, src, dst)


if __name__ == "__main__":
    main()


