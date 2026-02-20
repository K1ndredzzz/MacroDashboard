#!/bin/bash
# Start FRED Cloud Function locally

cd "$(dirname "$0")"

echo "Starting FRED Cloud Function..."
echo ""
echo "Access at: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop"
echo ""

functions-framework --target=ingest_fred_http --source=fred/main.py --debug --port=8080
