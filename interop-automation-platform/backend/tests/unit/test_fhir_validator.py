"""Unit tests for passthrough OperationOutcome parsing (Inferno parity)."""

from app.utils.fhir_helpers import count_operation_outcome_severities, parse_operation_outcome


def test_passthrough_preserves_all_issues_and_severities():
    outcome = {
        "issue": [
            {
                "severity": "information",
                "code": "informational",
                "details": {
                    "text": "Validate Observation against the Heart rate profile (http://example.org/heartrate)"
                },
                "expression": ["Observation"],
            },
            {
                "severity": "warning",
                "code": "not-found",
                "details": {
                    "text": (
                        "A definition for CodeSystem 'http://loinc.org' could not be found, "
                        "so the code cannot be validated"
                    )
                },
                "expression": ["Observation.code.coding[0].system"],
            },
            {
                "severity": "error",
                "code": "structure",
                "details": {"text": "Observation.component.code: minimum required = 1, but only found 0"},
                "expression": ["Observation.component[0]"],
            },
        ]
    }

    is_valid, issues = parse_operation_outcome(outcome)
    valid2, errors, warnings, info = count_operation_outcome_severities(outcome)

    assert is_valid is False
    assert valid2 is False
    assert len(issues) == 3
    assert errors == 1
    assert warnings == 1
    assert info == 1
    assert issues[0]["severity"] == "information"
    assert "Validate Observation" in issues[0]["message"]


def test_count_treats_fatal_as_error():
    outcome = {
        "issue": [
            {
                "severity": "fatal",
                "code": "exception",
                "details": {"text": "Fatal validation failure"},
                "expression": ["Resource"],
            }
        ]
    }

    is_valid, issues = parse_operation_outcome(outcome)
    _, errors, warnings, info = count_operation_outcome_severities(outcome)

    assert is_valid is False
    assert len(issues) == 1
    assert issues[0]["severity"] == "fatal"
    assert errors == 1
    assert warnings == 0
    assert info == 0


def test_extract_meta_profiles_from_bundle():
    from app.utils.fhir_helpers import extract_meta_profiles

    resource = """{
      "resourceType": "Bundle",
      "entry": [{
        "resource": {
          "resourceType": "Patient",
          "meta": {"profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"]}
        }
      }]
    }"""
    profiles = extract_meta_profiles(resource)
    assert profiles == ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"]


def test_empty_outcome_is_valid():
    is_valid, issues = parse_operation_outcome({})
    valid2, errors, warnings, info = count_operation_outcome_severities({})

    assert is_valid is True
    assert valid2 is True
    assert issues == []
    assert errors == warnings == info == 0
