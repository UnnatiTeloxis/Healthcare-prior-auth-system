import json

from fastapi import APIRouter, HTTPException

from app.api.v1.fhir_validator.schemas import (
    BatchValidationRequest,
    BatchValidationResult,
    ValidationRequest,
    ValidationResult,
)
from app.services.fhir_validator.inferno_client import inferno_client
from app.services.fhir_validator.history_service import history_service
from app.services.fhir_validator.validator import ProfileResolutionError, validation_service
from app.utils.fhir_helpers import detect_resource_type, is_valid_json


def _profile_resolution_http_error(exc: ProfileResolutionError) -> HTTPException:
    detail: dict[str, object] = {"message": exc.message}
    if exc.candidates:
        detail["candidates"] = exc.candidates
    return HTTPException(status_code=422, detail=detail)

router = APIRouter()


def _result_history_payload(result: ValidationResult) -> dict:
    return {
        "valid": result.valid,
        "resource_type": result.resource_type,
        "profiles": result.profiles,
        "summary": result.summary,
        "error_count": result.error_count,
        "warning_count": result.warning_count,
        "info_count": result.info_count,
        "issues": [issue.model_dump() if hasattr(issue, "model_dump") else issue.dict() for issue in result.issues],
        "operation_outcome": result.operation_outcome,
        "selected_ig": result.selected_ig,
        "resolved_profile": result.resolved_profile,
        "package_id": result.package_id,
        "package_version": result.package_version,
    }


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
    try:
        result = await validation_service.validate_resource(
            resource=request.resource,
            profiles=request.profiles,
            resource_type=request.resource_type,
            ig=request.ig,
            profile=request.profile,
        )
    except ProfileResolutionError as exc:
        raise _profile_resolution_http_error(exc) from exc
    try:
        if is_valid_json(request.resource):
            resource_json = json.loads(request.resource)
        else:
            resource_json = {
                "format": "xml" if request.resource.strip().startswith("<") else "text",
                "resource_type": request.resource_type or detect_resource_type(request.resource),
                "length": len(request.resource),
            }
        request_data = {
            "resource": resource_json,
            "profiles": result.profiles or request.profiles or [],
            "profile": request.profile,
            "ig": request.ig or result.selected_ig,
            "resource_type": request.resource_type,
            "selected_ig": result.selected_ig,
            "resolved_profile": result.resolved_profile,
        }
        history_service.save_validation_run(request_data, _result_history_payload(result))
    except Exception as exc:
        print(f"Warning: Failed to save validation run to history: {exc}")

    return result


@router.post("/batch", response_model=BatchValidationResult)
async def validate_batch(request: BatchValidationRequest):
    try:
        result = await validation_service.validate_batch(
            resources=request.resources,
            profiles=request.profiles,
            ig=request.ig,
            profile=request.profile,
        )
    except ProfileResolutionError as exc:
        raise _profile_resolution_http_error(exc) from exc
    try:
        for idx, validation_result in enumerate(result.results):
            resource_payload = request.resources[idx]
            if isinstance(resource_payload, str) and is_valid_json(resource_payload):
                resource_json = json.loads(resource_payload)
            elif isinstance(resource_payload, str):
                resource_json = {
                    "format": "xml" if resource_payload.strip().startswith("<") else "text",
                    "resource_type": detect_resource_type(resource_payload),
                    "length": len(resource_payload),
                }
            else:
                resource_json = resource_payload
            request_data = {
                "resource": resource_json,
                "profiles": validation_result.profiles or request.profiles or [],
                "profile": request.profile,
                "ig": request.ig or validation_result.selected_ig,
                "selected_ig": validation_result.selected_ig,
                "resolved_profile": validation_result.resolved_profile,
            }
            test_name = f"Batch Validation {idx + 1}: {validation_result.resource_type}"
            history_service.save_validation_run(
                request_data,
                _result_history_payload(validation_result),
                test_name,
            )
    except Exception as exc:
        print(f"Warning: Failed to save batch validation runs to history: {exc}")

    return result


@router.get("/profiles", response_model=list[str])
async def get_profiles():
    return await inferno_client.get_profiles()


@router.get("/profiles/by-ig")
async def get_profiles_by_ig():
    """Return Inferno's profile map: {packageId[#version]: [profileUrl, ...]}."""
    return await inferno_client.get_profiles_by_ig()
