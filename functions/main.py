from __future__ import annotations

import os

from src.pipeline.config import gcp, paths
from src.pipeline.dataproc_job import main as run_dataproc_job, main as run_dataproc_job_with_auth


def trigger(request):  # Google Cloud Functions HTTP entrypoint
    _ = request  # unused
    run_dataproc_job()
    return ("Triggered Dataproc pipeline", 200)

def trigger_with_auth(request):  # Google Cloud Functions HTTP entrypoint
    _ = request  # unused
    run_dataproc_job_with_auth()
    return ("Triggered Dataproc pipeline", 200)

