# Interop Automation Platform

Healthcare interoperability MVP with FHIR Validator, CRD Simulator, and DTR Simulator.

## FHIR Conformance Validator (Standalone UI)

A complete single-file validator UI is available at:

```
frontend/public/fhir-validator.html
```

**Open directly in browser** (no server needed):
- Double-click the file, or
- `start frontend/public/fhir-validator.html`

**Via Docker frontend** (after rebuild):
- http://localhost:3000/fhir-validator.html

Features: 5-step wizard, profile selection, JSON paste/upload, mock validation, results with filters, JSON export.

## Quick Start (Docker)

### Windows (PowerShell)

```powershell
cd interop-automation-platform

# Copy environment file
Copy-Item .env.example .env

# Build and start (recommended)
.\scripts\dev.ps1 start

# Or step by step
.\scripts\dev.ps1 build
.\scripts\dev.ps1 up
```

### Linux / macOS

```bash
cd interop-automation-platform

cp .env.example .env
./scripts/setup.sh

# Or use Makefile
make build
make up
```

> **Note:** PowerShell does not support `&&`. Run commands separately, or use `.\scripts\dev.ps1 start`.

## Services

| Service  | URL                         |
|----------|-----------------------------|
| Frontend | http://localhost:3000       |
| Backend  | http://localhost:8000       |
| API Docs | http://localhost:8000/docs  |
| Postgres | localhost:5432              |
| Redis    | localhost:6379              |

## Common Commands

### Docker (from project root)

| Task | PowerShell | Make (Git Bash / WSL) |
|------|------------|------------------------|
| Build | `.\scripts\dev.ps1 build` or `npm run docker:build` | `make build` |
| Start | `.\scripts\dev.ps1 up` or `npm run docker:up` | `make up` |
| Build + start | `.\scripts\dev.ps1 start` or `npm run start` | `make build` then `make up` |
| Logs | `.\scripts\dev.ps1 logs` | `make logs` |
| Stop | `.\scripts\dev.ps1 down` | `make down` |

### Frontend build

`package.json` lives in **`frontend/`**, not the project root.

```powershell
# Option 1: from project root (uses root package.json proxy)
npm run build

# Option 2: from frontend folder
cd frontend
npm install
npm run build
```

## Production

```powershell
Copy-Item .env.example .env
# Edit .env with production secrets

docker compose -f docker-compose.prod.yml up -d --build
```

## Deploy to Render.com (FREE)

Deployment files are **additive only** — existing Docker/dev setup is unchanged.

1. Fork or push this repository to GitHub
2. Create an account at [render.com](https://render.com)
3. Click **New +** → **Blueprint** and connect your repository
4. Select `render.yaml` (repo root or `interop-automation-platform/render.yaml`)
5. Set **`INFERNO_VALIDATOR_URL`** on the backend service (required for live FHIR validation)
6. Click **Apply** and wait 5–10 minutes

**Helper scripts** (commit + push deployment files):

```powershell
# Windows
.\scripts\deploy-render.ps1
```

```bash
# Linux / macOS
chmod +x scripts/deploy-render.sh
./scripts/deploy-render.sh
```

**After deploy:**

| Service | URL |
|---------|-----|
| Backend | `https://fhir-validator-backend.onrender.com` |
| Frontend | `https://fhir-validator-frontend.onrender.com` |
| Validator UI | `https://fhir-validator-frontend.onrender.com/fhir-validator.html` |

```bash
curl https://fhir-validator-backend.onrender.com/health
```

**Local Render-style stack:**

```bash
docker compose -f docker-compose.render.yml --env-file .env.production up -d --build
```

Full details: [docs/DEPLOYMENT_RENDER.md](docs/DEPLOYMENT_RENDER.md)

### Deployment files

| File | Purpose |
|------|---------|
| `render.yaml` | Render Blueprint (backend, frontend, Postgres, Redis) |
| `backend/Dockerfile.render` | Backend container for Render (`PORT` aware) |
| `frontend/Dockerfile.render` | Frontend production build |
| `frontend/nginx.render.conf` | Nginx config for Render |
| `docker-compose.render.yml` | Simplified local production stack |
| `.env.production` | Production environment template |
| `.dockerignore` | Docker build exclusions |
| `scripts/deploy-render.sh` | Render deploy helper (Unix) |
| `scripts/deploy-render.ps1` | Render deploy helper (Windows) |

## Local Development (without Docker)

```powershell
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `ENOENT package.json` at root | Ran `npm run build` expecting root package | Use `npm run build` from root (now works) or `cd frontend` first |
| `&&` is not valid | PowerShell syntax | Run commands separately or use `.\scripts\dev.ps1 start` |
| Docker daemon not running | Docker Desktop stopped | Start Docker Desktop, wait until running |
| `make` not found | Make not installed on Windows | Use `.\scripts\dev.ps1` instead |

## Project Structure

- `backend/` - FastAPI application
- `frontend/` - React + Vite SPA (nginx in production)
- `data/` - FHIR profiles, questionnaires, CQL, scenarios
- `scripts/` - Setup, seed, deploy scripts (`dev.ps1` for Windows)
- `docker-compose.yml` - Development stack with hot reload
- `docker-compose.prod.yml` - Production stack with resource limits
