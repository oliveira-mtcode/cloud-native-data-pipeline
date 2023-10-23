from __future__ import annotations

import os
from typing import Optional

from google.cloud import storage  # type: ignore

from .config import gcp
from .logging_utils import get_logger


logger = get_logger(__name__)


def get_gcs_client() -> storage.Client:
    return storage.Client(project=gcp.project_id) if gcp.project_id else storage.Client()


def gcs_download(bucket_name: str, blob_path: str, local_path: str) -> None:
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    blob.download_to_filename(local_path)
    logger.info("Downloaded gs://%s/%s to %s", bucket_name, blob_path, local_path)


def gcs_upload(bucket_name: str, local_path: str, blob_path: str) -> None:
    client = get_gcs_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(local_path)
    logger.info("Uploaded %s to gs://%s/%s", local_path, bucket_name, blob_path)


