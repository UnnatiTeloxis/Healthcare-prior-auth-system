"""
Dynamic IG package manager with ultra-fast metadata scanning and lazy loading.

Scans .tgz packages for metadata (package.json only - no full extraction),
exposes a catalog for the frontend dropdown, and loads selected IGs into
the Inferno validator wrapper on demand.
"""

import asyncio
import json
import logging
import os
import tarfile
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_PACKAGES_DIR_ENV = "FHIR_PACKAGES_PATH"
_DEFAULT_PACKAGES_DIR = "./fhir_packages"
_METADATA_CACHE_TTL_S = 300.0


class IGManager:
    def __init__(self) -> None:
        raw = os.getenv(_PACKAGES_DIR_ENV, _DEFAULT_PACKAGES_DIR).strip()
        self._packages_dir = Path(raw)
        self._metadata_cache: list[dict[str, Any]] | None = None
        self._metadata_ts: float = 0.0
        self._load_lock = asyncio.Lock()
        self._loaded_igs: dict[str, dict[str, Any]] = {}
        self._loading_in_progress: set[str] = set()

    @property
    def packages_dir(self) -> Path:
        return self._packages_dir

    def list_available_igs(self, force_refresh: bool = False) -> list[dict[str, Any]]:
        """
        Return metadata for all .tgz packages in the packages directory.
        Reads ONLY the package.json entry from each archive (fast).
        Results are cached for 5 minutes.
        """
        now = time.monotonic()
        if (
            not force_refresh
            and self._metadata_cache is not None
            and (now - self._metadata_ts) < _METADATA_CACHE_TTL_S
        ):
            return self._metadata_cache

        if not self._packages_dir.is_dir():
            logger.warning("IG packages directory not found: %s", self._packages_dir)
            self._metadata_cache = []
            self._metadata_ts = now
            return []

        igs: list[dict[str, Any]] = []
        for tgz_path in sorted(self._packages_dir.glob("*.tgz")):
            meta = self._read_package_metadata(tgz_path)
            if meta:
                igs.append(meta)

        igs.sort(key=lambda x: (x.get("name", ""), x.get("version", "")))
        self._metadata_cache = igs
        self._metadata_ts = now
        logger.info("Scanned %d IG packages from %s", len(igs), self._packages_dir)
        return igs

    def _read_package_metadata(self, filepath: Path) -> dict[str, Any] | None:
        """Read package.json from .tgz without extracting the entire archive."""
        try:
            with tarfile.open(filepath, "r:gz") as tar:
                pkg_member = None
                for member in tar.getmembers():
                    basename = os.path.basename(member.name)
                    if basename == "package.json" and member.isfile():
                        pkg_member = member
                        break

                if not pkg_member:
                    return None

                fobj = tar.extractfile(pkg_member)
                if not fobj:
                    return None

                data = json.loads(fobj.read().decode("utf-8"))

                fhir_versions = data.get("fhirVersion")
                if isinstance(fhir_versions, str):
                    fhir_versions = [fhir_versions]

                return {
                    "name": data.get("name", ""),
                    "version": data.get("version", ""),
                    "title": data.get("title") or data.get("name", ""),
                    "description": data.get("description", ""),
                    "fhir_versions": fhir_versions or ["4.0.1"],
                    "filename": filepath.name,
                    "canonical": data.get("canonical", ""),
                    "dependencies": data.get("dependencies", {}),
                }
        except Exception as exc:
            logger.warning("Failed reading metadata from %s: %s", filepath, exc)
            return None

    async def load_ig(self, package_name: str, version: str | None = None) -> dict[str, Any]:
        """
        Ensure an IG is available in the Inferno validator.
        Returns instantly if pre-loaded. For on-demand IGs, starts background
        upload and returns a "loading" status. Frontend should poll or retry.
        """
        from app.services.fhir_validator.inferno_client import inferno_client

        cache_key = f"{package_name}#{version}" if version else package_name

        if cache_key in self._loaded_igs:
            return self._loaded_igs[cache_key]

        # Check if IG is currently being loaded in background
        if cache_key in self._loading_in_progress:
            return {
                "package_name": package_name,
                "version": version or "",
                "profiles": [],
                "load_time_ms": 0,
                "loaded_at": 0,
                "preloaded": False,
                "status": "loading",
            }

        async with self._load_lock:
            if cache_key in self._loaded_igs:
                return self._loaded_igs[cache_key]

            start = time.monotonic()

            # Fast path: check if profiles for this IG already exist in Inferno
            try:
                profiles = await inferno_client.get_profiles()
                ig_profiles = [p for p in profiles if _profile_belongs_to_ig(p, package_name)]

                if ig_profiles:
                    elapsed_ms = (time.monotonic() - start) * 1000
                    loaded_info = {
                        "package_name": package_name,
                        "version": version or "",
                        "profiles": ig_profiles,
                        "load_time_ms": round(elapsed_ms),
                        "loaded_at": time.time(),
                        "preloaded": True,
                        "status": "ready",
                    }
                    self._loaded_igs[cache_key] = loaded_info
                    inferno_client._register_loaded_ig(package_name, version)
                    logger.info(
                        "IG %s ready (%dms, %d profiles)",
                        cache_key, round(elapsed_ms), len(ig_profiles),
                    )
                    return loaded_info
            except Exception:
                pass

            # Slow path: start background upload
            self._loading_in_progress.add(cache_key)
            asyncio.create_task(self._background_load_ig(package_name, version, cache_key))

            return {
                "package_name": package_name,
                "version": version or "",
                "profiles": [],
                "load_time_ms": 0,
                "loaded_at": 0,
                "preloaded": False,
                "status": "loading",
            }

    async def _background_load_ig(self, package_name: str, version: str | None, cache_key: str):
        """Upload IG to Inferno in the background."""
        from app.services.fhir_validator.inferno_client import inferno_client

        try:
            start = time.monotonic()
            result = await inferno_client.load_ig_by_id(package_name, version)
            profiles = await inferno_client.get_profiles()
            ig_profiles = [p for p in profiles if _profile_belongs_to_ig(p, package_name)]
            elapsed_ms = (time.monotonic() - start) * 1000

            loaded_info = {
                "package_name": package_name,
                "version": version or result.get("version", ""),
                "profiles": ig_profiles,
                "load_time_ms": round(elapsed_ms),
                "loaded_at": time.time(),
                "preloaded": False,
                "status": "ready",
            }
            self._loaded_igs[cache_key] = loaded_info
            logger.info("Background loaded IG %s in %dms (%d profiles)", cache_key, round(elapsed_ms), len(ig_profiles))
        except Exception as exc:
            logger.warning("Background IG load failed for %s: %s", cache_key, exc)
        finally:
            self._loading_in_progress.discard(cache_key)

    def get_loaded_igs(self) -> list[dict[str, Any]]:
        """Return list of currently loaded IGs."""
        return list(self._loaded_igs.values())

    def is_ig_loaded(self, package_name: str, version: str | None = None) -> bool:
        cache_key = f"{package_name}#{version}" if version else package_name
        return cache_key in self._loaded_igs


def _profile_belongs_to_ig(profile_url: str, package_name: str) -> bool:
    """Match profile URLs to IG package names using canonical URL patterns."""
    url_lower = profile_url.lower()
    if "us.core" in package_name or "us-core" in package_name:
        return "/us/core/" in url_lower
    if "davinci-crd" in package_name or "davinci.crd" in package_name:
        return "/davinci-crd/" in url_lower
    if "davinci-dtr" in package_name or "davinci.dtr" in package_name:
        return "/davinci-dtr/" in url_lower
    if "davinci-pas" in package_name or "davinci.pas" in package_name:
        return "/davinci-pas/" in url_lower
    return False


ig_manager = IGManager()
