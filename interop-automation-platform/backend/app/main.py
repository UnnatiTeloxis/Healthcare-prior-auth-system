from contextlib import asynccontextmanager
import asyncio
import logging
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import router
from app.services.fhir_validator.inferno_client import inferno_client

logger = logging.getLogger(__name__)

_RESERVED_PATHS = frozenset({
    "api", "health", "docs", "redoc", "openapi.json", "assets",
})


def _resolve_frontend_dist() -> Path | None:
    env_path = os.getenv("FRONTEND_DIST_PATH", "").strip()
    if env_path:
        candidate = Path(env_path)
        if candidate.is_dir():
            return candidate

    candidates = [
        Path(__file__).resolve().parent.parent / "frontend" / "dist",
        Path("/app/frontend/dist"),
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return None


FRONTEND_DIST = _resolve_frontend_dist()


async def _preload_validator_igs() -> None:
    for attempt in range(1, 31):
        try:
            await inferno_client.load_default_igs()
            if inferno_client._loaded_igs:
                version = await inferno_client.get_version()
                logger.info("FHIR validator IGs preloaded: %s", version)
                return
            logger.warning("IG preload attempt %s: no IGs loaded yet", attempt)
        except Exception as exc:
            logger.warning("FHIR validator IG preload attempt %s failed: %s", attempt, exc)
        await asyncio.sleep(10)

    logger.warning("FHIR validator IG preload gave up after retries; validation will retry on demand")
    inferno_client._igs_ready.set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    preload_task = asyncio.create_task(_preload_validator_igs())
    yield
    preload_task.cancel()
    await inferno_client.close()


app = FastAPI(
    title="Interop Automation Platform API",
    description="FHIR Validator, CRD Simulator, DTR Simulator",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "interop-platform"}


if FRONTEND_DIST:
    logger.info("Serving frontend static files from %s", FRONTEND_DIST)

    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/")
    async def serve_frontend_root():
        index_path = FRONTEND_DIST / "index.html"
        if index_path.is_file():
            return FileResponse(index_path)
        raise HTTPException(status_code=404, detail="Frontend index not found")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        first_segment = full_path.split("/", 1)[0]
        if first_segment in _RESERVED_PATHS or full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")

        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)

        index_path = FRONTEND_DIST / "index.html"
        if index_path.is_file():
            return FileResponse(index_path)

        raise HTTPException(status_code=404, detail="Page not found")
else:
    logger.info("Frontend dist not found — API-only mode")

    @app.get("/")
    async def root():
        return {
            "message": "Interop Automation Platform",
            "version": "1.0.0",
            "docs": "/docs",
        }
