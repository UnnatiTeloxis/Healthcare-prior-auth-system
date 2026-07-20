"""Compare our API OperationOutcome vs direct Inferno wrapper on the same inputs."""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SAMPLE = ROOT / "test-cases" / "hl7.fhir.us.core" / "01-patient-valid.json"
PROFILE = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"


def post_json(url: str, data: bytes, headers: dict | None = None) -> dict:
    req = urllib.request.Request(
        url,
        data=data,
        headers=headers or {"Content-Type": "application/fhir+json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read().decode("utf-8"))


def issue_key(issue: dict) -> tuple:
    details = issue.get("details") or {}
    msg = issue.get("diagnostics") or (details.get("text") if isinstance(details, dict) else "") or issue.get("message") or ""
    loc = ""
    if issue.get("expression"):
        loc = issue["expression"][0] if isinstance(issue["expression"], list) else str(issue["expression"])
    elif issue.get("location"):
        loc = issue["location"][0] if isinstance(issue["location"], list) else str(issue["location"])
    elif issue.get("location") is None and issue.get("location") == "":
        loc = ""
    return (
        str(issue.get("severity") or ""),
        str(issue.get("code") or ""),
        str(msg)[:200],
        str(loc),
    )


def summarize(label: str, issues: list[dict]) -> None:
    c = Counter(i.get("severity") for i in issues)
    print(f"\n=== {label} ({len(issues)} issues) ===")
    for sev in ("fatal", "error", "warning", "information"):
        print(f"  {sev}: {c.get(sev, 0)}")
    for i in issues[:12]:
        details = i.get("details") or {}
        msg = i.get("diagnostics") or (details.get("text") if isinstance(details, dict) else "") or i.get("message")
        print(f"  [{i.get('severity')}] {msg}")


def main() -> None:
    resource = SAMPLE.read_text(encoding="utf-8")

    # 1) Direct Inferno with profile (Advanced mode)
    q = "?" + urllib.parse.urlencode({"profile": PROFILE})
    direct_profile = post_json(
        f"http://localhost:4567/validate{q}",
        resource.encode("utf-8"),
        {"Content-Type": "application/fhir+json"},
    )
    summarize("Inferno direct + profile", direct_profile.get("issue") or [])

    # 2) Direct Inferno WITHOUT profile (meta.profile only — default mode)
    direct_meta = post_json(
        "http://localhost:4567/validate",
        resource.encode("utf-8"),
        {"Content-Type": "application/fhir+json"},
    )
    summarize("Inferno direct meta.profile only", direct_meta.get("issue") or [])

    # 3) Our API with profile
    api = post_json(
        "http://localhost:8000/api/v1/fhir/validate",
        json.dumps(
            {
                "resource": resource,
                "profiles": [PROFILE],
                "resource_type": "Patient",
            }
        ).encode("utf-8"),
        {"Content-Type": "application/json"},
    )
    print(
        f"\n=== API wrapper valid={api.get('valid')} e={api.get('error_count')} "
        f"w={api.get('warning_count')} i={api.get('info_count')} ==="
    )
    for i in (api.get("issues") or [])[:12]:
        print(f"  [{i.get('severity')}] {i.get('message')}")

    # Diff keys
    d_keys = {issue_key(i) for i in (direct_profile.get("issue") or [])}
    a_oo = api.get("operation_outcome") or {}
    a_keys = {issue_key(i) for i in (a_oo.get("issue") or [])}
    print("\n=== Diff direct vs API operation_outcome ===")
    print("only in direct:", len(d_keys - a_keys))
    for k in list(d_keys - a_keys)[:5]:
        print("  ", k)
    print("only in api OO:", len(a_keys - d_keys))
    for k in list(a_keys - d_keys)[:5]:
        print("  ", k)

    # Also compare API issues list vs OO
    api_issue_keys = {
        (
            i.get("severity"),
            i.get("code"),
            (i.get("message") or "")[:200],
            i.get("location") or "",
        )
        for i in (api.get("issues") or [])
    }
    print("\nAPI issues count", len(api_issue_keys), "OO count", len(a_keys))


if __name__ == "__main__":
    main()
