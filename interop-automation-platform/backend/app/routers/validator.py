from fastapi import APIRouter, HTTPException
from app.models.requests import ValidationRequest, BatchValidationRequest
from app.models.responses import ValidationResult, BatchValidationResult, ProfileInfo, ProfilesByIGResponse
from app.services.validation import validation_service
from app.services.inferno_client import inferno_client
from typing import List

router = APIRouter()


@router.post("/", response_model=ValidationResult)
async def validate_resource(request: ValidationRequest):
    """
    Validate a single FHIR resource against specified profiles.
    """
    try:
        result = await validation_service.validate_resource(
            resource=request.resource,
            profiles=request.profiles,
            resource_type=request.resource_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=BatchValidationResult)
async def validate_batch(request: BatchValidationRequest):
    """
    Validate multiple FHIR resources.
    """
    try:
        result = await validation_service.validate_batch(
            resources=request.resources,
            profiles=request.profiles
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profiles", response_model=List[str])
async def get_profiles():
    """
    Get list of all available profile URLs.
    """
    try:
        profiles = await inferno_client.get_profiles()
        return profiles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profiles/by-ig", response_model=dict)
async def get_profiles_by_ig():
    """
    Get profiles grouped by Implementation Guide.
    """
    try:
        profiles_by_ig = await inferno_client.get_profiles_by_ig()
        return profiles_by_ig
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
