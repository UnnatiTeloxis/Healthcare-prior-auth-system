# Deploy to Render.com

Single-URL production deploy: **UI + API + FHIR Validator** on one domain, with a co-deployed Inferno wrapper service.

## Architecture

| URL | Serves |
|-----|--------|
| `https://interop-platform.onrender.com/` | React SPA |
| `https://interop-platform.onrender.com/fhir-validator.html` | FHIR Conformance Validator UI |
| `https://interop-platform.onrender.com/api/v1/*` | Validation API |
| `https://interop-platform.onrender.com/health` | Health check |
| `https://interop-platform.onrender.com/docs` | Swagger docs |

| Service | Image | Role |
|---------|-------|------|
| `interop-platform` | `Dockerfile` (unified build) | Frontend + FastAPI + bundled IG packages |
| `fhir-validator-wrapper` | `infernocommunity/fhir-validator-service` | Inferno validation engine |

FHIR Implementation Guides are **bundled** in `backend/fhir_packages/` and loaded offline at runtime (no IG download from the internet).

## Quick deploy

1. Push to GitHub:
   ```powershell
   cd interop-automation-platform
   .\scripts\deploy-render.ps1
   ```

2. [Render Dashboard](https://dashboard.render.com) → **New +** → **Blueprint**

3. Connect repo and select `render.yaml`:
   - Monorepo root: `/render.yaml`
   - Or set **Root Directory** to `interop-automation-platform` and use its `render.yaml`

4. Click **Apply** (two services are created)

5. Wait 10–15 minutes for first build (frontend + backend in one Docker image)

## Verify

```bash
curl https://interop-platform.onrender.com/health
curl https://fhir-validator-wrapper.onrender.com/version
```

Open: `https://interop-platform.onrender.com/fhir-validator.html`

## Local test (same image as Render)

```bash
cd interop-automation-platform
docker build -t interop-platform .
docker run -p 8000:8000 -e PORT=8000 \
  -e INFERNO_VALIDATOR_URL=http://host.docker.internal:4567 \
  interop-platform
```

For full validation locally, run `docker compose up` (includes Inferno wrapper).

## FHIR packages (offline IGs)

Packages must exist in `backend/fhir_packages/` before deploy (already in repo if committed):

```powershell
New-Item -ItemType Directory -Force backend\fhir_packages | Out-Null
Invoke-WebRequest "https://hl7.org/fhir/us/core/package.tgz" -OutFile "backend\fhir_packages\us-core.tgz"
```

## Environment variables

| Variable | Service | Default in blueprint |
|----------|---------|----------------------|
| `INFERNO_VALIDATOR_URL` | interop-platform | `https://fhir-validator-wrapper.onrender.com` |
| `FHIR_PACKAGES_PATH` | interop-platform | `/app/fhir_packages` |
| `DEFAULT_IGS` | interop-platform | `hl7.fhir.us.core#6.1.0` |
| `TX_SERVER_URL` | wrapper | `https://tx.fhir.org/r4` |

If your wrapper service name differs, update `INFERNO_VALIDATOR_URL` in the Render dashboard.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `open Dockerfile: no such file` | Set Root Directory to `interop-automation-platform` |
| IG load errors | Ensure `backend/fhir_packages/*.tgz` are committed |
| Validation API errors | Check wrapper is up: `/version` on wrapper URL |
| Cold start slow | Free tier sleeps after ~15 min inactivity |
| Service name taken | Rename services in `render.yaml` and update `INFERNO_VALIDATOR_URL` |

## Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Production unified image (frontend build + backend) |
| `render.yaml` | Render Blueprint |
| `backend/Dockerfile` | Dev-only image for `docker-compose.yml` |
| `backend/fhir_packages/` | Bundled FHIR IG `.tgz` files |
| `.dockerignore` | Docker build exclusions |
