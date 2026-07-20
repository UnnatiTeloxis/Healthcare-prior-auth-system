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
        self._load_started_at: dict[str, float] = {}
        # Inferno can only usefully install one IG at a time; queue the rest.
        self._inferno_install_sem = asyncio.Semaphore(1)

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
                sd_count = 0
                for member in tar.getmembers():
                    basename = os.path.basename(member.name)
                    if basename == "package.json" and member.isfile() and pkg_member is None:
                        pkg_member = member
                    # Fast count: StructureDefinition-*.json files (exclude examples)
                    name_lower = member.name.lower().replace("\\", "/")
                    if (
                        member.isfile()
                        and "structuredefinition" in basename.lower()
                        and name_lower.endswith(".json")
                        and "/example" not in name_lower
                    ):
                        sd_count += 1

                if not pkg_member:
                    return None

                fobj = tar.extractfile(pkg_member)
                if not fobj:
                    return None

                data = json.loads(fobj.read().decode("utf-8"))

                fhir_versions = data.get("fhirVersion")
                if isinstance(fhir_versions, str):
                    fhir_versions = [fhir_versions]

                package_id = data.get("name", "")
                return {
                    "package_id": package_id,
                    "name": package_id,
                    "version": data.get("version", ""),
                    "title": data.get("title") or package_id,
                    "description": data.get("description", ""),
                    "fhir_versions": fhir_versions or ["4.0.1"],
                    "fhir_version": (fhir_versions or ["4.0.1"])[0],
                    "filename": filepath.name,
                    "canonical": data.get("canonical", ""),
                    "dependencies": data.get("dependencies", {}),
                    "cached": True,
                    "source": "local",
                    "structure_definition_count": sd_count,
                    "is_profile_ig": sd_count > 0,
                }
        except Exception as exc:
            logger.warning("Failed reading metadata from %s: %s", filepath, exc)
            return None

    def _local_structure_definition_count(self, package_name: str, version: str | None) -> int | None:
        """Return SD count for a local package, or None if not found locally.

        Reads only the one resolved .tgz — never triggers a full directory scan,
        which takes minutes over the Docker bind mount and blocks the event loop.
        """
        from app.services.fhir_validator.fhir_loader import get_fhir_package_loader

        loader = get_fhir_package_loader()
        path = loader.resolve_package_path(package_name, version)
        if not path:
            return None
        meta = self._read_package_metadata(path)
        if not meta:
            return None
        return int(meta.get("structure_definition_count") or 0)

    @staticmethod
    def _resolve_local_version(package_name: str, version: str | None) -> str | None:
        """Pick a locally cached version when the catalog version is missing or not on disk."""
        from app.services.fhir_validator.ig_package_fetcher import get_ig_package_fetcher

        fetcher = get_ig_package_fetcher()
        if not fetcher.is_enabled():
            return version
        if version and fetcher.is_cached(package_name, version):
            return version
        cached = fetcher.list_cached_versions(package_name)
        return cached[0] if cached else version

    async def load_ig(self, package_name: str, version: str | None = None) -> dict[str, Any]:
        """
        Ensure an IG is available in the Inferno validator.
        Returns instantly if pre-loaded. For on-demand IGs, starts background
        upload and returns a "loading" status. Frontend should poll or retry.
        """
        from app.services.fhir_validator.inferno_client import inferno_client

        version = self._resolve_local_version(package_name, version)
        cache_key = f"{package_name}#{version}" if version else package_name

        if cache_key in self._loaded_igs:
            return self._loaded_igs[cache_key]

        # Check if IG is currently being loaded in background
        if cache_key in self._loading_in_progress:
            stale = self._is_stale_loading(cache_key)
            if stale:
                return stale
            return {
                "package_id": package_name,
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

            # Skip Inferno entirely for local packages with zero StructureDefinitions
            # (mapping/example IGs). Installing them can take minutes downloading
            # terminology and still yields an empty profile list.
            sd_count = await asyncio.to_thread(
                self._local_structure_definition_count, package_name, version
            )
            if sd_count == 0:
                loaded_info = {
                    "package_id": package_name,
                    "package_name": package_name,
                    "version": version or "",
                    "profiles": [],
                    "load_time_ms": 0,
                    "loaded_at": time.time(),
                    "preloaded": False,
                    "status": "ready",
                    "error": (
                        f"{package_name} has no StructureDefinition profiles "
                        "(mapping/examples/terminology package). Choose US Core for profile validation."
                    ),
                }
                self._loaded_igs[cache_key] = loaded_info
                logger.info("Skipping Inferno install for non-profile IG %s", cache_key)
                return loaded_info

            start = time.monotonic()

            # Fast path: profiles already present in Inferno for this IG
            try:
                ig_profiles = await inferno_client.profiles_for_package(package_name, version)

                if ig_profiles:
                    elapsed_ms = (time.monotonic() - start) * 1000
                    loaded_info = {
                        "package_id": package_name,
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
            self._load_started_at[cache_key] = time.monotonic()
            asyncio.create_task(self._background_load_ig(package_name, version, cache_key))

            return {
                "package_id": package_name,
                "package_name": package_name,
                "version": version or "",
                "profiles": [],
                "load_time_ms": 0,
                "loaded_at": 0,
                "preloaded": False,
                "status": "loading",
            }

    def _is_stale_loading(self, cache_key: str) -> dict[str, Any] | None:
        """Fail IG loads that exceed IG_INSTALL_TIMEOUT so the UI can recover."""
        from app.config import settings

        started = self._load_started_at.get(cache_key)
        if not started:
            return None
        elapsed = time.monotonic() - started
        if elapsed < settings.IG_INSTALL_TIMEOUT:
            return None

        package_name, _, version = cache_key.partition("#")
        failed_info = {
            "package_id": package_name,
            "package_name": package_name,
            "version": version,
            "profiles": [],
            "load_time_ms": round(elapsed * 1000),
            "loaded_at": time.time(),
            "preloaded": False,
            "status": "failed",
            "error": (
                f"IG install timed out after {int(elapsed)}s. "
                "Inferno may still be busy — wait a minute and select the IG again."
            ),
        }
        self._loaded_igs[cache_key] = failed_info
        self._loading_in_progress.discard(cache_key)
        self._load_started_at.pop(cache_key, None)
        logger.warning("IG load timed out for %s after %.0fs", cache_key, elapsed)
        return failed_info

    async def _ensure_local_package_cache(self, package_name: str, version: str | None) -> None:
        """Download catalog IGs to fhir_packages/ so Inferno can upload local .tgz."""
        from app.config import settings
        from app.services.fhir_validator.ig_package_fetcher import get_ig_package_fetcher

        if not settings.AUTO_CACHE_CATALOG_IGS:
            return

        fetcher = get_ig_package_fetcher()
        if not fetcher.is_enabled():
            return

        resolved_version = version or ""
        if resolved_version and fetcher.is_cached(package_name, resolved_version):
            return
        if not resolved_version and fetcher.has_any_cached_version(package_name):
            return

        try:
            logger.info(
                "Caching %s from packages.fhir.org before Inferno install",
                f"{package_name}#{version or 'latest'}",
            )
            await fetcher.download_package(package_name, version, resolve_dependencies=True)
            self._metadata_cache = None
        except Exception as exc:
            logger.warning("Could not cache %s locally (%s); Inferno will download directly", package_name, exc)

    async def _install_ig_to_inferno(
        self,
        package_name: str,
        version: str | None,
    ) -> dict[str, Any]:
        from app.services.fhir_validator.inferno_client import inferno_client

        start = time.monotonic()
        result = await inferno_client.load_ig_by_id(package_name, version)
        ig_profiles = await inferno_client.profiles_for_package(
            package_name,
            version,
            load_result=result if isinstance(result, dict) else None,
        )
        elapsed_ms = (time.monotonic() - start) * 1000
        return {
            "result": result,
            "profiles": ig_profiles,
            "elapsed_ms": elapsed_ms,
        }

    async def _background_load_ig(self, package_name: str, version: str | None, cache_key: str):
        """Upload IG to Inferno in the background."""
        from app.config import settings

        try:
            await self._ensure_local_package_cache(package_name, version)

            async with self._inferno_install_sem:
                install = await asyncio.wait_for(
                    self._install_ig_to_inferno(package_name, version),
                    timeout=float(settings.IG_INSTALL_TIMEOUT),
                )

                loaded_info = {
                    "package_id": package_name,
                    "package_name": package_name,
                    "version": version or install["result"].get("version", ""),
                    "profiles": install["profiles"],
                    "load_time_ms": round(install["elapsed_ms"]),
                    "loaded_at": time.time(),
                    "preloaded": False,
                    "status": "ready",
                }
                self._loaded_igs[cache_key] = loaded_info
                logger.info(
                    "Background loaded IG %s in %dms (%d profiles)",
                    cache_key,
                    round(install["elapsed_ms"]),
                    len(install["profiles"]),
                )
        except asyncio.TimeoutError:
            logger.warning("Background IG load timed out for %s", cache_key)
            self._loaded_igs[cache_key] = {
                "package_id": package_name,
                "package_name": package_name,
                "version": version or "",
                "profiles": [],
                "load_time_ms": settings.IG_INSTALL_TIMEOUT * 1000,
                "loaded_at": time.time(),
                "preloaded": False,
                "status": "failed",
                "error": (
                    f"Inferno install timed out after {settings.IG_INSTALL_TIMEOUT}s. "
                    "Try again in a minute — first-time installs download dependencies."
                ),
            }
        except Exception as exc:
            logger.warning("Background IG load failed for %s: %s", cache_key, exc)
            self._loaded_igs[cache_key] = {
                "package_id": package_name,
                "package_name": package_name,
                "version": version or "",
                "profiles": [],
                "load_time_ms": 0,
                "loaded_at": time.time(),
                "preloaded": False,
                "status": "failed",
                "error": str(exc),
            }
        finally:
            self._loading_in_progress.discard(cache_key)
            self._load_started_at.pop(cache_key, None)

    def get_loaded_igs(self) -> list[dict[str, Any]]:
        """Return list of currently loaded IGs."""
        return list(self._loaded_igs.values())

    def is_ig_loaded(self, package_name: str, version: str | None = None) -> bool:
        cache_key = f"{package_name}#{version}" if version else package_name
        return cache_key in self._loaded_igs

    def clear_loaded_ig(self, package_name: str, version: str | None = None) -> None:
        """Drop cached load state so the next load attempt starts fresh."""
        cache_key = f"{package_name}#{version}" if version else package_name
        self._loaded_igs.pop(cache_key, None)
        self._loading_in_progress.discard(cache_key)
        self._load_started_at.pop(cache_key, None)

    def reset_loaded_state(self) -> None:
        """Clear in-memory IG load cache (e.g. before a fresh preload run)."""
        self._loaded_igs.clear()
        self._loading_in_progress.clear()
        self._load_started_at.clear()

    async def preload_all_local_igs(self) -> dict[str, int]:
        """
        Sequentially upload curated popular local IGs into Inferno.

        Only preloads the UI's POPULAR_IGS list (not every .tgz on disk).
        Skips terminology/core/extension dependency packages and non-profile IGs.
        """
        from app.config import settings
        from app.services.fhir_validator.inferno_client import inferno_client
        from app.services.fhir_validator.local_ig_catalog import local_ig_catalog

        if not inferno_client.engine_is_warm:
            logger.warning("IG preload skipped: Inferno engine is not ready yet")
            return {"total": 0, "loaded": 0, "skipped": 0, "failed": 0}

        # Only curated popular IGs — full catalog (~144) is available on demand.
        entries = local_ig_catalog.list_popular_cached()
        if not entries:
            logger.warning("Local IG preload skipped: no curated packages in fhir_packages/")
            return {"total": 0, "loaded": 0, "skipped": 0, "failed": 0}

        # Drop stale failed entries from prior sessions.
        self.reset_loaded_state()

        def _sort_key(entry) -> tuple:
            pid = entry.package_id.lower()
            priority = 9
            if "us.core" in pid:
                priority = 0
            elif "davinci" in pid:
                priority = 1
            elif pid.startswith("hl7.fhir.us."):
                priority = 2
            elif pid.startswith("hl7.fhir.uv."):
                priority = 3
            return (priority, entry.name.lower())

        entries = sorted(entries, key=_sort_key)
        total = len(entries)
        loaded = skipped = failed = 0

        logger.info("Preloading %d curated IG packages into Inferno (sequential)", total)
        for index, entry in enumerate(entries, start=1):
            package_id = entry.package_id
            version = entry.cached_version
            if _should_skip_preload_package(package_id):
                skipped += 1
                continue

            cache_key = f"{package_id}#{version}"
            # Do not call _local_structure_definition_count here — it scans every
            # .tgz on disk and blocks the async event loop for minutes.

            try:
                async with self._inferno_install_sem:
                    install = await asyncio.wait_for(
                        self._install_ig_to_inferno(package_id, version),
                        timeout=float(settings.IG_INSTALL_TIMEOUT),
                    )
                    elapsed_ms = install["elapsed_ms"]
                    ig_profiles = install["profiles"]
                    result = install["result"]
                    self._loaded_igs[cache_key] = {
                        "package_id": package_id,
                        "package_name": package_id,
                        "version": version or result.get("version", ""),
                        "profiles": ig_profiles,
                        "load_time_ms": round(elapsed_ms),
                        "loaded_at": time.time(),
                        "preloaded": True,
                        "status": "ready",
                    }
                loaded += 1
                logger.info(
                    "Preloaded IG %s/%s %s (%dms, %d profiles)",
                    index,
                    total,
                    cache_key,
                    round(elapsed_ms),
                    len(ig_profiles),
                )
            except asyncio.TimeoutError:
                failed += 1
                logger.warning("Preload timed out for %s after %ss", cache_key, settings.IG_INSTALL_TIMEOUT)
            except Exception as exc:
                failed += 1
                logger.warning("Preload failed for %s: %s", cache_key, exc)

        summary = {"total": total, "loaded": loaded, "skipped": skipped, "failed": failed}
        logger.info("Local IG preload finished: %s", summary)
        return summary


_SKIP_PRELOAD_PREFIXES = (
    "hl7.terminology",
    "hl7.fhir.r4.core",
    "hl7.fhir.r4b.core",
    "hl7.fhir.r5.core",
    "us.nlm.vsac",
    "fhir.dicom",
    "hl7.fhir.uv.extensions",
    "hl7.fhir.uv.xver",
    "us.cdc.phinvads",
)

# Huge dependency-only packages — skip explicit preload (Inferno pulls deps as needed).
_SKIP_PRELOAD_EXACT = frozenset({
    "hl7.fhir.uv.extensions",
    "hl7.fhir.uv.extensions.r4",
    "hl7.fhir.uv.extensions.r5",
    "hl7.fhir.us.bulkdata",
    "hl7.fhir.uv.bulkdata",
})


def _should_skip_preload_package(package_id: str) -> bool:
    lowered = package_id.lower()
    if lowered in _SKIP_PRELOAD_EXACT:
        return True
    return any(lowered.startswith(prefix) for prefix in _SKIP_PRELOAD_PREFIXES)


def _profile_belongs_to_ig(profile_url: str, package_name: str) -> bool:
    """Match profile URLs to IG package names using canonical URL patterns."""
    url_lower = profile_url.lower()
    pkg = package_name.lower()
    if "us.core" in pkg or "us-core" in pkg:
        return "/us/core/" in url_lower
    if "davinci-crd" in pkg or "davinci.crd" in pkg:
        return "/davinci-crd/" in url_lower
    if "davinci-dtr" in pkg or "davinci.dtr" in pkg:
        return "/davinci-dtr/" in url_lower
    if "davinci-pas" in pkg or "davinci.pas" in pkg:
        return "/davinci-pas/" in url_lower
    if "ccda" in pkg:
        return "/ccda/" in url_lower or "/c-cda/" in url_lower
    if "davinci-ra" in pkg or "davinci.ra" in pkg:
        return "/davinci-ra/" in url_lower or "/davinci/ra/" in url_lower
    # Generic fallback: last package segment often appears in the profile path.
    slug = pkg.rsplit(".", 1)[-1].replace("_", "-")
    if slug and len(slug) > 2:
        return slug in url_lower
    return False


ig_manager = IGManager()
