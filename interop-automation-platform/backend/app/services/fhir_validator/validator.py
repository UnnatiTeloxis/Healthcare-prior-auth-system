import asyncio
import logging

from app.api.v1.fhir_validator.schemas import (
    BatchValidationResult,
    ValidationIssue,
    ValidationResult,
)
from app.services.fhir_validator.inferno_client import inferno_client
from app.utils.fhir_helpers import (
    count_issue_severities,
    detect_resource_type,
    parse_operation_outcome,
)

logger = logging.getLogger(__name__)

# Inferno is CPU-bound; limited concurrency is faster than flooding it.
_BATCH_CONCURRENCY = 4


class ValidationService:
    async def validate_resource(
        self,
        resource: str,
        profiles: list[str],
        resource_type: str | None = None,
    ) -> ValidationResult:
        if not resource_type:
            resource_type = detect_resource_type(resource)

        try:
            operation_outcome = await inferno_client.validate_resource(resource, profiles)
            is_valid, issues = parse_operation_outcome(operation_outcome, resource)
            is_valid, error_count, warning_count, info_count = count_issue_severities(issues)

            return ValidationResult(
                valid=is_valid,
                resource_type=resource_type,
                profiles=profiles,
                issues=[ValidationIssue(**issue) for issue in issues],
                summary=_build_summary(is_valid, issues, error_count, warning_count, info_count),
                error_count=error_count,
                warning_count=warning_count,
                info_count=info_count,
                operation_outcome=operation_outcome,
            )
        except Exception as exc:
            logger.exception("FHIR validation failed")
            return ValidationResult(
                valid=False,
                resource_type=resource_type,
                profiles=profiles,
                issues=[
                    ValidationIssue(
                        severity="error",
                        code="validation-service-error",
                        message=f"Validation service error: {exc}",
                    )
                ],
                summary=f"Validation failed: {exc}",
                error_count=1,
                warning_count=0,
                info_count=0,
            )

    async def validate_batch(
        self,
        resources: list[str],
        profiles: list[str],
    ) -> BatchValidationResult:
        # Warm Inferno once for the whole batch, then validate with limited concurrency.
        await inferno_client.ensure_ready()

        semaphore = asyncio.Semaphore(_BATCH_CONCURRENCY)

        async def _one(resource: str) -> ValidationResult:
            async with semaphore:
                return await self.validate_resource(resource, profiles)

        results = await asyncio.gather(*[_one(resource) for resource in resources])
        valid_count = sum(1 for result in results if result.valid)

        return BatchValidationResult(
            results=results,
            total=len(results),
            valid_count=valid_count,
            invalid_count=len(results) - valid_count,
        )


def _build_summary(
    is_valid: bool,
    issues: list[dict[str, object]],
    error_count: int,
    warning_count: int,
    info_count: int,
) -> str:
    if is_valid:
        if warning_count or info_count:
            return (
                "Validation successful with "
                f"{warning_count} warning(s) and {info_count} information message(s)"
            )
        return "Validation successful - no issues found"

    summary_parts = [f"Validation failed with {error_count} error(s)"]
    missing_fields: list[str] = []
    invalid_fields: list[str] = []

    for issue in issues:
        if issue.get("severity") not in {"error", "fatal"}:
            continue

        message = str(issue.get("message") or "").lower()
        location = issue.get("location")
        if not location:
            continue

        if "minimum required" in message or "required element" in message:
            missing_fields.append(str(location))
        elif "invalid" in message or "not valid" in message:
            invalid_fields.append(str(location))

    if missing_fields:
        summary_parts.append(f"Missing required: {', '.join(sorted(set(missing_fields))[:3])}")
    if invalid_fields:
        summary_parts.append(f"Invalid values in: {', '.join(sorted(set(invalid_fields))[:3])}")

    return " | ".join(summary_parts)


validation_service = ValidationService()
