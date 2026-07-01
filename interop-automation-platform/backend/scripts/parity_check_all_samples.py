#!/usr/bin/env python3
"""Cross-check all FHIR sample files: wrapper vs API vs expected parity."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.utils.fhir_helpers import count_operation_outcome_severities, parse_operation_outcome

SAMPLES_ROOT = Path(__file__).resolve().parents[2] / "data/fhir-validator-samples"
WRAPPER = "http://localhost:4567"
BACKEND = "http://localhost:8000/api/v1/fhir/validate"


def counts_label(outcome: dict) -> str:
    _, e, w, i = count_operation_outcome_severities(outcome)
    return f"{e}/{w}/{i}"


def issue_fingerprints(outcome: dict) -> list[tuple[str, str, str]]:
    fps = []
    for issue in outcome.get("issue", []):
        sev = issue.get("severity", "information")
        loc = issue.get("expression") or issue.get("location") or [""]
        loc_s = loc[0] if isinstance(loc, list) else str(loc)
        msg = (issue.get("details") or {}).get("text") or issue.get("diagnostics") or ""
        fps.append((sev, loc_s, msg[:100]))
    return sorted(fps)


def collect_json_files() -> list[Path]:
    files: list[Path] = []
    for pattern in ("inferno-parity-suite/**/*.json", "test-suite/*.json"):
        files.extend(SAMPLES_ROOT.glob(pattern))
    return sorted(set(files))


def main() -> int:
    files = collect_json_files()
    client = httpx.Client(timeout=600.0)
    mismatches: list[str] = []
    api_wrapper_mismatch: list[str] = []

    # Preload US Core like Inferno hosted so wrapper and API see the same IG state.
    try:
        ig_resp = client.put(
            f"{WRAPPER}/igs/hl7.fhir.us.core",
            params={"version": "6.1.0"},
            timeout=600.0,
        )
        print(f"Preloaded US Core IG: HTTP {ig_resp.status_code}\n")
    except Exception as exc:
        print(f"Warning: US Core IG preload failed: {exc}\n")

    print(f"Running {len(files)} JSON samples...\n")
    print(f"{'File':<70} {'Wrapper':<10} {'API':<10} {'Match'}")
    print("-" * 100)

    for path in files:
        rel = path.relative_to(SAMPLES_ROOT).as_posix()
        resource = path.read_text(encoding="utf-8")

        # Skip invalid JSON syntax samples
        try:
            json.loads(resource)
        except json.JSONDecodeError:
            print(f"{rel:<70} {'SKIP':<10} {'SKIP':<10} invalid-json")
            continue

        wrapper_out = client.post(
            f"{WRAPPER}/validate",
            content=resource,
            headers={"Content-Type": "application/json"},
        ).json()
        api_resp = client.post(BACKEND, json={"resource": resource, "profiles": []}).json()

        w_label = counts_label(wrapper_out)
        api_label = f"{api_resp.get('error_count', '?')}/{api_resp.get('warning_count', '?')}/{api_resp.get('info_count', '?')}"
        match = w_label == api_label

        # Deep compare operation_outcome from API vs wrapper
        api_outcome = api_resp.get("operation_outcome") or {}
        w_fps = issue_fingerprints(wrapper_out)
        a_fps = issue_fingerprints(api_outcome)

        if w_fps != a_fps:
            match = False
            api_wrapper_mismatch.append(rel)

        status = "OK" if match else "MISMATCH"
        print(f"{rel:<70} {w_label:<10} {api_label:<10} {status}")

        if not match:
            mismatches.append(rel)

    print("\n=== MISMATCH DETAILS ===")
    for rel in mismatches:
        path = SAMPLES_ROOT / rel.replace("/", "\\") if "\\" not in rel else SAMPLES_ROOT / rel
        if not path.exists():
            path = SAMPLES_ROOT / rel
        resource = path.read_text(encoding="utf-8")
        wrapper_out = client.post(
            f"{WRAPPER}/validate",
            content=resource,
            headers={"Content-Type": "application/json"},
        ).json()
        api_resp = client.post(BACKEND, json={"resource": resource, "profiles": []}).json()
        print(f"\n--- {rel} ---")
        print(f"  wrapper: {counts_label(wrapper_out)}")
        print(f"  api:     {api_resp.get('error_count')}/{api_resp.get('warning_count')}/{api_resp.get('info_count')}")
        w_fps = issue_fingerprints(wrapper_out)
        a_fps = issue_fingerprints(api_resp.get("operation_outcome") or {})
        only_w = set(w_fps) - set(a_fps)
        only_a = set(a_fps) - set(w_fps)
        if only_w:
            print("  only in wrapper:")
            for x in list(only_w)[:5]:
                print(f"    {x}")
        if only_a:
            print("  only in api:")
            for x in list(only_a)[:5]:
                print(f"    {x}")

    client.close()
    print(f"\nTotal: {len(files)} | Mismatches: {len(mismatches)}")
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
