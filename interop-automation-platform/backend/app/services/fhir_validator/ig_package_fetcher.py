"""Download FHIR IG packages from packages.fhir.org with integrity checks and dependency closure."""

from __future__ import annotations

import asyncio
import hashlib
import io
import json
import logging
import re
import tarfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from app.services.fhir_validator.fhir_loader import FHIRPackageRef, get_fhir_package_loader

logger = logging.getLogger(__name__)

REGISTRY_BASE = "https://packages.fhir.org"
DOWNLOAD_TIMEOUT = httpx.Timeout(300.0, connect=15.0)
_REGISTRY_RETRY_MAX = 8
_REGISTRY_RETRY_BASE_DELAY = 3.0
_DEFAULT_REQUEST_DELAY = 2.0

# Core/tooling packages Inferno already ships; skip fetching these as dependencies.
_SKIP_DEPENDENCIES = frozenset({
    "hl7.fhir.r4.core",
    "hl7.fhir.r4.corexml",
    "hl7.fhir.r4.examples",
    "hl7.fhir.r4.expansions",
    "hl7.fhir.r4.elements",
    "hl7.fhir.pubpack",
    "hl7.terminology.r4",
    "hl7.terminology.r5",
    "us.nlm.vsac",
})


@dataclass(frozen=True)
class PackageMetadata:
    package_id: str
    version: str
    tarball: str
    shasum: str
    fhir_version: str = ""


