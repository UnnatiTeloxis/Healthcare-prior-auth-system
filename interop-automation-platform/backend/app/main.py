from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.routers import validator, igs
from app.services.inferno_client import inferno_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Don't load IGs on startup - user can load them via API if needed
    print("FHIR Validator API started. IGs can be loaded via /api/v1/igs/ endpoints.")
    yield
    await inferno_client.close()


app = FastAPI(
    title="FHIR Validator API",
    description="FHIR resource validation service using Inferno validator wrapper",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(validator.router, prefix="/api/v1/validate", tags=["Validation"])
app.include_router(igs.router, prefix="/api/v1/igs", tags=["Implementation Guides"])


@app.get("/")
async def root():
    return {
        "service": "FHIR Validator API",
        "status": "running",
        "inferno_url": settings.inferno_validator_url
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
