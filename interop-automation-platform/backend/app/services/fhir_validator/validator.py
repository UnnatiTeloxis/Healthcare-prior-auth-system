import asyncio
import logging
import re

from app.api.v1.fhir_validator.schemas import (
    BatchValidationResult,
    ValidationIssue,
    ValidationResult,
)
from app.services.fhir_validator.inferno_client import (
    ProfileValidationError,
    _split_ig_spec,
    inferno_client,
)
from app.utils.fhir_helpers import (
    count_issue_severities,
    detect_resource_type,
    extract_meta_profiles,
    parse_operation_outcome,
)

logger = logging.getLogger(__name__)


class ProfileResolutionError(Exception):
    """Raised when an IG is selected but a unique validation profile cannot be resolved."""

    def __init__(self, message: str, candidates: list[str] | None = None):
        super().__init__(message)
        self.message = message
        self.candidates = candidates or []


def _profile_belongs_to_package(profile_url: str, package_id: str) -> bool:
    url_lower = (profile_url or "").lower()
    package_lower = (package_id or "").lower()
    if "us.core" in package_lower or "us-core" in package_lower:
        return "/us/core/" in url_lower
    if "davinci-crd" in package_lower or "davinci.crd" in package_lower:
        return "/davinci-crd/" in url_lower
    if "davinci-dtr" in package_lower or "davinci.dtr" in package_lower:
        return "/davinci-dtr/" in url_lower
    if "davinci-pas" in package_lower or "davinci.pas" in package_lower:
        return "/davinci-pas/" in url_lower
    # Fallback: package fragment after last '.' often appears in path
    token = package_lower.rsplit(".", 1)[-1].replace("_", "-")
    return bool(token) and token in url_lower


def _normalize_explicit_profiles(profiles: list[str] | None, profile: str | None) -> list[str]:
    ordered: list[str] = []
    if profile:
        ordered.append(profile.strip())
    for url in profiles or []:
        cleaned = (url or "").strip()
        if cleaned and cleaned not in ordered:
            ordered.append(cleaned)
    return ordered


async def resolve_validation_profiles(
    *,
    resource: str,
    ig: str | None,
    profiles: list[str] | None,
    profile: str | None,
    resource_type: str | None,
) -> tuple[list[str], str | None, str | None, str | None]:
    """
    Resolve profiles for validation.

    Returns (profiles, selected_ig, package_id, package_version).
    Profile precedence when an IG is selected:
      1. Explicit profile(s) from the request
      2. meta.profile entries that belong to the selected IG
      3. Best resource-type match from profiles-by-ig
      4. Ambiguous / missing -> ProfileResolutionError (API maps to 422)
    """
    selected_ig = (ig or "").strip() or None
    package_id: str | None = None
    package_version: str | None = None
    resolved = _normalize_explicit_profiles(profiles, profile)

    if not selected_ig:
        return resolved, None, None, None

    package_id, package_version = _split_ig_spec(selected_ig)
    if not package_id:
        raise ProfileResolutionError("Invalid ig value; expected packageId or packageId#version")

    selected_ig = f"{package_id}#{package_version}" if package_version else package_id

    try:
        await inferno_client.load_ig_by_id(package_id, package_version)
    except Exception as exc:
        raise ProfileResolutionError(
            f"Failed to load Implementation Guide {selected_ig}: {exc}"
        ) from exc

    if resolved:
        for url in resolved:
            if not _profile_belongs_to_package(url, package_id):
                raise ProfileResolutionError(
                    f"Profile {url} does not belong to selected IG {selected_ig}"
                )
        return resolved, selected_ig, package_id, package_version

    meta_profiles = [
        url
        for url in extract_meta_profiles(resource)
        if _profile_belongs_to_package(url, package_id)
    ]
    if meta_profiles:
        return meta_profiles, selected_ig, package_id, package_version

    if not resource_type:
        resource_type = detect_resource_type(resource)
    if not resource_type:
        raise ProfileResolutionError(
            f"Could not detect resource type for IG {selected_ig}; select a profile explicitly"
        )

    candidates = await inferno_client.resolve_profiles_for_ig(selected_ig, resource_type)
    if len(candidates) == 1:
        return candidates, selected_ig, package_id, package_version
    if len(candidates) > 1:
        raise ProfileResolutionError(
            (
                f"Multiple {resource_type} profiles found for {selected_ig}. "
                "Select one explicitly before validating."
            ),
            candidates=candidates,
        )
    raise ProfileResolutionError(
        f"No {resource_type} profile found for {selected_ig}; select a profile explicitly"
    )


class ValidationService:
    async def validate_resource(
        self,
        resource: str,
        profiles: list[str] | None = None,
        resource_type: str | None = None,
        *,
        ig: str | None = None,
        profile: str | None = None,
    ) -> ValidationResult:
        if not resource_type:
            resource_type = detect_resource_type(resource)

        resolved_profiles, selected_ig, package_id, package_version = await resolve_validation_profiles(
            resource=resource,
            ig=ig,
            profiles=profiles,
            profile=profile,
            resource_type=resource_type,
        )
        resolved_profile = resolved_profiles[0] if resolved_profiles else None

        try:
            operation_outcome = await inferno_client.validate_resource(resource, resolved_profiles)
            is_valid, issues = parse_operation_outcome(operation_outcome, resource)
            is_valid, error_count, warning_count, info_count = count_issue_severities(issues)

            return ValidationResult(
                valid=is_valid,
                resource_type=resource_type,
                profiles=resolved_profiles,
                issues=[ValidationIssue(**issue) for issue in issues],
                summary=_build_summary(is_valid, issues, error_count, warning_count, info_count),
                error_count=error_count,
                warning_count=warning_count,
                info_count=info_count,
                operation_outcome=operation_outcome,
                selected_ig=selected_ig,
                resolved_profile=resolved_profile,
                package_id=package_id,
                package_version=package_version,
            )
        except ProfileValidationError as exc:
            logger.exception("Profile-specific FHIR validation failed without base-FHIR fallback")
            return ValidationResult(
                valid=False,
                resource_type=resource_type,
                profiles=resolved_profiles,
                issues=[
                    ValidationIssue(
                        severity="error",
                        code="profile-validation-error",
                        message=str(exc),
                    )
                ],
                summary=f"Validation failed for profile(s): {exc}",
                error_count=1,
                warning_count=0,
                info_count=0,
                selected_ig=selected_ig,
                resolved_profile=resolved_profile,
                package_id=package_id,
                package_version=package_version,
            )
        except Exception as exc:
            logger.exception("FHIR validation failed")
            return ValidationResult(
                valid=False,
                resource_type=resource_type,
                profiles=resolved_profiles,
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
                selected_ig=selected_ig,
                resolved_profile=resolved_profile,
                package_id=package_id,
                package_version=package_version,
            )

    async def validate_batch(
        self,
        resources: list[str],
        profiles: list[str] | None = None,
        *,
        ig: str | None = None,
        profile: str | None = None,
    ) -> BatchValidationResult:
        results = await asyncio.gather(
            *[
                self.validate_resource(resource, profiles, ig=ig, profile=profile)
                for resource in resources
            ]
        )
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


_RESOURCE_TYPE_RE = re.compile(r"(?<!^)(?=[A-Z])")


def resource_type_to_slug(resource_type: str) -> str:
    return _RESOURCE_TYPE_RE.sub("-", resource_type).lower()


validation_service = ValidationService()
