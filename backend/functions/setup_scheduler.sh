#!/bin/bash
# Configure Cloud Scheduler for FRED data collection

set -e

PROJECT_ID="gen-lang-client-0815236933"
REGION="us-central1"
JOB_NAME="ingest-fred-daily"
FUNCTION_URL=$(gcloud functions describe ingest-fred --region=$REGION --project=$PROJECT_ID --gen2 --format="value(serviceConfig.uri)")

echo "Configuring Cloud Scheduler..."
echo "Project: $PROJECT_ID"
echo "Job: $JOB_NAME"
echo "Function URL: $FUNCTION_URL"
echo ""

# Create scheduler job (runs daily at 8 AM UTC)
gcloud scheduler jobs create http $JOB_NAME \
  --location=$REGION \
  --schedule="0 8 * * *" \
  --uri="$FUNCTION_URL" \
  --http-method=POST \
  --headers="Content-Type=application/json" \
  --message-body='{"lookback_days": 7}' \
  --time-zone="UTC" \
  --project=$PROJECT_ID

echo ""
echo "Scheduler configured successfully!"
echo "Schedule: Daily at 8:00 AM UTC"
