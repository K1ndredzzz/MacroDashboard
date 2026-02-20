#!/bin/bash
# Deploy FastAPI to Cloud Run

set -e

PROJECT_ID="gen-lang-client-0815236933"
REGION="us-central1"
SERVICE_NAME="macro-dashboard-api"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "Deploying FastAPI to Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo "Region: $REGION"
echo ""

# Build and push Docker image
echo "Building Docker image..."
gcloud builds submit --tag $IMAGE_NAME --project=$PROJECT_ID

# Deploy to Cloud Run
echo ""
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image=$IMAGE_NAME \
  --platform=managed \
  --region=$REGION \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --timeout=300 \
  --max-instances=10 \
  --set-env-vars="GCP_PROJECT_ID=${PROJECT_ID},BQ_DATASET_CORE=macro_core,BQ_DATASET_MART=macro_mart,DEBUG=False,REDIS_ENABLED=False" \
  --project=$PROJECT_ID

echo ""
echo "Deployment complete!"
echo "Service URL:"
gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(status.url)"
