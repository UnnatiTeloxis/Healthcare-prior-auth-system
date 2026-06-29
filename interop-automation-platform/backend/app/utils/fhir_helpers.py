import json
import re
from typing import Any


def detect_resource_type(resource: str) -> str | None:
    resource = resource.strip()

    if resource.startswith("{"):
        try:
            parsed = json.loads(resource)
        except json.JSONDecodeError:
            return None
        return parsed.get("resourceType")

    if resource.startswith("<"):
        match = re.search(r"<(\w+)\s+xmlns", resource)
        if match:
            return match.group(1)

        match = re.search(r"<(\w+)[\s>]", resource)
        if match:
            return match.group(1)

    return None


def is_valid_json(resource: str) -> bool:
    try:
        json.loads(resource)
        return True
    except json.JSONDecodeError:
        return False


def is_valid_xml(resource: str) -> bool:
    return resource.strip().startswith("<")


_TX_NOISE_PHRASES = (
    "the validator is running without terminology services",
    "could not be found, so the code cannot be validated",
    "Unable to validate code",
    "Unable to check whether the code is in the value set",
    "A definition for CodeSystem",
)

_PROCESS_NOISE_PHRASES = (
    "which is required by the FHIR specification",
    "Validate resource against profile",
    "Validate Observation against the",
    "Validate Patient against the",
)

_PROMOTE_TO_WARNING_PHRASES = (
    "Reference to draft CodeSystem",
    "Reference to draft item",
)


def _is_tx_noise(message: str) -> bool:
    """Return True if the issue is a side-effect of TX being disabled."""
    return any(phrase in message for phrase in _TX_NOISE_PHRASES)


def _is_process_noise(severity: str, message: str) -> bool:
    """Informational messages about what profiles the validator checks (not issues)."""
    if severity != "information":
        return False
    return any(phrase in message for phrase in _PROCESS_NOISE_PHRASES)


def _should_promote_to_warning(severity: str, message: str) -> bool:
    """Inferno's hosted validator reports certain info-level issues as warnings."""
    if severity != "information":
        return False
    return any(phrase in message for phrase in _PROMOTE_TO_WARNING_PHRASES)


def parse_operation_outcome(operation_outcome: dict[str, Any]) -> tuple[bool, list[dict[str, Any]]]:
    issues: list[dict[str, Any]] = []
    has_errors = False

    if not operation_outcome or "issue" not in operation_outcome:
        return True, issues

    for issue in operation_outcome.get("issue", []):
        severity = issue.get("severity", "information")
        code = issue.get("code", "unknown")

        if severity == "fatal":
            has_errors = True
        elif severity == "error":
            has_errors = True

        message = ""
        details = issue.get("details") or {}
        if isinstance(details, dict):
            message = details.get("text") or ""
        if not message:
            message = issue.get("diagnostics") or ""

        if _is_tx_noise(message):
            continue

        if _is_process_noise(severity, message):
            continue

        if _should_promote_to_warning(severity, message):
            severity = "warning"

        location = None
        expression = issue.get("expression")
        raw_location = issue.get("location")
        if expression:
            location = expression[0] if isinstance(expression, list) else expression
        elif raw_location:
            location = raw_location[0] if isinstance(raw_location, list) else raw_location

        line = None
        column = None
        for extension in issue.get("extension", []):
            extension_url = extension.get("url", "")
            if extension_url.endswith("operationoutcome-issue-line"):
                line = extension.get("valueInteger")
            elif extension_url.endswith("operationoutcome-issue-col"):
                column = extension.get("valueInteger")

        issues.append(
            {
                "severity": severity,
                "code": code,
                "message": message,
                "location": location,
                "line": line,
                "column": column,
            }
        )

    seen: set[tuple[str, str, str]] = set()
    deduped: list[dict[str, Any]] = []
    for iss in issues:
        loc = iss.get("location") or ""
        norm_loc = re.sub(r"/\*[^*]*\*/", "", loc).rstrip("/")
        key = (iss["severity"], iss["message"], norm_loc)
        if key not in seen:
            seen.add(key)
            deduped.append(iss)

    return not has_errors, deduped
