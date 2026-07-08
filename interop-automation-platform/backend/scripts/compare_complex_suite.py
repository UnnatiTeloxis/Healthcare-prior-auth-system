"""Compare raw Inferno wrapper output vs parse_operation_outcome for complex suite."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.utils.fhir_helpers import parse_operation_outcome  # noqa: E402

SUITE_DIR = Path(__file__).resolve().parents[2] / "data/fhir-validator-samples/inferno-parity-suite/complex"
WRAPPER = "http://localhost:4567"
BACKEND = "http://localhost:8000/api/v1/fhir/validate"


def count_issues(issues: list[dict]) -> dict[str, int]:
    return {
        "errors": sum(1 for i in issues if i.get("severity") in ("error", "fatal")),
        "warnings": sum(1 for i in issues if i.get("severity") == "warning"),
        "info": sum(1 for i in issues if i.get("severity") == "information"),
    }


def raw_counts(outcome: dict) -> dict[str, int]:
    issues = outcome.get("issue", [])
    return {
        "errors": sum(1 for i in issues if i.get("severity") in ("error", "fatal")),
        "warnings": sum(1 for i in issues if i.get("severity") == "warning"),
        "info": sum(1 for i in issues if i.get("severity") == "information"),
    }


def main() -> None:
    files = sorted(SUITE_DIR.glob("*.json"))
    client = httpx.Client(timeout=600.0)
    mismatches = []

    print(f"{'File':<55} {'Raw E/W/I':<16} {'Parsed E/W/I':<16} {'API E/W/I':<16} Match")
    print("-" * 120)

    for path in files:
        resource = path.read_text(encoding="utf-8")
        raw = client.post(f"{WRAPPER}/validate", content=resource, headers={"Content-Type": "application/json"}).json()
        raw_c = raw_counts(raw)
        _, parsed_issues = parse_operation_outcome(raw)
        parsed_c = count_issues(parsed_issues)

        api = client.post(BACKEND, json={"resource": resource, "profiles": []}).json()
        api_c = {
            "errors": api.get("error_count", 0),
            "warnings": api.get("warning_count", 0),
            "info": api.get("info_count", 0),
        }

        raw_s = f"{raw_c['errors']}/{raw_c['warnings']}/{raw_c['info']}"
        parsed_s = f"{parsed_c['errors']}/{parsed_c['warnings']}/{parsed_c['info']}"
        api_s = f"{api_c['errors']}/{api_c['warnings']}/{api_c['info']}"

        # Inferno hosted parity target: after DISPLAY_ISSUES_ARE_WARNINGS, info->warning for display issues
        # Our parsed should align with what Inferno UI shows (not raw wrapper when filtered)
        match = parsed_c == api_c
        flag = "OK" if match else "MISMATCH"
        if raw_c != parsed_c or not match:
            mismatches.append((path.name, raw_c, parsed_c, api_c, raw, parsed_issues))

        print(f"{path.name:<55} {raw_s:<16} {parsed_s:<16} {api_s:<16} {flag}")

    print("\n=== FILTERING DELTA (raw vs parsed) ===")
    for name, raw_c, parsed_c, api_c, raw, parsed_issues in mismatches:
        if raw_c == parsed_c and parsed_c == api_c:
            continue
        print(f"\n--- {name} ---")
        print(f"  raw:    {raw_c}")
        print(f"  parsed: {parsed_c}")
        print(f"  api:    {api_c}")
        raw_msgs = []
        for issue in raw.get("issue", []):
            msg = (issue.get("details") or {}).get("text") or issue.get("diagnostics") or ""
            raw_msgs.append((issue.get("severity"), issue.get("expression") or issue.get("location"), msg[:120]))
        parsed_msgs = [(i["severity"], i.get("location"), i["message"][:120]) for i in parsed_issues]
        dropped = [m for m in raw_msgs if m not in [(p[0], p[1], p[2]) for p in parsed_msgs]]
        print("  dropped/changed by filter:")
        for sev, loc, msg in raw_msgs:
            in_parsed = any(p[2].startswith(msg[:80]) or msg.startswith(p[2][:80]) for p in parsed_msgs if p[0] == sev or (sev == "information" and p[0] == "warning"))
            if not in_parsed:
                print(f"    [{sev}] {loc}: {msg}")

    client.close()


if __name__ == "__main__":
    main()
