#!/bin/sh
set -e

export TX_SERVER_URL="${TX_SERVER_URL:-https://tx.fhir.org/r4}"
export DISPLAY_ISSUES_ARE_WARNINGS="${DISPLAY_ISSUES_ARE_WARNINGS:-true}"
export INFERNO_VALIDATOR_URL="${INFERNO_VALIDATOR_URL:-http://127.0.0.1:4567}"
export PORT="${PORT:-8000}"

echo "Starting Inferno FHIR validator wrapper..."
cd /home
./bin/InfernoValidationService &
INFERNO_PID=$!

echo "Waiting for Inferno on :4567..."
READY=0
i=1
while [ "$i" -le 90 ]; do
  if curl -sf "http://127.0.0.1:4567/version" >/dev/null 2>&1; then
    echo "Inferno validator ready"
    READY=1
    break
  fi
  sleep 2
  i=$((i + 1))
done

if [ "$READY" -ne 1 ]; then
  echo "Warning: Inferno validator did not become ready in time; API may fail until it starts"
fi

trap 'kill "$INFERNO_PID" 2>/dev/null || true' EXIT TERM INT

echo "Starting FastAPI on :${PORT}..."
cd /app
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
