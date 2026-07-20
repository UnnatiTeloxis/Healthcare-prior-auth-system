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


def profile_url_to_package_id(profile_url: str) -> str | None:
    """Best-effort map from a StructureDefinition URL to an NPM package id."""
    url = (profile_url or "").lower()
    if "/us/core/" in url or "hl7.org/fhir/us/core" in url:
        return "hl7.fhir.us.core"
    if "/davinci-crd/" in url or "davinci.crd" in url:
        return "hl7.fhir.us.davinci-crd"
    if "/davinci-dtr/" in url or "davinci.dtr" in url:
        return "hl7.fhir.us.davinci-dtr"
    if "/davinci-pas/" in url or "davinci.pas" in url:
        return "hl7.fhir.us.davinci-pas"
    # Generic HL7 path: http://hl7.org/fhir/{realm}/{guide}/StructureDefinition/...
    match = re.search(r"hl7\.org/fhir/([a-z0-9\-]+)/([a-z0-9\.\-]+)/structuredefinition/", url)
    if match:
        realm, guide = match.group(1), match.group(2)
        return f"hl7.fhir.{realm}.{guide}"
    return None


def extract_meta_profiles(resource: str) -> list[str]:
    """Collect profile URLs from a resource or nested bundle entries (JSON or XML)."""
    text = resource.strip()
    profiles: list[str] = []

    if text.startswith("<"):
        # FHIR XML: <profile value="http://..."/> or <profile value='...'/>
        for match in re.finditer(r'<profile\s+value=["\']([^"\']+)["\']', text, flags=re.IGNORECASE):
            url = match.group(1).strip()
            if url and url not in profiles:
                profiles.append(url)
        return profiles

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return []

    def add_from(obj: dict[str, Any]) -> None:
        if not isinstance(obj, dict):
            return
        meta = obj.get("meta")
        if isinstance(meta, dict):
            for url in meta.get("profile") or []:
                if isinstance(url, str) and url not in profiles:
                    profiles.append(url)

    if isinstance(parsed, dict):
        add_from(parsed)
        if parsed.get("resourceType") == "Bundle":
            for entry in parsed.get("entry") or []:
                if isinstance(entry, dict):
                    add_from(entry.get("resource") or {})

    return profiles


def _issue_message(issue: dict[str, Any]) -> str:
    details = issue.get("details") or {}
    if isinstance(details, dict):
        message = details.get("text") or ""
        if message:
            return message
    return issue.get("diagnostics") or ""


def _issue_location(issue: dict[str, Any]) -> str | None:
    expression = issue.get("expression")
    raw_location = issue.get("location")
    if expression:
        return expression[0] if isinstance(expression, list) else expression
    if raw_location:
        return raw_location[0] if isinstance(raw_location, list) else raw_location
    return None


def count_operation_outcome_severities(
    operation_outcome: dict[str, Any] | None,
) -> tuple[bool, int, int, int]:
    """Count severities directly from the validator OperationOutcome (Inferno parity)."""
    issues = operation_outcome.get("issue", []) if operation_outcome else []
    return count_issue_severities(issues)


def count_issue_severities(
    issues: list[dict[str, Any]],
) -> tuple[bool, int, int, int]:
    error_count = sum(1 for issue in issues if issue.get("severity") in {"error", "fatal"})
    warning_count = sum(1 for issue in issues if issue.get("severity") == "warning")
    info_count = sum(1 for issue in issues if issue.get("severity") == "information")
    return error_count == 0, error_count, warning_count, info_count


def parse_operation_outcome(
    operation_outcome: dict[str, Any],
    resource: str | None = None,
) -> tuple[bool, list[dict[str, Any]]]:
    """Map OperationOutcome issues 1:1 from Inferno — no severity or message changes."""
    del resource  # call-site compatibility only; never mutates issues
    if not operation_outcome or "issue" not in operation_outcome:
        return True, []

    is_valid, _, _, _ = count_operation_outcome_severities(operation_outcome)
    issues: list[dict[str, Any]] = []

    for issue in operation_outcome.get("issue", []):
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
                "severity": issue.get("severity", "information"),
                "code": issue.get("code", "unknown"),
                "message": _issue_message(issue),
                "location": _issue_location(issue),
                "line": line,
                "column": column,
            }
        )

    return is_valid, issues
