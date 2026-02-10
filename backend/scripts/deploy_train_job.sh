#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-about-nine-prototype-46a2c}"
REGION="${REGION:-asia-northeast3}"
JOB_NAME="${JOB_NAME:-train-chemistry-model}"
SERVICE_ACCOUNT="${SERVICE_ACCOUNT:-}"
IMAGE="${IMAGE:-gcr.io/${PROJECT_ID}/${JOB_NAME}:latest}"
SCHEDULE="${SCHEDULE:-0 12 * * *}"
TIMEZONE="${TIMEZONE:-Asia/Seoul}"
BUCKET="${FIREBASE_STORAGE_BUCKET:-}"

if [[ -z "${SERVICE_ACCOUNT}" ]]; then
  echo "SERVICE_ACCOUNT is required (e.g., train-chemistry@${PROJECT_ID}.iam.gserviceaccount.com)" >&2
  exit 1
fi
if [[ -z "${BUCKET}" ]]; then
  echo "FIREBASE_STORAGE_BUCKET is required" >&2
  exit 1
fi

echo "Building image: ${IMAGE}"
gcloud builds submit --project "${PROJECT_ID}" \
  --config backend/cloudbuild_train.yaml \
  --substitutions _IMAGE="${IMAGE}" \
  .

echo "Creating/Updating Cloud Run Job: ${JOB_NAME}"
gcloud run jobs deploy "${JOB_NAME}" \
  --image "${IMAGE}" \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --service-account "${SERVICE_ACCOUNT}" \
  --set-env-vars "CHEMISTRY_MODEL_PATH=/tmp/chemistry_model.pkl,FIREBASE_STORAGE_BUCKET=${BUCKET}" \
  --max-retries 1 \
  --task-timeout 1800

echo "Creating/Updating Scheduler job"
SCHEDULER_JOB="${JOB_NAME}-schedule"

gcloud scheduler jobs create http "${SCHEDULER_JOB}" \
  --location "${REGION}" \
  --project "${PROJECT_ID}" \
  --schedule "${SCHEDULE}" \
  --time-zone "${TIMEZONE}" \
  --uri "https://run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/${JOB_NAME}:run" \
  --http-method POST \
  --oauth-service-account-email "${SERVICE_ACCOUNT}" \
  --oauth-token-scope "https://www.googleapis.com/auth/cloud-platform" \
  --message-body '{}' \
  --headers "Content-Type=application/json" \
  --attempt-deadline 300s \
  --quiet || \

gcloud scheduler jobs update http "${SCHEDULER_JOB}" \
  --location "${REGION}" \
  --project "${PROJECT_ID}" \
  --schedule "${SCHEDULE}" \
  --time-zone "${TIMEZONE}" \
  --uri "https://run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${PROJECT_ID}/jobs/${JOB_NAME}:run" \
  --http-method POST \
  --oauth-service-account-email "${SERVICE_ACCOUNT}" \
  --oauth-token-scope "https://www.googleapis.com/auth/cloud-platform" \
  --message-body '{}' \
  --headers "Content-Type=application/json" \
  --attempt-deadline 300s \
  --quiet

echo "Done."
