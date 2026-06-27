from fastapi import APIRouter

from app.api.v1.fhir_validator.schemas import (
    BatchValidationRequest,
    BatchValidationResult,
    ValidationRequest,
    ValidationResult,
)
from app.services.fhir_validator.inferno_client import inferno_client
from app.services.fhir_validator.validator import validation_service

router = APIRouter()


@router.get("/health")
async def fhir_health():
    version = await inferno_client.get_version()
    return {
        "status": "ok",
        "tool": "fhir-validator",
        "inferno_url": inferno_client.base_url,
        "validator": version,
    }


@router.post("/", response_model=ValidationResult)
@router.post("/validate", response_model=ValidationResult)
async def validate_resource(request: ValidationRequest):
    return await validation_service.validate_resource(
        resource=request.resource,
        profiles=request.profiles,
        resource_type=request.resource_type,
    )


@router.post("/batch", response_model=BatchValidationResult)
async def validate_batch(request: BatchValidationRequest):
    return await validation_service.validate_batch(
        resources=request.resources,
        profiles=request.profiles,
    )


@router.get("/profiles", response_model=list[str])
async def get_profiles():
    return await inferno_client.get_profiles()


@router.get("/profiles/by-ig")
async def get_profiles_by_ig():
    return await inferno_client.get_profiles_by_ig()
