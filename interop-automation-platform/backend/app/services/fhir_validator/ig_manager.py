"""
Dynamic IG package manager with ultra-fast metadata scanning and lazy loading.

Scans .tgz packages for metadata (package.json only - no full extraction),
exposes a catalog for the frontend dropdown, and loads selected IGs into
the Inferno validator wrapper on demand.
"""

import asyncio
import io
import json
import logging
import os
import tarfile
import time
from pathlib import Path
from typing import Any

from app.services.fhir_validator.ig_constants import (
    HIDDEN_IG_DEPENDENCIES,
    IG_DISPLAY,
    IG_LOAD_ORDER,
    IG_PREFERRED_VERSIONS,
    SUPPORTED_IG_PACKAGES,
)

logger = logging.getLogger(__name__)

_PACKAGES_DIR_ENV = "FHIR_PACKAGES_PATH"
_UPLOADS_DIR_ENV = "FHIR_UPLOADS_PATH"
_DEFAULT_PACKAGES_DIR = "./fhir_packages"
_METADATA_CACHE_TTL_S = 300.0


class IGManager:
    def __init__(self) -> None:
        raw = os.getenv(_PACKAGES_DIR_ENV, _DEFAULT_PACKAGES_DIR).strip()
        self._packages_dir = Path(raw)
        # fhir_packages is often Docker-mounted :ro — uploads go to a writable sibling.
        uploads_raw = os.getenv(_UPLOADS_DIR_ENV, "").strip()
        if uploads_raw:
            self._uploads_dir = Path(uploads_raw)
        else:
            self._uploads_dir = self._packages_dir.parent / "fhir_packages_uploads"
        self._metadata_cache: list[dict[str, Any]] | None = None
        self._metadata_ts: float = 0.0
        self._load_lock = asyncio.Lock()
        self._loaded_igs: dict[str, dict[str, Any]] = {}
        self._loading_in_progress: set[str] = set()

    @property
    def packages_dir(self) -> Path:
        return self._packages_dir

    @property
    def uploads_dir(self) -> Path:
        return self._uploads_dir

    def list_available_igs(self, force_refresh: bool = False) -> list[dict[str, Any]]:
        """
        Return metadata for supported user-facing IG packages (one preferred version each).
        Reads ONLY the package.json entry from each archive (fast).
        """
        all_igs = self._scan_all_packages(force_refresh)
        by_name: dict[str, list[dict[str, Any]]] = {}
        for ig in all_igs:
            name = ig.get("name") or ""
            if name not in SUPPORTED_IG_PACKAGES:
                continue
            by_name.setdefault(name, []).append(ig)

        selected: list[dict[str, Any]] = []
        for name, versions in by_name.items():
            preferred = IG_PREFERRED_VERSIONS.get(name)
            chosen = None
            if preferred:
                chosen = next((v for v in versions if str(v.get("version")) == preferred), None)
            if chosen is None:
                # Prefer highest semver-ish string; fall back to first
                chosen = sorted(versions, key=lambda v: str(v.get("version") or ""), reverse=True)[0]
            display = IG_DISPLAY.get(name) or {}
            if display.get("title"):
                chosen = {**chosen, "title": display["title"]}
            if display.get("category"):
                chosen = {**chosen, "category": display["category"]}
            selected.append(chosen)

        # Stable UI order: IG_LOAD_ORDER first, then remaining alpha by title/name
        order = {n: i for i, n in enumerate(IG_LOAD_ORDER)}
        selected.sort(
            key=lambda ig: (
                order.get(ig.get("name") or "", 10_000),
                (ig.get("title") or ig.get("name") or "").lower(),
            )
        )
        return selected

    def _package_scan_dirs(self) -> list[Path]:
        dirs = [self._packages_dir]
        extra = self._packages_dir.parent / "fhir_packages_extra"
        if extra.is_dir() and extra not in dirs:
            dirs.append(extra)
        return [d for d in dirs if d.is_dir()]

    def _scan_all_packages(self, force_refresh: bool = False) -> list[dict[str, Any]]:
        """Scan every .tgz in packages + extras directories (including hidden dependencies)."""
        now = time.monotonic()
        if (
            not force_refresh
            and self._metadata_cache is not None
            and (now - self._metadata_ts) < _METADATA_CACHE_TTL_S
        ):
            return self._metadata_cache

        scan_dirs = self._package_scan_dirs()
        if not scan_dirs:
            logger.warning("IG packages directory not found: %s", self._packages_dir)
            self._metadata_cache = []
            self._metadata_ts = now
            return []

        igs: list[dict[str, Any]] = []
        seen_files: set[str] = set()
        for directory in scan_dirs:
            for tgz_path in sorted(directory.glob("*.tgz")):
                # De-dupe identical filenames across dirs
                key = tgz_path.name.lower()
                if key in seen_files:
                    continue
                seen_files.add(key)
                meta = self._read_package_metadata(tgz_path)
                if meta:
                    igs.append(meta)

        igs.sort(key=lambda x: (x.get("name", ""), x.get("version", "")))
        self._metadata_cache = igs
        self._metadata_ts = now
        logger.info("Scanned %d IG packages from %s", len(igs), ", ".join(str(d) for d in scan_dirs))
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

                data = json.loads(fobj.read().decode("utf-8-sig"))

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

    async def load_ig(
        self,
        package_name: str,
        version: str | None = None,
        *,
        wait: bool = True,
    ) -> dict[str, Any]:
        """
        Ensure an IG is available in the Inferno validator.

        When wait=True (default), uploads synchronously and returns ready status
        with profiles — used by validate / select so results match Inferno.
        When wait=False, kicks off background upload and returns "loading".
        """
        from app.services.fhir_validator.inferno_client import inferno_client

        # Da Vinci IGs depend on HRex — warm it without blocking the selected IG upload.
        pkg_l = (package_name or "").lower()
        if "davinci-" in pkg_l and "hrex" not in pkg_l:
            hrex_ver = IG_PREFERRED_VERSIONS.get("hl7.fhir.us.davinci-hrex", "1.2.0")
            try:
                await self.load_ig("hl7.fhir.us.davinci-hrex", hrex_ver, wait=False)
            except Exception as exc:
                logger.warning("HRex dependency load skipped for %s: %s", package_name, exc)

        cache_key = f"{package_name}#{version}" if version else package_name

        cached = self._loaded_igs.get(cache_key)
        if cached and not cached.get("inferno_pending"):
            return cached

        if inferno_client._is_ig_loaded(package_name, version):
            local = self._local_resource_profiles(package_name, version)
            resolved_version = (local or {}).get("version") or version or ""
            loaded_info = self._merge_loaded_ig_info(
                package_name,
                resolved_version,
                local if local is not None else cached,
                preloaded=True,
                inferno_pending=False,
            )
            self._loaded_igs[cache_key] = loaded_info
            return loaded_info

        cached = self._loaded_igs.get(cache_key)
        if cached and not cached.get("inferno_pending"):
            return cached

        local = self._local_resource_profiles(package_name, version)
        local_profiles = list((local or {}).get("profiles") or [])
        local_version = (local or {}).get("version") or version or ""

        # UI selection (wait=False): return local resource profiles; upload IG in background.
        if not wait and (cached or local is not None):
            profiles_out = (cached or {}).get("profiles") if cached else local_profiles
            if cache_key not in self._loading_in_progress:
                self._loading_in_progress.add(cache_key)
                asyncio.create_task(self._background_load_ig(package_name, version, cache_key))
            info = self._merge_loaded_ig_info(
                package_name,
                local_version or (cached or {}).get("version") or (version or ""),
                local if local is not None else cached,
                preloaded=bool(cached),
                inferno_pending=True,
            )
            info["profiles"] = profiles_out
            return info

        # Another request is uploading — wait for it when wait=True
        if cache_key in self._loading_in_progress:
            if wait:
                for _ in range(90):
                    await asyncio.sleep(1.0)
                    if cache_key in self._loaded_igs:
                        return self._loaded_igs[cache_key]
                    if cache_key not in self._loading_in_progress:
                        break
            else:
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
            cached = self._loaded_igs.get(cache_key)
            if cached and not cached.get("inferno_pending"):
                return cached

            start = time.monotonic()

            # Never use Inferno /profiles for IG profile lists — it mixes extension SDs
            # (e.g. familymemberhistory-patient-record) with resource profiles.
            if local is not None:
                if not wait:
                    self._loading_in_progress.add(cache_key)
                    asyncio.create_task(self._background_load_ig(package_name, version, cache_key))
                    return self._merge_loaded_ig_info(
                        package_name,
                        local_version,
                        local,
                        inferno_pending=True,
                    )

            if not wait:
                self._loading_in_progress.add(cache_key)
                asyncio.create_task(self._background_load_ig(package_name, version, cache_key))
                return self._merge_loaded_ig_info(
                    package_name,
                    local_version or (version or ""),
                    local,
                    inferno_pending=True,
                )

            # wait=True: IG must exist in Inferno for accurate ?profile= validation.
            if inferno_client._is_ig_loaded(package_name, version):
                loaded_info = self._merge_loaded_ig_info(
                    package_name,
                    local_version or (version or ""),
                    local if local is not None else cached,
                    preloaded=True,
                    inferno_pending=False,
                )
                self._loaded_igs[cache_key] = loaded_info
                return loaded_info

            return await self._upload_and_cache(package_name, version, cache_key)

    async def _upload_and_cache(
        self,
        package_name: str,
        version: str | None,
        cache_key: str,
    ) -> dict[str, Any]:
        """Upload IG to Inferno and cache profile list (prefer local archive scan)."""
        from app.services.fhir_validator.fhir_loader import get_fhir_package_loader
        from app.services.fhir_validator.inferno_client import inferno_client

        self._loading_in_progress.add(cache_key)
        try:
            start = time.monotonic()

            local = self._local_resource_profiles(package_name, version)
            resolved_version = (local or {}).get("version") or version or ""

            await inferno_client.load_ig_by_id(package_name, version)
            elapsed_ms = (time.monotonic() - start) * 1000

            loaded_info = self._merge_loaded_ig_info(
                package_name,
                resolved_version,
                local,
                load_time_ms=elapsed_ms,
                preloaded=False,
                inferno_pending=False,
            )
            self._loaded_igs[cache_key] = loaded_info
            logger.info(
                "Loaded IG %s in %dms (%d resource profiles)",
                cache_key,
                round(elapsed_ms),
                len(loaded_info.get("profiles") or []),
            )
            return loaded_info
        except Exception as exc:
            logger.warning("IG load failed for %s: %s", cache_key, exc)
            raise
        finally:
            self._loading_in_progress.discard(cache_key)

    async def _background_load_ig(self, package_name: str, version: str | None, cache_key: str):
        """Upload IG to Inferno in the background."""
        try:
            await self._upload_and_cache(package_name, version, cache_key)
        except Exception:
            pass

    async def preload_all_local_igs(self) -> list[dict[str, Any]]:
        """
        Ensure all supported IGs (+ hidden dependencies) are ready in Inferno.
        Called at backend warm-up so dropdown selection and validation are instant.
        """
        available = self._scan_all_packages(force_refresh=True)
        if not available:
            return []

        loadable = {
            ig.get("name")
            for ig in available
            if ig.get("name") in SUPPORTED_IG_PACKAGES or ig.get("name") in HIDDEN_IG_DEPENDENCIES
        }

        def sort_key(ig: dict[str, Any]) -> tuple[int, str]:
            name = ig.get("name", "")
            try:
                return (IG_LOAD_ORDER.index(name), name)
            except ValueError:
                return (len(IG_LOAD_ORDER), name)

        ordered = sorted(
            [ig for ig in available if ig.get("name") in loadable],
            key=sort_key,
        )
        results: list[dict[str, Any]] = []
        for ig in ordered:
            name = ig.get("name") or ""
            version = ig.get("version") or None
            if not name:
                continue
            try:
                results.append(await self.load_ig(name, version, wait=True))
            except Exception as exc:
                logger.warning("Preload skipped for %s#%s: %s", name, version, exc)
        return results

    def get_loaded_igs(self) -> list[dict[str, Any]]:
        """Return user-facing IGs currently loaded (excludes hidden dependencies)."""
        return [
            ig
            for ig in self._loaded_igs.values()
            if ig.get("package_name") in SUPPORTED_IG_PACKAGES
        ]

    def get_profile_cache(self) -> dict[str, dict[str, Any]]:
        """Return pre-warmed profile lists keyed by package#version (for instant UI)."""
        cache: dict[str, dict[str, Any]] = {}
        for key, ig in self._loaded_igs.items():
            if ig.get("package_name") not in SUPPORTED_IG_PACKAGES:
                continue
            cache[key] = {
                "package_name": ig.get("package_name"),
                "version": ig.get("version"),
                "profiles": ig.get("profiles") or [],
                "profiles_by_type": ig.get("profiles_by_type") or {},
                "extension_count": len(ig.get("extension_urls") or []),
                "status": ig.get("status", "ready"),
                "profile_count": len(ig.get("profiles") or []),
            }
        return cache

    def _local_resource_profiles(self, package_name: str, version: str | None) -> dict[str, Any] | None:
        """Resource constraint profiles from on-disk .tgz (never extension SDs)."""
        from app.services.fhir_validator.fhir_loader import get_fhir_package_loader

        try:
            loader = get_fhir_package_loader()
            package_bytes = loader.load_package_bytes(package_name, version)
            if not package_bytes:
                return None
            extracted = self.extract_package_definitions(package_bytes)
            return {
                "profiles": list(extracted.get("profiles") or []),
                "profiles_by_type": dict(extracted.get("profiles_by_type") or {}),
                "extension_urls": list(extracted.get("extension_urls") or []),
                "version": str(extracted.get("version") or version or ""),
            }
        except Exception:
            return None

    @staticmethod
    def _merge_loaded_ig_info(
        package_name: str,
        version: str,
        local: dict[str, Any] | None,
        *,
        load_time_ms: float = 0,
        preloaded: bool = False,
        inferno_pending: bool = False,
    ) -> dict[str, Any]:
        profiles = list((local or {}).get("profiles") or [])
        return {
            "package_name": package_name,
            "version": (local or {}).get("version") or version,
            "profiles": profiles,
            "profiles_by_type": dict((local or {}).get("profiles_by_type") or {}),
            "extension_urls": list((local or {}).get("extension_urls") or []),
            "load_time_ms": round(load_time_ms),
            "loaded_at": time.time(),
            "preloaded": preloaded,
            "status": "ready",
            "inferno_pending": inferno_pending,
        }

    def warm_local_profile_cache(self) -> int:
        """
        Extract StructureDefinition profiles from local .tgz for every supported IG.
        No Inferno upload — makes IG selection instant; Inferno loads on validate.
        """
        from app.services.fhir_validator.fhir_loader import get_fhir_package_loader

        loader = get_fhir_package_loader()
        if not loader.is_enabled():
            logger.warning("Local profile warm skipped — FHIR packages path not configured")
            return 0

        packages = list(SUPPORTED_IG_PACKAGES) + list(HIDDEN_IG_DEPENDENCIES)
        warmed = 0
        for name in packages:
            version = IG_PREFERRED_VERSIONS.get(name)
            cache_key = f"{name}#{version}" if version else name
            if cache_key in self._loaded_igs:
                warmed += 1
                continue
            try:
                package_bytes = loader.load_package_bytes(name, version)
                if not package_bytes:
                    continue
                extracted = self.extract_package_definitions(package_bytes)
                profiles = list(extracted.get("profiles") or [])
                resolved_version = version or str(extracted.get("version") or "")
                self._loaded_igs[cache_key] = self._merge_loaded_ig_info(
                    name,
                    resolved_version,
                    {
                        "profiles": profiles,
                        "profiles_by_type": extracted.get("profiles_by_type") or {},
                        "extension_urls": extracted.get("extension_urls") or [],
                        "version": resolved_version,
                    },
                    preloaded=True,
                    inferno_pending=True,
                )
                warmed += 1
            except Exception as exc:
                logger.debug("Profile warm skipped for %s: %s", cache_key, exc)

        logger.info("Local profile cache warmed for %d/%d IGs", warmed, len(packages))
        return warmed

    async def ensure_inferno_ready(self, package_name: str, version: str | None = None) -> None:
        """
        Guarantee the IG package is loaded in Inferno before ?profile= validation.
        UI may show profiles from local .tgz (inferno_pending); validation must upload first.
        """
        from app.services.fhir_validator.inferno_client import inferno_client

        pkg_l = (package_name or "").lower()
        if "davinci-" in pkg_l and "hrex" not in pkg_l:
            hrex_ver = IG_PREFERRED_VERSIONS.get("hl7.fhir.us.davinci-hrex", "1.2.0")
            await self.ensure_inferno_ready("hl7.fhir.us.davinci-hrex", hrex_ver)

        if inferno_client._is_ig_loaded(package_name, version):
            cache_key = f"{package_name}#{version}" if version else package_name
            cached = self._loaded_igs.get(cache_key)
            if cached:
                cached["inferno_pending"] = False
            return

        await self.load_ig(package_name, version, wait=True)

    async def ensure_inferno_for_profiles(self, profile_urls: list[str]) -> None:
        """Load every IG required by explicit ?profile= URLs (validation hot path)."""
        seen: set[str] = set()
        for profile_url in profile_urls or []:
            from app.services.fhir_validator.inferno_client import _ig_spec_for_profile_url, _split_ig_spec

            ig_spec = _ig_spec_for_profile_url(profile_url)
            if not ig_spec:
                continue
            package_id, ver = _split_ig_spec(ig_spec)
            key = f"{package_id}#{ver or ''}"
            if key in seen:
                continue
            seen.add(key)
            await self.ensure_inferno_ready(package_id, ver)

    def is_ig_loaded(self, package_name: str, version: str | None = None) -> bool:
        cache_key = f"{package_name}#{version}" if version else package_name
        return cache_key in self._loaded_igs

    def extract_package_definitions(
        self,
        package_data: bytes | None = None,
        *,
        tgz_path: Path | None = None,
    ) -> dict[str, Any]:
        """
        Read package.json + StructureDefinition URLs from a .tgz without full extract.
        Resource profiles (kind=resource, derivation=constraint) drive Inferno ?profile=.
        Extension SDs are returned separately (Extensions Pack / THO).
        """
        if package_data is not None:
            open_kwargs: dict[str, Any] = {
                "fileobj": io.BytesIO(package_data),
                "mode": "r:gz",
            }
        elif tgz_path is not None and tgz_path.is_file():
            open_kwargs = {"name": str(tgz_path), "mode": "r:gz"}
        else:
            raise ValueError("No package data provided")

        meta: dict[str, Any] = {
            "name": "",
            "version": "",
            "title": "",
            "canonical": "",
            "profiles": [],
            "extension_urls": [],
            "profiles_by_type": {},
        }
        with tarfile.open(**open_kwargs) as tar:
            for member in tar.getmembers():
                if not member.isfile():
                    continue
                basename = os.path.basename(member.name)
                if basename == "package.json":
                    fobj = tar.extractfile(member)
                    if not fobj:
                        continue
                    data = json.loads(fobj.read().decode("utf-8-sig"))
                    meta["name"] = data.get("name") or meta["name"]
                    meta["version"] = data.get("version") or meta["version"]
                    meta["title"] = data.get("title") or data.get("name") or meta["title"]
                    meta["canonical"] = data.get("canonical") or meta["canonical"]
                    continue

                if "StructureDefinition" not in basename or not basename.endswith(".json"):
                    continue
                fobj = tar.extractfile(member)
                if not fobj:
                    continue
                try:
                    sd = json.loads(fobj.read().decode("utf-8-sig"))
                except Exception:
                    continue
                if sd.get("resourceType") != "StructureDefinition":
                    continue
                url = (sd.get("url") or "").strip()
                if not url:
                    continue
                kind = sd.get("kind")
                derivation = sd.get("derivation")
                sd_type = sd.get("type") or ""
                if kind == "resource" and derivation == "constraint":
                    meta["profiles"].append(url)
                    meta["profiles_by_type"].setdefault(sd_type, []).append(url)
                elif kind == "complex-type" and sd_type == "Extension":
                    meta["extension_urls"].append(url)

        # De-dupe while preserving order
        meta["profiles"] = list(dict.fromkeys(meta["profiles"]))
        meta["extension_urls"] = list(dict.fromkeys(meta["extension_urls"]))
        for rt, urls in list(meta["profiles_by_type"].items()):
            meta["profiles_by_type"][rt] = list(dict.fromkeys(urls))
        return meta

    def persist_uploaded_package(self, package_data: bytes, *, package_name: str, version: str) -> Path:
        """Save uploaded .tgz to a writable uploads dir (fhir_packages is often :ro)."""
        self._uploads_dir.mkdir(parents=True, exist_ok=True)
        safe_name = (package_name or "custom.ig").replace("/", ".")
        safe_version = version or "0.0.0"
        dest = self._uploads_dir / f"{safe_name}-{safe_version}.tgz"
        dest.write_bytes(package_data)
        self._metadata_cache = None
        return dest

    async def ingest_uploaded_package(
        self,
        package_data: bytes,
        filename: str | None = None,
    ) -> dict[str, Any]:
        """
        Upload a custom IG to Inferno, extract profiles from the archive, and cache
        them so validation can send the same ?profile= URLs as Inferno Advanced.
        """
        from app.services.fhir_validator.inferno_client import inferno_client

        extracted = self.extract_package_definitions(package_data)
        package_name = extracted.get("name") or (filename or "custom.ig").replace(".tgz", "").replace(".tar.gz", "")
        version = extracted.get("version") or "0.0.0"
        title = extracted.get("title") or package_name

        try:
            self.persist_uploaded_package(package_data, package_name=package_name, version=version)
        except Exception as exc:
            logger.warning("Could not persist uploaded package: %s", exc)

        start = time.monotonic()
        inferno_result = await inferno_client.upload_custom_ig(package_data)
        inferno_client._register_loaded_ig(package_name, version, inferno_result)

        # Prefer archive-extracted resource profiles; fall back to Inferno /profiles
        # only for normal resource IGs (never for extensions/terminology packs — their
        # URL heuristics would match unrelated core StructureDefinitions).
        profiles = list(extracted.get("profiles") or [])
        pkg_lower = package_name.lower()
        is_support_pack = "extensions" in pkg_lower or "terminology" in pkg_lower
        if not profiles and not is_support_pack:
            try:
                all_profiles = await inferno_client.get_profiles()
                profiles = [p for p in all_profiles if _profile_belongs_to_ig(p, package_name)]
            except Exception:
                profiles = []

        # Extensions / THO packages: expose extension URLs so the UI can still show readiness.
        if not profiles and extracted.get("extension_urls"):
            # Do not send Extension SD URLs as ?profile= for Patient/etc.
            # Keep them available for membership checks / documentation only.
            pass

        elapsed_ms = (time.monotonic() - start) * 1000
        cache_key = f"{package_name}#{version}"
        loaded_info = {
            "package_name": package_name,
            "version": version,
            "title": title,
            "canonical": extracted.get("canonical") or "",
            "profiles": profiles,
            "extension_urls": extracted.get("extension_urls") or [],
            "profiles_by_type": extracted.get("profiles_by_type") or {},
            "load_time_ms": round(elapsed_ms),
            "loaded_at": time.time(),
            "preloaded": False,
            "status": "ready",
            "uploaded": True,
            "filename": filename or "",
            "inferno": {
                "id": inferno_result.get("id") or inferno_result.get("package_id") or package_name,
                "version": inferno_result.get("version") or version,
            },
        }
        self._loaded_igs[cache_key] = loaded_info
        logger.info(
            "Uploaded custom IG %s (%d resource profiles, %d extensions) in %dms",
            cache_key,
            len(profiles),
            len(loaded_info["extension_urls"]),
            round(elapsed_ms),
        )
        return loaded_info


