#!/usr/bin/env bash
# Fix demo/server FHIR validate HTTP 500 for selected IGs (DTR/IPA/etc).
# Root cause: backend marks IG "loaded" in memory while Inferno no longer has
# the StructureDefinition — /igs/load returns in <100ms without uploading.
#
# Run on the server:
#   cd /root/interop-automation-platform
#   bash scripts/fix-server-ig-500.sh

set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Pulling latest code (if git remote configured)"
git pull --ff-only || true

COMPOSE="docker compose"
if [[ -f docker-compose.prod.yml ]]; then
  COMPOSE="docker compose -f docker-compose.prod.yml"
fi

echo "==> Rebuilding backend (IG ensure + force-reload fixes)"
$COMPOSE up -d --build backend

echo "==> Restarting Inferno wrapper (clears OOM / missing profiles)"
$COMPOSE up -d fhir-validator-wrapper || $COMPOSE up -d fhir-validator-wrapper_prod || true

# Container names differ between compose files
BACKEND=$(docker ps --format '{{.Names}}' | grep -E 'interop_backend' | head -1 || true)
WRAPPER=$(docker ps --format '{{.Names}}' | grep -E 'fhir_validator_wrapper' | head -1 || true)

echo "==> Waiting for backend health"
for i in $(seq 1 60); do
  if docker exec "$BACKEND" curl -sf http://localhost:8000/health >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

echo "==> Force-reloading Da Vinci DTR + HRex + SDC into Inferno"
for spec in \
  "hl7.fhir.us.davinci-hrex|1.2.0" \
  "hl7.fhir.uv.sdc|4.0.0" \
  "hl7.fhir.us.davinci-dtr|2.2.0"
do
  name="${spec%%|*}"
  ver="${spec##*|}"
  echo "  - $name#$ver"
  curl -sf -X POST "http://127.0.0.1:8000/api/v1/igs/force-reload" \
    -H "Content-Type: application/json" \
    -d "{\"package_name\":\"$name\",\"version\":\"$ver\"}" \
    | head -c 200 || echo "(force-reload endpoint missing — restart backend with latest code)"
  echo
done

echo "==> Smoke validate DTR QuestionnaireResponse"
curl -sf -X POST "http://127.0.0.1:8000/api/v1/fhir/validate" \
  -H "Content-Type: application/json" \
  -d @- <<'EOF' | head -c 400
{"resource":"{\"resourceType\":\"QuestionnaireResponse\",\"status\":\"completed\",\"questionnaire\":\"http://example.org/q\",\"subject\":{\"reference\":\"Patient/1\"}}","profiles":["http://hl7.org/fhir/us/davinci-dtr/StructureDefinition/dtr-questionnaireresponse"]}
EOF
echo
echo "Done. Soft-refresh demo.teloxis.com and re-validate."
