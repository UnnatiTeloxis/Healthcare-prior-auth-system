import re
from typing import Any

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.api.v1.fhir_validator.schemas import IGInfo, LoadIGRequest
from app.services.fhir_validator.ig_catalog import POPULAR_IGS
from app.services.fhir_validator.ig_manager import ig_manager
from app.services.fhir_validator.ig_package_fetcher import get_ig_package_fetcher
from app.services.fhir_validator.inferno_client import inferno_client
from app.services.fhir_validator.inferno_ig_catalog import inferno_ig_catalog
from app.services.fhir_validator.local_ig_catalog import local_ig_catalog

router = APIRouter()

_PACKAGE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_VERSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]*$")
_POPULAR_IDS = {row["package_id"] for row in POPULAR_IGS}


def _validate_package_id(package_id: str) -> str:
    cleaned = (package_id or "").strip()
    if not cleaned or not _PACKAGE_ID_RE.match(cleaned):
        raise HTTPException(status_code=422, detail=f"Invalid package id: {package_id!r}")
    return cleaned


def _validate_version(version: str | None) -> str | None:
    if version is None or version == "":
        return None
    cleaned = version.strip()
    # Strip .tgz extension if present (from catalog URLs)
    if cleaned.endswith(".tgz"):
        cleaned = cleaned[:-4]
    if not _VERSION_RE.match(cleaned):
        raise HTTPException(status_code=422, detail=f"Invalid package version: {version!r}")
    return cleaned


def _normalize_available_ig(raw: dict[str, Any]) -> dict[str, Any]:
    package_id = raw.get("package_id") or raw.get("name") or ""
    version = raw.get("version") or ""
    fhir_versions = raw.get("fhir_versions") or []
    if isinstance(fhir_versions, str):
        fhir_versions = [fhir_versions]
    fhir_version = raw.get("fhir_version") or (fhir_versions[0] if fhir_versions else None)
    source = raw.get("source") or ("local" if raw.get("filename") else "inferno")
    cached = bool(raw.get("cached")) if "cached" in raw else bool(raw.get("filename"))
    return {
        "package_id": package_id,
        "name": package_id,
        "version": version,
        "title": raw.get("title") or package_id,
        "description": raw.get("description") or "",
        "fhir_version": fhir_version,
        "fhir_versions": fhir_versions,
        "filename": raw.get("filename"),
        "canonical": raw.get("canonical") or "",
        "package_type": raw.get("package_type"),
        "structure_definition_count": raw.get("structure_definition_count", 0),
        "is_profile_ig": raw.get("is_profile_ig", True),
        "source": source,
        "cached": cached,
        "popular": package_id in _POPULAR_IDS or bool(raw.get("popular")),
        "category": raw.get("category") or "",
    }


