# Deploy to Railway

## Why builds were failing

| Error | Cause | Fix |
|-------|-------|-----|
| `Detected Node` on backend | Railway used `interop-automation-platform/` root and found `package.json` | **Delete** root `package.json`; set service **Root Directory** to `backend` |
| `npm run build --prefix frontend` | Same root `package.json` `build` script | Delete root `package.json` |
| Frontend image build failed | Missing `axios`, peer deps, no production `start` script | Use `frontend/nixpacks.toml` + updated `package.json` |

## Architecture (two Railway services)

Create **two separate services** in one Railway project:

| Service | Root Directory | Start command |
|---------|----------------|---------------|
| `fhir-validator-backend` | `interop-automation-platform/backend` | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| `fhir-validator-frontend` | `interop-automation-platform/frontend` | `npm run start` |

If your Git repo root is `Healthcare-prior-auth-system`, paths are:

- `interop-automation-platform/backend`
- `interop-automation-platform/frontend`

## One-time setup

### 1. Remove root package.json (required)

From `interop-automation-platform/`:

```powershell
# Windows
Remove-Item package.json -ErrorAction SilentlyContinue
```

```bash
# Linux / macOS
rm -f package.json package-lock.json
```

This stops Railway from treating the monorepo folder as a Node app.

### 2. Create Railway project

1. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub**
2. Select `Healthcare-prior-auth-system` (branch: `interop-automation`)

### 3. Backend service

1. **New Service** → same repo
2. **Settings** → **Root Directory**: `interop-automation-platform/backend`
3. **Settings** → **Config file**: `railway.toml` (auto-detected)
4. **Variables** (minimum):

```env
PORT=8000
API_DEBUG=false
API_RELOAD=false
CORS_ORIGINS=*
INFERNO_VALIDATOR_URL=<your-inferno-wrapper-url>
TERMINOLOGY_SERVER_URL=https://tx.fhir.org/r4
DEFAULT_IGS=hl7.fhir.us.core#6.1.0
DATABASE_URL=<optional-postgres-url>
REDIS_URL=<optional-redis-url>
```

5. Deploy → verify: `https://<backend>.up.railway.app/health`

### 4. Frontend service

1. **New Service** → same repo
2. **Root Directory**: `interop-automation-platform/frontend`
3. **Variables**:

```env
BACKEND_URL=https://<your-backend-service>.up.railway.app
PORT=3000
```

`BACKEND_URL` is used by Vite preview to proxy `/api`, `/docs`, and `/health`.

4. Deploy → open `https://<frontend>.up.railway.app/fhir-validator.html`

## CLI deploy

```bash
# Install Railway CLI
npm i -g @railway/cli
railway login

# Backend
cd interop-automation-platform/backend
railway link
railway up

# Frontend (separate terminal)
cd interop-automation-platform/frontend
railway link
railway up
```

## Files added for Railway

| File | Purpose |
|------|---------|
| `railway.json` | Monorepo service map (reference) |
| `backend/railway.json` | Backend Railway config |
| `backend/railway.toml` | Backend Railway config (preferred) |
| `backend/nixpacks.toml` | Forces Python 3.11 + pip install |
| `backend/runtime.txt` | Python version hint |
| `frontend/railway.json` | Frontend Railway config |
| `frontend/railway.toml` | Frontend Railway config |
| `frontend/nixpacks.toml` | Forces Node 20 + legacy peer deps |

## Health checks

Backend already exposes:

- `GET /health` → `{"status":"healthy","service":"interop-platform"}`
- `GET /api/v1/health` (via router)

No changes to validation logic or API routes were required.

## Inferno wrapper

Live FHIR validation requires `INFERNO_VALIDATOR_URL` pointing to a running Inferno FHIR validator wrapper (same as Docker `fhir-validator-wrapper`).

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Still detects Node on backend | Confirm Root Directory is `interop-automation-platform/backend`, not parent folder |
| `Module not found: axios` | Run `npm install` in `frontend/` after pull (axios added to package.json) |
| API calls fail from UI | Set `BACKEND_URL` on frontend service to backend public URL |
| Build OOM on free tier | Upgrade plan or reduce build memory in Railway settings |
