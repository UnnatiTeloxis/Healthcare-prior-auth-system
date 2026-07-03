#!/bin/sh
# Upload only default IGs needed at startup (fast). Other packages load on demand.
set -e

BASE_URL="${INFERNO_VALIDATOR_URL:-http://127.0.0.1:4567}"
PACKAGES_DIR="${FHIR_PACKAGES_PATH:-/app/fhir_packages}"

if [ ! -d "$PACKAGES_DIR" ]; then
  echo "No FHIR packages directory at $PACKAGES_DIR"
  exit 0
fi

# US Core is required for most validations; load first and skip if already present.
if [ -f "$PACKAGES_DIR/us-core.tgz" ]; then
  echo "Preloading default IG us-core.tgz..."
  curl -sf -X POST -H "Content-Encoding: gzip" \
    --data-binary "@$PACKAGES_DIR/us-core.tgz" \
    "$BASE_URL/igs" >/dev/null \
    || echo "  warning: us-core may already be loaded"
fi

echo "Default IG preload finished"
