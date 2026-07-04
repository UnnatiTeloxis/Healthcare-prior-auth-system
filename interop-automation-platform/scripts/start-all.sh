#!/bin/sh
set -e

# Fast, reliable validation: profile/structure/cardinality (Inferno `-tx n/a` mode).
# Remote tx.fhir.org is slow and can crash startup when unreachable.
export DISABLE_TX="${DISABLE_TX:-true}"
export DISPLAY_ISSUES_ARE_WARNINGS="${DISPLAY_ISSUES_ARE_WARNINGS:-true}"
# Unset TX URL when TX is disabled so the engine does not try to connect.
if [ "$DISABLE_TX" = "true" ]; then
  unset TX_SERVER_URL
else
  export TX_SERVER_URL="${TX_SERVER_URL:-https://tx.fhir.org/r4}"
fi
export INFERNO_VALIDATOR_URL="${INFERNO_VALIDATOR_URL:-http://127.0.0.1:4567}"
export FHIR_PACKAGES_PATH="${FHIR_PACKAGES_PATH:-/app/fhir_packages}"
export PORT="${PORT:-8000}"
# Keep JVM heap modest so Java + Python fit on Render free tier (512 MB).
export JAVA_TOOL_OPTIONS="${JAVA_TOOL_OPTIONS:--Xms128m -Xmx256m -XX:+UseSerialGC -XX:+TieredCompilation -XX:TieredStopAtLevel=1}"

# Background: wait for Inferno (packages auto-load from /home/igs), then warm-up probe.
# Must not block binding PORT for Render.
warmup_inferno() {
  echo "Waiting for Inferno engine (background)..."
  i=1
  while [ "$i" -le 300 ]; do
    if curl -sf "http://127.0.0.1:4567/profiles" >/dev/null 2>&1; then
      echo "Inferno validator engine ready"
      # Only POST-upload if US Core profiles were not auto-loaded from /home/igs.
      if ! curl -sf "http://127.0.0.1:4567/profiles" | grep -q "us-core-patient"; then
        echo "US Core not in engine yet; uploading bundled package..."
        /preload-igs.sh || echo "Warning: IG preload had errors"
      else
        echo "US Core profiles auto-loaded from /home/igs"
      fi
      # JIT warm-up so first user request is fast.
      curl -sf -X POST -H "Content-Type: application/json" \
        -d '{"resourceType":"Patient","id":"warmup"}' \
        "http://127.0.0.1:4567/validate" >/dev/null \
        || echo "Warning: warm-up validate probe skipped"
      echo "Inferno warm-up complete"
      return 0
    fi
    sleep 0.5
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
