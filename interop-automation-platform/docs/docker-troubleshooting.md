# Docker troubleshooting

## 1. See actual build error logs

```powershell
cd interop-automation-platform

# Full build output
docker compose build --no-cache --progress=plain

# Backend only
docker compose build backend --progress=plain

# Frontend only
docker compose build frontend --progress=plain

# After a failed run
docker compose logs backend
docker compose logs frontend
```

## 2. Check Docker daemon is running

```powershell
docker --version
docker info
docker ps
```

If `docker info` fails, start **Docker Desktop** and wait until it shows **Running**.

## 3. Clean up failed builds

```powershell
docker compose down -v
docker system prune -f
docker builder prune -f
```

## 4. Build backend separately

```powershell
cd backend
docker build -t interop-backend .
```

## 5. Build frontend separately

```powershell
cd frontend
docker build -t interop-frontend .
```

## 6. Start the stack (PowerShell)

```powershell
cd interop-automation-platform
Copy-Item .env.example .env -ErrorAction SilentlyContinue
.\scripts\dev.ps1 start
```

## Common errors

| Error | Fix |
|-------|-----|
| `fhir.resources==7.2.0` not found | Fixed — MVP uses minimal `requirements.txt` |
| `Bind for 0.0.0.0:5432 failed` | Fixed — Postgres host port is **5433** |
| `http: server gave HTTP response to HTTPS client` | Docker registry/network issue — restart Docker Desktop, check VPN/proxy |
| `npm run build` at wrong folder | Run from `frontend/` or use `npm run build` at project root |
| No containers after build | Run `docker compose up -d` after successful build |

## Verify when working

```powershell
docker compose ps
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/health
curl http://localhost:3000
```
