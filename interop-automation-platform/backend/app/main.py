from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.v1.router import router
from app.services.fhir_validator.inferno_client import inferno_client


@asynccontextmanager
async def lifespan(app: FastAPI):
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
