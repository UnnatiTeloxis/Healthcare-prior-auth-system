import json

from fastapi import APIRouter, BackgroundTasks

from app.api.v1.fhir_validator.schemas import (
    BatchValidationRequest,
    BatchValidationResult,
    ValidationRequest,
    ValidationResult,
)
from app.services.fhir_validator.inferno_client import inferno_client
from app.services.fhir_validator.history_service import history_service
from app.services.fhir_validator.validator import validation_service
from app.utils.fhir_helpers import detect_resource_type, is_valid_json

router = APIRouter()


def _save_history_safe(request: ValidationRequest, result: ValidationResult) -> None:
    """Persist validation history off the request critical path (latency)."""
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
            "profiles": request.profiles or [],
            "resource_type": request.resource_type,
        }
        response_data = {
            "valid": result.valid,
            "resource_type": result.resource_type,
            "profiles": result.profiles,
            "summary": result.summary,
            "error_count": result.error_count,
            "warning_count": result.warning_count,
            "info_count": result.info_count,
            "issues": [
                issue.model_dump() if hasattr(issue, "model_dump") else issue.dict()
                for issue in result.issues
            ],
            "operation_outcome": result.operation_outcome,
        }
        history_service.save_validation_run(request_data, response_data)
    except Exception as exc:
        print(f"Warning: Failed to save validation run to history: {exc}")


@router.get("/health")
async def fhir_health():
    import os

    version = await inferno_client.get_version()
    disable_tx = os.getenv("DISABLE_TX", "true").strip().lower() in {"1", "true", "yes"}
    display_as_warnings = os.getenv("DISPLAY_ISSUES_ARE_WARNINGS", "false").strip().lower() in {
        "1",
        "true",
        "yes",
    }
    return {
        "status": "ok",
        "tool": "fhir-validator",
        "inferno_url": inferno_client.base_url,
        "validator": version,
        "inferno_parity": {
            "disable_tx": disable_tx,
            "display_issues_are_warnings": display_as_warnings,
            "content_type": "application/fhir+json",
            "note": (
                "Structure/profile issues match the local Inferno wrapper. "
                "With DISABLE_TX=true, offline CTS/LOINC terminology noise is "
                "suppressed by default (SUPPRESS_OFFLINE_TX_WARNINGS) so UI results "
                "align closer to hosted Inferno with live TX. Raw OperationOutcome "
                "is still returned on the response for inspection."
                if disable_tx
                else "Live terminology enabled — closest match to hosted Inferno Resource Validator."
            ),
            "suppress_offline_tx_warnings": (
                disable_tx
                and os.getenv("SUPPRESS_OFFLINE_TX_WARNINGS", "true").strip().lower()
                in {"1", "true", "yes"}
            ),
        },
    }


@router.post("/", response_model=ValidationResult)
@router.post("/validate", response_model=ValidationResult)
async def validate_resource(request: ValidationRequest, background_tasks: BackgroundTasks):
    result = await validation_service.validate_resource(
        resource=request.resource,
        profiles=request.profiles,
        resource_type=request.resource_type,
    )
    # Do not block the validate response on disk I/O — Inferno latency stays dominant.
    background_tasks.add_task(_save_history_safe, request, result)
    return result


@router.post("/batch", response_model=BatchValidationResult)
async def validate_batch(request: BatchValidationRequest):
    result = await validation_service.validate_batch(
        resources=request.resources,
        profiles=request.profiles,
    )
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
                "profiles": request.profiles or [],
            }
            response_data = {
                "valid": validation_result.valid,
                "resource_type": validation_result.resource_type,
                "profiles": validation_result.profiles,
                "summary": validation_result.summary,
                "error_count": validation_result.error_count,
                "warning_count": validation_result.warning_count,
                "info_count": validation_result.info_count,
                "issues": [issue.dict() for issue in validation_result.issues],
                "operation_outcome": validation_result.operation_outcome,
            }
            test_name = f"Batch Validation {idx + 1}: {validation_result.resource_type}"
            history_service.save_validation_run(request_data, response_data, test_name)
    except Exception as exc:
        print(f"Warning: Failed to save batch validation runs to history: {exc}")

    return result


@router.get("/profiles", response_model=list[str])
async def get_profiles():
    return await inferno_client.get_profiles()


@router.get("/profiles/by-ig")
async def get_profiles_by_ig():
    return await inferno_client.get_profiles_by_ig()
