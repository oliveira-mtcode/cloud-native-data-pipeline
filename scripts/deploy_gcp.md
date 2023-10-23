GCP Deployment (guide)

1) Buckets
- Create two buckets: one for raw, one for processed.

2) Upload raw data
- Place `sales.csv` and `customers.csv` under `raw/` prefix of the raw bucket.

3) Dataproc
- Create a Dataproc cluster with access to both buckets.
- Submit a Python job with main `src/pipeline/dataproc_job.py`.
- Set env vars for job: `GCP_PROJECT_ID, GCS_BUCKET_RAW, GCS_BUCKET_PROCESSED, GCP_REGION`.

4) Cloud Function (trigger)
- Deploy HTTP function using `functions/main.py` (Python 3.11 runtime).
- Add `functions/requirements.txt` for deps.
- Configure env vars: `GCP_PROJECT_ID, GCS_BUCKET_RAW, GCS_BUCKET_PROCESSED, GCP_REGION, DATAPROC_CLUSTER`.

5) Ruby report service
- Deploy as Cloud Run or run on a VM.
- Provide `GCP_PROJECT_ID` and `GCS_BUCKET_PROCESSED`. POST to `/report` to publish summary.