class IgPackageFetcher:
    def __init__(
        self,
        packages_path: Path | None = None,
        *,
        request_delay: float = _DEFAULT_REQUEST_DELAY,
    ) -> None:
        loader = get_fhir_package_loader()
        self.packages_dir = packages_path or loader.packages_dir
        self._client: httpx.AsyncClient | None = None
        self._lock = asyncio.Lock()
        self._request_delay = max(0.0, request_delay)
        self._last_request_at: float = 0.0

    def is_enabled(self) -> bool:
        return bool(self.packages_dir)

    def _ensure_dir(self) -> Path:
        if not self.packages_dir:
            raise RuntimeError("FHIR_PACKAGES_PATH is not configured")
        self.packages_dir.mkdir(parents=True, exist_ok=True)
        return self.packages_dir

    def package_path(self, package_id: str, version: str) -> Path:
        return self._ensure_dir() / f"{package_id}#{version}.tgz"

    def is_cached(self, package_id: str, version: str) -> bool:
        if not self.packages_dir:
            return False
        return self.package_path(package_id, version).is_file()

    def list_cached_versions(self, package_id: str) -> list[str]:
        if not self.packages_dir or not self.packages_dir.is_dir():
            return []
        prefix = f"{package_id}#"
        versions: list[str] = []
        for path in self.packages_dir.glob("*.tgz"):
            name = path.name
            if name.startswith(prefix):
                versions.append(name[len(prefix) : -4])
        return sorted(versions, reverse=True)

    def list_cached_packages(self) -> dict[str, list[str]]:
        """Return {package_id: [versions newest-first]} for every id#ver.tgz on disk."""
        if not self.packages_dir or not self.packages_dir.is_dir():
            return {}
        by_id: dict[str, list[str]] = {}
        for path in self.packages_dir.glob("*.tgz"):
            name = path.name
            if "#" not in name or not name.endswith(".tgz"):
                continue
            package_id, version = name[:-4].rsplit("#", 1)
            if not package_id or not version:
                continue
            by_id.setdefault(package_id, []).append(version)
        return {
            package_id: sorted(versions, reverse=True)
            for package_id, versions in by_id.items()
        }

    def has_any_cached_version(self, package_id: str) -> bool:
        return bool(self.list_cached_versions(package_id))

    async def _pace_registry_request(self) -> None:
        if self._request_delay <= 0:
            return
        if self._last_request_at:
            elapsed = time.monotonic() - self._last_request_at
            remaining = self._request_delay - elapsed
            if remaining > 0:
                await asyncio.sleep(remaining)

    async def _registry_get(self, url: str) -> httpx.Response:
        client = await self._get_client()
        response: httpx.Response | None = None

        for attempt in range(1, _REGISTRY_RETRY_MAX + 1):
            await self._pace_registry_request()
            response = await client.get(url)
            self._last_request_at = time.monotonic()

            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After", "").strip()
                if retry_after.isdigit():
                    delay = float(retry_after)
                else:
                    delay = _REGISTRY_RETRY_BASE_DELAY * (2 ** (attempt - 1))
                logger.warning(
                    "Rate limited (429) for %s; waiting %.0fs (attempt %d/%d)",
                    url,
                    delay,
                    attempt,
                    _REGISTRY_RETRY_MAX,
                )
                if attempt >= _REGISTRY_RETRY_MAX:
                    response.raise_for_status()
                await asyncio.sleep(delay)
                continue

            if response.status_code in {502, 503, 504} and attempt < _REGISTRY_RETRY_MAX:
                delay = _REGISTRY_RETRY_BASE_DELAY * attempt
                logger.warning(
                    "Registry %s for %s; retry in %.0fs",
                    response.status_code,
                    url,
                    delay,
                )
                await asyncio.sleep(delay)
                continue

            response.raise_for_status()
            return response

        assert response is not None
        response.raise_for_status()
        return response

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=DOWNLOAD_TIMEOUT)
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def fetch_metadata(
        self,
        package_id: str,
        version: str | None = None,
    ) -> PackageMetadata:
        client = await self._get_client()
        response = await self._registry_get(f"{REGISTRY_BASE}/{package_id}")
        data = response.json()
        if not isinstance(data, dict):
            raise ValueError(f"Invalid registry response for {package_id}")

        resolved_version = version
        if not resolved_version:
            resolved_version = str((data.get("dist-tags") or {}).get("latest") or "").strip()
        if not resolved_version:
            raise ValueError(f"No version found for package {package_id}")

        versions = data.get("versions") or {}
        row = versions.get(resolved_version)
        if not isinstance(row, dict):
            raise ValueError(f"Version {resolved_version} not found for {package_id}")

        dist = row.get("dist") or {}
        tarball = str(dist.get("tarball") or dist.get("url") or "").strip()
        if not tarball:
            tarball = f"{REGISTRY_BASE}/{package_id}/{resolved_version}"
        shasum = str(dist.get("shasum") or "").strip()
        fhir_version = str(row.get("fhirVersion") or row.get("fhirVersion") or "").strip()
        return PackageMetadata(
            package_id=package_id,
            version=resolved_version,
            tarball=tarball,
            shasum=shasum,
            fhir_version=fhir_version,
        )

    @staticmethod
    def _verify_shasum(data: bytes, expected: str) -> None:
        if not expected:
            return
        digest = hashlib.sha1(data).hexdigest()
        if digest.lower() != expected.lower():
            raise ValueError(f"Package shasum mismatch: expected {expected}, got {digest}")

    @staticmethod
    def _read_package_json(data: bytes) -> dict[str, Any]:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
            for member in archive.getmembers():
                if member.name.endswith("package/package.json") or member.name == "package.json":
                    extracted = archive.extractfile(member)
                    if extracted is None:
                        continue
                    payload = json.loads(extracted.read().decode("utf-8"))
                    if isinstance(payload, dict):
                        return payload
        return {}

    @staticmethod
    def _parse_dependencies(package_json: dict[str, Any]) -> dict[str, str]:
        deps = package_json.get("dependencies") or {}
        if not isinstance(deps, dict):
            return {}
        parsed: dict[str, str] = {}
        for name, spec in deps.items():
            dep_id = str(name).strip()
            if not dep_id or dep_id in _SKIP_DEPENDENCIES:
                continue
            version = _normalize_dep_version(str(spec))
            if version:
                parsed[dep_id] = version
        return parsed

    async def download_package(
        self,
        package_id: str,
        version: str | None = None,
        *,
        resolve_dependencies: bool = True,
    ) -> Path:
        """Download package (and dependency closure) to FHIR_PACKAGES_PATH."""
        if not self.is_enabled():
            raise RuntimeError("FHIR_PACKAGES_PATH is not configured")

        async with self._lock:
            return await self._download_package_locked(
                package_id,
                version,
                resolve_dependencies=resolve_dependencies,
                visited=set(),
            )

    async def _download_package_locked(
        self,
        package_id: str,
        version: str | None,
        *,
        resolve_dependencies: bool,
        visited: set[str],
    ) -> Path:
        metadata = await self.fetch_metadata(package_id, version)
        ig_key = f"{metadata.package_id}#{metadata.version}"
        if ig_key in visited:
            return self.package_path(metadata.package_id, metadata.version)
        visited.add(ig_key)

        target = self.package_path(metadata.package_id, metadata.version)
        if target.is_file():
            logger.debug("Package already cached: %s", target.name)
            data = target.read_bytes()
        else:
            logger.info("Downloading FHIR package %s from %s", ig_key, metadata.tarball)
            response = await self._registry_get(metadata.tarball)
            data = response.content
            self._verify_shasum(data, metadata.shasum)
            target.write_bytes(data)
            logger.info("Cached FHIR package %s (%d bytes)", target.name, len(data))

        if resolve_dependencies:
            package_json = self._read_package_json(data)
            for dep_id, dep_version in self._parse_dependencies(package_json).items():
                await self._download_package_locked(
                    dep_id,
                    dep_version,
                    resolve_dependencies=True,
                    visited=visited,
                )

        return target

    async def ensure_package_bytes(
        self,
        package_id: str,
        version: str | None = None,
    ) -> bytes | None:
        """Return cached or freshly downloaded package bytes."""
        if not self.is_enabled():
            return None
        try:
            path = await self.download_package(package_id, version, resolve_dependencies=True)
            return path.read_bytes()
        except Exception as exc:
            logger.warning("Failed to fetch package %s: %s", package_id, exc)
            return None


def _normalize_dep_version(spec: str) -> str:
    spec = spec.strip()
    if not spec:
        return ""
    # npm-style ranges: ^6.1.0, ~1.0.0, >=4.0.1
    match = re.search(r"(\d+\.\d+\.\d+(?:[-+][\w.]+)?)", spec)
    if match:
        return match.group(1)
    return spec


@dataclass(frozen=True)
class CachedPackageRef:
    package_id: str
    version: str

    @property
    def ig_key(self) -> str:
        return f"{self.package_id}#{self.version}"


def package_ref_from_path(path: Path) -> CachedPackageRef | None:
    stem = path.stem
    if "#" not in stem:
        return None
    package_id, version = stem.split("#", 1)
    return CachedPackageRef(package_id=package_id, version=version or "")


_fetcher: IgPackageFetcher | None = None


def get_ig_package_fetcher() -> IgPackageFetcher:
    global _fetcher
    if _fetcher is None:
        from app.config import settings

        path = settings.FHIR_PACKAGES_PATH.strip()
        _fetcher = IgPackageFetcher(packages_path=Path(path) if path else None)
    return _fetcher
