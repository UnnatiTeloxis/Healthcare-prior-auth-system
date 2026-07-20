from contextlib import asynccontextmanager, suppress
import asyncio
import logging
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import router
from app.services.fhir_validator.inferno_client import inferno_client

logger = logging.getLogger(__name__)

_RESERVED_PATHS = frozenset({
    "api", "health", "docs", "redoc", "openapi.json", "assets",
})


# backend/app/main.py → project root is three levels up (…/interop-automation-platform)
_BACKEND_ROOT = Path(__file__).resolve().parent.parent
_PROJECT_ROOT = _BACKEND_ROOT.parent


def _resolve_frontend_dist() -> Path | None:
    env_path = os.getenv("FRONTEND_DIST_PATH", "").strip()
    if env_path:
        candidate = Path(env_path)
        if candidate.is_dir():
            return candidate

    candidates = [
        _PROJECT_ROOT / "frontend" / "dist",
        _BACKEND_ROOT / "frontend" / "dist",
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

    # Prefer public/ over dist/ so local UI edits are served without a rebuild.
    candidates = [
        _PROJECT_ROOT / "frontend" / "public" / "fhir-validator.html",
        _BACKEND_ROOT / "frontend" / "public" / "fhir-validator.html",
        Path("/app/frontend/public/fhir-validator.html"),
        _PROJECT_ROOT / "frontend" / "dist" / "fhir-validator.html",
        _BACKEND_ROOT / "frontend" / "dist" / "fhir-validator.html",
        Path("/app/frontend/dist/fhir-validator.html"),
    ]
    if FRONTEND_DIST:
        candidates.append(FRONTEND_DIST / "fhir-validator.html")

    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


FHIR_VALIDATOR_HTML = _resolve_fhir_validator_html()


def _resolve_fhir_validator_public_dir() -> Path | None:
    env_path = os.getenv("FHIR_VALIDATOR_PUBLIC_PATH", "").strip()
    if env_path:
        candidate = Path(env_path)
        if candidate.is_dir():
            return candidate

    candidates = [
        _PROJECT_ROOT / "frontend" / "public",
        _BACKEND_ROOT / "frontend" / "public",
        Path("/app/frontend/public"),
    ]
    if FHIR_VALIDATOR_HTML:
        candidates.insert(0, FHIR_VALIDATOR_HTML.parent)

    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return None


FHIR_VALIDATOR_PUBLIC = _resolve_fhir_validator_public_dir()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm Inferno + pre-register all IGs so dropdown selection is instant.
    preload_task = asyncio.create_task(_warm_and_register_igs())
    try:
        yield
    finally:
        preload_task.cancel()
        with suppress(asyncio.CancelledError):
            await preload_task
        await inferno_client.close()


async def _warm_and_register_igs():
    """Warm up Inferno engine, then optionally preload all local IG packages."""
    from app.config import settings
    from app.services.fhir_validator.ig_manager import ig_manager

    try:
        warmed = await inferno_client.warm_up()
    except Exception as exc:
        logger.warning("Warm-up incomplete: %s — validation will retry on request", exc)
        warmed = False

    if warmed:
        logger.info("Inferno engine warmed up, validation ready")
    else:
        logger.warning(
            "Inferno engine not ready yet — validation will retry on request. "
            "Startup IG preload is deferred until the engine is ready."
        )

    if settings.PRELOAD_ALL_LOCAL_IGS:
        if not inferno_client.engine_is_warm:
            logger.info("Skipping startup IG preload until Inferno engine is ready")
            return
        try:
            summary = await ig_manager.preload_all_local_igs()
            logger.info("Startup IG preload complete: %s", summary)
        except Exception as exc:
            logger.warning("Startup IG preload failed: %s", exc)


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

    if FHIR_VALIDATOR_PUBLIC:
        worker_js = FHIR_VALIDATOR_PUBLIC / "fhir-validator-worker.js"
        if worker_js.is_file():
            logger.info("FHIR validator worker available at /fhir-validator-worker.js")

            @app.get("/fhir-validator-worker.js")
            async def serve_fhir_validator_worker():
                return FileResponse(worker_js, media_type="application/javascript")


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
