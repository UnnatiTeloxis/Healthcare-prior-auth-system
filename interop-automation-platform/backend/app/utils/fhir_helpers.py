import json
import os
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


def _env_flag(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes"}


def _suppress_offline_tx_noise() -> bool:
    """
    When terminology is offline (DISABLE_TX), Inferno cannot reach CTS/VSAC or use
    LOINC. That produces ValueSet-not-found / false 'not in ValueSet' warnings that
    hosted Inferno (live TX) does not show. Suppress those by default for UI parity.
    """
    if _env_flag("SUPPRESS_OFFLINE_TX_WARNINGS", "true"):
        return _env_flag("DISABLE_TX", "true")
    return False


_OFFLINE_TX_NOISE = (
    re.compile(r"ValueSet\s+'https?://cts\.nlm\.nih\.gov/[^']+'\s+not found", re.I),
    re.compile(
        r"A definition for CodeSystem\s+'https?://loinc\.org'\s+could not be found",
        re.I,
    ),
    re.compile(
        r"A definition for CodeSystem\s+'https?://www\.nlm\.nih\.gov/research/umls/rxnorm'\s+could not be found",
        re.I,
    ),
    re.compile(
        r"Unable to check whether the code is in the value set .+ because the code system https?://loinc\.org was not found",
        re.I,
    ),
    re.compile(
        r"None of the codings provided are in the value set .+"
        r"(cts\.nlm\.nih\.gov|observation-vitalsignresult|Vital Sign Result Type|us-core-vital-signs)",
        re.I,
    ),
    re.compile(
        r"The code provided \(https?://unitsofmeasure\.org#[^)]+\) is not in the value set "
        r"'Vital Signs Units'",
        re.I,
    ),
    re.compile(
        r"Resolved system https?://unitsofmeasure\.org .+, but the definition is only a fragment",
        re.I,
    ),
)


def _is_offline_tx_noise(message: str) -> bool:
    text = (message or "").strip()
    if not text:
        return False
    return any(pattern.search(text) for pattern in _OFFLINE_TX_NOISE)


def count_operation_outcome_severities(
    operation_outcome: dict[str, Any] | None,
) -> tuple[bool, int, int, int]:
    """Count severities directly from the validator OperationOutcome (Inferno parity)."""
    issues = operation_outcome.get("issue", []) if operation_outcome else []
    return count_issue_severities(issues)


def count_issue_severities(
    issues: list[dict[str, Any]],
) -> tuple[bool, int, int, int]:
    """
    Count severities exactly as Inferno/HL7 OperationOutcome reports them.
    Never remaps error↔warning. Treats legacy \"info\" as information.
    valid == no error and no fatal (Inferno Resource Validator semantics).
    """
    error_count = 0
    warning_count = 0
    info_count = 0
    for issue in issues:
        severity = str(issue.get("severity") or "information").lower().strip()
        if severity in {"error", "fatal"}:
            error_count += 1
        elif severity == "warning":
            warning_count += 1
        elif severity in {"information", "info"}:
            info_count += 1
        else:
            # Unknown severities stay visible as information — do not promote/demote.
            info_count += 1
    return error_count == 0, error_count, warning_count, info_count


def _normalize_issue_severity(raw: Any) -> str:
    """Passthrough Inferno severities; only normalize the legacy alias info→information."""
    severity = str(raw or "information").lower().strip()
    if severity == "info":
        return "information"
    if severity in {"fatal", "error", "warning", "information"}:
        return severity
    return "information"


def parse_operation_outcome(
    operation_outcome: dict[str, Any],
    resource: str | None = None,
) -> tuple[bool, list[dict[str, Any]]]:
    """Map OperationOutcome issues from Inferno; optionally drop offline TX noise."""
    del resource  # call-site compatibility only; never mutates issues
    if not operation_outcome or "issue" not in operation_outcome:
        return True, []

    suppress_tx = _suppress_offline_tx_noise()
    issues: list[dict[str, Any]] = []

    for issue in operation_outcome.get("issue", []):
        message = _issue_message(issue)
        if suppress_tx and _is_offline_tx_noise(message):
            continue

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
                "severity": _normalize_issue_severity(issue.get("severity")),
                "code": issue.get("code", "unknown"),
                "message": message,
                "location": _issue_location(issue),
                "line": line,
                "column": column,
            }
        )

    is_valid, _, _, _ = count_issue_severities(issues)
    return is_valid, issues
