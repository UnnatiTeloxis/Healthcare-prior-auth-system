# Deploy to Render.com (FREE tier)

This guide covers deploying the Interop Automation Platform to [Render.com](https://render.com) using the **Render Blueprint** (`render.yaml`). No application source code changes are required — only the deployment files in this document.

## Files added for Render

| File | Purpose |
|------|---------|
| `render.yaml` | Full-stack Blueprint (backend, frontend, Postgres, Redis) |
| `backend/Dockerfile.render` | Backend image with `PORT` support for Render |
| `backend/render.yaml` | Optional backend-only Blueprint |
| `frontend/Dockerfile.render` | Frontend production build + nginx |
| `frontend/nginx.render.conf` | Nginx proxy to backend on Render |
| `docker-compose.render.yml` | Local simplified stack (backend + frontend) |
| `.env.production` | Production environment template |
| `.dockerignore` | Root Docker build exclusions |
| `scripts/deploy-render.sh` | Linux/macOS push + deploy helper |
| `scripts/deploy-render.ps1` | Windows push + deploy helper |

Existing `Dockerfile`, `docker-compose.yml`, and `nginx.conf` files are **unchanged** and still used for local development.

## Prerequisites

1. GitHub repository with this project pushed
2. [Render.com](https://render.com) account (free tier)
3. **Inferno FHIR validator wrapper** URL for live validation (see below)

## Quick deploy (Blueprint)

1. Push this repo to GitHub:
   ```bash
   cd interop-automation-platform
   ./scripts/deploy-render.sh
   ```
   Windows:
   ```powershell
   cd interop-automation-platform
   .\scripts\deploy-render.ps1
   ```

2. In Render Dashboard: **New +** → **Blueprint**

3. Connect your GitHub repository

4. Choose the correct `render.yaml`:
   - Repo root is `Healthcare-prior-auth-system` → use `/render.yaml` at repository root
   - Repo root is `interop-automation-platform` → use `interop-automation-platform/render.yaml`

5. Set **Root Directory** (if needed):
   - Monorepo: leave root `render.yaml` (it sets `rootDir: interop-automation-platform`)
   - Or set Root Directory to `interop-automation-platform` and use that folder's `render.yaml`

6. After Blueprint preview, set **`INFERNO_VALIDATOR_URL`** on the backend service (marked `sync: false` in blueprint)

7. Click **Apply** and wait 5–10 minutes

## Service URLs

After deploy:

| Service | URL |
|---------|-----|
| Backend API | `https://fhir-validator-backend.onrender.com` |
| API Docs | `https://fhir-validator-backend.onrender.com/docs` |
| Health | `https://fhir-validator-backend.onrender.com/health` |
| Frontend | `https://fhir-validator-frontend.onrender.com` |
| FHIR Validator UI | `https://fhir-validator-frontend.onrender.com/fhir-validator.html` |

## Inferno validator (important)

Full FHIR conformance validation requires the **Inferno FHIR validator wrapper** (`INFERNO_VALIDATOR_URL`). The local `docker-compose.yml` runs this as `fhir-validator-wrapper`.

On Render free tier you must either:

- Host the wrapper elsewhere and set `INFERNO_VALIDATOR_URL` to its public URL, or
- Use Render private networking between services (paid feature) with a custom wrapper service

Without a reachable wrapper, `/health` still works but validation endpoints will fail.

## Environment variables

Copy from `.env.production` into Render Dashboard → each service → **Environment**:

| Variable | Service | Notes |
|----------|---------|-------|
| `PORT` | Backend | Set by Render automatically |
| `DATABASE_URL` | Backend | Linked from Render Postgres |
| `REDIS_URL` | Backend | Linked from Render Redis |
| `INFERNO_VALIDATOR_URL` | Backend | **You must set this** |
| `CORS_ORIGINS` | Backend | `*` or your frontend URL |
| `VITE_API_BASE_URL` | Frontend build | `/api/v1` (nginx proxies `/api`) |

## Verify deployment

```bash
curl https://fhir-validator-backend.onrender.com/health
```

Expected: `{"status":"healthy","service":"interop-platform"}`

Open the frontend URL in a browser and run a validation.

## Local Docker (Render-style)

```bash
cd interop-automation-platform
cp .env.production .env
docker compose -f docker-compose.render.yml up -d --build
```

- Frontend: http://localhost:3000  
- Backend: http://localhost:8000  

## Manual Docker build

```bash
# Backend
cd backend
docker build -f Dockerfile.render -t fhir-backend-render .
docker run -p 8000:8000 -e PORT=8000 fhir-backend-render

# Frontend
cd frontend
docker build -f Dockerfile.render -t fhir-frontend-render .
docker run -p 3000:80 fhir-frontend-render
```

## Free tier notes

- Services spin down after ~15 minutes of inactivity; first request may take 30–60 seconds
- Free Postgres and Redis are included in `render.yaml` but have storage/connection limits
- Rename services in `render.yaml` if names are already taken in your Render account

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Blueprint not found | Set Root Directory to `interop-automation-platform` or use repo-root `render.yaml` |
| Health check fails | Check backend logs; ensure `PORT` is used (Dockerfile.render) |
| Frontend 502 on `/api` | Update `backend_host` in `frontend/nginx.render.conf` to match your backend service URL |
| Validation errors | Set `INFERNO_VALIDATOR_URL` to a running Inferno wrapper |
| Cold start slow | Normal on free tier; upgrade or use a keep-alive ping |
