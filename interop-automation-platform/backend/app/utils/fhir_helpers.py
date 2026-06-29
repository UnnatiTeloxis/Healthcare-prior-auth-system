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

    return not has_errors, issues
