# Railway — Single URL Deployment

One Railway service serves **both** the React UI and FastAPI API on the same domain.

| URL | Serves |
|-----|--------|
| `https://your-app.railway.app/` | React SPA (`index.html`) |
| `https://your-app.railway.app/fhir-validator.html` | Standalone validator UI |
| `https://your-app.railway.app/api/v1/*` | FastAPI API |
| `https://your-app.railway.app/health` | Health check |
| `https://your-app.railway.app/docs` | Swagger API docs |

## Architecture

```
Railway (one service)
└── Docker image (interop-automation-platform/Dockerfile)
    ├── Stage 1: npm run build → frontend/dist
    └── Stage 2: uvicorn serves API + static files from /app/frontend/dist
```

## Railway setup

1. **Delete** the separate frontend service if you created one earlier.
2. Create **one** service from GitHub.
3. **Settings → Root Directory:** `interop-automation-platform`
4. Railway auto-detects `railway.json` → builds `Dockerfile`
5. **Variables** (minimum):

```env
INFERNO_VALIDATOR_URL=<your-inferno-wrapper-url>
CORS_ORIGINS=*
API_DEBUG=false
API_RELOAD=false
PORT=8000
```

6. Deploy → `railway up` or push to GitHub

## CLI deploy

```bash
cd interop-automation-platform
railway login
railway link
railway up
```

## Verify

```bash
curl https://your-app.railway.app/health
curl https://your-app.railway.app/docs
open https://your-app.railway.app/fhir-validator.html
```

## Local Docker test (same image as Railway)

```bash
cd interop-automation-platform
docker build -t fhir-validator .
docker run -p 8000:8000 -e PORT=8000 fhir-validator
```

- UI: http://localhost:8000/
- Validator: http://localhost:8000/fhir-validator.html
- API: http://localhost:8000/api/v1/
- Health: http://localhost:8000/health
- Docs: http://localhost:8000/docs

## Local development (unchanged)

```bash
# Terminal 1 — backend
cd backend && uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend with Vite proxy
cd frontend && npm run dev
```

Vite proxies `/api`, `/docs`, and `/health` to `localhost:8000`.

## Files removed (dual-service deploy)

- `backend/railway.json`
- `frontend/railway.json`
- `backend/railway.toml`
- `frontend/railway.toml`
- `backend/nixpacks.toml`
- `frontend/nixpacks.toml`

## Troubleshooting

| Issue | Fix |
|-------|-----|
| 404 on `/` | Rebuild image — frontend `dist` must exist in container |
| API works, UI blank | Check `docker build` logs for `npm run build` errors |
| `/docs` 404 | Ensure catch-all route is registered after API routes (already handled in `main.py`) |
| Validation fails | Set `INFERNO_VALIDATOR_URL` to a reachable Inferno wrapper |
