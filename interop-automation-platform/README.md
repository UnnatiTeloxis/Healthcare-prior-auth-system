# Interop Automation Platform

Healthcare interoperability MVP with FHIR Validator, CRD Simulator, and DTR Simulator.

## FHIR Conformance Validator (Standalone UI)

A complete single-file validator UI is available at:

```
frontend/public/fhir-validator.html
```

**With Docker (recommended):** http://localhost:8000/fhir-validator.html

Features: multi-step wizard, JSON/XML upload, Inferno-backed validation, results with filters, export.

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

## FHIR Validator (local)

Runs entirely on localhost via Docker Compose (Inferno wrapper + API + UI).

| URL | Purpose |
|-----|---------|
| http://localhost:8000/fhir-validator.html | Validator UI (API on same origin) |
| http://localhost:8000/health | API health |
| http://localhost:4567/version | Inferno wrapper |

Validation uses the same Inferno/HL7 engine settings as the hosted Inferno resource validator (`TX_SERVER_URL`, `DISPLAY_ISSUES_ARE_WARNINGS`). US Core is auto-loaded from `backend/fhir_packages/us-core.tgz`.

```powershell
cd interop-automation-platform
docker compose up -d
```

First start may take 1–3 minutes while Inferno loads packages; later validations are cached and concurrent for speed.

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
