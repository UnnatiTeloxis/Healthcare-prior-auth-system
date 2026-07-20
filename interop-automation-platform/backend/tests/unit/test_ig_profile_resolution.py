"""Unit tests for resolving profiles from a selected IG."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.fhir_validator.inferno_client import (
    InfernoClient,
    _match_profiles_for_resource_type,
    _split_ig_spec,
)
from app.services.fhir_validator.validator import ProfileResolutionError, resolve_validation_profiles

US_CORE_PROFILES = [
    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient",
    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-condition-problems-health-concerns",
    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-lab",
    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-vital-signs",
    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-medicationrequest",
]


@pytest.fixture
def client_with_profiles():
    client = InfernoClient()
    profiles_by_ig = {"hl7.fhir.us.core#6.1.0": US_CORE_PROFILES}
    with (
        patch.object(client, "load_ig_by_id", new=AsyncMock(return_value={"package_id": "hl7.fhir.us.core"})),
        patch.object(client, "get_profiles_by_ig", new=AsyncMock(return_value=profiles_by_ig)),
    ):
        yield client


def test_split_ig_spec_with_version():
    assert _split_ig_spec("hl7.fhir.us.core#6.1.0") == ("hl7.fhir.us.core", "6.1.0")


def test_split_ig_spec_without_version():
    assert _split_ig_spec("hl7.fhir.us.core") == ("hl7.fhir.us.core", None)


def test_match_exact_patient_profile():
    matched = _match_profiles_for_resource_type(US_CORE_PROFILES, "Patient")
    assert matched == ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"]


def test_match_medication_request_profile():
    matched = _match_profiles_for_resource_type(US_CORE_PROFILES, "MedicationRequest")
    assert matched == ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-medicationrequest"]


def test_match_observation_is_ambiguous():
    matched = _match_profiles_for_resource_type(US_CORE_PROFILES, "Observation")
    assert "http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-lab" in matched
    assert len(matched) >= 1


@pytest.mark.asyncio
async def test_resolves_exact_suffix_match(client_with_profiles: InfernoClient):
    profiles = await client_with_profiles.resolve_profiles_for_ig("hl7.fhir.us.core", "Patient")
    assert profiles == ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"]


@pytest.mark.asyncio
async def test_resolves_contains_match(client_with_profiles: InfernoClient):
    profiles = await client_with_profiles.resolve_profiles_for_ig("hl7.fhir.us.core", "MedicationRequest")
    assert profiles == ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-medicationrequest"]


@pytest.mark.asyncio
async def test_returns_candidates_for_ambiguous_type(client_with_profiles: InfernoClient):
    profiles = await client_with_profiles.resolve_profiles_for_ig("hl7.fhir.us.core", "Observation")
    assert len(profiles) >= 1
    assert all("observation" in p.lower() or "vital" in p.lower() for p in profiles) or len(profiles) >= 1


@pytest.mark.asyncio
async def test_returns_empty_for_unknown_type(client_with_profiles: InfernoClient):
    profiles = await client_with_profiles.resolve_profiles_for_ig("hl7.fhir.us.core", "Device")
    assert profiles == []


@pytest.mark.asyncio
async def test_returns_empty_when_ig_load_fails():
    client = InfernoClient()
    with patch.object(client, "load_ig_by_id", new=AsyncMock(side_effect=RuntimeError("boom"))):
        profiles = await client.resolve_profiles_for_ig("hl7.fhir.us.core", "Patient")
    assert profiles == []


@pytest.mark.asyncio
async def test_version_specific_key_preferred():
    client = InfernoClient()
    profiles_by_ig = {
        "hl7.fhir.us.core#5.0.1": ["http://old/us-core-patient"],
        "hl7.fhir.us.core#6.1.0": ["http://new/us-core-patient"],
    }
    with (
        patch.object(client, "load_ig_by_id", new=AsyncMock(return_value={})),
        patch.object(client, "get_profiles_by_ig", new=AsyncMock(return_value=profiles_by_ig)),
    ):
        profiles = await client.resolve_profiles_for_ig("hl7.fhir.us.core#6.1.0", "Patient")
    assert profiles == ["http://new/us-core-patient"]


@pytest.mark.asyncio
async def test_resolve_validation_profiles_prefers_explicit():
    resource = '{"resourceType":"Patient"}'
    with (
        patch(
            "app.services.fhir_validator.validator.inferno_client.load_ig_by_id",
            new=AsyncMock(return_value={}),
        ),
    ):
        profiles, selected, package_id, version = await resolve_validation_profiles(
            resource=resource,
            ig="hl7.fhir.us.core#6.1.0",
            profiles=["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"],
            profile=None,
            resource_type="Patient",
        )
    assert profiles == ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"]
    assert selected == "hl7.fhir.us.core#6.1.0"
    assert package_id == "hl7.fhir.us.core"
    assert version == "6.1.0"


@pytest.mark.asyncio
async def test_resolve_validation_profiles_uses_meta_profile():
    profile = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"
    resource = f'{{"resourceType":"Patient","meta":{{"profile":["{profile}"]}}}}'
    with patch(
        "app.services.fhir_validator.validator.inferno_client.load_ig_by_id",
        new=AsyncMock(return_value={}),
    ):
        profiles, selected, *_ = await resolve_validation_profiles(
            resource=resource,
            ig="hl7.fhir.us.core#6.1.0",
            profiles=[],
            profile=None,
            resource_type="Patient",
        )
    assert profiles == [profile]
    assert selected == "hl7.fhir.us.core#6.1.0"


@pytest.mark.asyncio
async def test_resolve_validation_profiles_ambiguous_raises():
    resource = '{"resourceType":"Observation"}'
    with (
        patch(
            "app.services.fhir_validator.validator.inferno_client.load_ig_by_id",
            new=AsyncMock(return_value={}),
        ),
        patch(
            "app.services.fhir_validator.validator.inferno_client.resolve_profiles_for_ig",
            new=AsyncMock(
                return_value=[
                    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-lab",
                    "http://hl7.org/fhir/us/core/StructureDefinition/us-core-vital-signs",
                ]
            ),
        ),
    ):
        with pytest.raises(ProfileResolutionError) as exc:
            await resolve_validation_profiles(
                resource=resource,
                ig="hl7.fhir.us.core#6.1.0",
                profiles=[],
                profile=None,
                resource_type="Observation",
            )
    assert "Multiple" in exc.value.message
    assert len(exc.value.candidates) == 2
