import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Paths:
    project_root: str = os.getenv("PROJECT_ROOT", os.getcwd())
    data_raw_dir: str = os.getenv("DATA_RAW_DIR", os.path.join(project_root, "data", "raw"))
    data_processed_dir: str = os.getenv("DATA_PROCESSED_DIR", os.path.join(project_root, "data", "processed"))
    models_dir: str = os.getenv("MODELS_DIR", os.path.join(project_root, "models"))
    reports_dir: str = os.getenv("REPORTS_DIR", os.path.join(project_root, "reports"))


@dataclass(frozen=True)
class GCPConfig:
    project_id: Optional[str] = os.getenv("GCP_PROJECT_ID")
    bucket_raw: Optional[str] = os.getenv("GCS_BUCKET_RAW")
    bucket_processed: Optional[str] = os.getenv("GCS_BUCKET_PROCESSED")
    region: str = os.getenv("GCP_REGION", "us-central1")
    dataproc_cluster: Optional[str] = os.getenv("DATAPROC_CLUSTER")


@dataclass(frozen=True)
class Modeling:
    forecast_horizon_days: int = int(os.getenv("FORECAST_HORIZON_DAYS", "14"))
    validation_days: int = int(os.getenv("VALIDATION_DAYS", "28"))
    model_type: str = os.getenv("MODEL_TYPE", "linear")  # linear | xgboost


paths = Paths()
gcp = GCPConfig()
modeling = Modeling()


