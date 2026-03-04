#!/bin/bash
set -euo pipefail

LOG_DIR="/var/log/cron"
LOG_FILE="$LOG_DIR/collector.log"
CRON_FILE="/etc/cron.d/data-collector"
ENV_FILE="/etc/default/macro-dashboard-collector"
RUNNER_FILE="/usr/local/bin/run-collector.sh"

mkdir -p "$LOG_DIR"
touch "$LOG_FILE"

PYTHON_BIN="$(command -v python3 || command -v python)"
CRON_SCHEDULE="${CRON_SCHEDULE:-0 */6 * * *}"

write_env_var() {
  local key="$1"
  local value="${!key:-}"
  printf 'export %s=%q\n' "$key" "$value" >> "$ENV_FILE"
}

echo "Starting Macro Dashboard Data Collector"
echo "========================================"
echo "Database: ${DATABASE_URL:-not_set}"
echo "Cron Schedule: ${CRON_SCHEDULE}"
echo "Python Bin: ${PYTHON_BIN}"
echo ""

# Persist required runtime environment for cron child process.
cat > "$ENV_FILE" <<'EOF'
#!/bin/bash
set -a
EOF
write_env_var "DATABASE_URL"
write_env_var "POSTGRES_HOST"
write_env_var "POSTGRES_PORT"
write_env_var "POSTGRES_DB"
write_env_var "POSTGRES_USER"
write_env_var "POSTGRES_PASSWORD"
write_env_var "FRED_API_KEY"
write_env_var "SKIP_GOLD_SERIES"
write_env_var "GOLD_SERIES_ID"
write_env_var "LOOKBACK_DAYS"
printf 'export PYTHON_BIN=%q\n' "$PYTHON_BIN" >> "$ENV_FILE"
chmod 0600 "$ENV_FILE"

# Use a wrapper script so cron runs with explicit env and absolute python path.
cat > "$RUNNER_FILE" <<'EOF'
#!/bin/bash
set -euo pipefail
source /etc/default/macro-dashboard-collector
cd /app
"$PYTHON_BIN" collect_data.py >> /var/log/cron/collector.log 2>&1
EOF
chmod +x "$RUNNER_FILE"

# Install root crontab
cat > "$CRON_FILE" <<EOF
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
$CRON_SCHEDULE $RUNNER_FILE
EOF
chmod 0644 "$CRON_FILE"
crontab "$CRON_FILE"

echo "Installed crontab:"
crontab -l
echo ""

# Run once immediately on startup, but do not kill cron daemon on failure.
echo "Running initial data collection..."
if ! "$RUNNER_FILE"; then
  echo "Initial data collection failed; cron daemon will continue running."
fi
echo ""

# Stream collector log to container stdout for observability.
tail -n 0 -F "$LOG_FILE" &
TAIL_PID=$!
trap 'kill "$TAIL_PID" 2>/dev/null || true' EXIT

echo "Starting cron daemon..."
exec cron -f
