# Run this from Windows PowerShell — it SSHs into the server and applies the fix.
# Usage:
#   powershell -ExecutionPolicy Bypass -File .\scripts\fix-server-ig-500.ps1
#
# You will be prompted for the root password for 103.212.121.26

$ErrorActionPreference = "Stop"
$ssh = "C:\Windows\System32\OpenSSH\ssh.exe"
$hostName = "root@103.212.121.26"

$remote = @'
set -e
cd /root/interop-automation-platform || cd ~/interop-automation-platform

echo "==> git pull"
git pull origin main || true

# Prefer prod compose if present
if [ -f docker-compose.prod.yml ]; then
  COMPOSE="docker compose -f docker-compose.prod.yml"
else
  COMPOSE="docker compose"
fi

echo "==> rebuild/restart backend + inferno"
$COMPOSE up -d --build backend fhir-validator-wrapper || $COMPOSE up -d --build

# Clear stale in-memory IG flags (critical after FileZilla-only updates)
BACKEND=$(docker ps --format '{{.Names}}' | grep -E 'interop_backend' | head -1)
WRAPPER=$(docker ps --format '{{.Names}}' | grep -E 'fhir_validator_wrapper' | head -1)
echo "backend=$BACKEND wrapper=$WRAPPER"
docker restart "$BACKEND" || true
sleep 8

echo "==> force-reload PAS + HRex + DTR"
for payload in \
  '{"package_name":"hl7.fhir.us.davinci-hrex","version":"1.2.0"}' \
  '{"package_name":"hl7.fhir.us.davinci-pas","version":"2.2.1"}' \
  '{"package_name":"hl7.fhir.us.davinci-dtr","version":"2.2.0"}' \
  '{"package_name":"hl7.fhir.us.davinci-crd","version":"2.2.1"}'
do
  echo "reload $payload"
  curl -sS -X POST http://127.0.0.1:8000/api/v1/igs/force-reload \
    -H 'Content-Type: application/json' \
    -d "$payload" | head -c 180 || echo "(force-reload not available yet — restart may be enough after pull)"
  echo
done

echo "==> smoke validate PAS claim-base"
curl -sS -X POST http://127.0.0.1:8000/api/v1/fhir/validate \
  -H 'Content-Type: application/json' \
  -d '{"resource":"{\"resourceType\":\"Claim\",\"status\":\"active\",\"use\":\"claim\",\"patient\":{\"reference\":\"Patient/1\"},\"created\":\"2024-01-01\",\"provider\":{\"reference\":\"Organization/1\"},\"priority\":{\"coding\":[{\"code\":\"normal\"}]},\"insurance\":[{\"sequence\":1,\"focal\":true,\"coverage\":{\"reference\":\"Coverage/1\"}}]}","profiles":["http://hl7.org/fhir/us/davinci-pas/StructureDefinition/profile-claim-base"]}' \
  | head -c 350
echo
echo "DONE"
'@

Write-Host "Connecting to $hostName (enter password when prompted)..." -ForegroundColor Cyan
& $ssh -t $hostName $remote
