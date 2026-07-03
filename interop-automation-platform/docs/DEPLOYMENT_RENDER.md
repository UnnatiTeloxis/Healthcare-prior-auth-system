# Deploy to Render.com — single service

Everything runs in **one** Web Service: Inferno validator + FastAPI + React UI.

| URL | Serves |
|-----|--------|
| `/` | React UI |
| `/fhir-validator.html` | FHIR Conformance Validator |
| `/api/v1/*` | Validation API |
| `/health` | Health check |
| `/docs` | Swagger |

Inferno wrapper listens on `127.0.0.1:4567` inside the container (not exposed publicly).

## Render settings (manual Web Service)

| Field | Value |
|-------|--------|
| **Branch** | `interop-automation` |
| **Root Directory** | `interop-automation-platform` |
| **Runtime** | Docker |
| **Dockerfile Path** | `./Dockerfile` |
| **Docker Build Context** | `.` |
| **Health Check Path** | `/health` |

### Environment variables

```env
PORT=8000
INFERNO_VALIDATOR_URL=http://127.0.0.1:4567
FHIR_PACKAGES_PATH=/app/fhir_packages
DEFAULT_IGS=hl7.fhir.us.core#6.1.0
TX_SERVER_URL=https://tx.fhir.org/r4
DISPLAY_ISSUES_ARE_WARNINGS=true
API_DEBUG=false
API_RELOAD=false
```

No second service required.

## Blueprint deploy

1. Render → **New +** → **Blueprint**
2. Connect GitHub repo
3. Use `render.yaml` (creates one service: `interop-platform`)

## Local test

```bash
cd interop-automation-platform
docker build -t interop-platform .
docker run -p 8000:8000 -e PORT=8000 interop-platform
```

First start may take 1–2 minutes (Inferno + IG preload).

## Free tier note

This image runs **Java (Inferno) + Python (FastAPI)** in 512 MB RAM. If the service crashes on startup, upgrade instance size or wait for cold start to complete.

## Verify

```bash
curl https://<your-service>.onrender.com/health
```

Open: `https://<your-service>.onrender.com/fhir-validator.html`
