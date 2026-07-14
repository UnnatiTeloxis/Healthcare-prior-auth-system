"""Quick test runner to verify test cases produce expected validation results."""
import json
import sys
import requests

API = "http://localhost:8000/api/v1/fhir/validate"

TESTS = [
    # (file, profile_url, expected_valid)
    # US Core
    ("us-core/01-patient-valid.json", "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient", True),
    ("us-core/02-patient-missing-required.json", "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient", False),
    ("us-core/03-patient-invalid-values.json", "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient", False),
    ("us-core/04-observation-vital-signs-valid.json", "http://hl7.org/fhir/us/core/StructureDefinition/us-core-blood-pressure", True),
    ("us-core/05-observation-missing-required.json", "http://hl7.org/fhir/us/core/StructureDefinition/us-core-blood-pressure", False),
    ("us-core/06-condition-valid.json", "http://hl7.org/fhir/us/core/StructureDefinition/us-core-condition-encounter-diagnosis", True),
    ("us-core/07-condition-invalid.json", "http://hl7.org/fhir/us/core/StructureDefinition/us-core-condition-encounter-diagnosis", False),
    ("us-core/10-empty-resource.json", "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient", False),
    # Base FHIR (no profile)
    ("us-core/08-encounter-valid.json", "", True),
    ("us-core/09-medication-request-valid.json", "", True),
    # DaVinci CRD
    ("davinci-crd/02-coverage-missing-fields.json", "", False),
    ("davinci-crd/04-service-request-invalid.json", "", False),
    ("davinci-crd/07-nutrition-order-invalid.json", "", False),
    # DaVinci PAS
    ("davinci-pas/02-claim-missing-required.json", "", False),
    ("davinci-pas/03-claim-invalid-values.json", "", False),
    ("davinci-pas/06-bundle-invalid.json", "", False),
]


def run():
    passed = 0
    failed = 0
    errors = 0

    for filepath, profile, expected_valid in TESTS:
        try:
            with open(filepath, encoding="utf-8") as f:
                resource_text = f.read()

            profiles = [profile] if profile else []
            body = {
                "resource": resource_text,
                "profiles": profiles,
                "resource_type": json.loads(resource_text).get("resourceType", ""),
            }

            r = requests.post(API, json=body, timeout=90)
            if r.status_code != 200:
                print(f"  ERROR | {filepath} => HTTP {r.status_code}")
                errors += 1
                continue

            data = r.json()
            actual_valid = data["valid"]
            if actual_valid == expected_valid:
                symbol = "PASS" if actual_valid else "PASS"
                print(f"  OK    | {filepath:<55} valid={actual_valid}  e={data['error_count']} w={data['warning_count']}")
                passed += 1
            else:
                print(f"  FAIL  | {filepath:<55} expected_valid={expected_valid} got={actual_valid}  e={data['error_count']} w={data['warning_count']}")
                failed += 1
        except Exception as exc:
            print(f"  ERROR | {filepath} => {exc}")
            errors += 1

    print(f"\n{'='*70}")
    print(f"Results: {passed} passed, {failed} failed, {errors} errors (total {len(TESTS)})")
    return 0 if (failed == 0 and errors == 0) else 1


if __name__ == "__main__":
    sys.exit(run())
