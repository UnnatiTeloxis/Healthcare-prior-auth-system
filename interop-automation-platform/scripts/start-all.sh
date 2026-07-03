#!/bin/sh
set -e

export TX_SERVER_URL="${TX_SERVER_URL:-https://tx.fhir.org/r4}"
export DISPLAY_ISSUES_ARE_WARNINGS="${DISPLAY_ISSUES_ARE_WARNINGS:-true}"
export INFERNO_VALIDATOR_URL="${INFERNO_VALIDATOR_URL:-http://127.0.0.1:4567}"
export FHIR_PACKAGES_PATH="${FHIR_PACKAGES_PATH:-/app/fhir_packages}"
export PORT="${PORT:-8000}"
export JAVA_TOOL_OPTIONS="${JAVA_TOOL_OPTIONS:--Xms256m -Xmx384m}"

echo "Starting Inferno FHIR validator wrapper (127.0.0.1 only)..."
cd /home
java -cp "/app/inferno-launcher:/home/lib/*" inferno.local.InfernoLocalLauncher &
INFERNO_PID=$!

echo "Waiting for Inferno engine on 127.0.0.1:4567..."
READY=0
i=1
while [ "$i" -le 120 ]; do
  if curl -sf "http://127.0.0.1:4567/profiles" >/dev/null 2>&1; then
    echo "Inferno validator engine ready"
    READY=1
    break
  fi
  sleep 2
  i=$((i + 1))
done

if [ "$READY" -ne 1 ]; then
  echo "Warning: Inferno validator did not become ready in time; API may fail until it starts"
else
  echo "Preloading bundled FHIR IGs before accepting API traffic..."
  /preload-igs.sh || echo "Warning: IG preload had errors; API will retry on first validation"
fi

trap 'kill "$INFERNO_PID" 2>/dev/null || true' EXIT TERM INT

echo "Starting FastAPI on 0.0.0.0:${PORT}..."
cd /app
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
