"""Maps IG package IDs to on-disk test-case folders (folder name = package ID)."""

from __future__ import annotations

import json
import os
from pathlib import Path

from app.services.fhir_validator.ig_constants import IG_DISPLAY, SUPPORTED_IG_PACKAGES

# Legacy short folder names (pre-rename); kept for backward compatibility only.
LEGACY_IG_TEST_FOLDER: dict[str, str] = {
    "hl7.fhir.us.core": "us-core",
    "hl7.fhir.us.ccda": "us-ccda",
    "hl7.fhir.us.qicore": "us-qicore",
    "hl7.fhir.us.carin-bb": "us-carin-bb",
    "hl7.fhir.us.bulkdata": "us-bulkdata",
    "hl7.fhir.us.odh": "us-odh",
    "hl7.fhir.us.military-service": "us-military-service",
    "hl7.fhir.us.vrdr": "us-vrdr",
    "hl7.fhir.us.davinci-crd": "davinci-crd",
    "hl7.fhir.us.davinci-dtr": "davinci-dtr",
    "hl7.fhir.us.davinci-pas": "davinci-pas",
    "hl7.fhir.us.davinci-pdex": "davinci-pdex",
    "hl7.fhir.us.davinci-cdex": "davinci-cdex",
    "hl7.fhir.us.davinci-pcde": "davinci-pcde",
    "hl7.fhir.us.davinci-alerts": "davinci-alerts",
    "hl7.fhir.us.davinci-drug-formulary": "davinci-drug-formulary",
    "hl7.fhir.us.davinci-deqm": "davinci-deqm",
    "hl7.fhir.us.davinci-ra": "davinci-ra",
    "hl7.fhir.us.mcode": "us-mcode",
    "hl7.fhir.us.ecr": "us-ecr",
    "hl7.fhir.us.pacio-adi": "us-pacio-adi",
    "hl7.fhir.us.pacio-cs": "us-pacio-cs",
    "hl7.fhir.us.pacio-fs": "us-pacio-fs",
    "hl7.fhir.uv.ipa": "fhir-uv-ipa",
    "hl7.fhir.uv.ips": "fhir-uv-ips",
    "hl7.fhir.uv.smart-app-launch": "fhir-uv-smart-app-launch",
    "hl7.fhir.uv.sdc": "fhir-uv-sdc",
    "hl7.fhir.uv.extensions.r4": "fhir-uv-extensions",
    "hl7.terminology.r4": "hl7-terminology",
}

TIERS = ("simple", "complex", "realistic")

_catalog_cache: list[dict] | None = None
_catalog_cache_mtime: float = 0.0


def _catalog_source_mtime(root: Path) -> float:
    latest = 0.0
    if not root.is_dir():
        return latest
    for tier_dir_name in TIERS:
        for ig_dir in root.iterdir():
            if not ig_dir.is_dir() or ig_dir.name.startswith("_"):
                continue
            tier_dir = ig_dir / tier_dir_name
            if not tier_dir.is_dir():
                continue
            for fp in tier_dir.glob("*.json"):
                try:
                    latest = max(latest, fp.stat().st_mtime)
                except OSError:
                    continue
    return latest


def test_cases_root() -> Path:
    raw = os.getenv("FHIR_TEST_CASES_PATH", "").strip()
    if raw:
        return Path(raw)
    for candidate in (
        Path("/app/test-cases"),
        Path(__file__).resolve().parents[4] / "test-cases",
    ):
        if candidate.is_dir():
            return candidate
    return Path(__file__).resolve().parents[4] / "test-cases"


def folder_for_package(package_id: str) -> str | None:
    """Resolve on-disk folder; prefers package_id folder (matches IG dropdown name)."""
    root = test_cases_root()
    if (root / package_id).is_dir():
        return package_id
    legacy = LEGACY_IG_TEST_FOLDER.get(package_id)
    if legacy and (root / legacy).is_dir():
        return legacy
    return None


def _sample_meta(path: Path) -> dict[str, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        profiles = (data.get("meta") or {}).get("profile") or []
        profile_url = ""
        if isinstance(profiles, list) and profiles:
            profile_url = str(profiles[0])
        elif isinstance(profiles, str):
            profile_url = profiles
        return {
            "resource_type": str(data.get("resourceType") or ""),
            "profile_url": profile_url,
        }
    except (json.JSONDecodeError, OSError, TypeError):
        return {"resource_type": "", "profile_url": ""}


def list_catalog() -> list[dict]:
    global _catalog_cache, _catalog_cache_mtime
    root = test_cases_root()
    mtime = _catalog_source_mtime(root)
    if _catalog_cache is not None and mtime <= _catalog_cache_mtime:
        return _catalog_cache

    out: list[dict] = []
    for package_id in sorted(SUPPORTED_IG_PACKAGES):
        folder = folder_for_package(package_id)
        if not folder:
            continue
        folder_path = root / folder
        samples: list[dict] = []
        if folder_path.is_dir():
            for tier in TIERS:
                tier_dir = folder_path / tier
                if not tier_dir.is_dir():
                    continue
                for fp in sorted(tier_dir.glob("*.json")):
                    meta = _sample_meta(fp)
                    samples.append(
                        {
                            "tier": tier,
                            "file": fp.name,
                            "path": f"{folder}/{tier}/{fp.name}",
                            "label": fp.stem.replace("-", " "),
                            "resource_type": meta["resource_type"],
                            "profile_url": meta["profile_url"],
                        }
                    )
        display = IG_DISPLAY.get(package_id) or {}
        out.append(
            {
                "package_id": package_id,
                "folder": folder,
                "title": display.get("title") or package_id,
                "category": display.get("category") or "",
                "sample_count": len(samples),
                "samples": samples,
            }
        )
    _catalog_cache = out
    _catalog_cache_mtime = mtime
    return out


def read_sample(relative_path: str) -> str:
    """Read a test-case JSON file; relative_path must be folder/tier/file.json."""
    root = test_cases_root().resolve()
    target = (root / relative_path).resolve()
    if not str(target).startswith(str(root)):
        raise ValueError("Invalid test-case path")
    if not target.is_file() or target.suffix.lower() != ".json":
        raise FileNotFoundError(relative_path)
    return target.read_text(encoding="utf-8")
