"""Unit tests for local IG catalog."""

from pathlib import Path

import app.services.fhir_validator.local_ig_catalog as local_mod
from app.services.fhir_validator.ig_package_fetcher import IgPackageFetcher
from app.services.fhir_validator.local_ig_catalog import LocalIgCatalog


def test_local_catalog_lists_cached_popular_packages(tmp_path: Path, monkeypatch):
    (tmp_path / "hl7.fhir.us.core#9.0.0.tgz").write_bytes(b"fake")

    fetcher = IgPackageFetcher(packages_path=tmp_path)
    monkeypatch.setattr(local_mod, "get_ig_package_fetcher", lambda: fetcher)

    catalog = LocalIgCatalog()
    entries = catalog.list_available()
    assert any(entry.package_id == "hl7.fhir.us.core" for entry in entries)
    core = next(entry for entry in entries if entry.package_id == "hl7.fhir.us.core")
    assert core.cached_version == "9.0.0"
    assert core.popular is True

    results = catalog.search("us core")
    assert results
    assert results[0]["package_id"] == "hl7.fhir.us.core"
    assert results[0]["cached"] is True


def test_local_catalog_lists_all_cached_packages(tmp_path: Path, monkeypatch):
    (tmp_path / "hl7.fhir.us.core#9.0.0.tgz").write_bytes(b"fake")
    (tmp_path / "hl7.fhir.us.breastcancer#1.0.0.tgz").write_bytes(b"fake")

    fetcher = IgPackageFetcher(packages_path=tmp_path)
    monkeypatch.setattr(local_mod, "get_ig_package_fetcher", lambda: fetcher)

    catalog = LocalIgCatalog()
    all_entries = catalog.list_available()
    assert {e.package_id for e in all_entries} == {
        "hl7.fhir.us.core",
        "hl7.fhir.us.breastcancer",
    }

    popular = catalog.list_popular_cached()
    assert [e.package_id for e in popular] == ["hl7.fhir.us.core"]
