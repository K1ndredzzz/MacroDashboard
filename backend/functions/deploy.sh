#!/bin/bash
# Deploy FRED Cloud Function to GCP

set -e

# Configuration
PROJECT_ID="gen-lang-client-0815236933"
REGION="us-central1"
FUNCTION_NAME="ingest-fred"
ENTRY_POINT="ingest_fred_http"
RUNTIME="python311"
MEMORY="512MB"
TIMEOUT="540s"

echo "Deploying FRED Cloud Function..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Function: $FUNCTION_NAME"
echo ""

# Deploy function
gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --runtime=$RUNTIME \
  --region=$REGION \
  --source=. \
  --entry-point=$ENTRY_POINT \
  --trigger-http \
  --allow-unauthenticated \
  --memory=$MEMORY \
  --timeout=$TIMEOUT \
  --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID,BQ_DATASET_RAW=macro_raw,BQ_DATASET_CORE=macro_core,BQ_DATASET_OPS=macro_ops" \
  --set-secrets="FRED_API_KEY=FRED_API_KEY:latest" \
  --project=$PROJECT_ID

echo ""
echo "Deployment complete!"
echo ""
echo "Function URL:"
gcloud functions describe $FUNCTION_NAME \
  --region=$REGION \
  --project=$PROJECT_ID \
  --gen2 \
  --format="value(serviceConfig.uri)"
