#!/bin/sh
# Pre-download FHIR core packages and US Core during docker build (has network).
set -e

export TX_SERVER_URL="${TX_SERVER_URL:-https://tx.fhir.org/r4}"
export DISPLAY_ISSUES_ARE_WARNINGS="${DISPLAY_ISSUES_ARE_WARNINGS:-true}"

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
while [ "$i" -le 120 ]; do
  if curl -sf "http://127.0.0.1:4567/profiles" >/dev/null 2>&1; then
    echo "Inferno engine ready"
    READY=1
    break
  fi
  sleep 5
  i=$((i + 1))
done

if [ "$READY" -ne 1 ]; then
  echo "Warning: Inferno warm-up timed out; runtime will download packages"
  exit 0
fi

if [ -f /app/fhir_packages/us-core.tgz ]; then
  echo "Loading bundled US Core IG..."
  curl -sf -X POST -H "Content-Encoding: gzip" \
    --data-binary "@/app/fhir_packages/us-core.tgz" \
    "http://127.0.0.1:4567/igs" || echo "Warning: US Core preload failed during warm-up"
fi

echo "Inferno warm-up complete (/root/.fhir cached in image)"
