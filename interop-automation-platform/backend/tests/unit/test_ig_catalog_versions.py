"""Unit tests for IG catalog version listing."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.fhir_validator.ig_catalog import IgCatalogService


@pytest.mark.asyncio
async def test_get_package_versions_filters_non_r4():
    service = IgCatalogService()
    payload = {
        "dist-tags": {"latest": "6.1.0"},
        "versions": {
            "2.0.0": {
                "fhirVersion": "STU3",
                "dist": {"tarball": "https://example/2.0.0", "shasum": "abc"},
            },
            "6.1.0": {
                "fhirVersion": "R4",
                "dist": {"tarball": "https://example/6.1.0", "shasum": "def"},
            },
        },
    }

    response = AsyncMock()
    response.raise_for_status = lambda: None
    response.json = lambda: payload
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=response)

    with patch.object(service, "_get_client", return_value=mock_client):
        latest, entries = await service.get_package_versions("hl7.fhir.us.core", fhir_version="R4")

    assert latest == "6.1.0"
    assert len(entries) == 1
    assert entries[0].version == "6.1.0"
    assert entries[0].is_latest is True
    assert entries[0].fhir_version == "R4"
