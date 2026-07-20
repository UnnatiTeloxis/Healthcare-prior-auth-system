"""Integration tests for IG-aware validation request/response contract."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.fhir_validator.inferno_client import ProfileValidationError, inferno_client

US_CORE_PATIENT_PROFILE = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"

VALID_US_CORE_PATIENT = (
    '{"resourceType":"Patient","meta":{"profile":["' + US_CORE_PATIENT_PROFILE + '"]},'
    '"identifier":[{"system":"http://hospital.example.org/mrn","value":"12345"}],'
    '"name":[{"family":"Doe","given":["Jane"]}],'
    '"gender":"female","birthDate":"1980-01-15"}'
)

INVALID_US_CORE_PATIENT = '{"resourceType":"Patient","gender":"female"}'


@pytest.fixture
def client():
    return TestClient(app)


def test_validate_reports_selected_ig_and_resolved_profile(client: TestClient):
    operation_outcome = {"issue": []}

    with (
        patch.object(inferno_client, "ensure_ready", new=AsyncMock()),
        patch.object(inferno_client, "load_ig_by_id", new=AsyncMock(return_value={"package_id": "hl7.fhir.us.core"})),
        patch.object(inferno_client, "ensure_igs_for_profiles", new=AsyncMock()),
        patch.object(inferno_client, "validate_resource", new=AsyncMock(return_value=operation_outcome)),
    ):
        response = client.post(
            "/api/v1/validate/",
            json={
                "resource": VALID_US_CORE_PATIENT,
                "profiles": [US_CORE_PATIENT_PROFILE],
                "ig": "hl7.fhir.us.core#6.1.0",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is True
    assert body["selected_ig"] == "hl7.fhir.us.core#6.1.0"
    assert body["resolved_profile"] == US_CORE_PATIENT_PROFILE
    assert body["package_id"] == "hl7.fhir.us.core"
    assert body["package_version"] == "6.1.0"
    assert body["profiles"] == [US_CORE_PATIENT_PROFILE]


def test_validate_failed_keeps_operation_outcome(client: TestClient):
    operation_outcome = {
        "issue": [
            {
                "severity": "error",
                "code": "required",
                "details": {"text": "Patient.name: minimum required = 1, but only found 0"},
                "expression": ["Patient.name"],
            }
        ]
    }

    with (
        patch.object(inferno_client, "ensure_ready", new=AsyncMock()),
        patch.object(inferno_client, "load_ig_by_id", new=AsyncMock(return_value={})),
        patch.object(inferno_client, "validate_resource", new=AsyncMock(return_value=operation_outcome)),
    ):
        response = client.post(
            "/api/v1/validate/",
            json={
                "resource": INVALID_US_CORE_PATIENT,
                "profile": US_CORE_PATIENT_PROFILE,
                "ig": "hl7.fhir.us.core#6.1.0",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is False
    assert body["selected_ig"] == "hl7.fhir.us.core#6.1.0"
    assert body["resolved_profile"] == US_CORE_PATIENT_PROFILE
    assert body["error_count"] >= 1
    assert body["operation_outcome"]["issue"]


def test_validate_base_fhir_without_ig_has_no_ig_metadata(client: TestClient):
    operation_outcome = {"issue": []}

    with (
        patch.object(inferno_client, "ensure_ready", new=AsyncMock()),
        patch.object(inferno_client, "validate_resource", new=AsyncMock(return_value=operation_outcome)),
    ):
        response = client.post(
            "/api/v1/validate/",
            json={"resource": '{"resourceType":"Patient","name":[{"family":"Doe"}]}'},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["selected_ig"] is None
    assert body["resolved_profile"] is None
    assert body["valid"] is True


def test_validate_ambiguous_profile_returns_422(client: TestClient):
    with (
        patch.object(inferno_client, "load_ig_by_id", new=AsyncMock(return_value={})),
        patch.object(
            inferno_client,
            "resolve_profiles_for_ig",
            new=AsyncMock(
                return_value=[
                    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-lab",
                    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-blood-pressure",
                ]
            ),
        ),
    ):
        response = client.post(
            "/api/v1/validate/",
            json={
                "resource": '{"resourceType":"Observation","status":"final","code":{"text":"x"}}',
                "ig": "hl7.fhir.us.core#6.1.0",
            },
        )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert "Multiple" in detail["message"]
    assert len(detail["candidates"]) == 2


def test_validate_does_not_fallback_to_base_fhir_on_profile_error(client: TestClient):
    with (
        patch.object(inferno_client, "load_ig_by_id", new=AsyncMock(return_value={})),
        patch.object(
            inferno_client,
            "validate_resource",
            new=AsyncMock(side_effect=ProfileValidationError("profile boom")),
        ),
    ):
        response = client.post(
            "/api/v1/validate/",
            json={
                "resource": INVALID_US_CORE_PATIENT,
                "ig": "hl7.fhir.us.core#6.1.0",
                "profile": US_CORE_PATIENT_PROFILE,
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is False
    assert body["selected_ig"] == "hl7.fhir.us.core#6.1.0"
    assert body["resolved_profile"] == US_CORE_PATIENT_PROFILE
    assert any(issue["code"] == "profile-validation-error" for issue in body["issues"])


def test_igs_available_and_load_contract(client: TestClient):
    with (
        patch(
            "app.api.v1.fhir_validator.igs.ig_manager.list_available_igs",
            return_value=[
                {
                    "package_id": "hl7.fhir.us.core",
                    "name": "hl7.fhir.us.core",
                    "version": "6.1.0",
                    "title": "US Core",
                    "description": "US Core IG",
                    "fhir_version": "4.0.1",
                    "fhir_versions": ["4.0.1"],
                }
            ],
        ),
        patch(
            "app.api.v1.fhir_validator.igs.ig_manager.load_ig",
            new=AsyncMock(
                return_value={
                    "package_id": "hl7.fhir.us.core",
                    "package_name": "hl7.fhir.us.core",
                    "version": "6.1.0",
                    "profiles": [US_CORE_PATIENT_PROFILE],
                    "status": "ready",
                }
            ),
        ),
    ):
        available = client.get("/api/v1/igs/available")
        assert available.status_code == 200
        igs = available.json()["igs"]
        assert igs[0]["package_id"] == "hl7.fhir.us.core"
        assert igs[0]["fhir_version"] == "4.0.1"

        loaded = client.post(
            "/api/v1/igs/load",
            json={"package_name": "hl7.fhir.us.core", "version": "6.1.0"},
        )
        assert loaded.status_code == 200
        body = loaded.json()["ig"]
        assert body["package_id"] == "hl7.fhir.us.core"
        assert body["profiles"] == [US_CORE_PATIENT_PROFILE]
        assert body["status"] == "ready"