def _merge_available_catalog(
    local_igs: list[dict[str, Any]],
    catalog_igs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Prefer locally cached packages; fill remaining slots from Inferno's known-IG list."""
    merged: dict[str, dict[str, Any]] = {}

    for item in catalog_igs:
        key = item.get("package_id") or ""
        if not key:
            continue
        normalized = _normalize_available_ig(item)
        merged[key] = normalized

    for item in local_igs:
        key = item.get("package_id") or item.get("name") or ""
        if not key:
            continue
        normalized = _normalize_available_ig(item)
        normalized["source"] = "local"
        normalized["cached"] = True
        existing = merged.get(key)
        if existing:
            # Keep Inferno title/description when local title is just the package id.
            if not normalized.get("title") or normalized["title"] == key:
                normalized["title"] = existing.get("title") or key
            if not normalized.get("description"):
                normalized["description"] = existing.get("description") or ""
            if not normalized.get("version") and existing.get("version"):
                normalized["version"] = existing["version"]
            normalized["popular"] = existing.get("popular") or normalized.get("popular")
            normalized["category"] = existing.get("category") or normalized.get("category")
        merged[key] = normalized

    entries = list(merged.values())
    entries.sort(
        key=lambda e: (
            0 if e.get("cached") else 1,
            0 if e.get("popular") else 1,
            0 if str(e.get("package_id", "")).startswith("hl7.fhir.us.") else 1,
            str(e.get("title") or e.get("package_id") or "").lower(),
            str(e.get("version") or ""),
        )
    )
    return entries


def _normalize_loaded_ig(raw: dict[str, Any]) -> dict[str, Any]:
    package_id = raw.get("package_id") or raw.get("package_name") or ""
    version = raw.get("version") or ""
    return {
        "package_id": package_id,
        "package_name": package_id,
        "name": package_id,
        "version": version,
        "profiles": list(raw.get("profiles") or []),
        "status": raw.get("status") or "ready",
        "load_time_ms": raw.get("load_time_ms") or 0,
        "loaded_at": raw.get("loaded_at") or 0,
        "preloaded": bool(raw.get("preloaded")),
        "error": raw.get("error"),
    }


@router.get("/", response_model=dict[str, Any])
async def list_igs():
    return await inferno_client.get_igs()


@router.get("/available")
async def list_available_igs(
    q: str | None = None,
    limit: int | None = Query(default=500, ge=1, le=5000),
    source: str = Query(
        default="all",
        description="local = only fhir_packages; inferno = Inferno catalog; all = merge both",
    ),
    refresh: bool = False,
):
    """
    IG dropdown catalog.

    By default merges local .tgz files with Inferno's known package list
    (same GET /igs catalog the Inferno Resource Validator UI uses).
    """
    try:
        local_raw: list[dict[str, Any]] = []
        catalog_raw: list[dict[str, Any]] = []
        catalog_source = None

        if source in {"local", "all"}:
            # Filename-based catalog (fast). Avoid opening every .tgz — that blocks
            # the event loop for minutes with ~200 packages and empties the UI dropdown.
            local_raw = [
                {
                    "package_id": entry.package_id,
                    "name": entry.package_id,
                    "version": entry.cached_version,
                    "title": entry.name,
                    "description": entry.description,
                    "fhir_version": entry.fhir_version,
                    "fhir_versions": [entry.fhir_version],
                    "filename": f"{entry.package_id}#{entry.cached_version}.tgz",
                    "cached": True,
                    "source": "local",
                    "popular": entry.popular,
                    "category": entry.category,
                    # Unknown until package is opened; treat as selectable profile IG.
                    "is_profile_ig": True,
                    "structure_definition_count": 1,
                }
                for entry in local_ig_catalog.list_available()
            ]

        if source in {"inferno", "all"}:
            catalog_raw = await inferno_ig_catalog.list_entries(force=refresh)
            catalog_source = inferno_ig_catalog.source_url

        if source == "local":
            igs = [_normalize_available_ig(item) for item in local_raw]
            for ig in igs:
                ig["source"] = "local"
                ig["cached"] = True
        elif source == "inferno":
            igs = [_normalize_available_ig(item) for item in catalog_raw]
        else:
            igs = _merge_available_catalog(local_raw, catalog_raw)

        if q:
            needle = q.lower().strip()
            igs = [
                ig
                for ig in igs
                if needle in (ig.get("package_id") or "").lower()
                or needle in (ig.get("title") or "").lower()
                or needle in (ig.get("description") or "").lower()
                or needle in (ig.get("category") or "").lower()
            ]

        total = len(igs)
        if limit is not None:
            igs = igs[:limit]

        return {
            "success": True,
            "igs": igs,
            "count": len(igs),
            "total": total,
            "catalog_source": catalog_source,
            "source_mode": source,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/load")
async def load_ig_on_demand(request: LoadIGRequest):
    """
    Load a specific IG into the Inferno validator on demand.
    Lets Inferno fetch from packages.fhir.org directly for faster loading.
    """
    package_id = _validate_package_id(request.package_id or request.package_name or "")
    version = _validate_version(request.version)

    try:
        if request.retry:
            ig_manager.clear_loaded_ig(package_id, version)
        result = await ig_manager.load_ig(package_id, version)
        normalized = _normalize_loaded_ig(result)
        return {
            "success": True,
            "ig": normalized,
        }
    except HTTPException:
        raise
    except TimeoutError as exc:
        raise HTTPException(
            status_code=504,
            detail=f"Timed out loading IG {package_id}: {exc}",
        ) from exc
    except Exception as exc:
        message = str(exc)
        status = 502 if "Inferno" in message or "validator" in message.lower() else 400
        raise HTTPException(
            status_code=status,
            detail=f"Failed to load IG {package_id}: {exc}",
        ) from exc


@router.get("/loaded")
async def list_loaded_igs():
    """Return list of IGs currently loaded in the validator."""
    igs = [_normalize_loaded_ig(item) for item in ig_manager.get_loaded_igs()]
    return {
        "success": True,
        "igs": igs,
        "count": len(igs),
        "ready_count": sum(1 for ig in igs if ig.get("status") == "ready"),
    }


@router.get("/preload-status")
async def preload_status():
    """Warmup progress: IGs already installed into Inferno this session."""
    igs = [_normalize_loaded_ig(item) for item in ig_manager.get_loaded_igs()]
    return {
        "success": True,
        "ready_count": sum(1 for ig in igs if ig.get("status") == "ready"),
        "failed_count": sum(1 for ig in igs if ig.get("status") == "failed"),
        "loading_count": sum(1 for ig in igs if ig.get("status") == "loading"),
        "igs": igs,
    }


@router.put("/{package_id}", response_model=IGInfo)
async def load_ig(package_id: str, version: str | None = None):
    package_id = _validate_package_id(package_id)
    version = _validate_version(version)
    try:
        result = await inferno_client.load_ig_by_id(package_id, version)
        return IGInfo(
            id=str(result.get("id") or result.get("package_id") or package_id),
            version=str(result.get("version") or version or "") or None,
            profiles=list(result.get("profiles") or []),
            canonical_url=result.get("canonical_url") or result.get("canonical"),
        )
    except TimeoutError as exc:
        raise HTTPException(status_code=504, detail=f"Timed out loading IG {package_id}: {exc}") from exc
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to load IG {package_id}: {exc}",
        ) from exc


@router.post("/upload", response_model=IGInfo)
async def upload_ig(file: UploadFile = File(...)):
    """Trusted custom IG upload (.tgz). Not part of the normal public selection workflow."""
    if not file.filename or not file.filename.endswith((".tgz", ".tar.gz")):
        raise HTTPException(status_code=400, detail="File must be a .tgz or .tar.gz package")

    try:
        package_data = await file.read()
        result = await inferno_client.upload_custom_ig(package_data)
        return IGInfo(
            id=str(result.get("id") or result.get("package_id") or file.filename),
            version=str(result.get("version") or "") or None,
            profiles=list(result.get("profiles") or []),
            canonical_url=result.get("canonical_url") or result.get("canonical"),
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to upload IG: {exc}") from exc


@router.get("/version")
async def get_version():
    return await inferno_client.get_version()
