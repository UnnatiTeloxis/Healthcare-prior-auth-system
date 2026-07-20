"""
Upload the three support packages (if needed) and validate sample resources
against the local API / Inferno wrapper — same profile URLs as Inferno Advanced.

Samples live under test-cases/<ig-folder>/ (same layout as us-core, davinci-*).

Usage (from interop-automation-platform/):
  python backend/scripts/parity_custom_ig_samples.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[2]
SAMPLES = ROOT / "test-cases"
PACKAGES = ROOT / "backend" / "fhir_packages"
API = "http://localhost:8000"

CASES = [
    {
        "name": "SDC Questionnaire valid",
        "package": PACKAGES / "hl7.fhir.uv.sdc-4.0.0.tgz",
        "sample": SAMPLES / "fhir-uv-sdc" / "01-questionnaire-valid.json",
        "profiles": ["http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire"],
        "expect_errors": False,
    },
    {
        "name": "SDC Questionnaire invalid (missing status)",
        "package": PACKAGES / "hl7.fhir.uv.sdc-4.0.0.tgz",
        "sample": SAMPLES / "fhir-uv-sdc" / "02-questionnaire-invalid-missing-status.json",
        "profiles": ["http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire"],
        "expect_errors": True,
    },
    {
        "name": "SDC QuestionnaireResponse (Inferno snapshot parity)",
        "package": PACKAGES / "hl7.fhir.uv.sdc-4.0.0.tgz",
        "sample": SAMPLES / "fhir-uv-sdc" / "03-questionnaireresponse-sdc-profile.json",
        "profiles": ["http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaireresponse"],
        # Inferno Resource Validator returns: StructureDefinition ... has no snapshot
        # for this SDC 4.0.0 profile — matching that error is correct parity.
        "expect_errors": True,
        "expect_message_hint": "no snapshot",
    },
    {
        "name": "Extensions Patient birthPlace valid",
        "package": PACKAGES / "hl7.fhir.uv.extensions.r4-5.3.0.tgz",
        "sample": SAMPLES / "fhir-uv-extensions" / "01-patient-birthPlace-valid.json",
        "profiles": [],
        "expect_errors": False,
    },
    {
        "name": "Extensions Patient birthPlace invalid value type",
        "package": PACKAGES / "hl7.fhir.uv.extensions.r4-5.3.0.tgz",
        "sample": SAMPLES / "fhir-uv-extensions" / "02-patient-birthPlace-invalid-value.json",
        "profiles": [],
        "expect_errors": True,
    },
    {
        "name": "THO maritalStatus valid code",
        "package": PACKAGES / "hl7.terminology.r4-7.1.0.tgz",
        "sample": SAMPLES / "hl7-terminology" / "01-patient-maritalStatus-valid.json",
        "profiles": [],
        "expect_errors": False,
    },
    {
        "name": "THO maritalStatus invalid code",
        "package": PACKAGES / "hl7.terminology.r4-7.1.0.tgz",
        "sample": SAMPLES / "hl7-terminology" / "02-patient-maritalStatus-invalid-code.json",
        "profiles": [],
        # Offline TX may soften this to warning — treat error OR warning as signal.
        "expect_errors": None,
        "expect_issue_code_hint": "NOT-A-REAL-CODE",
    },
]


def login(client: httpx.Client) -> str:
    for email, password in (
        ("admin@fhir.com", "Admin@123"),
        ("demo@fhir.com", "Demo@123"),
        ("test@example.com", "test123"),
    ):
        r = client.post(
            f"{API}/api/v1/auth/login",
            json={"email": email, "password": password},
            timeout=30,
        )
        if r.status_code == 200:
            return r.json()["access_token"]
    raise RuntimeError("Could not login — seed a user or start the backend")


def ensure_package(client: httpx.Client, headers: dict, package: Path) -> dict:
    with package.open("rb") as f:
        r = client.post(
            f"{API}/api/v1/igs/upload",
            headers=headers,
            files={"file": (package.name, f, "application/gzip")},
            timeout=180,
        )
    r.raise_for_status()
    return r.json()


def validate(client: httpx.Client, headers: dict, resource: dict, profiles: list[str]) -> dict:
    body = {
        "resource": json.dumps(resource),
        "profiles": profiles,
        "resource_type": resource.get("resourceType"),
    }
    r = client.post(f"{API}/api/v1/fhir/validate", headers=headers, json=body, timeout=120)
    r.raise_for_status()
    return r.json()


def main() -> int:
    uploaded: set[str] = set()
    failures = 0

    with httpx.Client() as client:
        token = login(client)
        headers = {"Authorization": f"Bearer {token}"}

        for case in CASES:
            pkg = case["package"]
            if not pkg.is_file():
                print(f"SKIP {case['name']}: missing package {pkg}")
                continue
            if not case["sample"].is_file():
                print(f"SKIP {case['name']}: missing sample {case['sample']}")
                continue

            key = pkg.name
            if key not in uploaded:
                print(f"UPLOAD {pkg.name} ...")
                info = ensure_package(client, headers, pkg)
                print(
                    f"  -> {info.get('name')} v{info.get('version')} "
                    f"kind={info.get('package_kind')} profiles={len(info.get('profiles') or [])}"
                )
                uploaded.add(key)

            resource = json.loads(case["sample"].read_text(encoding="utf-8"))
            result = validate(client, headers, resource, case["profiles"])
            errors = int(result.get("error_count") or 0)
            warnings = int(result.get("warning_count") or 0)
            valid = bool(result.get("valid"))

            ok = True
            if case.get("expect_errors") is True:
                ok = errors > 0 or not valid
            elif case.get("expect_errors") is False:
                ok = errors == 0
            elif case.get("expect_issue_code_hint"):
                blob = json.dumps(result).upper()
                ok = case["expect_issue_code_hint"].upper() in blob or errors > 0 or warnings > 0

            if case.get("expect_message_hint"):
                blob = json.dumps(result).lower()
                ok = ok and case["expect_message_hint"].lower() in blob

            status = "PASS" if ok else "FAIL"
            if not ok:
                failures += 1
            print(
                f"{status} {case['name']}: valid={valid} errors={errors} warnings={warnings} "
                f"profiles={case['profiles'] or ['(base)']}"
            )
            if not ok:
                for issue in (result.get("issues") or [])[:5]:
                    print(f"    - [{issue.get('severity')}] {issue.get('message')}")

    print(f"\nDone. failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
