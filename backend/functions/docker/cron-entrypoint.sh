#!/bin/bash
set -e

echo "Starting Macro Dashboard Data Collector"
echo "========================================"
echo "Database: $DATABASE_URL"
echo "Cron Schedule: ${CRON_SCHEDULE:-0 */6 * * *}"
echo ""

# Create cron job
CRON_SCHEDULE="${CRON_SCHEDULE:-0 */6 * * *}"
echo "$CRON_SCHEDULE cd /app && python -m ingest_fred.main >> /var/log/cron/collector.log 2>&1" > /etc/cron.d/data-collector

# Set permissions
chmod 0644 /etc/cron.d/data-collector

# Apply cron job
crontab /etc/cron.d/data-collector

# Run once immediately on startup
echo "Running initial data collection..."
cd /app && python -m ingest_fred.main

# Start cron in foreground
echo "Starting cron daemon..."
cron -f
