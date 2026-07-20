"""Unit tests for IG package fetcher helpers."""

import io
import json
import tarfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from app.services.fhir_validator.ig_package_fetcher import (
    IgPackageFetcher,
    _normalize_dep_version,
)


def _build_package_tgz(package_id: str, version: str, dependencies: dict[str, str] | None = None) -> bytes:
    package_json = {
        "name": package_id,
        "version": version,
        "dependencies": dependencies or {},
    }
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        payload = json.dumps(package_json).encode("utf-8")
        info = tarfile.TarInfo(name="package/package.json")
        info.size = len(payload)
        archive.addfile(info, io.BytesIO(payload))
    return buffer.getvalue()


def test_normalize_dep_version():
    assert _normalize_dep_version("^6.1.0") == "6.1.0"
    assert _normalize_dep_version("~1.0.0") == "1.0.0"
    assert _normalize_dep_version(">=4.0.1") == "4.0.1"
    assert _normalize_dep_version("6.1.0") == "6.1.0"


def test_read_package_json_and_dependencies(tmp_path: Path):
    fetcher = IgPackageFetcher(packages_path=tmp_path)
    data = _build_package_tgz(
        "hl7.fhir.us.core",
        "6.1.0",
        {"hl7.fhir.uv.extensions": "^1.0.0", "hl7.fhir.r4.core": "4.0.1"},
    )
    package_json = fetcher._read_package_json(data)
    deps = fetcher._parse_dependencies(package_json)
    assert "hl7.fhir.uv.extensions" in deps
    assert deps["hl7.fhir.uv.extensions"] == "1.0.0"
    assert "hl7.fhir.r4.core" not in deps


def test_verify_shasum_accepts_matching_digest():
    fetcher = IgPackageFetcher(packages_path=Path("/tmp"))
    data = b"example-package"
    import hashlib

    digest = hashlib.sha1(data).hexdigest()
    fetcher._verify_shasum(data, digest)


def test_verify_shasum_rejects_mismatch():
    fetcher = IgPackageFetcher(packages_path=Path("/tmp"))
    with pytest.raises(ValueError, match="shasum mismatch"):
        fetcher._verify_shasum(b"bad", "deadbeef")


@pytest.mark.asyncio
async def test_download_package_writes_cache(tmp_path: Path):
    fetcher = IgPackageFetcher(packages_path=tmp_path)
    package_bytes = _build_package_tgz("hl7.fhir.us.davinci-crd", "2.1.0")

    metadata_response = AsyncMock()
    metadata_response.raise_for_status = lambda: None
    metadata_response.json = lambda: {
        "dist-tags": {"latest": "2.1.0"},
        "versions": {
            "2.1.0": {
                "fhirVersion": "R4",
                "dist": {
                    "tarball": "https://packages.fhir.org/hl7.fhir.us.davinci-crd/2.1.0",
                    "shasum": "",
                },
            }
        },
    }

    tarball_response = AsyncMock()
    tarball_response.raise_for_status = lambda: None
    tarball_response.content = package_bytes

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(side_effect=[metadata_response, tarball_response])

    with patch.object(fetcher, "_get_client", return_value=mock_client):
        path = await fetcher.download_package(
            "hl7.fhir.us.davinci-crd",
            "2.1.0",
            resolve_dependencies=False,
        )

    assert path.is_file()
    assert path.name == "hl7.fhir.us.davinci-crd#2.1.0.tgz"
    assert fetcher.is_cached("hl7.fhir.us.davinci-crd", "2.1.0")
