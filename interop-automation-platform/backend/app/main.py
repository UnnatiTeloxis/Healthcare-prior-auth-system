from contextlib import asynccontextmanager
import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router
from app.services.fhir_validator.inferno_client import inferno_client

logger = logging.getLogger(__name__)


async def _preload_validator_igs() -> None:
    try:
        await inferno_client.load_default_igs()
        version = await inferno_client.get_version()
        logger.info("FHIR validator IGs preloaded: %s", version)
    except Exception as exc:
        logger.warning("FHIR validator IG preload skipped: %s", exc)
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


@app.get("/")
async def root():
    return {
        "message": "Interop Automation Platform",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "interop-platform"}
