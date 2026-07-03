#!/bin/sh
# Pre-download FHIR core packages and default IG during docker build (has network).
set -e

export TX_SERVER_URL="${TX_SERVER_URL:-https://tx.fhir.org/r4}"
export DISPLAY_ISSUES_ARE_WARNINGS="${DISPLAY_ISSUES_ARE_WARNINGS:-true}"
export JAVA_TOOL_OPTIONS="${JAVA_TOOL_OPTIONS:--Xms384m -Xmx512m -XX:+TieredCompilation -XX:TieredStopAtLevel=1}"

cd /home
java -cp "/app/inferno-launcher:/home/lib/*" inferno.local.InfernoLocalLauncher &
INFERNO_PID=$!

cleanup() {
  kill "$INFERNO_PID" 2>/dev/null || true
  wait "$INFERNO_PID" 2>/dev/null || true
}
trap cleanup EXIT

echo "Waiting for Inferno engine (profiles endpoint)..."
READY=0
i=1
while [ "$i" -le 180 ]; do
  if curl -sf "http://127.0.0.1:4567/profiles" >/dev/null 2>&1; then
    echo "Inferno engine ready"
    READY=1
    break
  fi
  sleep 1
  i=$((i + 1))
done

if [ "$READY" -ne 1 ]; then
  echo "Warning: Inferno warm-up timed out; runtime will download packages"
  exit 0
fi

FHIR_PACKAGES_PATH=/app/fhir_packages INFERNO_VALIDATOR_URL=http://127.0.0.1:4567 /preload-igs.sh

echo "Running warm-up validation probe..."
curl -sf -X POST -H "Content-Type: application/json" \
  -d '{"resourceType":"Patient","id":"warmup"}' \
  "http://127.0.0.1:4567/validate" >/dev/null || echo "Warning: warm-up validate probe skipped"

echo "Inferno warm-up complete (/root/.fhir cached in image)"