def _profile_belongs_to_ig(profile_url: str, package_name: str) -> bool:
    """Match profile URLs to IG package names using canonical URL patterns."""
    url_lower = (profile_url or "").lower().split("|", 1)[0]
    pkg = (package_name or "").lower()
    if not url_lower or not pkg:
        return False

    needles: list[str] = []
    if "us.core" in pkg or "us-core" in pkg:
        needles = ["/us/core/"]
    elif "davinci-hrex" in pkg:
        needles = ["/davinci-hrex/"]
    elif "davinci-crd" in pkg:
        needles = ["/davinci-crd/"]
    elif "davinci-dtr" in pkg:
        needles = ["/davinci-dtr/"]
    elif "davinci-pas" in pkg:
        needles = ["/davinci-pas/"]
    elif "davinci-pdex" in pkg and "plan-net" not in pkg:
        needles = ["/davinci-pdex/", "davinci-pdex"]
    elif "davinci-cdex" in pkg:
        needles = ["/davinci-cdex/", "davinci-cdex"]
    elif "davinci-pcde" in pkg:
        needles = ["/davinci-pcde/", "davinci-pcde"]
    elif "davinci-alerts" in pkg:
        needles = ["/davinci-alerts/", "davinci-alerts"]
    elif "drug-formulary" in pkg:
        needles = ["drug-formulary", "davinci-drug-formulary"]
    elif "davinci-deqm" in pkg:
        needles = ["/davinci-deqm/", "davinci-deqm"]
    elif "davinci-ra" in pkg:
        needles = ["/davinci-ra/", "davinci-ra"]
    elif "uv.sdc" in pkg or pkg.endswith(".sdc"):
        needles = ["/uv/sdc/"]
    elif "uv.ipa" in pkg or pkg.endswith(".ipa"):
        needles = ["/uv/ipa/"]
    elif "uv.ips" in pkg or pkg.endswith(".ips"):
        needles = ["/uv/ips/"]
    elif "smart-app-launch" in pkg:
        needles = ["smart-app-launch", "/uv/smart-app-launch"]
    elif "mcode" in pkg:
        needles = ["/us/mcode/"]
    elif "carin-bb" in pkg or "carin.bb" in pkg:
        needles = ["/us/carin-bb/", "carin-bb"]
    elif "qicore" in pkg:
        needles = ["/us/qicore/"]
    elif "ccda" in pkg:
        needles = ["/us/ccda/", "ccda"]
    elif "bulkdata" in pkg or "bulk-data" in pkg:
        needles = ["bulkdata", "bulk-data"]
    elif ".odh" in pkg or pkg.endswith("odh"):
        needles = ["/us/odh/", "odh"]
    elif "military-service" in pkg:
        needles = ["military-service"]
    elif "vrdr" in pkg:
        needles = ["/us/vrdr/", "vrdr"]
    elif "ecr" in pkg and "davinci" not in pkg:
        needles = ["/us/ecr/", "/ecr/"]
    elif "pacio-adi" in pkg:
        needles = ["pacio-adi"]
    elif "pacio-cs" in pkg:
        needles = ["pacio-cs"]
    elif "pacio-fs" in pkg:
        needles = ["pacio-fs"]
    elif "extensions" in pkg:
        needles = ["/uv/extensions/"]
    elif "terminology" in pkg:
        needles = ["terminology.hl7.org"]

    if needles:
        return any(n in url_lower for n in needles)

    parts = [p for p in pkg.replace("hl7.fhir.", "").replace("hl7.", "").split(".") if p]
    parts = [p for p in parts if p not in {"r4", "r4b", "r5", "fhir"}]
    if len(parts) >= 2:
        needle = f"/{parts[-2]}/{parts[-1]}/"
        if needle in url_lower:
            return True
    if parts:
        token = parts[-1]
        if len(token) >= 3 and token in url_lower:
            return True
    return False


ig_manager = IGManager()
