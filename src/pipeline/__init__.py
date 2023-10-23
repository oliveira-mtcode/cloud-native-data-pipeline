"""
Cloud-Native Retail Analytics Pipeline using Polars.

Modules:
- config: centralized configuration
- logging_utils: structured logging setup
- ingest: read CSV/Parquet from local or GCS
- transform: cleaning and canonical transformations
- features: feature engineering for forecasting
- model: training, evaluation, forecasting
- orchestrate: end-to-end orchestration entrypoint
- gcp_utils: helpers for GCS, Dataproc
- dataproc_job: entrypoint for Dataproc cluster jobs
"""

__all__ = [
    "config",
    "logging_utils",
    "ingest",
    "transform",
    "features",
    "model",
    "orchestrate",
    "gcp_utils",
    "dataproc_job",
]


