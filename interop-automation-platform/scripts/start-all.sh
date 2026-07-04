#!/bin/sh
set -e

export TX_SERVER_URL="${TX_SERVER_URL:-https://tx.fhir.org/r4}"
export DISPLAY_ISSUES_ARE_WARNINGS="${DISPLAY_ISSUES_ARE_WARNINGS:-true}"
export INFERNO_VALIDATOR_URL="${INFERNO_VALIDATOR_URL:-http://127.0.0.1:4567}"
export FHIR_PACKAGES_PATH="${FHIR_PACKAGES_PATH:-/app/fhir_packages}"
export PORT="${PORT:-8000}"
# Keep JVM heap modest so Java + Python fit on Render free tier (512 MB).
export JAVA_TOOL_OPTIONS="${JAVA_TOOL_OPTIONS:--Xms128m -Xmx256m -XX:+UseSerialGC -XX:+TieredCompilation -XX:TieredStopAtLevel=1}"

# Background: wait for Inferno, then preload default IGs (must not block PORT bind).
warmup_inferno() {
  echo "Waiting for Inferno engine (background)..."
  i=1
  while [ "$i" -le 300 ]; do
    if curl -sf "http://127.0.0.1:4567/profiles" >/dev/null 2>&1; then
      echo "Inferno validator engine ready"
      echo "Preloading bundled FHIR IGs (background)..."
      /preload-igs.sh || echo "Warning: IG preload had errors; API will retry on first validation"
      return 0
    fi
    sleep 1
    i=$((i + 1))
  done
  echo "Warning: Inferno did not become ready in time; validation will wait on demand"
}

echo "Starting Inferno FHIR validator wrapper (127.0.0.1 only)..."
cd /home
java -cp "/app/inferno-launcher:/home/lib/*" inferno.local.InfernoLocalLauncher &
INFERNO_PID=$!

warmup_inferno &
WARMUP_PID=$!

trap 'kill "$INFERNO_PID" "$WARMUP_PID" 2>/dev/null || true' EXIT TERM INT

# Bind public PORT immediately so Render health/port scan succeeds.
echo "Starting FastAPI on 0.0.0.0:${PORT}..."
cd /app
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
