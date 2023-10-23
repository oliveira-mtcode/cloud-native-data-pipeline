Cloud-Native Retail Analytics Pipeline (Polars + GCP)

### Why this exists
Retail teams need fast, reliable answers: How are sales trending? Which stores will sell more next week? This repo provides an end-to-end, cloud-native pipeline that ingests raw CSV/Parquet data, cleans and transforms it with Polars, engineers forecasting-ready features, trains a lightweight baseline model, and publishes forecasts and human-friendly summaries. Everything is containerized and testable.

### What you get
- **Fast transformations with Polars**: CSV and Parquet support at scale
- **Feature engineering**: daily store totals, customer-centric metrics, gap-filling
- **Forecasting**: transparent baseline (Linear Regression) with holdout validation
- **Cloud-native**: GCS for storage, Dataproc for heavy jobs, Cloud Functions to trigger
- **Reproducibility**: Docker images + pytest unit/integration tests
- **Stakeholder summaries**: minimal Ruby service that writes GCS JSON summaries

### Quickstart (local)
1) Install Docker and Python 3.11
2) Build images and run locally:
```bash
docker compose build
docker compose run --rm pipeline
```
Place your files at `data/raw/sales.csv` and `data/raw/customers.csv`. Outputs land in `data/processed/` including `forecast.parquet` and `forecast.csv`.

Run tests:
```bash
pip install -r requirements.txt
pytest -q
```

### Project layout
```text
src/
  pipeline/
    __init__.py
    config.py           # central config (paths, GCP, modeling)
    logging_utils.py    # structured logging
    ingest.py           # read CSV/Parquet, write outputs
    transform.py        # cleaning, canonical schema
    features.py         # daily store totals, customer features, gap-filling
    model.py            # baseline model + forecasting
    orchestrate.py      # local end-to-end runner
    gcp_utils.py        # GCS helpers
    dataproc_job.py     # Dataproc job entrypoint
functions/
  main.py               # Cloud Function trigger
services/
  ruby_report/          # minimal Sinatra service
docker/
  Dockerfile.pipeline
  Dockerfile.ruby_report
docker-compose.yml
requirements.txt
tests/
data/
  raw/
```

### Workflow (text flow)
1) Raw data lands in GCS (`gs://<raw-bucket>/raw/sales.*`, `gs://<raw-bucket>/raw/customers.*`).
2) A Cloud Function HTTP endpoint triggers the Dataproc job.
3) Dataproc job:
   - downloads raw files from GCS
   - runs the Polars pipeline (clean → features → model → forecast)
   - writes processed outputs and forecasts to `gs://<processed-bucket>/processed/`
4) Ruby service reads forecast CSV from GCS and writes `reports/summary.json` back to the processed bucket.

### Data model
- **sales**: `date, store_id, product_id, quantity, price` (+ optional `customer_id`)
- **customers**: `customer_id, signup_date`

Transformations include:
- standardize columns/types, drop invalid rows, compute `revenue = quantity * price`
- aggregate daily store metrics: `qty_sum, rev_sum, num_txn`
- customer features: `customer_num_txn, customer_ltv, customer_avg_basket`
- handle missing dates via forward-fill for stable time series inputs

Modeling:
- Baseline linear regression with lags (`rev_lag1`, `rev_lag7`, `qty_lag1`, `num_txn`)
- Rolling forecast per store for `FORECAST_HORIZON_DAYS` (default 14)

### Configuration
Environment variables:
- PROJECT_ROOT, DATA_RAW_DIR, DATA_PROCESSED_DIR
- FORECAST_HORIZON_DAYS (default 14), VALIDATION_DAYS (default 28), MODEL_TYPE
- GCP_PROJECT_ID, GCP_REGION, GCS_BUCKET_RAW, GCS_BUCKET_PROCESSED, DATAPROC_CLUSTER

### GCP deployment (high level)
1) Create two buckets: raw and processed; upload initial CSVs under `raw/`.
2) Deploy Cloud Function (2nd gen) with `functions/` and set env vars.
3) Create Dataproc cluster or use serverless batches with access to buckets.
4) Submit `src/pipeline/dataproc_job.py` as the job main.

### Ruby report service
Run locally:
```bash
docker compose up ruby_report
curl -X POST "http://localhost:4567/report" -d "forecast_csv_blob=processed/forecast.csv"
```

### Testing
- Unit tests: `pytest -q`
- End-to-end: `tests/test_integration_e2e.py` creates tiny synthetic inputs and asserts outputs exist.

### Observability
- Python logging with counts and file paths at each stage.

### License
MIT
