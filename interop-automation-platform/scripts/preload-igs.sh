#!/bin/sh
# Upload bundled FHIR IGs to a running Inferno instance (127.0.0.1:4567).
set -e

BASE_URL="${INFERNO_VALIDATOR_URL:-http://127.0.0.1:4567}"
PACKAGES_DIR="${FHIR_PACKAGES_PATH:-/app/fhir_packages}"

if [ ! -d "$PACKAGES_DIR" ]; then
  echo "No FHIR packages directory at $PACKAGES_DIR"
  exit 0
fi

for pkg in "$PACKAGES_DIR"/*.tgz; do
  [ -f "$pkg" ] || continue
  name=$(basename "$pkg")
  echo "Preloading IG package $name..."
  if curl -sf -X POST -H "Content-Encoding: gzip" \
    --data-binary "@$pkg" \
    "$BASE_URL/igs"; then
    echo "  loaded $name"
  else
    echo "  warning: failed to load $name (may already be loaded)"
  fi
done

echo "Bundled IG preload finished"
