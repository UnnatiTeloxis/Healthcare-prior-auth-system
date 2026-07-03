from contextlib import asynccontextmanager
import asyncio
import logging
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import router
from app.config import settings
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


def _resolve_fhir_validator_html() -> Path | None:
    env_path = os.getenv("FHIR_VALIDATOR_HTML_PATH", "").strip()
    if env_path:
        candidate = Path(env_path)
        if candidate.is_file():
            return candidate

    candidates = [
        Path("/app/frontend/dist/fhir-validator.html"),
        Path("/app/frontend/public/fhir-validator.html"),
        Path(__file__).resolve().parent.parent / "frontend" / "dist" / "fhir-validator.html",
        Path(__file__).resolve().parent.parent / "frontend" / "public" / "fhir-validator.html",
    ]
    if FRONTEND_DIST:
        candidates.insert(0, FRONTEND_DIST / "fhir-validator.html")

    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


FHIR_VALIDATOR_HTML = _resolve_fhir_validator_html()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Production: block until Inferno is warm so first validation is fast.
    # Dev (--reload): preload in background to avoid stalling hot reload.
    if settings.API_RELOAD:
        preload_task = asyncio.create_task(inferno_client.ensure_ready())
        try:
            yield
        finally:
            preload_task.cancel()
            with asyncio.suppress(asyncio.CancelledError):
                await preload_task
    else:
        await inferno_client.ensure_ready()
        yield
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


if FHIR_VALIDATOR_HTML:
    logger.info("FHIR validator UI available at /fhir-validator.html (%s)", FHIR_VALIDATOR_HTML)

    @app.get("/fhir-validator.html")
    async def serve_fhir_validator_page():
        return FileResponse(FHIR_VALIDATOR_HTML)


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
        validator_path = FRONTEND_DIST / "fhir-validator.html"
        if validator_path.is_file():
            return RedirectResponse(url="/fhir-validator.html", status_code=302)
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
        if FHIR_VALIDATOR_HTML:
            return RedirectResponse(url="/fhir-validator.html", status_code=302)
        return {
            "message": "Interop Automation Platform",
            "version": "1.0.0",
            "docs": "/docs",
        }
